from fastapi import status


class VoteError(Exception):
	status_code = status.HTTP_400_BAD_REQUEST
	detail = "vote error"

	def __init__(self, detail: str | None = None):
		super().__init__(detail or self.detail)
		if detail is not None:
			self.detail = detail


class VotePollNotFoundError(VoteError):
	status_code = status.HTTP_404_NOT_FOUND
	detail = "Poll not found"


class VoteExpiredError(VoteError):
	status_code = status.HTTP_410_GONE
	detail = "poll expired"


class VoteClosedError(VoteError):
	status_code = status.HTTP_409_CONFLICT
	detail = "already closed poll"


class VoteAlreadyCastError(VoteError):
	status_code = status.HTTP_409_CONFLICT
	detail = "you can vote only once"


class VoteNoOptionError(VoteError):
	status_code = status.HTTP_400_BAD_REQUEST
	detail = "this poll has no option"


class VoteMultipleChoiceNotAllowedError(VoteError):
	status_code = status.HTTP_400_BAD_REQUEST
	detail = "this poll can't select multiple option"


class VoteOptionNotFoundError(VoteError):
	status_code = status.HTTP_400_BAD_REQUEST
	detail = "that option not exist in db"


