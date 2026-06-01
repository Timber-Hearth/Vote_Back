from fastapi import status


class PollError(Exception):
	status_code = status.HTTP_400_BAD_REQUEST
	detail = "poll error"

	def __init__(self, detail: str | None = None):
		super().__init__(detail or self.detail)
		if detail is not None:
			self.detail = detail


class PollNotFoundError(PollError):
	status_code = status.HTTP_404_NOT_FOUND
	detail = "Poll not found"


