from pydantic import BaseModel
from typing import List, Optional

class UserBase(BaseModel):
    name: str
    email: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    loans: List["Loan"] = []

    class Config:
        orm_mode = True

class LoanBase(BaseModel):
    amount: float
    annual_interest_rate: float
    loan_term: int

class LoanCreate(LoanBase):
    owner_id: int

class Loan(LoanBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True