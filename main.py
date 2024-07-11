from typing import List
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, crud
from database import engine, SessionLocal, get_db
import utils

# Create the database tables based on the models
models.Base.metadata.create_all(bind=engine)

# Initialize the FastAPI app
app = FastAPI()

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user with the given details.

    Args:
    - user: UserCreate schema with user details.
    - db: Database session.

    Returns:
    - The created user.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.post("/loans/", response_model=schemas.Loan)
def create_loan(loan: schemas.LoanCreate, db: Session = Depends(get_db)):
    """
    Create a new loan with the given details.

    Args:
    - loan: LoanCreate schema with loan details.
    - db: Database session.

    Returns:
    - The created loan.
    """
    return crud.create_user_loan(db=db, loan=loan)

@app.get("/loans/{loan_id}", response_model=schemas.Loan)
def read_loan(loan_id: int, db: Session = Depends(get_db)):
    """
    Fetch a loan by its ID.

    Args:
    - loan_id: The ID of the loan.
    - db: Database session.

    Returns:
    - The loan with the specified ID.
    """
    db_loan = crud.get_loan(db, loan_id=loan_id)
    if db_loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    return db_loan

@app.get("/users/{user_id}/loans", response_model=List[schemas.Loan])
def read_loans_by_user(user_id: int, db: Session = Depends(get_db)):
    """
    Fetch all loans for a specific user.

    Args:
    - user_id: The ID of the user.
    - db: Database session.

    Returns:
    - A list of loans for the specified user.
    """
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return crud.get_loans_by_user(db, user_id=user_id)

@app.get("/loans/{loan_id}/schedule")
def get_loan_schedule(loan_id: int, db: Session = Depends(get_db)):
    """
    Fetch the amortization schedule for a specific loan.

    Args:
    - loan_id: The ID of the loan.
    - db: Database session.

    Returns:
    - The amortization schedule for the specified loan.
    """
    db_loan = crud.get_loan(db, loan_id=loan_id)
    if db_loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    schedule = utils.calculate_amortization_schedule(
        db_loan.amount, db_loan.annual_interest_rate, db_loan.loan_term
    )
    return schedule

@app.get("/users/{user_id}/monthly_payments")
def calculate_monthly_payments(user_id: int, db: Session = Depends(get_db)):
    """
    Fetch the monthly payment breakdown for all loans of a specific user.

    Args:
    - user_id: The ID of the user.
    - db: Database session.

    Returns:
    - A list of dictionaries with the monthly payment breakdown.
    """
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    loans = crud.get_loans_by_user(db, user_id=user_id)
    monthly_payments = {}

    # Aggregate payments for each month across all loans
    for loan in loans:
        schedule = utils.calculate_amortization_schedule(
            loan.amount, loan.annual_interest_rate, loan.loan_term
        )
        for payment in schedule:
            month = payment["month"]
            if month not in monthly_payments:
                monthly_payments[month] = {
                    "total_principal_payment": 0.0,
                    "total_interest_payment": 0.0,
                    "total_monthly_payment": 0.0,
                }
            monthly_payments[month]["total_principal_payment"] += payment["principal_payment"]
            monthly_payments[month]["total_interest_payment"] += payment["interest_payment"]
            monthly_payments[month]["total_monthly_payment"] += payment["monthly_payment"]

    # Convert the dictionary to a list of monthly payments
    monthly_payments_list = [
        {
            "month": month,
            "total_principal_payment": round(data["total_principal_payment"], 2),
            "total_interest_payment": round(data["total_interest_payment"], 2),
            "total_monthly_payment": round(data["total_monthly_payment"], 2),
        }
        for month, data in monthly_payments.items()
    ]

    return monthly_payments_list

@app.get("/users/{user_id}/total_payments")
def calculate_total_payments(user_id: int, db: Session = Depends(get_db)):
    """
    Fetch the total payments breakdown for all loans of a specific user.

    Args:
    - user_id: The ID of the user.
    - db: Database session.

    Returns:
    - A dictionary with the total payments breakdown.
    """
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    loans = crud.get_loans_by_user(db, user_id=user_id)
    total_principal_paid = 0.0
    total_interest_paid = 0.0
    total_payments = 0.0

    # Aggregate total payments across all loans
    for loan in loans:
        schedule = utils.calculate_amortization_schedule(
            loan.amount, loan.annual_interest_rate, loan.loan_term
        )
        for payment in schedule:
            total_principal_paid += payment["principal_payment"]
            total_interest_paid += payment["interest_payment"]
            total_payments += payment["monthly_payment"]

    return {
        "total_principal_paid": round(total_principal_paid, 2),
        "total_interest_paid": round(total_interest_paid, 2),
        "total_payments": round(total_payments, 2)
    }

@app.get("/loans/{loan_id}/summary/{month}")
def get_loan_summary(loan_id: int, month: int, db: Session = Depends(get_db)):
    """
    Fetch a summary of a loan for a specific month.

    Args:
    - loan_id: The ID of the loan.
    - month: The month for which to fetch the summary.
    - db: Database session.

    Returns:
    - A summary of the loan for the specified month.
    """
    db_loan = crud.get_loan(db, loan_id=loan_id)
    if db_loan is None:
        raise HTTPException(status_code=404, detail="Loan not found")
    schedule = utils.calculate_amortization_schedule(
        db_loan.amount, db_loan.annual_interest_rate, db_loan.loan_term
    )
    if month < 1 or month > len(schedule):
        raise HTTPException(status_code=400, detail="Invalid month number")

    principal_paid = sum([x['principal_payment'] for x in schedule[:month]])
    interest_paid = sum([x['interest_payment'] for x in schedule[:month]])
    current_balance = schedule[month - 1]['remaining_balance']

    return {
        "current_balance": current_balance,
        "principal_paid": principal_paid,
        "interest_paid": interest_paid
    }