from functools import partial
from contextlib import redirect_stdout
from io import StringIO
import unittest
import os
import shutil

import picsort

# Solved unittest dots and error messages printing together thanks to /u/treyhunner
# https://www.reddit.com/r/learnpython/comments/5f0vko/disable_printing_in_unit_tests/dago5w7/


class TestArgumentParsing(unittest.TestCase):
    """Tests for the picsort.parse_user_input function."""

    def parse_user_input(self, string_args):
        """
        Wrapper method for picsort.parse_user_input.
        Accepts arguments as a string instead of a list for convenience.

        :param string_args: A string of arguments.
        :return: An argparse.Namespace object containing parsed arguments.
        """

        return picsort.parse_user_input(string_args.split())

    def test_default_destination_is_source(self):
        """Fails if the destination doesn't match the source by default."""
        result = self.parse_user_input('source')
        self.assertEqual(result.source, result.destination)

    def test_destination_is_supplied(self):
        """Fails if the destination defaults to source, even though another was provided."""
        result = self.parse_user_input('source destination')
        self.assertEqual(result.destination, 'destination')


class TestStringSplitting(unittest.TestCase):
    """Tests for the picsort.split_string function."""

    def __init__(self, *args, **kwargs):
        super(TestStringSplitting, self).__init__(*args, **kwargs)
        self.split_string = partial(picsort.split_string, '20010203')

    def test_split_string_valid(self):
        """Fails if the string isn't split in the expected manner."""
        self.assertEqual(self.split_string(4, 2, 2), ['2001', '02', '03'])

    def test_split_string_with_non_positive_point(self):
        """Fails if the program doesn't exit when a part value is less than or equal to 0."""
        with redirect_stdout(StringIO()) as stdout:
            with self.assertRaises(SystemExit) as e:
                self.split_string(3, -2, 4)

        expected_message = 'Error: Non-positive value entered; Parts must be positive whole numbers.\n'
        self.assertEqual(stdout.getvalue(), expected_message)
        self.assertEqual(e.exception.code, 1)

    def test_split_string_with_non_whole_point(self):
        """Fails if the program doesn't exit when supplied with a non-whole number."""
        with redirect_stdout(StringIO()) as stdout:
            with self.assertRaises(SystemExit) as e:
                self.split_string(1.23, 2)

        expected_message = 'Error: Non-whole value entered; Parts must be positive whole numbers.\n'
        self.assertEqual(stdout.getvalue(), expected_message)
        self.assertEqual(e.exception.code, 1)

    def test_split_string_with_too_long_parts(self):
        """Fails if the program doesn't exit when splitting a string into too big parts."""
        with redirect_stdout(StringIO()) as stdout:
            with self.assertRaises(SystemExit) as e:
                self.split_string(20)

        expected_message = 'Error: Parts are larger than the whole.\n'
        self.assertEqual(stdout.getvalue(), expected_message)
        self.assertEqual(e.exception.code, 1)

    def test_split_string_with_too_short_parts(self):
        """Fails if the program doesn't extend the last part to fit the string length."""
        self.assertEqual(self.split_string(4, 2), ['2001', '0203'])


def create_files(*files):
    """
    Creates files needed for testing.

    :param files: A list or tuple of paths to create.
    :return: None
    """
    try:
        os.mkdir('tests/temp')
    except FileExistsError:
        pass

    temp_path = os.path.join(os.getcwd(), 'tests', 'temp')
    path_from_temp = partial(os.path.join, temp_path)

    for file in files:
        if os.path.dirname(file):
            os.makedirs(path_from_temp(os.path.dirname(file)), exist_ok=True)
        if not file.endswith('/'):
            with open(path_from_temp(file), 'w'):
                pass


class TestFileChecking(unittest.TestCase):
    """Tests for file checking."""

    def setUp(self):
        """Creates files to search through."""
        files = (
            '20010203_102030.jpg',
            'jpg_2.jpg',
            'mp4_1.mp4',
            'mp4_2.mp4',
            'txt_1.txt'
        )
        create_files(*files)

        self.temp_path = os.path.join(os.getcwd(), 'tests', 'temp')
        self.path_from_temp = partial(os.path.join, self.temp_path)

    def tearDown(self):
        """Deletes temporary files that were used for running tests."""
        if shutil.rmtree.avoids_symlink_attacks:
            shutil.rmtree(self.temp_path)

    def test_directory_extension_check(self):
        """Fails if False isn't returned when a directory is tested for a set extension."""
        self.assertFalse(picsort.file_has_wanted_extension(self.temp_path))

    def test_mp3_extension_check(self):
        """Fails if True isn't returned when a JPG file is tested for a set extension."""
        file_path = self.path_from_temp('jpg_2.jpg')
        self.assertTrue(picsort.file_has_wanted_extension(file_path))

    def test_txt_extension_check(self):
        """Fails if False isn't returned when a TXT file is tested for a set extension."""
        file_path = self.path_from_temp('txt_01.txt')
        self.assertFalse(picsort.file_has_wanted_extension(file_path))

    def test_is_time_string_valid(self):
        """Fails if True isn't returned when a valid string is checked to be a time string."""
        self.assertTrue(picsort.is_time_string('20010203_010203.jpg'))

    def test_is_time_string_random_string(self):
        """Fails if False isn't returned when a non time string is checked."""
        self.assertFalse(picsort.is_time_string('test.txt'))

    def test_is_time_string_invalid_length(self):
        """Fails if False isn't returned when a string with invalid length is passed in."""
        self.assertFalse(picsort.is_time_string('20010203.jpg'))

    def test_is_time_string_no_underscore(self):
        """Fails if False isn't returned when a string is missing an underscore."""
        self.assertFalse(picsort.is_time_string('20010203010203.jpg'))


class TestFileSearching(unittest.TestCase):
    """Tests for file searching."""

    def setUp(self):
        """Creates files to search through."""
        files = (
            'directory/',
            'txt_1.txt',
            'jpg_1.jpg',
            '200102_03010203.jpg',
            '20010203_010203.mp4',
            '20010203_010203.txt'
        )
        create_files(*files)

        self.temp_path = os.path.join(os.getcwd(), 'tests', 'temp')
        self.path_from_temp = partial(os.path.join, self.temp_path)

    def tearDown(self):
        """Deletes temporary files that were used for running tests."""
        if shutil.rmtree.avoids_symlink_attacks:
            shutil.rmtree(self.temp_path)

    def test_find_proper_file(self):
        """Fails if a list containing only '20010203_010203.mp4' isn't returned."""
        self.assertEqual(list(picsort.get_files(self.temp_path)),
                         [self.path_from_temp('20010203_010203.mp4')])

    def test_source_is_not_a_directory(self):
        """Fails if the program doesn't exit when source isn't a directory."""
        with redirect_stdout(StringIO()) as stdout:
            with self.assertRaises(SystemExit) as e:
                picsort.get_files(self.path_from_temp('txt_1.txt'))

        expected_message = 'Error: Source must be a directory.\n'
        self.assertEqual(stdout.getvalue(), expected_message)
        self.assertEqual(e.exception.code, 1)

    def test_source_does_not_exist(self):
        """Fails if the program doesn't exit when source doesn't exist."""
        with redirect_stdout(StringIO()) as stdout:
            with self.assertRaises(SystemExit) as e:
                picsort.get_files(self.path_from_temp('imaginary_directory/'))

        expected_message = "Error: Source doesn't exist.\n"
        self.assertEqual(stdout.getvalue(), expected_message)
        self.assertEqual(e.exception.code, 1)


if __name__ == '__main__':
    unittest.main()
