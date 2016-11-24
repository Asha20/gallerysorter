from sys import argv, exit
import argparse


def split_string(string, *sizes):
    """
    Splits a string into specified sizes.

    :param string: The string to split.
    :param sizes: A list of sizes to split the string in.
    :return: A tuple containing parts of the original string.
    """

    sizes = [float(size) for size in sizes]

    if tuple(size for size in sizes if not size.is_integer()):
        print('Error: Non-whole value entered; Parts must be positive whole numbers.')
        exit(1)

    if tuple(size for size in sizes if size <= 0):
        print('Error: Non-positive value entered; Parts must be positive whole numbers.')
        exit(1)

    if sum(sizes) > len(string):
        print('Error: Parts are larger than the whole.')
        exit(1)
    elif sum(sizes) < len(string):
        sizes[-1] = len(string) - sum(sizes[:-1])

    position = 0
    parts = []
    for size in sizes:
        size = int(size)
        parts.append(string[position:position+size])
        position += size

    return parts


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
    print(split_string('20010203', *argv[1:]))
