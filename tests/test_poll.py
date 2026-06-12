from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from src.core.database import Base, get_db
from src.core.security import GetCurrentUserFromJwt
from src.main import app
from src.models import PollOption, Polls, QrTokens, User, Vote
from src.schemas.requests.poll import CreatePollRequest
from src.services.poll_service import ServiceCreatePoll


class FakeSession:
	def __init__(self):
		self.added: list[object] = []
		self.did_commit = False

	def add(self, obj: object) -> None:
		self.added.append(obj)

	def flush(self) -> None:
		for obj in self.added:
			if isinstance(obj, Polls) and obj.id is None:
				obj.id = uuid4()

	def commit(self) -> None:
		self.did_commit = True

	def refresh(self, _: object) -> None:
		return


@pytest.fixture()
def db_session(tmp_path):
	db_file = tmp_path / "poll_test.db"
	db_engine = create_engine(
		f"sqlite+pysqlite:///{db_file}",
		connect_args={"check_same_thread": False},
	)

	@event.listens_for(db_engine, "connect")
	def SetSqliteForeignKeys(dbapi_connection, _connection_record):
		cursor = dbapi_connection.cursor()
		cursor.execute("PRAGMA foreign_keys=ON")
		cursor.close()

	TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
	Base.metadata.create_all(bind=db_engine)

	db = TestingSessionLocal()
	try:
		yield db
	finally:
		db.close()


@pytest.fixture()
def client(db_session):
	def override_get_db():
		try:
			yield db_session
		finally:
			pass

	app.dependency_overrides[get_db] = override_get_db
	with TestClient(app) as test_client:
		yield test_client
	app.dependency_overrides.clear()


def CreatePollWithRelations(db_session, *, owner_id=1, token="poll-token"):
	owner_user = User(id=owner_id, login_id=f"tester-{owner_id}", password_hash="hash")
	db_session.add(owner_user)
	db_session.flush()

	poll = Polls(
		owner_id=owner_user.id,
		title="test poll",
		description="desc",
		is_public_result=False,
		is_closed=False,
		allow_multiple_choice=False,
		delete_after_hours=24,
	)
	db_session.add(poll)
	db_session.flush()

	option = PollOption(id=1, poll_id=poll.id, option_text="A", display_order=1)
	db_session.add(option)
	db_session.flush()

	qr_token = QrTokens(poll_id=poll.id, tokens=token)
	vote = Vote(id=1, poll_id=poll.id, option_id=option.id, anonymous_id=uuid4())
	db_session.add_all([qr_token, vote])
	db_session.commit()

	return owner_user, poll, token


def test_create_poll_request_requires_at_least_two_options():
	with pytest.raises(ValidationError):
		CreatePollRequest(title="Lunch", options=["single"])


def test_create_poll_request_rejects_empty_options():
	with pytest.raises(ValidationError):
		CreatePollRequest(title="Lunch", options=["", "   "])


def test_service_create_poll_saves_poll_and_options():
	db_session: Any = FakeSession()
	start_time = datetime.now(UTC)
	request = CreatePollRequest(
		title="Lunch",
		description="pick one",
		options=["soup", "pork", "cutlet"],
		delete_after_hours=5,
		allow_multiple_choice=False,
		is_public_result=True,
	)

	result = ServiceCreatePoll(db=db_session, owner_id=1, request=request)

	# ServiceCreatePoll은 이제 dict를 반환
	assert isinstance(result, dict)
	assert "poll_id" in result
	assert "token" in result
	poll_id_str = result["poll_id"]
	
	# db_session.added에서 Polls 객체 찾기
	polls_objs = [obj for obj in db_session.added if isinstance(obj, Polls)]
	assert len(polls_objs) == 1
	poll = polls_objs[0]
	
	assert poll.id is not None
	assert str(poll.id) == poll_id_str
	assert poll.title == "Lunch"
	assert poll.expire_at is not None
	assert db_session.did_commit is True

	expire_at = poll.expire_at
	if expire_at.tzinfo is None:
		expire_at = expire_at.replace(tzinfo=UTC)
	delta_seconds = (expire_at - start_time).total_seconds()
	assert 4.9 * 3600 <= delta_seconds <= 5.1 * 3600

	poll_options = [obj for obj in db_session.added if isinstance(obj, PollOption)]
	assert len(poll_options) == 3
	assert [option.option_text for option in poll_options] == ["soup", "pork", "cutlet"]
	assert [option.display_order for option in poll_options] == [1, 2, 3]
	assert all(option.poll_id == poll.id for option in poll_options)
	
	# QR 토큰도 생성되었는지 확인
	qr_tokens = [obj for obj in db_session.added if isinstance(obj, QrTokens)]
	assert len(qr_tokens) == 1
	assert qr_tokens[0].tokens == result["token"]


