from src.models.poll_group import PollGroup

from src.models.vote import Vote

from src.schemas.responses.poll_group import Response_Option


def VoteProcess(db, vote_qr: str, normalized_annonymou_id: str, options: list[int]):
    try:
        if db == None:
            raise Exception("DB 세션이 유효하지 않습니다.")
        if db.query(Vote).filter(Vote.anonymous_id == normalized_annonymou_id).first():
            raise Exception("이미 투표한 사용자입니다.")
        if len(options) == 0:
            raise Exception("투표할 항목이 없습니다.")
        datas = db.query(PollGroup).filter(PollGroup.qr_token == vote_qr).first()
        if datas is None:
            raise Exception("투표할 항목이 존재하지 않습니다.")
        for option in options:
            vote = Vote(
                poll_group_qr=vote_qr,
                option_id=option,
                anonymous_id=normalized_annonymou_id
            )
            db.add(vote)
        db.commit()
    except Exception as e:
        db.rollback()
        print(e)
        raise e