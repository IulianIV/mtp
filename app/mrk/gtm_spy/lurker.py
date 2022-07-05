
# better-me add fallback situations when there are no arguments given.
def find_in_index(value: str, index: dict) -> dict:
    """
    Attempts to find 'value' in 'index'.
    Considering that a container hold a lot of information, it is best to index items in dictionaries that
    hold other dictionaries as values, even in the case of single key-value pairs.
    Keeping this consistency avoids having to write exception cases.

    :param value: Dictionary key to look for
    :type value: string
    :param index: Dictionary to search into
    :type index: dictionary
    :return: Dictionary containing value data
    :rtype: dictionary
    """

    return index[value]