def test_service_create_poll_stores_no_options_on_poll_row():
	db_session: Any = FakeSession()
	request = CreatePollRequest(title="Snack", options=["A", "B"])
	result = ServiceCreatePoll(db=db_session, owner_id=2, request=request)

	# ServiceCreatePoll은 이제 dict를 반환
	assert isinstance(result, dict)
	
	# db_session.added에서 Polls 객체 찾기
	polls_objs = [obj for obj in db_session.added if isinstance(obj, Polls)]
	assert len(polls_objs) == 1
	poll = polls_objs[0]
	
	assert isinstance(poll, Polls)
	assert not hasattr(poll, "options")


def test_remove_poll_requires_authentication(client, db_session):
	_, _, token = CreatePollWithRelations(db_session)

	response = client.delete(f"/polls/{token}/remove")

	assert response.status_code == 401


def test_remove_poll_rejects_non_owner(client, db_session):
	_, _, token = CreatePollWithRelations(db_session, owner_id=1)
	not_owner_user = User(id=2, login_id="tester-2", password_hash="hash")
	db_session.add(not_owner_user)
	db_session.commit()

	app.dependency_overrides[GetCurrentUserFromJwt] = lambda: not_owner_user
	response = client.delete(f"/polls/{token}/remove")

	assert response.status_code == 403
	assert response.json()["detail"] == "You don't have permission to remove this poll"


def test_remove_poll_deletes_related_rows(client, db_session):
	owner_user, poll, token = CreatePollWithRelations(db_session)
	app.dependency_overrides[GetCurrentUserFromJwt] = lambda: owner_user

	response = client.delete(f"/polls/{token}/remove")

	assert response.status_code == 200
	assert response.json() == {"message": "success"}
	assert db_session.query(Polls).filter(Polls.id == poll.id).first() is None
	assert db_session.query(PollOption).filter(PollOption.poll_id == poll.id).count() == 0
	assert db_session.query(QrTokens).filter(QrTokens.poll_id == poll.id).count() == 0
	assert db_session.query(Vote).filter(Vote.poll_id == poll.id).count() == 0


def test_remove_poll_get_method_is_not_allowed(client, db_session):
	owner_user, _, token = CreatePollWithRelations(db_session)
	app.dependency_overrides[GetCurrentUserFromJwt] = lambda: owner_user

	response = client.get(f"/polls/{token}/remove")

	assert response.status_code == 405


def test_close_poll_requires_authentication(client, db_session):
	_, _, token = CreatePollWithRelations(db_session)

	response = client.post(f"/polls/{token}/close")

	assert response.status_code == 401


def test_close_poll_rejects_non_owner(client, db_session):
	_, poll, token = CreatePollWithRelations(db_session, owner_id=1)
	not_owner_user = User(id=2, login_id="close-tester-2", password_hash="hash")
	db_session.add(not_owner_user)
	db_session.commit()

	app.dependency_overrides[GetCurrentUserFromJwt] = lambda: not_owner_user
	response = client.post(f"/polls/{token}/close")

	assert response.status_code == 403
	assert response.json()["detail"] == "You don't have permission to close this poll"
	assert db_session.query(Polls).filter(Polls.id == poll.id).first().is_closed is False


def test_close_poll_marks_poll_closed_for_owner(client, db_session):
	owner_user, poll, token = CreatePollWithRelations(db_session)
	app.dependency_overrides[GetCurrentUserFromJwt] = lambda: owner_user

	response = client.post(f"/polls/{token}/close")

	assert response.status_code == 200
	assert response.json() == {"message": "success"}
	assert db_session.query(Polls).filter(Polls.id == poll.id).first().is_closed is True


