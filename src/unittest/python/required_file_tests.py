from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main, mock, skipIf

from common import URL_RAW, URL_UNKNOWN, TEST_STRING
from required_files.required_files import RequiredFile, FileAdapter


class TestRequiredFile(TestCase):
    def setUp(self) -> None:
        self.tmpDir = TemporaryDirectory()

    def tearDown(self) -> None:
        self.tmpDir.cleanup()
        del self.tmpDir

    def test_url_works_fine(self):
        target = Path(self.tmpDir.name) / 'target.tmp'
        new_target = Path(RequiredFile(URL_RAW, target).check())
        self.assertEqual(target, new_target)
        self.assertTrue(new_target.exists())
        self.assertEqual(new_target.read_text(), TEST_STRING)

    def test_bad_url(self):
        with self.assertRaises(ValueError) as ex:
            target = Path(self.tmpDir.name) / 'target.tmp'
            RequiredFile(URL_UNKNOWN, target).check()
            self.assertEqual(str(ex), '404: Not Found')

    def test_good_create_directories(self):
        target = Path(self.tmpDir.name) / 'dir1/test.txt'
        RequiredFile(URL_RAW, target)
        self.assertTrue(target.parent.exists())

    def test_bad_create_directories(self):
        with self.assertRaises(FileNotFoundError):
            RequiredFile(URL_RAW, '')

    def test__is_file_present(self):
        target = Path(self.tmpDir.name) / 'test.txt'
        target.touch()
        tmp = RequiredFile(URL_RAW, target)
        self.assertTrue(tmp._is_file_present())

    def test__is_file_present__not(self):
        target = Path(self.tmpDir.name) / 'test2.txt'
        tmp = RequiredFile(URL_RAW, target)
        self.assertFalse(tmp._is_file_present())

    @skipIf(not FileAdapter, '`FileAdapter` is not available')
    @mock.patch('required_files.required_files.FileAdapter', __bool__=lambda x: False)
    def test_FileAdapter_not_available(self, file_adapter):
        self.test_url_works_fine()

    def test__download_with_filename(self):
        target = Path(self.tmpDir.name) / 'target.tmp'
        RequiredFile._download(URL_RAW, str(target))
        self.assertTrue(target.exists())
        self.assertEqual(target.read_text(), TEST_STRING)

    def test__download_with_PathLike(self):
        target = Path(self.tmpDir.name) / 'target.tmp'
        RequiredFile._download(URL_RAW, target)
        self.assertTrue(target.exists())
        self.assertEqual(target.read_text(), TEST_STRING)

    def test__download_with_filepointer(self):
        target = Path(self.tmpDir.name) / 'target.tmp'

        with open(target, 'w+b') as fp:
            RequiredFile._download(URL_RAW, fp)
            fp.seek(0)

        self.assertTrue(target.exists())
        self.assertEqual(target.read_text(), TEST_STRING)

    def test__download_with_something_strange(self):
        with self.assertRaises(AttributeError):  # 'NoneType' object has no attribute 'write'
            RequiredFile._download(URL_RAW, None)

    def test__download_with_bad_url(self):
        with self.assertRaises(ValueError):
            RequiredFile._download(URL_UNKNOWN, None)

    @mock.patch('required_files.required_files.RequiredFile._download')
    def test_filename_present(self, download_method):
        target = Path(self.tmpDir.name) / 'target.tmp'
        target.touch()
        new_target = Path(RequiredFile(URL_RAW, target).check())
        self.assertFalse(download_method.called)
        self.assertEqual(target, new_target)
        self.assertTrue(new_target.exists())
        self.assertEqual(new_target.read_text(), '')

    def test_good_download_to_tmpfile(self):
        fp = RequiredFile._download_to_tmpfile(URL_RAW)
        self.assertEqual(fp.read(), TEST_STRING.encode('utf8'))
        fp.close()

    def test_bad_download_to_tmpfile(self):
        with self.assertRaises(ValueError):
            RequiredFile._download_to_tmpfile(URL_UNKNOWN)


if __name__ == '__main__':
    main()
