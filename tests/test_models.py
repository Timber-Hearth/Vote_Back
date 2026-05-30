from src.models import PollOption, Polls, QrTokens, User, Vote


def test_model_tables_are_registered():
    assert User.__tablename__ == "users"
    assert Polls.__tablename__ == "polls"
    assert PollOption.__tablename__ == "poll_options"
    assert Vote.__tablename__ == "votes"
    assert QrTokens.__tablename__ == "qr_tokens"


def test_vote_has_option_id_column_for_selected_choice():
    # Vote needs option_id so each ballot can point to a concrete option.
    assert "option_id" in Vote.__table__.columns


def test_poll_option_has_unique_order_per_poll_constraint():
    constraint_names = {constraint.name for constraint in PollOption.__table__.constraints}
    assert "uq_poll_options_poll_order" in constraint_names


def test_vote_has_duplicate_vote_guard_constraint():
    constraint_names = {constraint.name for constraint in Vote.__table__.constraints}
    assert "uq_votes_poll_anon" in constraint_names


def test_user_has_login_and_password_hash_columns():
    assert "login_id" in User.__table__.columns
    assert "password_hash" in User.__table__.columns


def test_vote_anonymous_id_is_required():
    assert Vote.__table__.columns["anonymous_id"].nullable is False

