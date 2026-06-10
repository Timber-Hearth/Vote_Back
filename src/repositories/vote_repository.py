from collections.abc import Sequence

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models import PollOption, Vote
from src.repositories.id_allocator import AllocateNextBigIntIds


def GetOptionsByPollID(db: Session, poll_id):
	return db.query(PollOption).filter(PollOption.poll_id == poll_id).all()


def HasAnonymousVoteForOptionIDs(
	db: Session,
	poll_id,
	anonymous_id,
	option_ids: Sequence[int],
) -> bool:
	if not option_ids:
		return False

	return (
		db.query(Vote)
		.filter(Vote.poll_id == poll_id)
		.filter(Vote.anonymous_id == anonymous_id)
		.filter(Vote.option_id.in_(option_ids))
		.first()
		is not None
	)

# TODO : 이거 수정할거 있는지 확인해
def CreateVotes(
	db: Session,
	poll_id,
	anonymous_id,
	option_ids: Sequence[int],
) -> None:
	vote_ids = AllocateNextBigIntIds(db, Vote, count=len(option_ids))
	vote_instances = []
	for vote_id, option_id in zip(vote_ids, option_ids):
		vote_payload = {
			"id": vote_id,
			"poll_id": poll_id,
			"option_id": option_id,
			"anonymous_id": anonymous_id,
		}
		vote_instances.append(Vote(**vote_payload))

	db.add_all(vote_instances)
	try:
		db.commit()
	except Exception:
		db.rollback()
		raise

def CalculateVoteCount(db: Session, poll_id):
	rows = (
		db.query(Vote.option_id, func.count(Vote.id))
		.filter(Vote.poll_id == poll_id)
		.group_by(Vote.option_id)
		.all()
	)
	return {option_id: count for option_id, count in rows}



