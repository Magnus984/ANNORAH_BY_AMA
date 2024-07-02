from db_models import User, Owner
from werkzeug.security import generate_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


engine = create_engine("mysql+mysqldb://root:windowsql@localhost:3306/annorah_by_ama")
Session = sessionmaker(bind=engine)
session = Session()

email = "hildatetteh23@gmail.com"
user = User(
    username=email,
    email=email,
    password_hash=generate_password_hash("hilda_password")
)
session.add(user)
session.commit()
owner = Owner(
    first_name="Hilda",
    last_name="Tetteh",
    user_id=user.id
)
session.add(owner)
session.commit()