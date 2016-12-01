from functools import partial
from contextlib import redirect_stdout
from io import StringIO
import unittest
import os
import shutil

import picsort

# Solved unittest dots and error messages printing together thanks to /u/treyhunner
# https://www.reddit.com/r/learnpython/comments/5f0vko/disable_printing_in_unit_tests/dago5w7/

TEMP_PATH = os.path.join(os.getcwd(), 'tests', 'temp')
path_from_temp = partial(os.path.join, TEMP_PATH)


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

    for file in files:
        if os.path.dirname(file):
            os.makedirs(path_from_temp(os.path.dirname(file)), exist_ok=True)
        if not file.endswith('/'):
            with open(path_from_temp(file), 'w'):
                pass


class TestArgumentParsing(unittest.TestCase):
    """Tests for the picsort.parse_user_input function."""

    def test_default_destination_is_source(self):
        """Fails if the destination doesn't match the source by default."""
        result = picsort.parse_user_input(['source'])
        self.assertEqual(result.source, result.destination)

    def test_destination_is_supplied(self):
        """Fails if the destination defaults to source, even though another was provided."""
        result = picsort.parse_user_input(['source', 'destination'])
        self.assertEqual(result.destination, 'destination')


class TestStringSplitting(unittest.TestCase):
    """Tests for the picsort.split_string function."""

    def test_split_string_valid(self):
        """Fails if the string isn't split in the expected manner."""
        self.assertEqual(picsort.TimeFileUtilities.split_name('20010203')[:3], ['2001', '02', '03'])


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

    def tearDown(self):
        """Deletes temporary files that were used for running tests."""
        if shutil.rmtree.avoids_symlink_attacks:
            shutil.rmtree(TEMP_PATH)

    def test_is_time_string_valid(self):
        """Fails if True isn't returned when a valid string is checked to be a time string."""
        self.assertTrue(picsort.TimeFileUtilities.is_time_string('20010203_010203'))

    def test_is_time_string_random_string(self):
        """Fails if False isn't returned when a non time string is checked."""
        self.assertFalse(picsort.TimeFileUtilities.is_time_string('test.txt'))

    def test_is_time_string_invalid_length(self):
        """Fails if False isn't returned when a string with invalid length is passed in."""
        self.assertFalse(picsort.TimeFileUtilities.is_time_string('20010203.jpg'))

    def test_is_time_string_no_underscore(self):
        """Fails if False isn't returned when a string is missing an underscore."""
        self.assertFalse(picsort.TimeFileUtilities.is_time_string('20010203010203.jpg'))


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

    def tearDown(self):
        """Deletes temporary files that were used for running tests."""
        if shutil.rmtree.avoids_symlink_attacks:
            shutil.rmtree(TEMP_PATH)

    def test_find_proper_file(self):
        """Fails if a list containing only '20010203_010203.mp4' isn't returned."""
        try:
            self.assertEqual(picsort.get_files(TEMP_PATH),
                             (path_from_temp('20010203_010203.mp4')))
        except (picsort.InvalidTimeFormatError, picsort.NotAFileError):
            pass

    def test_source_is_not_a_directory(self):
        """Fails if the program doesn't exit when source isn't a directory."""
        with redirect_stdout(StringIO()) as stdout:
            with self.assertRaises(SystemExit) as e:
                picsort.get_files(path_from_temp('txt_1.txt'))

        expected_message = 'Error: Source must be a directory.\n'
        self.assertEqual(stdout.getvalue(), expected_message)
        self.assertEqual(e.exception.code, 1)

    def test_source_does_not_exist(self):
        """Fails if the program doesn't exit when source doesn't exist."""
        with redirect_stdout(StringIO()) as stdout:
            with self.assertRaises(SystemExit) as e:
                picsort.get_files(path_from_temp('imaginary_directory/'))

        expected_message = "Error: Source doesn't exist.\n"
        self.assertEqual(stdout.getvalue(), expected_message)
        self.assertEqual(e.exception.code, 1)


class TestFileOrganizing(unittest.TestCase):
    """Tests for organizing files into folders."""

    def setUp(self):
        """Creates files to organize."""
        files = (
            '20010203_010203.jpg',
            '20010204_010203.jpg',
            'subdirectory/20020201_010203.jpg'
        )
        self.create_files = partial(create_files, *files)

    def test_organize_files(self):
        """Fails if files aren't organized into folders properly."""
        self.create_files()
        paths = picsort.organize_files(TEMP_PATH, False, picsort.get_files(TEMP_PATH))
        expected = (
            '2001/February 2001/20010203_010203.jpg',
            '2001/February 2001/20010204_010203.jpg'
        )

        self.assertEqual(paths, tuple(os.path.join(TEMP_PATH, item) for item in expected))
        self.addCleanup(shutil.rmtree, TEMP_PATH)

    def test_organize_recursive(self):
        """Fails if files within subdirectories aren't organized into folder properly."""
        self.create_files()
        paths = picsort.organize_files(TEMP_PATH, False, picsort.get_files_recursively(TEMP_PATH))
        expected = (
            '2001/February 2001/20010203_010203.jpg',
            '2001/February 2001/20010204_010203.jpg',
            '2002/February 2002/20020201_010203.jpg'
        )

        self.assertEqual(paths, tuple(os.path.join(TEMP_PATH, item) for item in expected))
        self.addCleanup(shutil.rmtree, TEMP_PATH)


if __name__ == '__main__':
    unittest.main()
