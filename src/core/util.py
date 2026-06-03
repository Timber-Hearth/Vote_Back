import os
from hashlib import sha256

def StrConvertToHashForRedis(str: str) -> str:
    return sha256(str.encode("UTF-8")).hexdigest()

def IsDebugMode() -> bool:
    return bool(int(os.environ.get("DEBUG_MODE", 0)))