from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple
import json
import os

class Expense:
    def __init__(self, amount: float, category: str, date: str, description: str = ''):
        self.amount = amount
        self.category = category
        self.date = date
        self.description = description

    def to_dict(self):
        return {
            'amount': self.amount,
            'category': self.category,
            'date': self.date,
            'description': self.description
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            amount=data['amount'],
            category=data['category'],
            date=data['date'],
            description=data.get('description', '')
        )

class ExpenseManager:
    def __init__(self):
        self.expenses: List[Expense] = []
        self.monthly_budget = 0
        self.data_file = 'expense_data.json'
        self.load_data()

    def save_data(self):
        data = {
            'expenses': [exp.to_dict() for exp in self.expenses],
            'monthly_budget': self.monthly_budget
        }
        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Error saving data: {str(e)}")

    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    self.expenses = [Expense.from_dict(exp) for exp in data.get('expenses', [])]
                    self.monthly_budget = data.get('monthly_budget', 0)
        except Exception as e:
            print(f"Error loading data: {str(e)}")
            self.expenses = []
            self.monthly_budget = 0

    def get_current_month_expenses(self) -> float:
        current_month = datetime.now().strftime('%Y-%m')
        return sum(exp.amount for exp in self.expenses 
                  if exp.date.startswith(current_month))

    def would_exceed_budget(self, amount: float) -> bool:
        if self.monthly_budget <= 0:  # No budget set
            return False
        current_month_total = self.get_current_month_expenses()
        return (current_month_total + amount) > self.monthly_budget

    def add_expense(self, date: str, category: str, amount: float, description: str = ''):
        try:
            if self.would_exceed_budget(amount):
                current_total = self.get_current_month_expenses()
                remaining = self.monthly_budget - current_total
                return False, f"Cannot add expense of ₹{amount}. It exceeds your monthly budget. Remaining budget: ₹{remaining:.2f}"
            
            expense = Expense(amount=amount, category=category, date=date, description=description)
            self.expenses.append(expense)
            self.save_data()
            return True, "Expense added successfully"
        except Exception as e:
            print(f"Error adding expense: {str(e)}")
            return False, str(e)

    def get_expenses_by_date(self, date: str) -> Dict:
        try:
            today = datetime.strptime(date, '%Y-%m-%d')
            yesterday = today - timedelta(days=1)
            last_month = today.replace(day=1) - timedelta(days=1)
            last_year = today.replace(year=today.year-1)

            expenses = [{'amount': exp.amount, 'category': exp.category} 
                       for exp in self.expenses if exp.date == date]
            
            return {
                'total': sum(exp.amount for exp in self.expenses if exp.date == date),
                'comparison': {
                    'yesterday': self.get_total_expenses(yesterday.strftime('%Y-%m-%d')),
                    'last_month': self.get_total_expenses(last_month.strftime('%Y-%m-%d')),
                    'last_year': self.get_total_expenses(last_year.strftime('%Y-%m-%d'))
                },
                'expenses': expenses
            }
        except Exception as e:
            print(f"Error getting expenses by date: {str(e)}")
            return {'total': 0, 'comparison': {'yesterday': 0, 'last_month': 0, 'last_year': 0}, 'expenses': []}

    def get_all_expenses(self) -> List[Dict]:
        try:
            return [{'amount': exp.amount, 'category': exp.category, 'date': exp.date} 
                    for exp in self.expenses]
        except Exception as e:
            print(f"Error getting all expenses: {str(e)}")
            return []

    def get_total_expenses(self, date: str) -> float:
        try:
            return sum(exp.amount for exp in self.expenses if exp.date == date)
        except Exception as e:
            print(f"Error getting total expenses: {str(e)}")
            return 0.0

    def set_budget(self, amount: float):
        try:
            self.monthly_budget = amount
            self.save_data()
            return True
        except Exception as e:
            print(f"Error setting budget: {str(e)}")
            return False

    def get_budget(self) -> float:
        return self.monthly_budget

    def delete_expense(self, date: str, category: str, amount: float) -> Tuple[bool, str]:
        try:
            # Find the expense to delete
            for i, expense in enumerate(self.expenses):
                if (expense.date == date and 
                    expense.category == category and 
                    expense.amount == amount):
                    del self.expenses[i]
                    self.save_data()
                    return True, "Expense deleted successfully"
            return False, "Expense not found"
        except Exception as e:
            print(f"Error deleting expense: {str(e)}")
            return False, str(e)

    def reset_expenses(self) -> Tuple[bool, str]:
        try:
            self.expenses = []
            self.save_data()
            return True, "All expenses have been reset successfully"
        except Exception as e:
            print(f"Error resetting expenses: {str(e)}")
            return False, str(e) 