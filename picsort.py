from sys import argv, exit
import ntpath
import os
import argparse


def split_string(string, *sizes):
    """
    Splits a string into specified sizes.

    :param string: The string to split.
    :param sizes: A list of sizes to split the string in.
    :return: A tuple containing parts of the original string.
    """
    # These default part lengths fit the YMD_HMS format;
    # Refer to picsort.is_time_string docstring for details.
    if not sizes:
        sizes = (4, 2, 2, 1, 2, 2, 2)

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


def file_has_wanted_extension(path, *extensions):
    """
    Identifies if a file has one of the defined extensions.

    :param path: The path to test.
    :param extensions: A list of extensions to check for. Defaults to JPG and MP4.
    :return: True if path has wanted extension; False otherwise (or if path is a folder).
    """
    if os.path.isdir(path):
        return False

    if not extensions:
        extensions = ('.jpg', '.mp4')

    if os.path.splitext(path)[1].lower() in extensions:
        return True
    else:
        return False


def is_time_string(path):
    """
    Checks if a given file has a time string name. A time string name
    has the format YMD_HMS. Explanation below.

    YMD_HMS:
        Y - Year (4 digits)
        M - Month (2 digits)
        D - Day (2 digits)
        _ - Single underscore
        H - Hour (2 digits)
        M - Minute (2 digits)
        S - Second (2 digits)
    Y, M, D, H, M and S are all valid integers.

    Example: 20010203_102030.jpg - This JPG was created on the
    3rd of February of 2001, at the time 10:20:30.


    :param path: Path to test if it is a valid time string.
    :return: True if path is a valid time string; False otherwise.
    """
    file_name = os.path.splitext(ntpath.basename(path))[0]
    if len(file_name) != 15:
        return False

    parts = split_string(file_name)
    try:
        parts.remove('_')
        for part in parts:
            _ = int(part)
    except ValueError:
        return False

    return True


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
