from db import SessionLocal
from models.user import User

email = "test@example.com"
s = SessionLocal()
u = s.query(User).filter_by(email=email.strip().lower()).first()
if u:
    s.delete(u)
    s.commit()
    print("User deleted:", email)
else:
    print("User not found")
s.close()

