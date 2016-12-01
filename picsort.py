from sys import argv, exit
from shutil import copyfile
import ntpath
import os
import argparse


class NotAFileError(Exception):
    """Raised when a file is expected but a directory is supplied."""


class InvalidExtensionError(Exception):
    """Raised when a file doesn't have an expected extension."""


class InvalidTimeFormatError(Exception):
    """Raised when a string doesn't follow the YMD_HMS format."""


class TimeFileUtilities:
    """Namespace class for storing utility TimeFile methods."""

    allowed_extensions = ('.jpg', '.mp4')

    @staticmethod
    def split_name(file_name):
        """
        Splits a string into parts that match the YMD_HMS format.

        :param file_name: The file name to split.
        :return: A tuple containing parts of the original string.
        """
        sizes = (4, 2, 2, 1, 2, 2, 2)

        position = 0
        parts = []
        for size in sizes:
            size = size
            parts.append(file_name[position:position + size])
            position += size

        return parts

    @staticmethod
    def is_time_string(file_name):
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


        :param file_name: Path to test if it is a valid time string.
        :return: True if path is a valid time string; False otherwise.
        """
        if len(file_name) != 15:
            return False

        parts = TimeFileUtilities.split_name(file_name)
        try:
            parts.remove('_')
            for part in parts:
                _ = int(part)
        except ValueError:
            return False

        return True

    @staticmethod
    def get_allowed_extensions(extensions=allowed_extensions):
        """
        Adjusts user-entered extensions to make sure they're valid.

        :param extensions: An iterable of possibly faulty extensions.
        :return: A tuple of fixed, allowed extensions.
        """
        new_extensions = []
        for extension in extensions:
            if not extension.startswith('.'):
                new_extensions.append('.{0}'.format(extension.lower()))
            else:
                new_extensions.append(extension.lower())

        return new_extensions


class TimeFile:
    """For easier managing of files using the time format."""

    def __init__(self, path):
        """
        Defines all the parts that the YMD_HMS format defines,
        along with the current and sorted path.

        :param path: Path to a file for creating the TimeFile.
        """
        if os.path.isdir(path):
            raise NotAFileError

        month_names = ('January', 'February', 'March', 'April', 'May', 'June', 'July',
                       'August', 'September', 'October', 'November', 'December')

        self.path = path
        self.file_name = os.path.splitext(ntpath.basename(path))[0]
        self.extension = os.path.splitext(self.path)[1].lower()

        if self.extension not in TimeFileUtilities.get_allowed_extensions():
            raise InvalidExtensionError

        if not TimeFileUtilities.is_time_string(self.file_name):
            raise InvalidTimeFormatError

        self.year, self.month, self.day, _, \
            self.hour, self.minute, self.second = TimeFileUtilities.split_name(self.file_name)

        self.month_name = month_names[int(self.month) - 1]

    def get_sorted_file_path(self, destination):
        """
        Forms a new path to sort the file using
        the year and the month name.

        :param destination: Destination directory where to sort the files in.
        :return: A string which represents the new file path.
        """
        year_and_month = '{0} {1}'.format(self.month_name, self.year)
        return os.path.join(destination, self.year, year_and_month,
                            self.file_name + self.extension)

    def __str__(self):
        return self.path


def get_files_recursively(source):
    """
    Finds files recursively that have the valid time string format (YMD_HMS)
    and that have one of the selected extensions.

    :param source: The directory to search for files in.
    :return: A tuple of picsort.TimeFile objects.
    """
    result = []

    if not os.path.exists(source):
        print("Error: Source doesn't exist.")
        exit(1)

    if not os.path.isdir(source):
        print('Error: Source must be a directory.')
        exit(1)

    all_file_paths = (os.path.join(root, file) for root, dirs, files in os.walk(source)
                      for file in files)

    for file in all_file_paths:
        try:
            result.append(TimeFile(file))
        except (InvalidExtensionError, NotAFileError):
            continue

    return tuple(result)


def get_files(source):
    """
    Finds files that have the valid time string format (YMD_HMS)
    and that have one of the selected extensions.

    :param source: The directory to search for files in.
    :return: A tuple of picsort.TimeFile objects.
    """
    result = []

    if not os.path.exists(source):
        print("Error: Source doesn't exist.")
        exit(1)

    if not os.path.isdir(source):
        print('Error: Source must be a directory.')
        exit(1)

    for file in os.listdir(source):
        try:
            result.append(TimeFile(os.path.join(source, file)))
        except (InvalidExtensionError, NotAFileError):
            continue

    return tuple(result)


def organize_files(destination, copy, time_files):
    """
    Organizes files into folders.

    :param destination: The destination directory to sort files into.
    :param copy: Copies files if True; Moves files if False.
    :param time_files: An iterable of picsort.TimeFile objects to sort.
    :return: A tuple of new sorted file paths.
    """
    result = []

    for time_file in time_files:
        new_path = time_file.get_sorted_file_path(destination)
        os.makedirs(os.path.dirname(new_path), exist_ok=True)

        if copy:
            copyfile(time_file.path, new_path)
        else:
            os.rename(time_file.path, new_path)
        result.append(new_path)

    return tuple(result)


def parse_user_input(args=argv[1:]):
    """
    Parses arguments provided by the user.

    :param args: Arguments to parse; defaults to command line arguments.
    :return: An argparse.Namespace object containing parsed arguments.
    """
    source_help = 'Source directory to search.'
    destination_help = 'Destination to move organized files in (default: equal to source.)'
    help_help = 'Show this help message and exit.'  # Heh
    recursive_help = 'Searches the whole source directory tree for files.'
    extensions_help = 'List of extensions to allow sorting for (default: JPG, MP4.)'
    copy_help = 'Copies files into destination instead of moving them.'

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('source', help=source_help)
    parser.add_argument('destination', nargs='?', help=destination_help)
    parser.add_argument('-h', '--help', action='help', help=help_help)
    parser.add_argument('-r', '--recursive', action='store_true', help=recursive_help)
    parser.add_argument('-e', '--extensions', nargs='+', default=('.jpg', '.mp4'), help=extensions_help)
    parser.add_argument('-c', '--copy', action='store_true', help=copy_help)

    result = parser.parse_args(args)
    result.destination = result.source if not result.destination else result.destination

    return result


if __name__ == '__main__':
    settings = parse_user_input()
    TimeFileUtilities.allowed_extensions = settings.extensions

    if settings.recursive:
        files = get_files_recursively(settings.source)
    else:
        files = get_files(settings.source)

    organize_files(os.getcwd(), settings.copy, files)
