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

class _TestPODConverter(edq.util.serial.PODConverter):
    """ A class that can convert to-from a POD. """

    def __init__(self,
            value: str,
            ) -> None:
        self.value: str = value

    def to_pod(self,
            serialization_options: typing.Union[typing.Dict[str, typing.Any], None] = None,
            ) -> str:
        return self.value

class _TestDictConverter(edq.util.serial.DictConverter):
    """ A class with many differnt types to serial. """

    serialization_omit_none = True

    def __init__(self,
            value_str: typing.Union[str, None] = None,
            value_int: typing.Union[int, None] = None,

            enum_str: typing.Union[_TestEnumStr, None] = None,
            enum_int: typing.Union[_TestEnumInt, None] = None,
            enum_mix: typing.Union[_TestEnumMix, None] = None,

            nested: typing.Union['_TestDictConverter', None] = None,

            list_str: typing.Union[typing.List[str], None] = None,
            list_nested: typing.Union[typing.List['_TestDictConverter'], None] = None,
            tuple_str: typing.Union[typing.Tuple[str, ...], None] = None,
            set_str: typing.Union[typing.Set[str], None] = None,

            dict_str: typing.Union[typing.Dict[str, str], None] = None,
            dict_mixed: typing.Union[typing.Dict[str, typing.Union[str, int, _TestEnumStr, _TestEnumInt]], None] = None,
            dict_nested: typing.Union[typing.Dict[str, '_TestDictConverter'], None] = None,

            **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)

        self.value_str: typing.Union[str, None] = value_str
        self.value_int: typing.Union[int, None] = value_int

        self.enum_str: typing.Union[_TestEnumStr, None] = enum_str
        self.enum_int: typing.Union[_TestEnumInt, None] = enum_int
        self.enum_mix: typing.Union[_TestEnumMix, None] = enum_mix

        self.nested: typing.Union[_TestDictConverter, None] = nested

        self.list_str: typing.Union[typing.List[str], None] = list_str
        self.list_nested: typing.Union[typing.List['_TestDictConverter'], None] = list_nested
        # Skip a nested set/tuple because our testing type is mutable.
        self.tuple_str: typing.Union[typing.Tuple[str, ...], None] = tuple_str
        self.set_str: typing.Union[typing.Set[str], None] = set_str

        self.dict_str: typing.Union[typing.Dict[str, str], None] = dict_str
        self.dict_mixed: typing.Union[typing.Dict[str, typing.Union[str, int, _TestEnumStr, _TestEnumInt]], None] = dict_mixed
        self.dict_nested: typing.Union[typing.Dict[str, '_TestDictConverter'], None] = dict_nested

    def __eq__(self, other: object) -> bool:
        """ Add in a hard equality check so exact types are checked. """

        if (not isinstance(other, _TestDictConverter)):
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

