from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    """
    User model representing a user in the system.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

    # Relationship to the Loan model
    loans = relationship("Loan", back_populates="owner")

class Loan(Base):
    """
    Loan model representing a loan in the system.
    """
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    annual_interest_rate = Column(Float)
    loan_term = Column(Integer)

    # Foreign key relationship to the User model
    owner_id = Column(Integer, ForeignKey("users.id"))

    # Relationship to the User model
    owner = relationship("User", back_populates="loans")