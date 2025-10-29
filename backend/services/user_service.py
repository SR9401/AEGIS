from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from extensions import bcrypt
from models.user import User, Role

class ValidUser:

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
        if not password:
            raise ValueError("password_required")
        if len(password) < 8:
            raise ValueError("weak_password")

    @staticmethod
    def _parse_role(value: Optional[str]) -> Optional[Role]:
        if value is None:
            return None
        try:
            # Role enum déclaré avec des NOMS en MAJ (ADMIN, ...) et des VALEURS en minuscule
            return Role[value.strip().upper()]
        except Exception:
            raise ValueError("invalid_role")

    # ---------- CREATE ----------
    @staticmethod
    def create_user(session: Session, data: dict) -> User:
        e = data.get("email")
        email = ValidUser._normalize_email(e)
        p = data.get("password")
        fn = (str(data.get("first_name")).strip() or None) if data.get("first_name") is not None else None
        ln = (str(data.get("last_name")).strip() or None) if data.get("last_name") is not None else None
        ValidUser._validate_new_user_input(fn, ln, email, p)

        existing = session.query(User).filter_by(email=email).first()
        if existing:
            raise ValueError("email_taken")

        password_hash = bcrypt.generate_password_hash(p).decode("utf-8")
        role_enum = ValidUser._parse_role(data.get("role"))

        user_kwargs = {"first_name": fn, "last_name": ln, "email": email, "password_hash": password_hash}
        if role_enum is not None:
            user_kwargs["role"] = role_enum
        user = User(**user_kwargs)
        session.add(user)
        try:
            session.flush()  # laisse le commit au middleware/teardown si tu en as un
        except IntegrityError:
            session.rollback()
            raise ValueError("email_taken")
        return user

    # ---------- LIST ----------
    @staticmethod
    def list_users(session: Session, role: Optional[str] = None, email_like: Optional[str] = None,
                   limit: int = 50, offset: int = 0) -> List[User]:
        q = session.query(User)
        if role is not None:
            role_enum = ValidUser._parse_role(role)
            q = q.filter(User.role == role_enum)
        if email_like:
            q = q.filter(User.email.ilike(f"%{email_like}%"))
        q = q.order_by(User.created_at.desc()).limit(limit).offset(offset)
        return q.all()

    # ---------- GET ----------
    @staticmethod
    def get_user(session: Session, user_id: str) -> User:
        u = session.get(User, user_id)
        if not u:
            raise ValueError("not_found")
        return u

    # ---------- UPDATE ----------
    @staticmethod
    def update_user(session: Session, user_id: str, data: dict) -> User:
        u = session.get(User, user_id)
        if not u:
            raise ValueError("not_found")

        # champs éditables
        if "first_name" in data:
            v = data.get("first_name")
            u.first_name = (str(v).strip() or u.first_name) if v is not None else u.first_name

        if "last_name" in data:
            v = data.get("last_name")
            u.last_name = (str(v).strip() or u.last_name) if v is not None else u.last_name

        if "role" in data:
            role_enum = ValidUser._parse_role(data.get("role"))
            u.role = role_enum

        if "password" in data:
            p = data.get("password")
            if not p:
                raise ValueError("password_required")
            if len(p) < 8:
                raise ValueError("weak_password")
            u.password_hash = bcrypt.generate_password_hash(p).decode("utf-8")

        if "email" in data and data.get("email"):
            new_email = ValidUser._normalize_email(data.get("email"))
            # email déjà pris par un autre ?
            exists = session.query(User).filter(User.email == new_email, User.id != u.id).first()
            if exists:
                raise ValueError("email_taken")
            u.email = new_email

        try:
            session.flush()
        except IntegrityError:
            session.rollback()
            raise ValueError("email_taken")
        return u

    # ---------- DELETE ----------
    @staticmethod
    def delete_user(session: Session, user_id: str) -> None:
        u = session.get(User, user_id)
        if not u:
            raise ValueError("not_found")
        session.delete(u)