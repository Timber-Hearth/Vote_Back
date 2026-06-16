from fastapi import APIRouter, Header, HTTPException
import os
import subprocess

migration_router = APIRouter(tags=["migration"])

SECRET = "불타는군단"

@migration_router.post("/internal/migrate")
def migrate(x_secret: str = Header(None)):
    if x_secret != SECRET:
        raise HTTPException(status_code=403, detail="nope")

    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        capture_output=True,
        text=True
    )

    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "code": result.returncode
    }