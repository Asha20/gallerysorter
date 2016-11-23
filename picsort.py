from sys import argv
import argparse


def parse_user_input(args=argv[1:]):
    """
    Parses arguments provided by the user.

    :param args: Arguments to parse; defaults to command line arguments.
    :return: An argparse.Namespace object containing parsed arguments.
    """

    destination_help = 'Destination to move organized files in (defaults to source if not included).'
    recursive_help = 'Searches the whole source directory tree for files.'
    copy_help = 'Copies files into destination instead of moving them.'

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('source', help='Source directory to search.')
    parser.add_argument('destination', nargs='?', help=destination_help)
    parser.add_argument('-h', '--help', action='help', help='Show this help message and exit.')
    parser.add_argument('-r', '--recursive', action='store_true', help=recursive_help)
    parser.add_argument('-c', '--copy', action='store_true', help=copy_help)

    result = parser.parse_args(args)
    result.destination = result.source if not result.destination else result.destination

    return result


if __name__ == '__main__':
    print(parse_user_input())
