from pydantic import BaseModel
from typing import List, Optional

class LoanBase(BaseModel):
    """
    Base schema for Loan.
    """
    amount: float
    annual_interest_rate: float
    loan_term: int

class LoanCreate(LoanBase):
    """
    Schema for creating a Loan.
    """
    owner_id: int

class Loan(LoanBase):
    """
    Schema for returning a Loan.
    """
    id: int
    owner_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    """
    Base schema for User.
    """
    name: str
    email: str

class UserCreate(UserBase):
    """
    Schema for creating a User.
    """
    pass

class User(UserBase):
    """
    Schema for returning a User with their loans.
    """
    id: int
    loans: List[Loan] = []

    class Config:
        orm_mode = True