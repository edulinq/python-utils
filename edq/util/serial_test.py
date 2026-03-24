import enum
import typing

import edq.testing.unittest
import edq.util.serial

class _TestEnumStr(enum.StrEnum):
    """ A test enum that only has strings. """

    FIRST = 'a'
    SECOND = 'b'

class _TestEnumInt(enum.IntEnum):
    """ A test enum that only has ints. """

    FIRST = 1
    SECOND = 2

class _TestEnumMix(enum.Enum):
    """ A test enum that has mixed values. """

    FIRST = 'z'
    SECOND = 9

class _BaseTestClass(edq.util.serial.DictConverter):
    """ A class with many differnt types to serial. """

    def __init__(self,
            value_str: typing.Union[str, None] = None,
            value_int: typing.Union[str, None] = None,
            enum_str: typing.Union[_TestEnumStr, None] = None,
            enum_int: typing.Union[_TestEnumInt, None] = None,
            enum_mix: typing.Union[_TestEnumMix, None] = None,
            nested: typing.Union['_BaseTestClass', None] = None,
            **kwargs: typing.Any) -> None:
        self.value_str: typing.Union[str, None] = value_str
        self.value_int: typing.Union[int, None] = value_int
        self.enum_str: typing.Union[_TestEnumStr, None] = enum_str
        self.enum_int: typing.Union[_TestEnumInt, None] = enum_int
        self.enum_mix: typing.Union[_TestEnumMix, None] = enum_mix
        self.nested: typing.Union[_BaseTestClass, None] = nested

    def __eq__(self, other: object) -> bool:
        """ Add in a hard equality check so exact types are checked. """

        if (not isinstance(other, _BaseTestClass)):
            return False

        self_vars = vars(self)
        other_vars = vars(other)

        if (self_vars.keys() != other_vars.keys()):
            return False

        for key in self_vars.keys():
            if (type(self_vars[key]) != type(other_vars[key])):
                return False

            if (self_vars[key] != other_vars[key]):
                return False

        return True

class TestDictConverter(edq.testing.unittest.BaseTest):
    """ Test the DictConverter. """

    def test_conversion_base(self):
        """
        Test the base functionality for converting to and from a type.
        """

        # [(value, expected dict, error_substring), ...]
        # Nulls will be inserted into the expected dicts for missing keys.
        test_cases = [
            # Base
            (
                _BaseTestClass(value_str = 'abc'),
                {
                    'value_str': 'abc',
                },
                None,
            ),
            (
                _BaseTestClass(value_int = 123),
                {
                    'value_int': 123,
                },
                None,
            ),
            (
                _BaseTestClass(enum_str = _TestEnumStr.FIRST),
                {
                    'enum_str': 'a',
                },
                None,
            ),
            (
                _BaseTestClass(enum_int = _TestEnumInt.FIRST),
                {
                    'enum_int': 1,
                },
                None,
            ),
            (
                _BaseTestClass(enum_mix = _TestEnumMix.FIRST),
                {
                    'enum_mix': 'z',
                },
                None,
            ),
            (
                _BaseTestClass(nested = _BaseTestClass(enum_str = _TestEnumStr.FIRST)),
                {
                    'nested': {
                        'enum_str': 'a',
                    },
                },
                None,
            ),

            # Bad Enums Types
            (
                _BaseTestClass(enum_str = _TestEnumStr.FIRST),
                {
                    'enum_str': 1,
                },
                'is not a valid',
            ),
            (
                _BaseTestClass(enum_int = _TestEnumInt.FIRST),
                {
                    'enum_int': '1',
                },
                'is not a valid',
            ),

            # Bad Enum Value
            (
                _BaseTestClass(enum_mix = _TestEnumMix.FIRST),
                {
                    'enum_mix': 'ZZZ',
                },
                'is not a valid',
            ),
        ]

        for (i, test_case) in enumerate(test_cases):
            (value, expected_dict, error_substring) = test_case

            # Insert null values for missing keys into the expected dict.
            to_normalize = [expected_dict]
            while (len(to_normalize) > 0):
                normalize = to_normalize.pop(0)

                if ('nested' in normalize):
                    to_normalize.append(normalize['nested'])

                for key in vars(value).keys():
                    if (key not in normalize):
                        normalize[key] = None

            with self.subTest(msg = f"Case {i}:"):
                try:
                    actual_dict = value.to_dict()
                    new_object = value.__class__.from_dict(expected_dict)
                except AssertionError:
                    # The subttest failed an assertion.
                    raise
                except Exception as ex:
                    error_string = self.format_error_string(ex)
                    if (error_substring is None):
                        self.fail(f"Unexpected error: '{error_string}'.")

                    self.assertIn(error_substring, error_string, 'Error is not as expected.')

                    continue

                if (error_substring is not None):
                    self.fail(f"Did not get expected error: '{error_substring}'.")

                self.assertJSONDictEqual(expected_dict, actual_dict)
                self.assertJSONEqual(value, new_object)
