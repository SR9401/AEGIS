from db import SessionLocal, engine
from models.user import User
from extensions import bcrypt

print("Engine URL:", getattr(getattr(engine, 'url', None), 'render_as_string', lambda: str(engine.url))())
email = "test@example.com"

s = SessionLocal()
u = s.query(User).filter_by(email=email.strip().lower()).first()
if not u:
    print("USER_NOT_FOUND")
else:
    print("FOUND:", u.id, u.email)
    print("role raw type:", type(u.role), "repr:", repr(u.role))
    print("stored password_hash (prefix,len):", (u.password_hash or "")[:10], len(u.password_hash or ""))
    ok = bcrypt.check_password_hash(u.password_hash, "MonPass123!")
    print("bcrypt.check_password_hash('MonPass123!') ->", ok)
s.close()

