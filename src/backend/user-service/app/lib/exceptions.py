from fastapi import status


class UserServiceError(Exception):
    """Base class for domain errors mapped to HTTP responses.

    Subclasses set ``status_code``; the message passed at construction time is
    surfaced to the client in the response envelope.
    """

    status_code: int = status.HTTP_400_BAD_REQUEST
    default_message: str = "User service error"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class UsernameNotFound(UserServiceError):
    status_code = status.HTTP_404_NOT_FOUND
    default_message = "Username not found"


class UsernamePasswordIncorrect(UserServiceError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_message = "Username or Password is incorrect"


class UsernameTaken(UserServiceError):
    status_code = status.HTTP_409_CONFLICT
    default_message = "Username is already taken"


class InvalidCredentials(UserServiceError):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_message = "Could not validate credentials"
