import typing

BOOL_TRUE_STRINGS: typing.Set[str] = {
    'true', 't',
    'yes', 'y',
    '1',
}

BOOL_FALSE_STRINGS: typing.Set[str] = {
    'false', 'f',
    'no', 'n',
    '0',
}

def soft_boolean(raw_text: typing.Union[str, bool]) -> typing.Union[bool, None]:
    """
    Parse a boolean from a string using common string representations for true/false.
    This function assumes the entire string is the boolean (not just a part of it).
    If the string is not true or false, then return None.
    """

    if (isinstance(raw_text, bool)):
        return raw_text

    text = str(raw_text).lower().strip()

    if (text in BOOL_TRUE_STRINGS):
        return True

    if (text in BOOL_FALSE_STRINGS):
        return False

    return None

def boolean(raw_text: typing.Union[str, bool]) -> bool:
    """
    Like soft_boolean(), but raise an exception if no boolean is parsed.
    """

    if (isinstance(raw_text, bool)):
        return raw_text

    text = str(raw_text).lower().strip()

    if (text in BOOL_TRUE_STRINGS):
        return True

    if (text in BOOL_FALSE_STRINGS):
        return False

    raise ValueError(f"Could not convert text to boolean: '{raw_text}'.")
