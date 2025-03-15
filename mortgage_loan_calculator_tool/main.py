# Engine tool registry
import sys
import os
import logging
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.append(project_root)
from engine.tool_framework import run_tool, BaseTool

# Other imports goes here
import math

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

# Tool implementation
@run_tool
class MortgageLoanCalculatorTool(BaseTool):
    """
    A tool to calculate mortgage loans.

    Args:
        loan_details (dict): A dictionary containing loan details with the following keys:
            - principal (float): The loan amount in dollars
            - annual_interest_rate (float): Annual interest rate as a percentage (e.g., 5.5 for 5.5%)
            - loan_term_years (int): The loan term in years
            - down_payment (float, optional): Down payment amount in dollars
            - property_tax (float, optional): Annual property tax in dollars
            - insurance (float, optional): Annual insurance premium in dollars
            - pmi (float, optional): Private mortgage insurance as a percentage

    Returns:
        dict: A dictionary containing mortgage calculation results including:
            - monthly_payment: Principal and interest payment
            - total_payment: Total amount paid over the loan term
            - total_interest: Total interest paid over the loan term
            - monthly_breakdown: Detailed monthly payment including taxes and insurance if provided
            - amortization_schedule: Year-by-year breakdown of payments (if requested)
    """

    def calculate_mortgage_loan(self, loan_details: dict):
        try:
            # Extract required parameters
            principal = float(loan_details.get('principal', 0))
            annual_interest_rate = float(loan_details.get('annual_interest_rate', 0))
            loan_term_years = int(loan_details.get('loan_term_years', 30))
            
            # Extract optional parameters
            down_payment = float(loan_details.get('down_payment', 0))
            property_tax = float(loan_details.get('property_tax', 0))
            insurance = float(loan_details.get('insurance', 0))
            pmi_rate = float(loan_details.get('pmi', 0))
            
            # Validate inputs
            if principal <= 0:
                return "Error: Loan principal must be greater than zero"
            if annual_interest_rate < 0:
                return "Error: Interest rate cannot be negative"
            if loan_term_years <= 0:
                return "Error: Loan term must be greater than zero"
            
            # Adjust principal by down payment
            loan_amount = principal - down_payment
            if loan_amount <= 0:
                return "Error: Loan amount after down payment must be greater than zero"
            
            # Calculate monthly interest rate
            monthly_interest_rate = annual_interest_rate / 100 / 12
            
            # Calculate number of payments
            num_payments = loan_term_years * 12
            
            # Calculate PMI if applicable (typically required if down payment < 20%)
            pmi_monthly = 0
            if down_payment < (0.2 * principal) and pmi_rate > 0:
                pmi_monthly = (loan_amount * pmi_rate / 100) / 12
            
            # Calculate monthly payment (principal and interest)
            if monthly_interest_rate > 0:
                monthly_payment = loan_amount * (monthly_interest_rate * math.pow(1 + monthly_interest_rate, num_payments)) / (math.pow(1 + monthly_interest_rate, num_payments) - 1)
            else:
                # If interest rate is 0, simple division
                monthly_payment = loan_amount / num_payments
            
            # Calculate monthly property tax and insurance
            monthly_property_tax = property_tax / 12 if property_tax > 0 else 0
            monthly_insurance = insurance / 12 if insurance > 0 else 0
            
            # Calculate total monthly payment including taxes, insurance, and PMI
            total_monthly_payment = monthly_payment + monthly_property_tax + monthly_insurance + pmi_monthly
            
            # Calculate total payment over the life of the loan
            total_principal_interest = monthly_payment * num_payments
            total_payment = total_principal_interest + (monthly_property_tax + monthly_insurance + pmi_monthly) * num_payments
            
            # Calculate total interest
            total_interest = total_principal_interest - loan_amount
            
            # Create amortization schedule (yearly summary)
            amortization_schedule = []
            remaining_balance = loan_amount
            
            for year in range(1, loan_term_years + 1):
                year_interest = 0
                year_principal = 0
                
                for month in range(1, 13):
                    if remaining_balance <= 0:
                        break
                        
                    # Calculate interest for this month
                    month_interest = remaining_balance * monthly_interest_rate
                    
                    # Calculate principal for this month
                    month_principal = monthly_payment - month_interest
                    
                    # Update running totals
                    year_interest += month_interest
                    year_principal += month_principal
                    
                    # Update remaining balance
                    remaining_balance -= month_principal
                    if remaining_balance < 0:
                        remaining_balance = 0
                
                amortization_schedule.append({
                    'year': year,
                    'principal_paid': round(year_principal, 2),
                    'interest_paid': round(year_interest, 2),
                    'remaining_balance': round(remaining_balance, 2)
                })
            
            # Prepare result
            result = {
                'monthly_payment': round(monthly_payment, 2),
                'total_monthly_payment': round(total_monthly_payment, 2),
                'total_payment': round(total_payment, 2),
                'total_interest': round(total_interest, 2),
                'monthly_breakdown': {
                    'principal_and_interest': round(monthly_payment, 2),
                    'property_tax': round(monthly_property_tax, 2),
                    'insurance': round(monthly_insurance, 2),
                    'pmi': round(pmi_monthly, 2)
                },
                'amortization_schedule': amortization_schedule
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in MortgageLoanCalculatorTool: {e}", exc_info=True)
            return f"Error: {e}"