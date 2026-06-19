from fastapi import APIRouter, Depends
from google.cloud import storage

qr_router = APIRouter(tags=["qr"])


@qr_router.get(
    path="/{token}",
    summary="QR 코드 존재 여부 확인/ 있으면 가져옴",
    description="QR 코드 존재 여부 확인",
    response_description="QR 코드 존재 여부 확인 결과",
    responses={
        200: {"description": "QR 코드가 존재합니다."},
        404: {"description": "QR 코드를 찾을 수 없습니다."},
        500: {"description": "서버 에러"},
    }
)
def Get_Qr(token: str):
    try:
        client = storage.Client()
        bucket = client.bucket("qr_imgs")
        blob = bucket.blob(f"qr/{token}.png")
        if not blob.exists():
            return {"message": "QR 코드를 찾을 수 없습니다."}

        return {
            "message": "QR 코드가 존재합니다.",
            "qr_url": blob.public_url
        }
    except Exception as e:
        return {"message": "서버 에러", "error": str(e)}