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


if __name__ == '__main__':
    unittest.main()