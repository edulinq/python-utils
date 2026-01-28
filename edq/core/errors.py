import typing

class UtilsError(Exception):
    """ General errors raised from this library. """

class RetryError(UtilsError):
    """ An error that came up after trying an operation for a specified number of times (e.g., network retries). """

    def __init__(self, message: str, retry_errors: typing.Union[typing.List[Exception], None] = None) -> None:
        super().__init__(message)

        if (retry_errors is None):
            retry_errors = []

        self.retry_errors: typing.List[Exception] = retry_errors
        """ Any errors that occurred and prompted the retries. """

    def contains_instance(self, target_type: typing.Type) -> bool:
        """ Check if one of the retry errors has the given type. """

        for retry_error in self.retry_errors:
            if (isinstance(retry_error, target_type)):
                return True

        return False
