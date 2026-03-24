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

    def skip_field(self, name: str) -> bool:
        """ Check if a field should be skipped. """

        if (self.skip_fields is None):
            return False

        return (name in self.skip_fields)

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
        This implementation will convert enums and DictConverters automatically.
        """

        self._dictconverter_options.raise_to_dict()

        data: typing.Dict[str, typing.Any] = {}

        for (key, value) in vars(self).items():
            if (self._dictconverter_options.skip_field(key)):
                continue

            if (isinstance(value, DictConverter)):
                value = value.to_dict()
            elif (isinstance(value, enum.Enum)):
                value = value.value

            data[key] = value

        return data

    @classmethod
    def prep_init_data(cls, data: typing.Dict[str, typing.Any], **kwargs: typing.Any) -> typing.Dict[str, typing.Any]:
        """
        Prepare data to be passed into this class' constructor.

        By default, this is called by from_dict().
        A child can override this or prep_init_data() depending on the functionality they want.

        A general (but inefficient) implementation is provided by default.
        This implementation will attempt to use type hints (of the classes constructor) to convert enums and DictConverters.
        """

        new_data = {}
        constructor_types = typing.get_type_hints(cls.__init__)

        for (key, value) in data.items():
            if (cls._dictconverter_options.skip_field(key)):
                continue

            constructor_type = constructor_types.get(key, None)

            # Attempt to match each piece of data with and argument (and argument type).
            # In the case of a typing.Union, use the first matching type.
            allowed_types: typing.Tuple[typing.Any, ...] = tuple()
            if (constructor_type is not None):
                allowed_types = tuple([constructor_type])
                if (typing.get_origin(constructor_type) is typing.Union):
                    allowed_types = typing.get_args(constructor_type)

            for allowed_type in allowed_types:
                if (issubclass(allowed_type, DictConverter) and isinstance(value, dict)):
                    value = allowed_type.from_dict(value)
                    break

                if (issubclass(allowed_type, enum.Enum) and (value is not None)):
                    value = allowed_type(value)
                    break

            new_data[key] = value

        return new_data

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
