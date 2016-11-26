from functools import partial
import unittest
import os
import shutil

import picsort


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
        with self.assertRaises(SystemExit) as e:
            self.split_string(3, -2, 4)

        self.assertEqual(e.exception.code, 1)

    def test_split_string_with_non_whole_point(self):
        """Fails if the program doesn't exit when supplied with a non-whole number."""
        with self.assertRaises(SystemExit) as e:
            self.split_string(1.23, 2)

        self.assertEqual(e.exception.code, 1)

    def test_split_string_with_too_long_parts(self):
        """Fails if the program doesn't exit when splitting a string into too big parts."""
        with self.assertRaises(SystemExit) as e:
            self.split_string(20)

        self.assertEqual(e.exception.code, 1)

    def test_split_string_with_too_short_parts(self):
        """Fails if the program doesn't extend the last part to fit the string length."""
        self.assertEqual(self.split_string(4, 2), ['2001', '0203'])


class TestFileSearch(unittest.TestCase):
    """Tests for file searching."""

    def setUp(self):
        """Creates files to search through."""
        files = (
            '20010203_102030.jpg',
            'jpg_2.jpg',
            'mp4_1.mp4',
            'mp4_2.mp4',
            'txt_1.txt',
        )

        try:
            os.mkdir('tests/temp')
        except FileExistsError:
            pass

        self.temp_path = os.path.join(os.getcwd(), 'tests', 'temp')
        self.path_from_temp = partial(os.path.join, self.temp_path)

        for file in files:
            with open(os.path.join(self.temp_path, file), 'w'):
                pass

    def tearDown(self):
        """Deletes temporary files that were used for running tests."""
        if shutil.rmtree.avoids_symlink_attacks:
            shutil.rmtree(os.path.join(os.getcwd(), 'tests', 'temp'))

    def test_directory_extension_check(self):
        """Fails if True is returned when a directory is tested for a set extension."""
        self.assertFalse(picsort.file_has_wanted_extension(self.temp_path))

    def test_mp3_extension_check(self):
        """Fails if False is returned when a JPG file is tested for a set extension."""
        file_path = self.path_from_temp('jpg_2.jpg')
        self.assertTrue(picsort.file_has_wanted_extension(file_path))

    def test_txt_extension_check(self):
        """Fails if True is returned when a TXT file is tested for a set extension."""
        file_path = self.path_from_temp('txt_01.txt')
        self.assertFalse(picsort.file_has_wanted_extension(file_path))

if __name__ == '__main__':
    unittest.main()
