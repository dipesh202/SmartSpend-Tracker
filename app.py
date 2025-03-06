from flask import Flask, request, jsonify, send_file, send_from_directory
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Set the backend to non-interactive 'Agg'
import matplotlib.pyplot as plt
import io
from expense_manager import ExpenseManager

app = Flask(__name__, static_folder='static')
expense_manager = ExpenseManager()

@app.route('/')
def serve_frontend():
    return send_from_directory('static', 'index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/api/add_expense', methods=['POST'])
def add_expense():
    try:
        data = request.json
        if not all(key in data for key in ['date', 'category', 'amount']):
            return jsonify({'error': 'Missing required fields'}), 400

        # Validate amount
        try:
            amount = float(data['amount'])
            if amount <= 0:
                return jsonify({'error': 'Amount must be greater than 0'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid amount format'}), 400

        # Validate category
        valid_categories = ['food', 'transportation', 'entertainment', 'shopping', 
                          'bills', 'healthcare', 'education', 'other']
        if data['category'] not in valid_categories:
            return jsonify({'error': 'Invalid category'}), 400

        success, message = expense_manager.add_expense(
            data['date'],
            data['category'],
            amount,
            data.get('description', '')
        )
        
        if success:
            return jsonify({'status': 'success', 'message': message})
        else:
            return jsonify({'error': message}), 400
    except Exception as e:
        print(f"Error adding expense: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_expenses', methods=['GET'])
def get_expenses():
    try:
        date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        expenses = expense_manager.get_expenses_by_date(date)
        return jsonify(expenses)
    except Exception as e:
        print(f"Error getting expenses: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/set_budget', methods=['POST'])
def set_budget():
    try:
        data = request.json
        if 'amount' not in data:
            return jsonify({'error': 'Missing budget amount'}), 400

        # Validate amount
        try:
            amount = float(data['amount'])
            if amount <= 0:
                return jsonify({'error': 'Budget amount must be greater than 0'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid amount format'}), 400

        success = expense_manager.set_budget(amount)
        if success:
            return jsonify({'status': 'success', 'message': 'Budget set successfully'})
        else:
            return jsonify({'error': 'Failed to set budget'}), 500
    except Exception as e:
        print(f"Error setting budget: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_budget', methods=['GET'])
def get_budget():
    try:
        budget = expense_manager.get_budget()
        return jsonify({'budget': budget})
    except Exception as e:
        print(f"Error getting budget: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/reset_expenses', methods=['POST'])
def reset_expenses():
    try:
        success, message = expense_manager.reset_expenses()
        if success:
            return jsonify({'status': 'success', 'message': message})
        else:
            return jsonify({'error': message}), 500
    except Exception as e:
        print(f"Error resetting expenses: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/delete_expense', methods=['POST'])
def delete_expense():
    try:
        data = request.json
        if not all(key in data for key in ['date', 'category', 'amount']):
            return jsonify({'error': 'Missing required fields'}), 400

        success, message = expense_manager.delete_expense(
            data['date'],
            data['category'],
            float(data['amount'])
        )
        
        if success:
            return jsonify({'status': 'success', 'message': message})
        else:
            return jsonify({'error': message}), 400
    except Exception as e:
        print(f"Error deleting expense: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_chart', methods=['GET'])
def get_chart():
    try:
        # Create figure with Agg backend
        plt.clf()  # Clear any existing plots
        plt.figure(figsize=(8, 8))
        
        # Get expense data
        expenses = expense_manager.get_all_expenses()
        categories = {}
        
        for expense in expenses:
            if expense['category'] in categories:
                categories[expense['category']] += expense['amount']
            else:
                categories[expense['category']] = expense['amount']
        
        if not categories:
            # If no expenses, create an empty pie chart
            plt.pie([1], labels=['No Expenses'], colors=['#e2e8f0'])
        else:
            # Create pie chart with actual data
            plt.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%')
        
        plt.title('Expense Distribution')
        
        # Save plot to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()  # Close the figure to free memory
        
        return send_file(buf, mimetype='image/png')
    except Exception as e:
        print(f"Error generating chart: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 