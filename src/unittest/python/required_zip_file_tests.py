from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main, mock

from common import (
    TESTFILE_NAME,
    TEST_STRING,
    URL_ZIP_WITH_DIR_STRUCTURE,
    URL_ZIP_WITH_MULTIPLE_DIRS,
    URL_ZIP_WITH_SINGLE_DIR,
    URL_ZIP_WITHOUT_DIR,
)
from required_files import RequiredZipFile


class TestRequiredZipFile(TestCase):
    def setUp(self) -> None:
        self.tmp_dir = TemporaryDirectory()

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()
        del self.tmp_dir

    def test_basic_zip_skip_dir_false(self):
        expected_file = (
            Path(
                RequiredZipFile(
                    URL_ZIP_WITHOUT_DIR, self.tmp_dir.name, file_to_check=TESTFILE_NAME, skip_initial_dir=False
                ).check()
            )
            / TESTFILE_NAME
        )
        self.assertTrue(expected_file.exists())
        self.assertEqual(expected_file.read_text(), TEST_STRING)

    def test_basic_zip_skip_dir_true(self):
        p = (
            Path(
                RequiredZipFile(
                    URL_ZIP_WITHOUT_DIR, self.tmp_dir.name, file_to_check=TESTFILE_NAME, skip_initial_dir=True
                ).check()
            )
            / TESTFILE_NAME
        )
        self.assertTrue(p.exists())
        self.assertEqual(p.read_text(), TEST_STRING)

    def test_single_dir_zip_skip_dir_false(self):
        expected_file = (
            Path(
                RequiredZipFile(
                    URL_ZIP_WITH_SINGLE_DIR, self.tmp_dir.name, file_to_check=TESTFILE_NAME, skip_initial_dir=False
                ).check()
            )
            / 'dir1'
            / TESTFILE_NAME
        )
        self.assertTrue(expected_file.exists())
        self.assertEqual(expected_file.read_text(), TEST_STRING)

    def test_single_dir_zip_skip_dir_true(self):
        expected_file = (
            Path(
                RequiredZipFile(
                    URL_ZIP_WITH_SINGLE_DIR, self.tmp_dir.name, file_to_check=TESTFILE_NAME, skip_initial_dir=True
                ).check()
            )
            / TESTFILE_NAME
        )
        self.assertTrue(expected_file.exists())
        self.assertEqual(expected_file.read_text(), TEST_STRING)

    def test_multi_dir_zip_skip_dir_false(self):
        expected_file = Path(
            RequiredZipFile(
                URL_ZIP_WITH_MULTIPLE_DIRS, self.tmp_dir.name, file_to_check=TESTFILE_NAME, skip_initial_dir=False
            ).check()
        )
        file1 = expected_file / 'dir1' / TESTFILE_NAME
        file2 = expected_file / 'dir2' / TESTFILE_NAME
        self.assertTrue(file1.exists())
        self.assertEqual(file1.read_text(), TEST_STRING)
        self.assertTrue(file2.exists())
        self.assertEqual(file2.read_text(), TEST_STRING)

    def test_multi_dir_zip_skip_dir_true(self):
        expected_file = Path(
            RequiredZipFile(
                URL_ZIP_WITH_MULTIPLE_DIRS, self.tmp_dir.name, file_to_check=TESTFILE_NAME, skip_initial_dir=True
            ).check()
        )
        file1 = expected_file / 'dir1' / TESTFILE_NAME
        file2 = expected_file / 'dir2' / TESTFILE_NAME
        self.assertTrue(file1.exists())
        self.assertEqual(file1.read_text(), TEST_STRING)
        self.assertTrue(file2.exists())
        self.assertEqual(file2.read_text(), TEST_STRING)

    def test_structured_dir_zip_skip_dir_false(self):
        p = Path(
            RequiredZipFile(
                URL_ZIP_WITH_DIR_STRUCTURE, self.tmp_dir.name, file_to_check=TESTFILE_NAME, skip_initial_dir=False
            ).check()
        )
        file1 = p / 'dir1' / TESTFILE_NAME
        file2 = p / 'dir1/dir2' / TESTFILE_NAME
        self.assertTrue(file1.exists())
        self.assertTrue(file2.exists())
        self.assertEqual(file1.read_text(), TEST_STRING)
        self.assertEqual(file2.read_text(), TEST_STRING)

    def test_structured_dir_zip_skip_dir_true(self):
        p = Path(
            RequiredZipFile(
                URL_ZIP_WITH_DIR_STRUCTURE, self.tmp_dir.name, file_to_check=TESTFILE_NAME, skip_initial_dir=True
            ).check()
        )
        file1 = p / TESTFILE_NAME
        file2 = p / 'dir2' / TESTFILE_NAME
        self.assertTrue(file1.exists())
        self.assertTrue(file2.exists())
        self.assertEqual(file1.read_text(), TEST_STRING)
        self.assertEqual(file2.read_text(), TEST_STRING)

    @mock.patch('required_files.required_files.ZipfileMixin._process_zip')
    def test_when_file_is_present(self, process_zip):
        target_file = Path(self.tmp_dir.name) / TESTFILE_NAME
        target_file.touch()

        expected_file = (
            Path(
                RequiredZipFile(
                    URL_ZIP_WITHOUT_DIR, self.tmp_dir.name, file_to_check=TESTFILE_NAME, skip_initial_dir=False
                ).check()
            )
            / TESTFILE_NAME
        )
        self.assertFalse(process_zip.called)
        self.assertEqual(expected_file, target_file)
        self.assertTrue(expected_file.exists())
        self.assertEqual(expected_file.read_text(), '')


if __name__ == '__main__':
    main()
