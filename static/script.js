document.addEventListener('DOMContentLoaded', () => {
    // Display current date in the add expense card
    const currentDate = new Date().toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
    });
    document.getElementById('current-date').textContent = currentDate;

    // Handle expense form submission
    const expenseForm = document.getElementById('expense-form');
    expenseForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const category = document.getElementById('category').value;
        const amount = document.getElementById('amount').value;
        const description = document.getElementById('description').value;

        if (!category || !amount) {
            alert('Please fill in all required fields');
            return;
        }

        try {
            const response = await fetch('/api/add_expense', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    date: new Date().toISOString().split('T')[0],
                    category, 
                    amount: parseFloat(amount),
                    description
                })
            });

            const data = await response.json();
            if (response.ok) {
                alert('Success: ' + data.message);
                expenseForm.reset();
                updateExpenses();
                updateChart();
                updateBudget();
            } else {
                if (data.error && data.error.includes('budget limit')) {
                    alert('Error: ' + data.error + '\nPlease increase your budget before adding this expense.');
                    return; // Prevent further action
                } else {
                    alert('Error: ' + data.error);
                }
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to add expense');
        }
    });

    // Handle budget setting
    const setBudgetBtn = document.getElementById('set-budget');
    setBudgetBtn.addEventListener('click', async () => {
        const amount = document.getElementById('budget-amount').value;
        
        if (!amount) {
            alert('Please enter a budget amount');
            return;
        }

        try {
            const response = await fetch('/api/set_budget', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ amount: parseFloat(amount) })
            });

            const data = await response.json();
            if (response.ok) {
                alert('Budget set successfully!');
                document.getElementById('budget-amount').value = '';
                updateBudget();
            } else {
                alert(data.error || 'Failed to set budget');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to set budget');
        }
    });

    // Handle reset expenses
    const resetBtn = document.getElementById('reset-expenses');
    resetBtn.addEventListener('click', async () => {
        if (!confirm('Are you sure you want to delete all expenses? This action cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch('/api/reset_expenses', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();
            if (response.ok) {
                alert('Success: ' + data.message);
                updateExpenses();
                updateChart();
            } else {
                alert('Error: ' + (data.error || 'Failed to reset expenses'));
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to reset expenses');
        }
    });

    // Update expenses display
    async function updateExpenses() {
        try {
            const currentDate = new Date().toISOString().split('T')[0];
            const response = await fetch(`/api/get_expenses?date=${currentDate}`);
            const data = await response.json();
            
            if (data.error) {
                console.error('Error fetching expenses:', data.error);
                return;
            }
            
            // Update totals
            document.getElementById('today-total').textContent = `₹${data.total.toFixed(2)}`;
            document.getElementById('yesterday-total').textContent = `₹${data.comparison.yesterday.toFixed(2)}`;
            document.getElementById('last-month-total').textContent = `₹${data.comparison.last_month.toFixed(2)}`;
            document.getElementById('last-year-total').textContent = `₹${data.comparison.last_year.toFixed(2)}`;
            
            // Update expenses list
            const expensesList = document.getElementById('expenses-list');
            expensesList.innerHTML = '';
            
            if (data.expenses && data.expenses.length > 0) {
                data.expenses.forEach(expense => {
                    const li = document.createElement('li');
                    li.className = 'expense-item';
                    li.innerHTML = `
                        <div class="expense-content">
                            <span>${expense.category}</span>
                            <span>₹${expense.amount.toFixed(2)}</span>
                        </div>
                        <button class="delete-expense" title="Delete expense">
                            <i class="fas fa-trash-alt"></i>
                        </button>
                    `;

                    // Add delete button handler
                    const deleteBtn = li.querySelector('.delete-expense');
                    deleteBtn.addEventListener('click', async () => {
                        if (confirm('Are you sure you want to delete this expense?')) {
                            try {
                                const response = await fetch('/api/delete_expense', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json'
                                    },
                                    body: JSON.stringify({
                                        date: currentDate,
                                        category: expense.category,
                                        amount: expense.amount
                                    })
                                });

                                const data = await response.json();
                                if (response.ok) {
                                    alert('Success: ' + data.message);
                                    updateExpenses();
                                    updateChart();
                                    updateBudget();
                                } else {
                                    alert('Error: ' + data.error);
                                }
                            } catch (error) {
                                console.error('Error:', error);
                                alert('Failed to delete expense');
                            }
                        }
                    });

                    expensesList.appendChild(li);
                });
            } else {
                expensesList.innerHTML = '<li>No expenses for today</li>';
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }

    // Update budget display
    async function updateBudget() {
        try {
            const response = await fetch('/api/get_budget');
            const data = await response.json();
            
            if (data.error) {
                console.error('Error fetching budget:', data.error);
                return;
            }
            
            document.getElementById('month-total').textContent = `₹${data.budget.toFixed(2)}`;
        } catch (error) {
            console.error('Error:', error);
        }
    }

    // Update chart
    async function updateChart() {
        try {
            const chartImg = document.getElementById('expense-chart');
            chartImg.src = '/api/get_chart?' + new Date().getTime();
        } catch (error) {
            console.error('Error:', error);
        }
    }

    // Initial load
    updateExpenses();
    updateBudget();
    updateChart();
});