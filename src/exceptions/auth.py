from fastapi import status


class AuthError(Exception):
	status_code = status.HTTP_400_BAD_REQUEST
	detail = "auth error"

	def __init__(self, detail: str | None = None):
		super().__init__(detail or self.detail)
		if detail is not None:
			self.detail = detail


class UserAlreadyExistsError(AuthError):
	status_code = status.HTTP_409_CONFLICT
	detail = "User already exists"


class InvalidCredentialsError(AuthError):
	status_code = status.HTTP_401_UNAUTHORIZED
	detail = "invalid"


