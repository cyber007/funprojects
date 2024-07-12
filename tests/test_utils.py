import pytest
from utils import calculate_amortization_schedule


def test_calculate_amortization_schedule():
    """
    Test the calculation of the amortization schedule.
    """
    amount = 10000
    annual_interest_rate = 5.0
    loan_term = 24

    # Calculate the amortization schedule
    schedule = calculate_amortization_schedule(amount, annual_interest_rate, loan_term)

    assert len(schedule) == loan_term  # Assert the schedule length matches the loan term
    assert round(schedule[0]["monthly_payment"], 2) == 438.71  # Assert the first month's payment is correct
    assert round(schedule[-1]["remaining_balance"], 2) == 0.0  # Assert the remaining balance at the end is zero
    assert sum([p["principal_payment"] for p in schedule]) == pytest.approx(amount,
                                                                            rel=1e-2)  # Assert total principal paid equals the loan amount