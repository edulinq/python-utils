import enum
import os
import typing

import edq.core.errors

import edq.util.json

PODType = typing.Union[bool, float, int, str, typing.List['PODType'], typing.Dict[str, 'PODType'], None]  # pylint: disable=invalid-name
""" A "Plain Old Data" type that can be easily represented (e.g. in JSON). """

DictSerializerClass = typing.TypeVar('DictSerializerClass', bound = 'DictSerializer')
DictDeserializerClass = typing.TypeVar('DictDeserializerClass', bound = 'DictDeserializer')
DictConverterClass = typing.TypeVar('DictConverterClass', bound = 'DictConverter')

PODSerializerClass = typing.TypeVar('PODSerializerClass', bound = 'PODSerializer')
PODDeserializerClass = typing.TypeVar('PODDeserializerClass', bound = 'PODDeserializer')
PODConverterClass = typing.TypeVar('PODConverterClass', bound = 'PODConverter')

class PODSerializer:
    """
    A class that can represent itself as a POD type.
    Sibling to PODDeserializer.
    """

    def to_pod(self,
            serialization_options: typing.Union[typing.Dict[str, typing.Any], None] = None,
            ) -> PODType:
        """
        Get a POD representation of this object.

        The default implementation will convert to a dict (similar to a DictSerializer).
        """

        return {key: generic_to_pod(value, serialization_options) for (key, value) in vars(self).items()}

class PODDeserializer:
    """
    A class that can construct itself from a POD type.
    Sibling to PODSerializer.
    """

    @classmethod
    def from_pod(cls: typing.Type[PODDeserializerClass],
            data: PODType,
            serialization_options: typing.Union[typing.Dict[str, typing.Any], None] = None,
            ) -> PODDeserializerClass:
        """
        Create an instance of this class from a POD.

        The default implementation will call the class' constructor with one of two things:
        a splat/unpacking (**) of the incoming data if the data is a dict,
        otherwise the data itself.
        """

        if (isinstance(data, dict)):
            return cls(**data)  # type: ignore[call-arg]

        return cls(data)  # type: ignore[call-arg]

class PODConverter(PODSerializer, PODDeserializer):
    """ A PODSerializer and PODDeserializer. """

class DictSerializationBase:
    """
    A base class for the dict serialization classes.

    Note that this causes diamond inheritance for classes that extend DictConverter,
    but since this class only provides simple functionality not overwritten by any branch child,
    there should be no issues.
    """

    serialization_skip_fields: typing.Union[typing.Set[str], None] = None
    """ A list of field names to skip. """

    serialization_omit_none: bool = False
    """ Do not include None (null) fields in serialization. """

    serialization_omit_empty: bool = False
    """ Do not include empty fields (fields with a __len__ that return 0) in serialization. """

    @classmethod
    def skip_field(cls, name: str, value: typing.Any) -> bool:
        """ Check if a field should be skipped. """

        if ((cls.serialization_skip_fields is not None) and (name in cls.serialization_skip_fields)):
            return True

        if (cls.serialization_omit_none and (value is None)):
            return True

        if (cls.serialization_omit_empty and hasattr(value, '__len__') and (len(value) == 0)):
            return True

        return False

class DictSerializer(DictSerializationBase):
    """
    A base class for class that can represent itself as a dict.
    The intention is that the dict can then be cleanly converted to/from JSON.

    General (but inefficient) implementations of several core Python equality, comparison, and representation methods are provided.
    A default hash implementation is provided, but it is up to child classes themselves to ensure they are immutable
    if they want to be used as set elements or dict keys.
    """

    def to_dict(self,
            serialization_options: typing.Union[typing.Dict[str, typing.Any], None] = None,
            ) -> typing.Dict[str, typing.Any]:
        """
        Return a dict that can be used to represent this object.
        If the dict is passed to from_dict(), an identical object should be reconstructed.

        A general (but inefficient) implementation is provided by default.
        """

        data: typing.Dict[str, typing.Any] = {}

        for (key, value) in vars(self).items():
            if (self.skip_field(key, value)):
                continue

            data[key] = generic_to_pod(value, serialization_options)

        return data

    def __eq__(self, other: object) -> bool:
        """
        Check for equality.

        This check uses to_dict() and compares the results.
        This may not be complete or efficient depending on the child class.
        """

        # Note the hard type check (done so we can keep this method general).
        if (type(self) != type(other)):  # pylint: disable=unidiomatic-typecheck
            return False

        return bool(self.to_dict() == other.to_dict())  # type: ignore[attr-defined]

    def __lt__(self, other: 'DictSerializer') -> bool:
        return repr(self) < repr(other)

    def __hash__(self) -> int:
        return hash(repr(self))

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return edq.util.json.dumps(self)

