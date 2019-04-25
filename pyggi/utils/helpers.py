import os

weighted_choice = lambda s : random.choice(sum(([v] * wt for v,wt in s),[]))

def get_file_extension(file_path):
    """
    :param file_path: The path of file
    :type file_path: str
    :return: file extension
    :rtype: str
    """
    _, file_extension = os.path.splitext(file_path)
    return file_extension