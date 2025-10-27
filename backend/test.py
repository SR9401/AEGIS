
from db import SessionLocal
from models.user import User
from extensions import bcrypt

email = "test@example.com"
session = SessionLocal()

u = session.query(User).filter_by(email=email.strip().lower()).first()
if not u:
    print("USER_NOT_FOUND")
else:
    print("FOUND:", u.id, u.email, "is_active=", getattr(u, "is_active", None))
    ok = bcrypt.check_password_hash(u.password_hash, "MonPass123!")
    print("bcrypt.verify('MonPass123!') =>", ok)
    print("stored password_hash prefix:", (u.password_hash or "")[:6])
    print("stored password_hash len:", len(u.password_hash or ""))
session.close()

