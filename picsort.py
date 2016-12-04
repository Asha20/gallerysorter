#!/usr/bin/python3

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
    def get_allowed_extensions(extensions=None):
        """
        Adjusts user-entered extensions to make sure they're valid.

        :param extensions: An iterable of possibly faulty extensions.
        :return: A tuple of fixed, allowed extensions.
        """
        if not extensions:
            extensions = TimeFileUtilities.allowed_extensions

        new_extensions = []
        for extension in extensions:
            if not extension.startswith('.'):
                new_extensions.append('.{0}'.format(extension.lower()))
            else:
                new_extensions.append(extension.lower())

        return new_extensions

    @staticmethod
    def reset_allowed_extensions():
        """
        Resets allowed extensions to JPG and MP4.

        :return: None.
        """
        TimeFileUtilities.allowed_extensions = ('.jpg', '.mp4')


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
        self.file_name_with_extension = self.file_name + self.extension

        if self.extension not in TimeFileUtilities.get_allowed_extensions():
            raise InvalidExtensionError

        if not TimeFileUtilities.is_time_string(self.file_name):
            raise InvalidTimeFormatError

        self.year, self.month, self.day, _, \
            self.hour, self.minute, self.second = TimeFileUtilities.split_name(self.file_name)

        self.month_name = month_names[int(self.month) - 1]

    def get_sorted_file_path(self, destination, absolute=True):
        """
        Forms a new path to sort the file using
        the year and the month name.

        :param destination: Destination directory where to sort the files in.
        :param absolute: Whether the return path should be absolute or relative to the destination.
        :return: A string which represents the new file path.
        """
        year_and_month = '{0} {1}'.format(self.month_name, self.year)
        if absolute:
            return os.path.join(destination, self.year, year_and_month, self.file_name_with_extension)
        else:
            return os.path.join(self.year, year_and_month, self.file_name_with_extension)

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
        except (InvalidExtensionError, InvalidTimeFormatError, NotAFileError):
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

    if not os.path.exists(source) or not os.path.isdir(source):
        print('Error: Invalid/Nonexistent source.')
        exit(1)

    for file in os.listdir(source):
        try:
            result.append(TimeFile(os.path.join(source, file)))
        except (InvalidExtensionError, InvalidTimeFormatError, NotAFileError):
            continue

    return tuple(result)


def organize_files(destination, time_files, copy=False, verbose=False):
    """
    Organizes files into folders.

    :param destination: The destination directory to sort files into.
    :param time_files: An iterable of picsort.TimeFile objects to sort.
    :param copy: Copies files if True; Moves files if False.
    :param verbose:
    :return: A tuple of new sorted file paths.
    """
    result = []

    # Removes files whose source matches the destination.
    time_files = tuple(time_file for time_file in time_files if
                       time_file.path != time_file.get_sorted_file_path(destination))

    if verbose:
        mode = 'Copying' if copy else 'Moving'
        print('{mode} {number} files:'.format(mode=mode, number=len(time_files)))

    for count, time_file in enumerate(time_files):
        new_path = time_file.get_sorted_file_path(destination, absolute=True)
        os.makedirs(os.path.dirname(new_path), exist_ok=True)

        if copy:
            copyfile(time_file.path, new_path)
        else:
            os.rename(time_file.path, new_path)

        result.append(new_path)

        if verbose:
            print(' {count}/{total} {file} -> {directory}'.format(
                count=count+1,
                total=len(time_files),
                file=os.path.relpath(time_file.path, destination),
                directory=os.path.relpath(new_path, destination)
            ))

    print('Done organizing!')

    return tuple(result)


def list_files(source, file_getter):
    """
    Prints out all of the valid files within source that would get sorted.

    :param source: The source to search through for files.
    :param file_getter: Function used to get TimeFile objects.
    :return: A list containing all of the relative paths printed.
    """
    relative_paths = []
    time_files = file_getter(source)
    print('Printing files:')

    for time_file in time_files:
        relative_path = os.path.relpath(time_file.path, source)
        print(' -', relative_path)
        relative_paths.append(relative_path)

    print('Number of files:', len(time_files))

    return tuple(relative_paths)


def parse_user_input(args=argv[1:]):
    """
    Parses arguments provided by the user.

    :param args: Arguments to parse; defaults to command line arguments.
    :return: An argparse.Namespace object containing parsed arguments.
    """
    help_help = 'Show this help message and exit.'  # Heh.

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-h', '--help', action='help', help=help_help)
    subparsers = parser.add_subparsers(dest='subparser')

    sp_sort_help = 'Sorts files that have a valid name format and a valid extension.'
    sp_sort_source_help = 'Source directory to search.'
    sp_sort_destination_help = 'Destination to move organized files in (default: equal to source.)'
    sp_sort_recursive_help = 'Searches the whole source directory tree for files.'
    sp_sort_copy_help = 'Copies files into destination instead of moving them.'
    sp_sort_verbose_help = "Prints out the files as they're being organized."
    sp_sort_ext_help = 'List of extensions to allow sorting for (default: JPG, MP4.)'

    sp_sort = subparsers.add_parser('sort', add_help=False, help=sp_sort_help)
    sp_sort.add_argument('-h', '--help', action='help', help=help_help)
    sp_sort.add_argument('source', help=sp_sort_source_help)
    sp_sort.add_argument('destination', nargs='?', help=sp_sort_destination_help)
    sp_sort.add_argument('-r', '--recursive', action='store_true', help=sp_sort_recursive_help)
    sp_sort.add_argument('-c', '--copy', action='store_true', help=sp_sort_copy_help)
    sp_sort.add_argument('-v', '--verbose', action='store_true', help=sp_sort_verbose_help)
    sp_sort.add_argument('-e', '--extensions', nargs='+', default=('.jpg', '.mp4'), help=sp_sort_ext_help)

    sp_list_help = 'Prints out the files that would be sorted within the provided source directory.'
    sp_list_source_help = 'Directory to list valid files from.'
    sp_list_recursive_help = 'Searches the whole source directory tree for files.'
    sp_list_ext_help = 'List of extensions to look for (default: JPG, MP4.)'

    sp_list = subparsers.add_parser('list', add_help=False, help=sp_list_help)
    sp_list.add_argument('-h', '--help', action='help', help=help_help)
    sp_list.add_argument('source', help=sp_list_source_help)
    sp_list.add_argument('-r', '--recursive', action='store_true', help=sp_list_recursive_help)
    sp_list.add_argument('-e', '--extensions', nargs='+', default=('.jpg', '.mp4'), help=sp_list_ext_help)

    if len(args) == 0:
        parser.print_usage()
        exit(1)

    settings = parser.parse_args(args)
    if settings.subparser == 'sort':
        settings.destination = settings.source if not settings.destination else settings.destination

    TimeFileUtilities.allowed_extensions = settings.extensions

    return settings


def pick_an_action(settings):
    """
    Decides what the program should do depending on the selected subparser.

    :param settings: An argparse.Namespace of parser user arguments.
    :return: None.
    """
    file_getter = get_files_recursively if settings.recursive else get_files

    if settings.subparser == 'list':
        list_files(settings.source, file_getter)
    elif settings.subparser == 'sort':
        files = file_getter(settings.source)
        organize_files(settings.destination, files, copy=settings.copy, verbose=settings.verbose)


if __name__ == '__main__':
    settings = parse_user_input()

    pick_an_action(settings)
    exit(0)
