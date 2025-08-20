import typing
import unittest

import edq.util.json
import edq.util.reflection

FORMAT_STR: str = "\n--- Expected ---\n%s\n--- Actual ---\n%s\n---\n"

class BaseTest(unittest.TestCase):
    """
    A base class for unit tests.
    """

    maxDiff = None
    """ Don't limit the size of diffs. """

    def assertJSONDictEqual(self, a: typing.Any, b: typing.Any, msg: typing.Union[str, None] = None) -> None:  # pylint: disable=invalid-name
        """
        Like unittest.TestCase.assertDictEqual(),
        but will try to convert each comparison argument to a dict if it is not already,
        and uses an assertion message containing the full JSON representation of the arguments.

        If a custom message is provided, it will replace the default JSON-based message.
        """

        if (not isinstance(a, dict)):
            if (isinstance(a, edq.util.json.DictConverter)):
                a = a.to_dict()
            else:
                a = vars(a)

        if (not isinstance(b, dict)):
            if (isinstance(b, edq.util.json.DictConverter)):
                b = b.to_dict()
            else:
                b = vars(b)

        a_json = edq.util.json.dumps(a, indent = 4)
        b_json = edq.util.json.dumps(b, indent = 4)

        if (msg is None):
            msg = FORMAT_STR % (a_json, b_json)

        super().assertDictEqual(a, b, msg = msg)

    def assertJSONListEqual(self, a: typing.List[typing.Any], b: typing.List[typing.Any], msg: typing.Union[str, None] = None) -> None:  # pylint: disable=invalid-name
        """
        Call assertDictEqual(), but supply a message containing the full JSON representation of the arguments.
        If a custom message is provided, it will replace the default JSON-based message.
        """

        a_json = edq.util.json.dumps(a, indent = 4)
        b_json = edq.util.json.dumps(b, indent = 4)

        if (msg is None):
            msg = FORMAT_STR % (a_json, b_json)

        super().assertListEqual(a, b, msg = msg)

    def format_error_string(self, ex: typing.Union[BaseException, None]) -> str:
        """
        Format an error string from an exception so it can be checked for testing.
        The type of the error will be included,
        and any nested errors will be joined together.
        """

        parts = []

        while (ex is not None):
            type_name = edq.util.reflection.get_qualified_name(ex)
            message = str(ex)

            parts.append(f"{type_name}: {message}")

            ex = ex.__cause__

        return "; ".join(parts)
