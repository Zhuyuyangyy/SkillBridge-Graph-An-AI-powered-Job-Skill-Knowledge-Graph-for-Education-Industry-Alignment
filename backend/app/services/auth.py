import base64
import hashlib
import hmac
import json
import os
import re
import secrets
import time
from datetime import datetime, timedelta

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import User, UserSession

TOKEN_TTL_HOURS = 24
CAPTCHA_TTL_SECONDS = 300
CAPTCHA_SECRET = os.getenv("AUTH_SECRET", "shurong-zhilian-local-auth-secret")
USERNAME_PATTERN = re.compile(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d_]{6,20}$")
EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
SPECIAL_PATTERN = re.compile(r"[!@#$%^&*()_\-+=\[\]{};:'\",.<>/?\\|`~]")


def hash_password(password: str, salt: str | None = None) -> str:
    actual_salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), actual_salt.encode("utf-8"), 120_000)
    return f"pbkdf2_sha256${actual_salt}${base64.b64encode(digest).decode('ascii')}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        algorithm, salt, expected = password_hash.split("$", 2)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    candidate = hash_password(password, salt).split("$", 2)[2]
    return hmac.compare_digest(candidate, expected)


def validate_username(username: str) -> None:
    if not USERNAME_PATTERN.match(username):
        raise HTTPException(status_code=400, detail="用户名需为 6-20 位，且至少包含英文字母和数字，可使用下划线")


def validate_email(email: str) -> None:
    if not EMAIL_PATTERN.match(email.strip()):
        raise HTTPException(status_code=400, detail="请输入有效邮箱地址")


def validate_password(password: str) -> None:
    if len(password) < 8 or len(password) > 32:
        raise HTTPException(status_code=400, detail="密码长度需为 8-32 位")
    if not any(char.isdigit() for char in password):
        raise HTTPException(status_code=400, detail="密码至少需要包含数字")
    optional_categories = [
        any(char.isupper() for char in password),
        any(char.islower() for char in password),
        bool(SPECIAL_PATTERN.search(password)),
    ]
    if not any(optional_categories):
        raise HTTPException(status_code=400, detail="密码需在大写字母、小写字母、特殊符号中至少包含一种")


def _captcha_signature(payload: str) -> str:
    return hmac.new(CAPTCHA_SECRET.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).hexdigest()


def generate_math_captcha() -> dict:
    left = secrets.randbelow(9) + 1
    right = secrets.randbelow(9) + 1
    operator = ["+", "-", "×"][secrets.randbelow(3)]
    if operator == "-" and left < right:
        left, right = right, left
    answer = left + right if operator == "+" else left - right if operator == "-" else left * right
    data = {
        "left": left,
        "right": right,
        "operator": operator,
        "answer": answer,
        "expires_at": int(time.time()) + CAPTCHA_TTL_SECONDS,
        "nonce": secrets.token_urlsafe(8),
    }
    payload = base64.urlsafe_b64encode(json.dumps(data, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).decode("ascii").rstrip("=")
    return {
        "question": f"{left} {operator} {right} = ?",
        "token": f"{payload}.{_captcha_signature(payload)}",
        "expires_in": CAPTCHA_TTL_SECONDS,
    }


def verify_math_captcha(token: str, answer: str) -> None:
    try:
        payload, signature = token.split(".", 1)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="验证码无效，请刷新后重试") from exc
    if not hmac.compare_digest(_captcha_signature(payload), signature):
        raise HTTPException(status_code=400, detail="验证码无效，请刷新后重试")
    try:
        padded_payload = payload + "=" * (-len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(padded_payload.encode("ascii")).decode("utf-8"))
    except (ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=400, detail="验证码无效，请刷新后重试") from exc
    if int(data.get("expires_at", 0)) < int(time.time()):
        raise HTTPException(status_code=400, detail="验证码已过期，请刷新后重试")
    try:
        user_answer = int(str(answer).strip())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="请输入正确的验证码结果") from exc
    if user_answer != int(data.get("answer", -9999)):
        raise HTTPException(status_code=400, detail="验证码结果不正确")


def create_session(db: Session, user: User) -> str:
    token = secrets.token_urlsafe(36)
    db.add(
        UserSession(
            user_id=user.id,
            token=token,
            expires_at=datetime.utcnow() + timedelta(hours=TOKEN_TTL_HOURS),
        )
    )
    db.commit()
    return token


def current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="未登录或登录已失效")
    token = authorization.split(" ", 1)[1].strip()
    session = db.scalar(select(UserSession).where(UserSession.token == token))
    if not session or session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="登录已过期")
    user = db.get(User, session.user_id)
    if not user or user.status != "active":
        raise HTTPException(status_code=401, detail="账号不可用")
    return user


def require_roles(*roles: str):
    def dependency(user: User = Depends(current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="当前账号无权访问该功能")
        return user

    return dependency


def user_to_public(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "display_name": user.display_name,
        "email": user.email,
        "phone": user.phone,
        "organization": user.organization,
        "status": user.status,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }
