import os

def get_file_extension(file_path):
    """
    :param file_path: The path of file
    :type file_path: str
    :return: file extension
    :rtype: str
    """
    _, file_extension = os.path.splitext(file_path)
    return file_extension

def check_file_extension(source_path, extension):
    """
    :param source_path: The path of the source file
    :type source_path: str
    :return: whether the file's extention is *.py* or not
    :rtype: bool
    """
    return get_file_extension(source_path) == '.' + extension

def have_the_same_file_extension(file_path_1, file_path_2):
    """
    :param file_path_1: The path of file 1
    :type file_path_1: str
    :param file_path_2: The path of file 2
    :type file_path_2: str
    :return: same or not
    :rtype: bool
    """
    return get_file_extension(file_path_1) == get_file_extension(file_path_2)