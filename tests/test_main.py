import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db
from database import Base

# Create a new SQLite database for testing purposes
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Apply the dependency override to the app
app.dependency_overrides[get_db] = override_get_db

# Create the test database schema
Base.metadata.create_all(bind=engine)

# Initialize the test client
client = TestClient(app)

def test_create_user():
    """
    Test the creation of a new user.
    """
    response = client.post("/users/", json={"name": "John Doe", "email": "john.doe@example.com"})
    assert response.status_code == 200  # Assert the status code is 200 OK
    assert response.json()["email"] == "john.doe@example.com"  # Assert the returned email is correct

def test_create_loan():
    """
    Test the creation of a new loan for a user.
    """
    response = client.post("/users/", json={"name": "Jane Doe", "email": "jane.doe@example.com"})
    assert response.status_code == 200
    user_id = response.json()["id"]

    response = client.post("/loans/", json={"amount": 10000, "annual_interest_rate": 5.0, "loan_term": 24, "owner_id": user_id})
    assert response.status_code == 200
    assert response.json()["amount"] == 10000  # Assert the loan amount is correct

def test_read_loan():
    """
    Test fetching a loan by its ID.
    """
    response = client.post("/users/", json={"name": "Jake Doe", "email": "jake.doe@example.com"})
    assert response.status_code == 200
    user_id = response.json()["id"]

    response = client.post("/loans/", json={"amount": 5000, "annual_interest_rate": 3.5, "loan_term": 12, "owner_id": user_id})
    assert response.status_code == 200
    loan_id = response.json()["id"]

    response = client.get(f"/loans/{loan_id}")
    assert response.status_code == 200
    assert response.json()["amount"] == 5000  # Assert the loan amount is correct

def test_read_loans_by_user():
    """
    Test fetching all loans for a specific user.
    """
    response = client.post("/users/", json={"name": "Jill Doe", "email": "jill.doe@example.com"})
    assert response.status_code == 200
    user_id = response.json()["id"]

    client.post("/loans/", json={"amount": 8000, "annual_interest_rate": 4.5, "loan_term": 36, "owner_id": user_id})
    client.post("/loans/", json={"amount": 12000, "annual_interest_rate": 6.0, "loan_term": 48, "owner_id": user_id})

    response = client.get(f"/users/{user_id}/loans")
    assert response.status_code == 200
    assert len(response.json()) == 2  # Assert the user has 2 loans

def test_get_loan_schedule():
    """
    Test fetching the amortization schedule for a loan.
    """
    response = client.post("/users/", json={"name": "Jack Doe", "email": "jack.doe@example.com"})
    assert response.status_code == 200
    user_id = response.json()["id"]

    response = client.post("/loans/", json={"amount": 15000, "annual_interest_rate": 4.0, "loan_term": 36, "owner_id": user_id})
    assert response.status_code == 200
    loan_id = response.json()["id"]

    response = client.get(f"/loans/{loan_id}/schedule")
    assert response.status_code == 200
    assert len(response.json()) == 36  # Assert the schedule length matches the loan term

def test_calculate_monthly_payments():
    """
    Test calculating the monthly payments for a user's loans.
    """
    response = client.post("/users/", json={"name": "Janet Doe", "email": "janet.doe@example.com"})
    assert response.status_code == 200
    user_id = response.json()["id"]

    client.post("/loans/", json={"amount": 20000, "annual_interest_rate": 3.5, "loan_term": 48, "owner_id": user_id})
    client.post("/loans/", json={"amount": 10000, "annual_interest_rate": 4.0, "loan_term": 36, "owner_id": user_id})

    response = client.get(f"/users/{user_id}/monthly_payments")
    assert response.status_code == 200
    monthly_payments = response.json()
    assert len(monthly_payments) > 0  # Assert that there are monthly payments calculated

def test_calculate_total_payments():
    """
    Test calculating the total payments for a user's loans.
    """
    response = client.post("/users/", json={"name": "James Doe", "email": "james.doe@example.com"})
    assert response.status_code == 200
    user_id = response.json()["id"]

    client.post("/loans/", json={"amount": 20000, "annual_interest_rate": 3.5, "loan_term": 48, "owner_id": user_id})

    response = client.get(f"/users/{user_id}/total_payments")
    assert response.status_code == 200
    assert "total_principal_paid" in response.json()  # Assert the response includes the total principal paid
    assert "total_interest_paid" in response.json()  # Assert the response includes the total interest paid
    assert "total_payments" in response.json()  # Assert the response includes the total payments

def test_get_loan_summary():
    """
    Test fetching a loan summary for a specific month.
    """
    response = client.post("/users/", json={"name": "Jim Doe", "email": "jim.doe@example.com"})
    assert response.status_code == 200
    user_id = response.json()["id"]

    response = client.post("/loans/", json={"amount": 25000, "annual_interest_rate": 5.0, "loan_term": 60, "owner_id": user_id})
    assert response.status_code == 200
    loan_id = response.json()["id"]

    response = client.get(f"/loans/{loan_id}/summary/12")
    assert response.status_code == 200
    summary = response.json()
    assert "current_balance" in summary  # Assert the response includes the current balance
    assert "principal_paid" in summary  # Assert the response includes the principal paid
    assert "interest_paid" in summary  # Assert the response includes the interest paid