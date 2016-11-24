from functools import partial
import unittest

import picsort


class TestArgumentParser(unittest.TestCase):
    """Tests for argument parsing."""

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

if __name__ == '__main__':
    unittest.main()