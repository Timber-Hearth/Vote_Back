from fastapi import APIRouter, Header, HTTPException
import os
import subprocess

migration_router = APIRouter(tags=["migration"])

@migration_router.post("/internal/migrate")
def migrate():
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