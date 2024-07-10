from sqlalchemy.orm import Session
import models, schemas

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_loans(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Loan).offset(skip).limit(limit).all()

def create_user_loan(db: Session, loan: schemas.LoanCreate):
    db_loan = models.Loan(**loan.dict())
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan

def get_loan(db: Session, loan_id: int):
    return db.query(models.Loan).filter(models.Loan.id == loan_id).first()

def get_loans_by_user(db: Session, user_id: int):
    return db.query(models.Loan).filter(models.Loan.owner_id == user_id).all()

def get_loans_by_user(db: Session, user_id: int):
    return db.query(models.Loan).filter(models.Loan.owner_id == user_id).all()