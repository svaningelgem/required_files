from unittest import TestCase, main

from required_files import RequiredCommand


class TestRequiredCommand(TestCase):
    def test_command_is_there(self):
        COMMAND_TO_CHECK = 'python --version'
        self.assertEqual(RequiredCommand(COMMAND_TO_CHECK).check(), COMMAND_TO_CHECK)

    def test_command_is_not_there(self):
        with self.assertRaises(ValueError):
            RequiredCommand('p1p2p3ython_surely_not_there').check()


if __name__ == '__main__':
    main()
