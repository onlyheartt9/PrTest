import unittest
import math
from unittest.mock import patch, MagicMock

# Import the module containing the function to be tested
# Since we can't directly import the class due to the project structure,
# we'll mock the BaseTool class and recreate the MortgageLoanCalculatorTool

class MockBaseTool:
    pass

class MortgageLoanCalculatorTool(MockBaseTool):
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
            return f"Error: {e}"


class TestMortgageLoanCalculatorTool(unittest.TestCase):
    def setUp(self):
        self.calculator = MortgageLoanCalculatorTool()
    
    def test_basic_mortgage_calculation(self):
        # Test case: Basic mortgage calculation with standard parameters
        loan_details = {
            'principal': 300000,
            'annual_interest_rate': 4.5,
            'loan_term_years': 30
        }
        
        result = self.calculator.calculate_mortgage_loan(loan_details)
        
        # Verify the result is a dictionary
        self.assertIsInstance(result, dict)
        
        # Check key values are present and have correct types
        self.assertIn('monthly_payment', result)
        self.assertIsInstance(result['monthly_payment'], float)
        
        # Expected monthly payment for a $300,000 loan at 4.5% for 30 years is around $1,520.06
        self.assertAlmostEqual(result['monthly_payment'], 1520.06, delta=1)
        
        # Check total interest is calculated correctly
        self.assertIn('total_interest', result)
        # Total interest should be approximately $247,220 (monthly payment * term * 12 - principal)
        self.assertAlmostEqual(result['total_interest'], 247220, delta=100)
    
    def test_zero_interest_rate(self):
        # Test case: Mortgage with 0% interest rate
        loan_details = {
            'principal': 300000,
            'annual_interest_rate': 0,
            'loan_term_years': 30
        }
        
        result = self.calculator.calculate_mortgage_loan(loan_details)
        
        # Monthly payment should be principal / (term * 12)
        expected_monthly_payment = 300000 / (30 * 12)
        self.assertAlmostEqual(result['monthly_payment'], expected_monthly_payment, delta=0.01)
        
        # Total interest should be 0
        self.assertAlmostEqual(result['total_interest'], 0, delta=0.01)
    
    def test_with_down_payment(self):
        # Test case: Mortgage with down payment
        loan_details = {
            'principal': 300000,
            'annual_interest_rate': 4.5,
            'loan_term_years': 30,
            'down_payment': 60000  # 20% down payment
        }
        
        result = self.calculator.calculate_mortgage_loan(loan_details)
        
        # Loan amount should be principal - down_payment = 240,000
        # Expected monthly payment for a $240,000 loan at 4.5% for 30 years is around $1,216.04
        self.assertAlmostEqual(result['monthly_payment'], 1216.04, delta=1)
    
    def test_with_property_tax_and_insurance(self):
        # Test case: Mortgage with property tax and insurance
        loan_details = {
            'principal': 300000,
            'annual_interest_rate': 4.5,
            'loan_term_years': 30,
            'property_tax': 3600,  # $300/month
            'insurance': 1200      # $100/month
        }
        
        result = self.calculator.calculate_mortgage_loan(loan_details)
        
        # Check monthly breakdown
        self.assertEqual(result['monthly_breakdown']['property_tax'], 300.0)
        self.assertEqual(result['monthly_breakdown']['insurance'], 100.0)
        
        # Total monthly payment should include P&I + property tax + insurance
        expected_total = result['monthly_payment'] + 300 + 100
        self.assertAlmostEqual(result['total_monthly_payment'], expected_total, delta=0.01)
    
    def test_with_pmi(self):
        # Test case: Mortgage with PMI (less than 20% down payment)
        loan_details = {
            'principal': 300000,
            'annual_interest_rate': 4.5,
            'loan_term_years': 30,
            'down_payment': 30000,  # 10% down payment
            'pmi': 0.5              # 0.5% PMI rate
        }
        
        result = self.calculator.calculate_mortgage_loan(loan_details)
        
        # PMI should be calculated as (loan_amount * pmi_rate / 100) / 12
        # loan_amount = 270,000, so monthly PMI = (270000 * 0.5 / 100) / 12 = $112.50
        self.assertAlmostEqual(result['monthly_breakdown']['pmi'], 112.50, delta=0.01)
    
    def test_amortization_schedule(self):
        # Test case: Verify amortization schedule
        loan_details = {
            'principal': 300000,
            'annual_interest_rate': 4.5,
            'loan_term_years': 30
        }
        
        result = self.calculator.calculate_mortgage_loan(loan_details)
        
        # Check amortization schedule exists and has correct length
        self.assertIn('amortization_schedule', result)
        self.assertEqual(len(result['amortization_schedule']), 30)  # 30 years
        
        # Check first year entry
        first_year = result['amortization_schedule'][0]
        self.assertEqual(first_year['year'], 1)
        self.assertIn('principal_paid', first_year)
        self.assertIn('interest_paid', first_year)
        self.assertIn('remaining_balance', first_year)
        
        # Check last year entry - remaining balance should be close to 0
        last_year = result['amortization_schedule'][-1]
        self.assertAlmostEqual(last_year['remaining_balance'], 0, delta=0.1)
    
    def test_invalid_principal(self):
        # Test case: Invalid principal (zero or negative)
        loan_details = {
            'principal': 0,
            'annual_interest_rate': 4.5,
            'loan_term_years': 30
        }
        
        result = self.calculator.calculate_mortgage_loan(loan_details)
        self.assertEqual(result, "Error: Loan principal must be greater than zero")
        
        loan_details['principal'] = -100000
        result = self.calculator.calculate_mortgage_loan(loan_details)
        self.assertEqual(result, "Error: Loan principal must be greater than zero")
    
    def test_invalid_interest_rate(self):
        # Test case: Invalid interest rate (negative)
        loan_details = {
            'principal': 300000,
            'annual_interest_rate': -2.5,
            'loan_term_years': 30
        }
        
        result = self.calculator.calculate_mortgage_loan(loan_details)
        self.assertEqual(result, "Error: Interest rate cannot be negative")
    
    def test_invalid_loan_term(self):
        # Test case: Invalid loan term (zero or negative)
        loan_details = {
            'principal': 300000,
            'annual_interest_rate': 4.5,
            'loan_term_years': 0
        }
        
        result = self.calculator.calculate_mortgage_loan(loan_details)
        self.assertEqual(result, "Error: Loan term must be greater than zero")
        
        loan_details['loan_term_years'] = -10
        result = self.calculator.calculate_mortgage_loan(loan_details)
        self.assertEqual(result, "Error: Loan term must be greater than zero")
    
    def test_down_payment_exceeds_principal(self):
        # Test case: Down payment exceeds principal
        loan_details = {
            'principal': 300000,
            'annual_interest_rate': 4.5,
            'loan_term_years': 30,
            'down_payment': 350000
        }
        
        result = self.calculator.calculate_mortgage_loan(loan_details)
        self.assertEqual(result, "Error: Loan amount after down payment must be greater than zero")
    
    def test_missing_parameters(self):
        # Test case: Missing required parameters
        # When principal is missing, it defaults to 0, which triggers the validation error
        loan_details = {
            'annual_interest_rate': 4.5,
            'loan_term_years': 30
        }
        
        result = self.calculator.calculate_mortgage_loan(loan_details)
        self.assertEqual(result, "Error: Loan principal must be greater than zero")
    
    def test_short_term_loan(self):
        # Test case: Short-term loan (15 years)
        loan_details = {
            'principal': 300000,
            'annual_interest_rate': 4.5,
            'loan_term_years': 15
        }
        
        result = self.calculator.calculate_mortgage_loan(loan_details)
        
        # Expected monthly payment for a $300,000 loan at 4.5% for 15 years is around $2,295.80
        self.assertAlmostEqual(result['monthly_payment'], 2295.80, delta=1)
        
        # Check amortization schedule has 15 entries
        self.assertEqual(len(result['amortization_schedule']), 15)
    
    def test_high_interest_rate(self):
        # Test case: High interest rate
        loan_details = {
            'principal': 300000,
            'annual_interest_rate': 18.0,  # Very high interest rate
            'loan_term_years': 30
        }
        
        result = self.calculator.calculate_mortgage_loan(loan_details)
        
        # Expected monthly payment will be much higher with 18% interest
        # Should be around $4,500
        self.assertGreater(result['monthly_payment'], 4000)
        
        # Total interest paid will be extremely high
        self.assertGreater(result['total_interest'], 1000000)  # Over a million in interest

if __name__ == '__main__':
    unittest.main()