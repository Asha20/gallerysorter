#!/usr/bin/python3

from functools import partial
from contextlib import redirect_stdout
from io import StringIO
import unittest
import os
import shutil

import gallerysorter

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
    """Tests for the gallerysorter.parse_user_input function."""

    def test_default_destination_is_source(self):
        """Fails if the destination doesn't match the source by default."""
        result = gallerysorter.parse_user_input(['sort', '.'])
        self.assertEqual(result.source, result.destination)

    def test_destination_is_supplied(self):
        """Fails if the destination defaults to source, even though another was provided."""
        result = gallerysorter.parse_user_input(['sort', '.', '..'])
        self.assertEqual(result.destination, '..')

    def test_user_entered_extensions(self):
        """Fails if gallerysorter.TimeFile._allowed_extensions doesn't match the input."""
        args = 'sort . -e MP3 TXT'.split(' ')
        gallerysorter.TimeFile.set_allowed_extensions(gallerysorter.parse_user_input(args).extensions)
        self.assertEqual(gallerysorter.TimeFile._allowed_extensions, ['.mp3', '.txt'])
        gallerysorter.TimeFile.set_allowed_extensions()

    def test_source_is_not_a_directory(self):
        """Fails if the program doesn't exit when source isn't a directory."""
        with redirect_stdout(StringIO()) as stdout:
            with self.assertRaises(SystemExit) as e:
                gallerysorter.parse_user_input(['sort', '1.mp3'])

        expected_message = 'Error: Invalid/Nonexistent source.\n'
        self.assertEqual(stdout.getvalue(), expected_message)
        self.assertEqual(e.exception.code, 1)

    def test_source_does_not_exist(self):
        """Fails if the program doesn't exit when source doesn't exist."""
        with redirect_stdout(StringIO()) as stdout:
            with self.assertRaises(SystemExit) as e:
                gallerysorter.parse_user_input(['sort', 'imaginary_directory'])

        expected_message = 'Error: Invalid/Nonexistent source.\n'
        self.assertEqual(stdout.getvalue(), expected_message)
        self.assertEqual(e.exception.code, 1)


class TestFileChecking(unittest.TestCase):
    """Tests for file checking."""

    @classmethod
    def setUpClass(cls):
        """Creates files to search through."""
        files = (
            '20010203_102030.jpg',
            'jpg_2.jpg',
            'mp4_1.mp4',
            'mp4_2.mp4',
            'txt_1.txt'
        )
        create_files(*files)

    @classmethod
    def tearDownClass(cls):
        """Deletes temporary files that were used for running tests."""
        if shutil.rmtree.avoids_symlink_attacks:
            shutil.rmtree(TEMP_PATH)

    def test_is_time_string_valid(self):
        """Fails if True isn't returned when a valid string is checked to be a time string."""
        self.assertTrue(gallerysorter.TimeFile.is_time_string('20010203_010203'))

    def test_is_time_string_random_string(self):
        """Fails if False isn't returned when a non time string is checked."""
        self.assertFalse(gallerysorter.TimeFile.is_time_string('test.txt'))

    def test_is_time_string_invalid_length(self):
        """Fails if False isn't returned when a string with invalid length is passed in."""
        self.assertFalse(gallerysorter.TimeFile.is_time_string('20010203.jpg'))

    def test_is_time_string_no_underscore(self):
        """Fails if False isn't returned when a string is missing an underscore."""
        self.assertFalse(gallerysorter.TimeFile.is_time_string('20010203010203.jpg'))


class TestFileSearching(unittest.TestCase):
    """Tests for file searching."""

    @classmethod
    def setUpClass(cls):
        """Creates files to search through."""
        files = (
            'directory/20010203_010204.jpg',
            'txt_1.txt',
            'jpg_1.jpg',
            '200102_03010203.jpg',
            '20010203_010203.mp4',
            '20010203_010203.txt'
        )
        create_files(*files)

    @classmethod
    def tearDownClass(cls):
        """Deletes temporary files that were used for running tests."""
        if shutil.rmtree.avoids_symlink_attacks:
            shutil.rmtree(TEMP_PATH)

    def test_find_proper_file(self):
        """Fails if a list containing a gallerysorter.TimeFile with path '20010203_010203.mp4' isn't returned."""
        try:
            self.assertEqual(gallerysorter.get_files(TEMP_PATH)[0].path,
                             (path_from_temp('20010203_010203.mp4')))
        except IndexError:
            pass

    def test_print_files(self):
        """Fails if the expected files aren't printed out."""
        with redirect_stdout(StringIO()):
            relative_paths = gallerysorter.list_files(TEMP_PATH, gallerysorter.get_files)

        self.assertEqual(relative_paths, ('20010203_010203.mp4',))

    def test_print_files_recursively(self):
        """Fails if the expected files aren't printed out."""
        with redirect_stdout(StringIO()):
            relative_paths = gallerysorter.list_files(TEMP_PATH, gallerysorter.get_files_recursively)

        self.assertEqual(relative_paths, ('20010203_010203.mp4', 'directory/20010203_010204.jpg'))


class TestFileOrganizing(unittest.TestCase):
    """Tests for organizing files into folders."""

    @classmethod
    def setUpClass(cls):
        """Creates files to organize."""
        files = (
            '20010203_010203.jpg',
            '20010204_010203.jpg',
            'subdirectory/20020201_010203.jpg'
        )
        cls.create_files = partial(create_files, *files)

    def test_organize_files(self):
        """Fails if files aren't organized into folders properly."""
        self.create_files()
        with redirect_stdout(StringIO()):
            paths = gallerysorter.organize_files(TEMP_PATH, gallerysorter.get_files(TEMP_PATH), copy=False)
        expected = (
            '2001/February 2001/20010203_010203.jpg',
            '2001/February 2001/20010204_010203.jpg'
        )

        self.addCleanup(shutil.rmtree, TEMP_PATH)
        self.assertEqual(paths, tuple(os.path.join(TEMP_PATH, item) for item in expected))

    def test_organize_files_recursively(self):
        """Fails if files within subdirectories aren't organized into folder properly."""
        self.create_files()
        with redirect_stdout(StringIO()):
            paths = gallerysorter.organize_files(TEMP_PATH,
                                                 gallerysorter.get_files_recursively(TEMP_PATH), copy=False)

        expected = (
            '2001/February 2001/20010203_010203.jpg',
            '2001/February 2001/20010204_010203.jpg',
            '2002/February 2002/20020201_010203.jpg'
        )

        self.addCleanup(shutil.rmtree, TEMP_PATH)
        self.assertEqual(paths, tuple(os.path.join(TEMP_PATH, item) for item in expected))


if __name__ == '__main__':
    unittest.main()
