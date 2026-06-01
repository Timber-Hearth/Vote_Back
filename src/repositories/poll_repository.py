from collections.abc import Sequence

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models import PollOption, Polls, QrTokens


def CreatePollWithOptionsAndToken(
	db: Session,
	*,
	owner_id: int,
	title: str,
	description: str | None,
	options: Sequence[str],
	allow_multiple_choice: bool,
	is_public_result: bool,
	expire_at,
	delete_after_hours: int,
	token: str,
):
	poll = Polls(
		owner_id=owner_id,
		title=title,
		description=description,  # type: ignore[arg-type]
		is_closed=False,
		is_public_result=is_public_result,
		expire_at=expire_at,
		allow_multiple_choice=allow_multiple_choice,
		delete_after_hours=delete_after_hours,
	)
	db.add(poll)
	db.flush()

	current_max_option_id = db.query(func.coalesce(func.max(PollOption.id), 0)).scalar() or 0
	option_instances = [
		PollOption(
			id=current_max_option_id + index,
			poll_id=poll.id,
			option_text=option_text,
			display_order=index,
		)
		for index, option_text in enumerate(options, start=1)
	]
	db.add_all(option_instances)

	qr_token = QrTokens(
		poll_id=poll.id,
		tokens=token,
	)
	db.add(qr_token)

	try:
		db.commit()
	except Exception:
		db.rollback()
		raise

	db.refresh(poll)
	return poll, token


def GetPollByToken(db: Session, token: str):
	qr_token = db.query(QrTokens).filter(QrTokens.tokens == token).first()
	if not qr_token:
		return None

	return db.query(Polls).filter(Polls.id == qr_token.poll_id).first()


def GetOptionsByPollID(db: Session, poll_id):
	return db.query(PollOption).filter(PollOption.poll_id == poll_id).all()



