import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.database import Base, get_db
from src.main import app
from src.models import PollOption, Polls, QrTokens, User, Vote


@pytest.fixture()
def db_session(tmp_path):
	db_file = tmp_path / "vote_test.db"
	engine = create_engine(
		f"sqlite+pysqlite:///{db_file}",
		connect_args={"check_same_thread": False},
	)
	TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
	Base.metadata.create_all(bind=engine)

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


def create_poll(db_session, *, allow_multiple_choice=False, is_closed=False, token="poll-token"):
	user = User(id=1, login_id="tester", password_hash="hash")
	db_session.add(user)
	db_session.flush()

	poll = Polls(
		owner_id=user.id,
		title="test poll",
		description="desc",
		is_public_result=False,
		is_closed=is_closed,
		allow_multiple_choice=allow_multiple_choice,
		delete_after_hours=24,
	)
	db_session.add(poll)
	db_session.flush()

	option_one = PollOption(id=1, poll_id=poll.id, option_text="A", display_order=1)
	option_two = PollOption(id=2, poll_id=poll.id, option_text="B", display_order=2)
	db_session.add_all([option_one, option_two])
	db_session.add(QrTokens(poll_id=poll.id, tokens=token))
	db_session.commit()

	return poll, token, [option_one.id, option_two.id]


def test_vote_route_persists_multiple_votes_for_multiple_choice_poll(client, db_session):
	poll, token, option_ids = create_poll(db_session, allow_multiple_choice=True)

	response = client.post(f"/vote/{token}", json={"option_ids": option_ids})

	assert response.status_code == 200
	assert response.json() == {"success": "vote done"}

	cookie_value = response.cookies.get("anonymous_id")
	assert cookie_value is not None
	uuid.UUID(cookie_value)

	votes = db_session.query(Vote).filter(Vote.poll_id == poll.id).all()
	assert len(votes) == 2
	assert {vote.option_id for vote in votes} == set(option_ids)


def test_vote_route_rejects_duplicate_vote_for_same_option(client, db_session):
	_, token, option_ids = create_poll(db_session)

	first_response = client.post(f"/vote/{token}", json={"option_ids": [option_ids[0]]})
	assert first_response.status_code == 200

	second_response = client.post(f"/vote/{token}", json={"option_ids": [option_ids[0]]})

	assert second_response.status_code == 409
	assert second_response.json()["detail"] == "you can vote only once"


def test_vote_route_rejects_invalid_option_id(client, db_session):
	_, token, _ = create_poll(db_session)

	response = client.post(f"/vote/{token}", json={"option_ids": [999999]})

	assert response.status_code == 400
	assert response.json()["detail"] == "that option not exist in db"


def test_vote_route_replaces_invalid_anonymous_cookie_and_still_votes(client, db_session):
	_, token, option_ids = create_poll(db_session)
	client.cookies.set("anonymous_id", "not-a-uuid")

	response = client.post(f"/vote/{token}", json={"option_ids": [option_ids[0]]})

	assert response.status_code == 200
	cookie_value = response.cookies.get("anonymous_id")
	assert cookie_value is not None
	uuid.UUID(cookie_value)



