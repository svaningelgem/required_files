import os
import re
import subprocess
import tempfile
from abc import ABC, abstractmethod
from logging import getLogger
from os import PathLike
from pathlib import Path
from typing import BinaryIO, Union
from urllib.parse import urljoin

import bs4
import requests

try:
    from requests_file import FileAdapter
except ImportError:  # pragma: no cover
    FileAdapter = None


LOGGER = getLogger('required-files')
LOGGER.setLevel('INFO')


class Required(ABC):
    @abstractmethod
    def check(self) -> Union[str, Path]:
        """
        This method fires of the downloading/checking.
        It should be implemented in any class that is considered 'Required'

        :returns: string, depending on the implementation, but mostly a filename or a path.
        """


class RequiredCommand(Required):
    """Checks if we can execute a certain command."""

    def __init__(self, *command):
        self.command = command

    def check(self) -> Union[str, Path]:
        try:
            subprocess.run(self.command)
        except Exception as e:
            raise ValueError(str(e))

        return self.command[0]


class RequiredFile(Required):
    def __init__(self, url: str, save_as: Union[str, os.PathLike]):
        self.url = url
        self.filename = Path(save_as)
        self._create_directories()

    def _create_directories(self):
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)

    def _is_file_present(self):
        return os.path.exists(self.filename)

    @staticmethod
    def _download_to_tmpfile(url: str):
        tmp_fp = tempfile.TemporaryFile('wb+')
        try:
            RequiredFile._download(url, tmp_fp)
        except ValueError:
            tmp_fp.close()
            raise

        tmp_fp.seek(0)
        return tmp_fp

    @staticmethod
    def _download(url, save_to: Union[str, os.PathLike, BinaryIO]) -> None:
        with requests.Session() as s:
            if FileAdapter:
                s.mount('file://', FileAdapter())

            r = s.get(url)
            if not r:
                raise ValueError(r.content.decode('utf8'))

            if isinstance(save_to, str) or isinstance(save_to, PathLike):
                with open(save_to, 'wb') as fp:
                    fp.write(r.content)
            else:
                save_to.write(r.content)

    def _return_result(self):
        return Path(self.filename).absolute()

    def check(self) -> Union[str, Path]:
        if not self._is_file_present():
            self._download(self.url, self.filename)

        return self._return_result()


class ZipfileMixin:
    # Multiple inheritance can't handle different arguments to __init__, so I prefer to do it this way.
    #   That way it's clear which arguments are needed.
    def _zip_init(self, file_to_check):
        self.file_to_check = file_to_check

    @staticmethod
    def _has_initial_dir(all_files: list) -> bool:
        """
        Checks if the first reference in the zip file is the initial dir for ALL the files?
        """
        initial_dir = all_files[0]
        if initial_dir[-1] != '/':  # First entry is NOT a dir?
            return False

        initial_dir_l = len(initial_dir)

        for fname in all_files:
            if fname[0:initial_dir_l] != initial_dir:
                return False

        return True

    @staticmethod
    def _process_zip(zip_in, into_dir: Path, skip_initial_dir: bool = True) -> None:
        """
        Extracts all contents of a zip file into a directory.

        :param zip_in: Pathlike|file pointer|file name
        :param into_dir: where to extract it in.
        :param skip_initial_dir: skip the initial dir or not?
        :return:
        """
        import zipfile

        with zipfile.ZipFile(zip_in) as zip_ref:
            all_files = zip_ref.namelist()
            if skip_initial_dir and __class__._has_initial_dir(all_files):
                initial_dir_l = len(all_files[0])
                for filename in all_files[1:]:
                    tgt = into_dir / filename[initial_dir_l:]

                    if filename[-1] == '/':
                        os.makedirs(tgt, exist_ok=True)
                    else:
                        with zip_ref.open(filename, mode='r') as zip_fp:
                            with open(tgt, mode='wb') as fp:
                                fp.write(zip_fp.read())
            else:
                zip_ref.extractall(into_dir)

        zip_in.close()

    def _create_directories(self):
        os.makedirs(self.filename, exist_ok=True)

    def _is_file_present(self):
        return os.path.exists(Path(self.filename) / self.file_to_check)


class RequiredZipFile(ZipfileMixin, RequiredFile):
    """
    Download a ZIP file from a certain URL.
    """

    def __init__(self, url, save_as, file_to_check, skip_initial_dir=True):
        """
        Download a zip and extract it.

        :param url: The URL to download
        :param save_as: Save into this directory
        :param file_to_check: To quickly check if we already downloaded this zip?
        :param skip_initial_dir: Oftentimes in a zip there is a single root directory. Ignore this when extracting?
        """
        super().__init__(url, save_as)
        self._zip_init(file_to_check)
        self.skip_initial_dir = skip_initial_dir

    def check(self) -> Union[str, Path]:
        if not self._is_file_present():
            self._process_zip(
                self._download_to_tmpfile(self.url), into_dir=self.filename, skip_initial_dir=self.skip_initial_dir
            )

        return self._return_result()


class RequiredLatestFromWebMixin(ABC):
    @abstractmethod
    def _get_real_url(self, soup: bs4.BeautifulSoup):
        """Returns the real URL based on a parsed HTML file."""

    @abstractmethod
    def _should_i_skip_this_filename(self, filename):
        """Checks if the filename is OK to use."""

    def figure_out_url(self, url):
        r = requests.get(url)
        soup = bs4.BeautifulSoup(r.content, features='lxml')
        return self._get_real_url(soup)

    def check(self) -> Union[str, Path]:
        if not self._is_file_present():
            self.url = self.figure_out_url(self.url)

        return super().check()


class BitBucketURLRetrieverMixin:
    def _get_real_url(self, soup: bs4.BeautifulSoup):
        for entry in soup.select('tr.iterable-item td.name a'):
            filename = entry.get_text().strip()
            if self._should_i_skip_this_filename(filename):
                continue

            new_url = urljoin(self.url, entry.get('href'))
            LOGGER.info(f'Found new BitBucket url: {new_url}')
            return new_url

        raise ValueError("Couldn't find an URL for this release??")


class GithubURLRetrieverMixin:
    def _get_real_url(self, soup: bs4.BeautifulSoup):
        for details in soup.select('details div.Box div.d-flex'):
            span = details.select('span')
            if not span:
                continue

            filename = span[0].get_text().strip()
            if self._should_i_skip_this_filename(filename):
                continue

            new_url = urljoin(self.url, details.select('a')[0].get('href'))
            LOGGER.info(f'Found new Github url: {new_url}')
            return new_url

        raise ValueError("Couldn't find github url for this release??")


class RequiredLatestBitbucketFile(BitBucketURLRetrieverMixin, RequiredLatestFromWebMixin, RequiredFile):
    """
    This class fetches a file from Bitbucket according to a pattern
    """
    def __init__(self, url, save_as, file_regex):
        super().__init__(url, save_as)
        self.file_regex = re.compile(file_regex)

    def _should_i_skip_this_filename(self, filename):
        return not self.file_regex.match(filename)


class RequiredLatestGithubZipFile(GithubURLRetrieverMixin, RequiredLatestFromWebMixin, RequiredZipFile):
    """
    This class fetches a ZIP file from Github and extracts it.
    """
    def _should_i_skip_this_filename(self, filename):
        retVal = not filename.lower().endswith('.zip')
        LOGGER.debug(f'RequiredLatestGithubZipFile._should_i_skip_this_filename:: {retVal}')
        return retVal
