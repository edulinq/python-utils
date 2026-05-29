import enum
import typing

def has_value(enum_class: typing.Type[enum.Enum], value: typing.Any) -> bool:
    """ Check if the given value is one of the possible values for the given enum. """

    if (value in enum_class):
        return True

    enum_values = {member.value for member in enum_class}
    return (value in enum_values)
