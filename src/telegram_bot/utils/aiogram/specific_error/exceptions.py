from aiogram.exceptions import TelegramAPIError, TelegramBadRequest


class SpecificAPIError(TelegramAPIError):
    match: str = ""
    __subclasses: list[type["SpecificAPIError"]] = []  # noqa: RUF012

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        if not hasattr(
            cls,
            f"_{cls.__name__}__group",
        ):  # obtaining "protected" attribute of the class
            cls.__subclasses.append(
                cls,
            )  # if the class is an error class and not class for error grouping, add to subclasses

    @classmethod
    def match_error_description(cls, description: str) -> bool:
        if (
            not cls.match
        ):  # prevent false catching by classes that didn't override the 'match' value
            return False

        return cls.match.casefold() in description.casefold()

    @classmethod
    def specify_error(cls, error: TelegramAPIError) -> TelegramAPIError:
        error_description = error.message

        for specific_error in cls.__subclasses:
            if specific_error is cls:
                continue

            if specific_error.match_error_description(error_description):
                return specific_error(method=error.method, message=error.message)
        return error


class MessageError(TelegramBadRequest, SpecificAPIError):
    __group = True  # __ prefix is needed for variable owned by this class, it will not propagate to classes based on it


class MessageNotModifiedError(MessageError):
    match = "message is not modified"


class MessageCantBeDeletedError(MessageError):
    match = "message can't be deleted"


class InvalidQueryIDError(TelegramBadRequest, SpecificAPIError):
    match = "query is too old and response timeout expired or query id is invalid"
