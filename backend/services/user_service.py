import uuid
from datetime import datetime
from typing import Dict
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from extensions import bcrypt
from models.user import User, Role


class ValidUser():

    @staticmethod
    def _normalize_email(email: str) -> str:
        
        if email is None:
            raise ValueError("email_required")
        e = email.strip()
        if not e:
            raise ValueError("email_required")
        if "@" not in e or "." not in e.split("@", 1)[1]:
            raise ValueError("invalid_email")
        return e.lower()

    @staticmethod
    def _validate_new_user_input(first_name: str, last_name: str, email: str, password: str) -> None:
        if not first_name or not last_name:
            raise ValueError("first_name and last_name are required.")
        if not email or "@" not in email:
            raise ValueError("invalid_email")
        if not password or len(password) < 8:
            raise ValueError("Password must be at least 8 characters long.")
    @staticmethod   
    def create_user(session, data):
        e = data.get("email")
        email = ValidUser._normalize_email(e)
        p = data.get("password")
        fn = data.get("first_name")
        if fn is not None:
            fn = str(fn).strip() or None
        ln = data.get("last_name")
        if ln is not None:
            ln = str(ln).strip() or None
        ValidUser._validate_new_user_input(fn, ln, email, p)

        existing = session.query(User).filter_by(email=email).first()
        if existing:
            raise ValueError("email_taken")
        password_hash = bcrypt.generate_password_hash(p).decode("utf-8")
        
        r = data.get("role")
        role_enum = None
        if r:
            try:
                role_enum = Role[r.strip().upper()]
            except Exception:
                raise ValueError("invalid_role")

        user_kwargs = {"first_name": fn, "last_name": ln, "email": email, "password_hash": password_hash}
        if role_enum is not None:
            user_kwargs["role"] = role_enum
        user = User(**user_kwargs)
        session.add(user)
        try:
            session.flush()
        except IntegrityError:
            session.rollback()
            raise ValueError("email_taken")
        return user