class DictDeserializer(DictSerializationBase):
    """
    A base class for class that can reconstruct (deserialize) themselves from a dict.
    The intention is that the class can be cleanly converted from JSON.

    Any class that uses the default implementations should have a constructor
    that accepts arguments with the same name as their members.
    It is generally recommended to also have the constructor accept a kwargs,
    since values will be blindly passed to the constructor.
    """

    @classmethod
    def prep_init_data(cls,
            data: typing.Dict[str, typing.Any],
            serialization_options: typing.Union[typing.Dict[str, typing.Any], None] = None,
            ) -> typing.Dict[str, typing.Any]:
        """
        Prepare data to be passed into this class' constructor.

        By default, this is called by from_dict().
        A child can override this or prep_init_data() depending on the functionality they want.

        A general (but inefficient) implementation is provided by default.
        This implementation will attempt to use type hints (of the classes constructor) to convert enums and DictDeserializers.
        """

        new_data = {}
        constructor_types = typing.get_type_hints(cls.__init__)

        for (key, value) in data.items():
            if (cls.skip_field(key, value)):
                continue

            new_data[key] = _from_pod(constructor_types.get(key, None), value, serialization_options)

        return new_data

    @classmethod
    def from_dict(cls: typing.Type[DictDeserializerClass],
            data: typing.Dict[str, typing.Any],
            serialization_options: typing.Union[typing.Dict[str, typing.Any], None] = None,
            ) -> DictDeserializerClass:
        """
        Return an instance of this subclass created using the given dict.
        If the dict came from to_dict(), the returned object should be equivalent to the original.

        By default, this function just calls the class' constructor with the output of prep_init_data().
        A child can override this or prep_init_data() depending on the functionality they want.

        A general (but inefficient) implementation is provided by default.
        This implementation will attempt to use type hints (of the classes constructor) to convert enums and DictDeserializers.
        """

        new_data = cls.prep_init_data(data)
        return cls(**new_data)

    @classmethod
    def from_path(cls: typing.Type[DictDeserializerClass],
            path: str,
            serialization_options: typing.Union[typing.Dict[str, typing.Any], None] = None,
            ) -> DictDeserializerClass:
        """ Read the path (as JSON) and call from_dict(). """

        if (serialization_options is None):
            serialization_options = {}

        serialization_options['base_dir'] = os.path.dirname(os.path.abspath(path))
        data = edq.util.json.load_path(path)

        return cls.from_dict(data, serialization_options)

class DictConverter(DictSerializer, DictDeserializer):
    """ A DictSerializer and DictDeserializer. """

def _check_issubclass(allowed_type: typing.Any, target: typing.Type) -> bool:
    """
    Call issubclass(), but squash and type errors.
    issubclass() can be picky about the input types is accepts.
    """

    if (allowed_type is None):
        return False

    try:
        return issubclass(allowed_type, target)
    except TypeError:
        return False

def generic_to_pod(
        raw_value: typing.Any,
        serialization_options: typing.Union[typing.Dict[str, typing.Any], None] = None,
        ) -> PODType:
    """
    Attempt to convert a value to a POD type.

    Has special handling for:
        - DictSerializer
        - PODSerializer
        - enum.Enum
        - (list, tuple, set)
        - dict
    """

    if (raw_value is None):
        return None

    # Simple types that are already POD.
    if (isinstance(raw_value, (bool, float, int, str))):
        return raw_value

    if (isinstance(raw_value, DictSerializer)):
        return raw_value.to_dict(serialization_options)

    if (isinstance(raw_value, PODSerializer)):
        return raw_value.to_pod(serialization_options)

    if (isinstance(raw_value, enum.Enum)):
        return raw_value.value

    if (isinstance(raw_value, (list, tuple, set))):
        items = [generic_to_pod(item, serialization_options) for item in raw_value]

        # Sort sets for consistency.
        if (isinstance(raw_value, set)):
            # Sort using the string representation of the items (since the set could be heterogeneous and have non-comparable items).
            sort_list = sorted([(item, i) for (i, item) in enumerate(map(str, items))])
            items = [items[i] for (_, i) in sort_list]

        return items

    if (isinstance(raw_value, dict)):
        return {key: generic_to_pod(value, serialization_options) for (key, value) in raw_value.items()}


    raise ValueError(f"Unable to convert value to simple (edq.util.serial.POD) type: '{raw_value}' (type: '{type(raw_value)}').")

def _from_pod(
        type_hint: typing.Any,
        raw_value: typing.Any,
        serialization_options: typing.Union[typing.Dict[str, typing.Any], None] = None,
        ) -> typing.Any:
    """ Attempt to convert a value to the hinted value. """

    if (type_hint is None):
        return raw_value

    allowed_types: typing.Tuple[typing.Any, ...] = tuple([type_hint])

    # Check if the hint is a union.
    if (typing.get_origin(type_hint) is typing.Union):
        allowed_types = typing.get_args(type_hint)

    if (len(allowed_types) == 0):
        return raw_value

    # Check each possible type and match the first one.
    for allowed_type in allowed_types:
        if (_check_issubclass(allowed_type, DictDeserializer) and isinstance(raw_value, dict)):
            return allowed_type.from_dict(raw_value, serialization_options)

        if (_check_issubclass(allowed_type, PODDeserializer)):
            return allowed_type.from_pod(raw_value, serialization_options)

        if (_check_issubclass(allowed_type, enum.Enum) and (raw_value in allowed_type)):
            return allowed_type(raw_value)

        # Sequence container types.
        if ((typing.get_origin(allowed_type) in (list, tuple, set)) and isinstance(raw_value, (list, tuple, set))):
            collection_type = typing.get_origin(allowed_type)

            item_type = None
            args = typing.get_args(allowed_type)
            if (len(args) > 0):
                item_type = args[0]

            return collection_type([_from_pod(item_type, item, serialization_options) for item in raw_value])

        # Dict
        if ((typing.get_origin(allowed_type) is dict) and isinstance(raw_value, dict)):
            key_type = None
            value_type = None

            args = typing.get_args(allowed_type)
            if (len(args) == 2):
                key_type = args[0]
                value_type = args[1]

            return {
                _from_pod(key_type, key, serialization_options): _from_pod(value_type, value, serialization_options)
                for (key, value)
                in raw_value.items()
            }

    # No special conversion was made, try to force the first type.

    force_type = allowed_types[0]
    if (not isinstance(force_type, type)):
        force_type = typing.get_origin(force_type)

    if (force_type is not None):
        return force_type(raw_value)

    return raw_value
