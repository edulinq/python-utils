import dataclasses
import enum
import os
import typing

import edq.core.errors

import edq.util.json

ConverterClass = typing.TypeVar('ConverterClass', bound = 'DictConverter')

@dataclasses.dataclass
class DictConverterOptions:
    """ Options to control dict converter functionality. """

    allow_to_dict: bool = True
    """ Allows the use of the to_dict() method. """

    allow_from_dict: bool = True
    """ Allows the use of the from_dict() class method. """

    skip_fields: typing.Union[typing.Set[str], None] = None
    """ A list of field names to skip. """

    omit_none: bool = False
    """ Do not include None (null) fields in serialization. """

    omit_empty: bool = False
    """ Do not include empty fields (fields with a __len__ that return 0) in serialization. """

    def skip_field(self, name: str, value: typing.Any) -> bool:
        """ Check if a field should be skipped. """

        if ((self.skip_fields is not None) and (name in self.skip_fields)):
            return True

        if (self.omit_none and (value is None)):
            return True

        if (self.omit_empty and hasattr(value, '__len__') and (len(value) == 0)):
            return True

        return False

    def raise_to_dict(self) -> None:
        """ Raise an exception if to_dict() should not be called. """

        if (self.allow_to_dict):
            return

        raise(edq.core.errors.SerializationError("Use of to_dict() has been disallowed for this class."))

    def raise_from_dict(self) -> None:
        """ Raise an exception if from_dict() should not be called. """

        if (self.allow_from_dict):
            return

        raise(edq.core.errors.SerializationError("Use of from_dict() has been disallowed for this class."))

class DictConverter():
    """
    A base class for class that can represent (serialize) and reconstruct (deserialize) themselves as/from a dict.
    The intention is that the dict can then be cleanly converted to/from JSON.

    General (but inefficient) implementations of several core Python equality, comparison, and representation methods are provided.
    A default hash implementation is provided, but it is up to child classes themselves to ensure they are immutable
    (if they want to be used as set elements or dict keys).

    Any class that uses the default implementations should have a constructor
    that accepts arguments with the same name as their members.
    It is generally recommended to also have the constructor accept a kwargs,
    since values will be blindly passed to the constructor.
    """

    _dictconverter_options: DictConverterOptions = DictConverterOptions()

    def to_dict(self, **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        """
        Return a dict that can be used to represent this object.
        If the dict is passed to from_dict(), an identical object should be reconstructed.

        A general (but inefficient) implementation is provided by default.
        """

        self._dictconverter_options.raise_to_dict()

        data: typing.Dict[str, typing.Any] = {}

        for (key, value) in vars(self).items():
            if (self._dictconverter_options.skip_field(key, value)):
                continue

            data[key] = self._to_pod(value)

        return data

    def _to_pod(self, raw_value: typing.Any) -> typing.Any:
        """
        Attempt to convert a single value to a simpler type for use in to_dict().

        Has special handling for:
         - DictConverter
         - enum.Enum
         - (list, tuple, set)
         - dict
        """

        if (raw_value is None):
            return None

        if (isinstance(raw_value, DictConverter)):
            return raw_value.to_dict()

        if (isinstance(raw_value, enum.Enum)):
            return raw_value.value

        if (isinstance(raw_value, (list, tuple, set))):
            items = [self._to_pod(item) for item in raw_value]

            # Sort sets for consistency.
            if (isinstance(raw_value, set)):
                items.sort()

            return items

        if (isinstance(raw_value, dict)):
            return {key: self._to_pod(value) for (key, value) in raw_value.items()}

        return raw_value

    @classmethod
    def prep_init_data(cls, data: typing.Dict[str, typing.Any], **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        """
        Prepare data to be passed into this class' constructor.

        By default, this is called by from_dict().
        A child can override this or prep_init_data() depending on the functionality they want.

        A general (but inefficient) implementation is provided by default.
        This implementation will attempt to use type hints (of cls.__init__()) to convert enums and DictConverters.
        """

        new_data = {}
        constructor_types = typing.get_type_hints(cls.__init__)

        for (key, value) in data.items():
            if (cls._dictconverter_options.skip_field(key, value)):
                continue

            new_data[key] = cls._from_pod(constructor_types.get(key, None), value)

        return new_data

    @classmethod
    def _from_pod(cls, type_hint: typing.Any, raw_value: typing.Any) -> typing.Any:
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
            if (_check_issubclass(allowed_type, DictConverter) and isinstance(raw_value, dict)):
                return allowed_type.from_dict(raw_value)

            if (_check_issubclass(allowed_type, enum.Enum) and (raw_value in allowed_type)):
                return allowed_type(raw_value)

            # Sequence container types.
            if ((typing.get_origin(allowed_type) in (list, tuple, set)) and isinstance(raw_value, (list, tuple, set))):
                collection_type = typing.get_origin(allowed_type)

                item_type = None
                args = typing.get_args(allowed_type)
                if (len(args) > 0):
                    item_type = args[0]

                return collection_type([cls._from_pod(item_type, item) for item in raw_value])

            # Dict
            if ((typing.get_origin(allowed_type) is dict) and isinstance(raw_value, dict)):
                key_type = None
                value_type = None

                args = typing.get_args(allowed_type)
                if (len(args) == 2):
                    key_type = args[0]
                    value_type = args[1]

                return {cls._from_pod(key_type, key): cls._from_pod(value_type, value) for (key, value) in raw_value.items()}

        # No special conversion was made, try to force the first type.

        force_type = allowed_types[0]
        if (not isinstance(force_type, type)):
            force_type = typing.get_origin(force_type)

        if (force_type is not None):
            return force_type(raw_value)

        return raw_value

    @classmethod
    def from_dict(cls: typing.Type[ConverterClass], data: typing.Dict[str, typing.Any], **kwargs: typing.Any) -> ConverterClass:
        """
        Return an instance of this subclass created using the given dict.
        If the dict came from to_dict(), the returned object should be equivalent to the original.

        By default, this function just calls the class' constructor with the output of prep_init_data().
        A child can override this or prep_init_data() depending on the functionality they want.

        A general (but inefficient) implementation is provided by default.
        This implementation will attempt to use type hints (of the classes constructor) to convert enums and DictConverters.
        """

        cls._dictconverter_options.raise_from_dict()

        new_data = cls.prep_init_data(data)
        return cls(**new_data)

    @classmethod
    def from_path(cls: typing.Type[ConverterClass], path: str, **kwargs: typing.Any) -> ConverterClass:
        """ Read the path (as JSON) and call from_dict(). """

        kwargs['base_dir'] = os.path.dirname(os.path.abspath(path))
        data = edq.util.json.load_path(path)

        return cls.from_dict(data, **kwargs)

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

    def __lt__(self, other: 'DictConverter') -> bool:
        return repr(self) < repr(other)

    def __hash__(self) -> int:
        return hash(repr(self))

    def __str__(self) -> str:
        return repr(self)

    def __repr__(self) -> str:
        return edq.util.json.dumps(self)

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
