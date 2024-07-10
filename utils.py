import numpy_financial as npf

def calculate_amortization_schedule(amount, annual_interest_rate, loan_term):
    monthly_interest_rate = annual_interest_rate / 12 / 100
    number_of_payments = loan_term

    monthly_payment = npf.pmt(monthly_interest_rate, number_of_payments, -amount)
    schedule = []

    remaining_balance = amount
    for month in range(1, loan_term + 1):
        interest_payment = remaining_balance * monthly_interest_rate
        principal_payment = monthly_payment - interest_payment
        remaining_balance -= principal_payment

        schedule.append({
            "month": month,
            "remaining_balance": round(remaining_balance, 2),
            "monthly_payment": round(monthly_payment, 2),
            "principal_payment": round(principal_payment, 2),
            "interest_payment": round(interest_payment, 2)
        })

    return schedule