class TestSerialization(edq.testing.unittest.BaseTest):
    """ Test basic serialization. """

    def test_dictconverter_base(self) -> None:
        """
        Test the base functionality for converting to and from a dict.
        """

        # [(value, expected dict, error_substring), ...]
        test_cases: typing.List[typing.Tuple[
                edq.util.serial.DictConverter,
                typing.Dict[str, typing.Any],
                typing.Union[str, None],
        ]] = [
            # Base
            (
                _TestDictConverter(value_str = 'abc'),
                {
                    'value_str': 'abc',
                },
                None,
            ),
            (
                _TestDictConverter(value_int = 123),
                {
                    'value_int': 123,
                },
                None,
            ),
            (
                _TestDictConverter(enum_str = _TestEnumStr.FIRST),
                {
                    'enum_str': 'a',
                },
                None,
            ),
            (
                _TestDictConverter(enum_int = _TestEnumInt.FIRST),
                {
                    'enum_int': 1,
                },
                None,
            ),
            (
                _TestDictConverter(enum_mix = _TestEnumMix.FIRST),
                {
                    'enum_mix': 'z',
                },
                None,
            ),
            (
                _TestDictConverter(nested = _TestDictConverter(enum_str = _TestEnumStr.FIRST)),
                {
                    'nested': {
                        'enum_str': 'a',
                    },
                },
                None,
            ),

            # Sequence Types
            (
                _TestDictConverter(list_str = ['a', 'b', 'c']),
                {
                    'list_str': ['a', 'b', 'c'],
                },
                None,
            ),
            (
                _TestDictConverter(list_nested = [
                        _TestDictConverter(value_str = 'abc'),
                        _TestDictConverter(enum_int = _TestEnumInt.FIRST),
                        _TestDictConverter(nested = _TestDictConverter(enum_str = _TestEnumStr.FIRST)),
                ]),
                {
                    'list_nested': [
                        {
                            'value_str': 'abc',
                        },
                        {
                            'enum_int': 1,
                        },
                        {
                            'nested': {
                                'enum_str': 'a',
                            }
                        },
                    ],
                },
                None,
            ),
            (
                _TestDictConverter(tuple_str = ('a', 'b', 'c')),
                {
                    'tuple_str': ['a', 'b', 'c'],
                },
                None,
            ),
            (
                _TestDictConverter(set_str = {'a', 'b', 'c'}),
                {
                    'set_str': ['a', 'b', 'c'],
                },
                None,
            ),

            # Dicts
            (
                _TestDictConverter(dict_str = {
                    'a': 'b',
                    'c': 'd',
                }),
                {
                    'dict_str': {
                        'a': 'b',
                        'c': 'd',
                    },
                },
                None,
            ),
            (
                _TestDictConverter(dict_mixed = {
                    'a': 'abc',
                    'b': 1,
                    'c': _TestEnumStr.FIRST,
                    'd': _TestEnumInt.FIRST,
                }),
                {
                    'dict_mixed': {
                        'a': 'abc',
                        'b': 1,
                        'c': 'a',
                        'd': 1,
                    },
                },
                None,
            ),
            (
                _TestDictConverter(dict_nested = {
                    'a': _TestDictConverter(value_str = 'abc'),
                    'b': _TestDictConverter(enum_int = _TestEnumInt.FIRST),
                    'c': _TestDictConverter(nested = _TestDictConverter(enum_str = _TestEnumStr.FIRST)),
                }),
                {
                    'dict_nested': {
                        'a': {
                            'value_str': 'abc',
                        },
                        'b': {
                            'enum_int': 1,
                        },
                        'c': {
                            'nested': {
                                'enum_str': 'a',
                            }
                        },
                    },
                },
                None,
            ),

            # Bad Enums Types
            (
                _TestDictConverter(enum_str = _TestEnumStr.FIRST),
                {
                    'enum_str': 1,
                },
                'is not a valid',
            ),
            (
                _TestDictConverter(enum_int = _TestEnumInt.FIRST),
                {
                    'enum_int': '1',
                },
                'is not a valid',
            ),

            # Bad Enum Value
            (
                _TestDictConverter(enum_mix = _TestEnumMix.FIRST),
                {
                    'enum_mix': 'ZZZ',
                },
                'is not a valid',
            ),
        ]

        for (i, test_case) in enumerate(test_cases):
            (value, expected_dict, error_substring) = test_case

            with self.subTest(msg = f"Case {i}:"):
                try:
                    actual_dict = value.to_dict()
                    new_object = value.__class__.from_dict(expected_dict)
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

    def test_generic_to_pod__base(self) -> None:
        """
        Test the base functionality of the generic to pod function.
        """

        # [(raw value, expected pod value, error_substring), ...]
        test_cases = [
            # Simple Types
            (
                True,
                True,
                None,
            ),
            (
                1,
                1,
                None,
            ),
            (
                1.2,
                1.2,
                None,
            ),
            (
                'abc',
                'abc',
                None,
            ),
            (
                None,
                None,
                None,
            ),

            # Simple Sequences
            (
                [False, 1, 1.2, 'abc', None],
                [False, 1, 1.2, 'abc', None],
                None,
            ),
            (
                (False, 1, 1.2, 'abc', None),
                [False, 1, 1.2, 'abc', None],
                None,
            ),
            (
                {False, 1, 1.2, 'abc', None},
                [1, 1.2, False, None, 'abc'],
                None,
            ),

            # Simple Dict
            (
                {'a': False, 'b': 1, 'c': 1.2, 'd': 'abc', 'e': None},
                {'a': False, 'b': 1, 'c': 1.2, 'd': 'abc', 'e': None},
                None,
            ),

            # Enum
            (
                _TestEnumStr.FIRST,
                'a',
                None,
            ),
            (
                _TestEnumInt.FIRST,
                1,
                None,
            ),
            (
                _TestEnumMix.FIRST,
                'z',
                None,
            ),
            (
                [_TestEnumStr.FIRST, _TestEnumInt.FIRST, _TestEnumMix.FIRST],
                ['a', 1, 'z'],
                None,
            ),

            # DictSerializer
            (
                _TestDictConverter(value_str = 'abc'),
                {
                    'value_str': 'abc',
                },
                None,
            ),

            # PODSerializer
            (
                _TestPODConverter('abc'),
                'abc',
                None,
            ),

            # Nested
            (
                [
                    1,
                    [
                        {'a': _TestDictConverter(nested = _TestDictConverter(enum_str = _TestEnumStr.FIRST))},
                    ],
                ],
                [
                    1,
                    [
                        {
                            'a': {
                                'nested': {
                                    'enum_str': 'a',
                                },
                            },
                        },
                    ],
                ],
                None,
            ),

            # Non-POD
            (
                b'123',
                None,
                'Unable to convert value to simple (edq.util.serial.POD) type',
            ),
        ]

        for (i, test_case) in enumerate(test_cases):
            (raw_value, expected, error_substring) = test_case

            with self.subTest(msg = f"Case {i}: {raw_value}"):
                try:
                    actual = edq.util.serial.generic_to_pod(raw_value)
                except Exception as ex:
                    error_string = self.format_error_string(ex)
                    if (error_substring is None):
                        self.fail(f"Unexpected error: '{error_string}'.")

                    self.assertIn(error_substring, error_string, 'Error is not as expected.')

                    continue

                if (error_substring is not None):
                    self.fail(f"Did not get expected error: '{error_substring}'.")

                self.assertEqual(expected, actual)
