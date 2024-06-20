from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Float, Table, create_engine
from sqlalchemy.orm import relationship

engine =create_engine("mysql+mysqldb://root:windowsql@localhost:3306/annorah_by_ama")
Base = declarative_base()


class User(Base):
    """Represents a User table in the database"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(120), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default='user')
    owner = relationship("Owner", back_populates="user", uselist=False)
    buyer = relationship("Buyer", back_populates="user", uselist=False)

    def __repr__(self):
        return f"<User {self.username}>"


class Owner(Base):
    """Represents an Owner table in the database"""
    __tablename__ = 'owner'
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String(45), nullable=False)
    last_name = Column(String(45), nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="owner")
    dresses = relationship("Dress", back_populates="owner")

    def __repr__(self):
        return f"<Owner {self.id}>"

    
order_table = Table(
    "order",
    Base.metadata,
    Column("buyer_id", ForeignKey("buyers.id")),
    Column("dresses_id", ForeignKey("dresses.id")),
)


class Buyer(Base):
    """Represents a Buyer table in the database"""
    __tablename__ = 'buyers'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(45), nullable=False)
    last_name = Column(String(45), nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="buyer")
    dresses = relationship(
        "Dress", secondary=order_table,
        back_populates="buyers"
        )

    def __repr__(self):
        return f"<Buyer {self.id}>"


class Dress(Base):
    """Represents a Dress table in the database"""
    __tablename__ = 'dresses'

    id = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False)
    description = Column(String(100), nullable=True)
    price = Column(Float(precision=2), nullable=False)

    owner_id = Column(Integer, ForeignKey("owner.id"))
    owner = relationship("Owner", back_populates="dresses")
    buyers = relationship(
        "Buyer", secondary=order_table,
        back_populates="dresses"
        )

    def __repr__(self):
        return f"<Dress {self.id}>"


Base.metadata.create_all(engine)