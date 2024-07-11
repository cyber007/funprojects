from sqlalchemy.orm import Session
import models, schemas

# Fetch a user by their ID
def get_user(db: Session, user_id: int):
    """
    Fetch a user by their ID.

    Args:
    - db: Database session.
    - user_id: The ID of the user.

    Returns:
    - The user with the specified ID, or None if not found.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()

# Fetch a user by their email
def get_user_by_email(db: Session, email: str):
    """
    Fetch a user by their email.

    Args:
    - db: Database session.
    - email: The email of the user.

    Returns:
    - The user with the specified email, or None if not found.
    """
    return db.query(models.User).filter(models.User.email == email).first()

# Fetch a list of users with pagination support
def get_users(db: Session, skip: int = 0, limit: int = 10):
    """
    Fetch a list of users with pagination support.

    Args:
    - db: Database session.
    - skip: Number of records to skip.
    - limit: Maximum number of records to return.

    Returns:
    - A list of users.
    """
    return db.query(models.User).offset(skip).limit(limit).all()

# Create a new user in the database
def create_user(db: Session, user: schemas.UserCreate):
    """
    Create a new user in the database.

    Args:
    - db: Database session.
    - user: UserCreate schema with user details.

    Returns:
    - The created user.
    """
    db_user = models.User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Fetch a list of loans with pagination support
def get_loans(db: Session, skip: int = 0, limit: int = 10):
    """
    Fetch a list of loans with pagination support.

    Args:
    - db: Database session.
    - skip: Number of records to skip.
    - limit: Maximum number of records to return.

    Returns:
    - A list of loans.
    """
    return db.query(models.Loan).offset(skip).limit(limit).all()

# Create a new loan for a user
def create_user_loan(db: Session, loan: schemas.LoanCreate):
    """
    Create a new loan for a user.

    Args:
    - db: Database session.
    - loan: LoanCreate schema with loan details.

    Returns:
    - The created loan.
    """
    db_loan = models.Loan(**loan.dict())
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan

# Fetch a loan by its ID
def get_loan(db: Session, loan_id: int):
    """
    Fetch a loan by its ID.

    Args:
    - db: Database session.
    - loan_id: The ID of the loan.

    Returns:
    - The loan with the specified ID, or None if not found.
    """
    return db.query(models.Loan).filter(models.Loan.id == loan_id).first()

# Fetch all loans for a specific user
def get_loans_by_user(db: Session, user_id: int):
    """
    Fetch all loans for a specific user.

    Args:
    - db: Database session.
    - user_id: The ID of the user.

    Returns:
    - A list of loans for the specified user.
    """
    return db.query(models.Loan).filter(models.Loan.owner_id == user_id).all()