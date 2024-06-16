import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import streamlit as st
import calendar

class ExpenseManager:
    def __init__(self, file_name='expenses.json'):
        self.file_name = file_name
        self.data = self.load_data()

    def load_data(self):
        try:
            with open(self.file_name, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {'income': [], 'expenses': [], 'categories': []}

    def save_data(self):
        with open(self.file_name, 'w') as f:
            json.dump(self.data, f, indent=4)

    def add_income(self, amount, description, date):
        self.data['income'].append({
            'amount': amount,
            'description': description,
            'date': date.strftime('%Y-%m-%d')
        })
        self.save_data()

    def update_income(self, index, amount, description, date):
        if 0 <= index < len(self.data['income']):
            self.data['income'][index].update({
                'amount': amount,
                'description': description,
                'date': date.strftime('%Y-%m-%d')
            })
            self.save_data()
        else:
            st.error("Invalid index")

    def delete_income(self, index):
        if 0 <= index < len(self.data['income']):
            del self.data['income'][index]
            self.save_data()
        else:
            st.error("Invalid index")

    def add_category(self, category_name, description):
        if category_name not in [cat['name'] for cat in self.data['categories'] if isinstance(cat, dict)]:
            self.data['categories'].append({'name': category_name, 'description': description})
            self.save_data()

    def update_category(self, old_category_name, new_category_name, new_description):
        for category in self.data['categories']:
            if category['name'] == old_category_name:
                category['name'] = new_category_name
                category['description'] = new_description
                for expense in self.data['expenses']:
                    if expense['category'] == old_category_name:
                        expense['category'] = new_category_name
                self.save_data()
                return
        st.error("Category does not exist!")

    def delete_category(self, category_name):
        self.data['categories'] = [cat for cat in self.data['categories'] if cat['name'] != category_name]
        self.data['expenses'] = [expense for expense in self.data['expenses'] if expense['category'] != category_name]
        self.save_data()

    def add_expense(self, amount, description, category, date):
        if category not in [cat['name'] for cat in self.data['categories'] if isinstance(cat, dict)]:
            st.error("Category does not exist!")
            return
        self.data['expenses'].append({
            'amount': amount,
            'description': description,
            'category': category,
            'date': date.strftime('%Y-%m-%d')
        })
        self.save_data()

    def update_expense(self, index, amount, description, category, date):
        if 0 <= index < len(self.data['expenses']):
            self.data['expenses'][index].update({
                'amount': amount,
                'description': description,
                'category': category,
                'date': date.strftime('%Y-%m-%d')
            })
            self.save_data()
        else:
            st.error("Invalid index")

    def delete_expense(self, index):
        if 0 <= index < len(self.data['expenses']):
            del self.data['expenses'][index]
            self.save_data()
        else:
            st.error("Invalid index")

    def list_expenses(self, period=None):
        if period:
            expenses_by_period = [expense for expense in self.data['expenses'] if expense['date'][:len(period)] == period]
            for idx, expense in enumerate(expenses_by_period):
                st.write(f"{idx + 1}. {expense['description']} - {expense['amount']} VND - {expense['category']} - {expense['date']}")
        else:
            for idx, expense in enumerate(self.data['expenses']):
                st.write(f"{idx + 1}. {expense['description']} - {expense['amount']} VND - {expense['category']} - {expense['date']}")

    def list_income(self):
        for idx, income in enumerate(self.data['income']):
            st.write(f"{idx + 1}. {income['description']} - {income['amount']} VND - {income['date']}")

    def summarize_expenses(self, period):
        summary = {}
        for expense in self.data['expenses']:
            date = datetime.strptime(expense['date'], '%Y-%m-%d')
            if period == 'day':
                key = date.strftime('%Y-%m-%d')
            elif period == 'month':
                key = date.strftime('%Y-%m')

            if key not in summary:
                summary[key] = 0
            summary[key] += expense['amount']
        
        return summary

    def summarize_income(self, period):
        summary = {}
        for income in self.data['income']:
            date = datetime.strptime(income['date'], '%Y-%m-%d')
            if period == 'day':
                key = date.strftime('%Y-%m-%d')
            elif period == 'month':
                key = date.strftime('%Y-%m')

            if key not in summary:
                summary[key] = 0
            summary[key] += income['amount']
        
        return summary

    def plot_line_summary(self, period, specific_period):
        expense_summary = self.summarize_expenses(period)
        income_summary = self.summarize_income(period)

        if specific_period:
            expense_summary = {k: v for k, v in expense_summary.items() if specific_period in k}
            income_summary = {k: v for k, v in income_summary.items() if specific_period in k}

        dates = list(expense_summary.keys())
        expense_amounts = list(expense_summary.values())
        income_amounts = [income_summary.get(date, 0) for date in dates]

        plt.figure(figsize=(10, 5))
        plt.plot(dates, expense_amounts, marker='o', label='Expenses')
        plt.plot(dates, income_amounts, marker='o', label='Income')
        plt.xlabel(f'Time ({period})')
        plt.ylabel('Amount (VND)')
        plt.title(f'Income and Expense Summary by {period.capitalize()}')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(plt)

    def plot_pie_summary(self, period, specific_period):
        category_summary = {}
        for expense in self.data['expenses']:
            date = datetime.strptime(expense['date'], '%Y-%m-%d')
            if period == 'day' and specific_period == date.strftime('%Y-%m-%d'):
                key = expense['category']
            elif period == 'month' and specific_period == date.strftime('%Y-%m'):
                key = expense['category']
            else:
                continue

            if key not in category_summary:
                category_summary[key] = 0
            category_summary[key] += expense['amount']

        if category_summary:
            plt.figure(figsize=(7, 7))
            plt.pie(category_summary.values(), labels=category_summary.keys(), autopct='%1.1f%%', startangle=140)
            plt.axis('equal')
            plt.title(f'Expense Distribution by Category ({period.capitalize()})')
            st.pyplot(plt)

def main():
    manager = ExpenseManager()
    
    st.title("Expense Manager")

    menu = ["Income", "Category of Expenses", "Expenses", "Summarize and Plot Summary"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Income":
        sub_menu = ["Add", "Update", "Delete", "View"]
        sub_choice = st.sidebar.selectbox("Income Menu", sub_menu)
        
        if sub_choice == "Add":
            st.subheader("Add Income")
            amount = st.number_input("Enter amount:", min_value=0, step=1)
            description = st.text_input("Enter description:")
            date = st.date_input("Enter date:")
            if st.button("Add Income"):
                manager.add_income(amount, description, date)
                st.success("Income added successfully!")

        elif sub_choice == "Update":
            st.subheader("Update Income")
            incomes = [f"{idx + 1}. {inc['description']} - {inc['amount']} VND - {inc['date']}" for idx, inc in enumerate(manager.data['income'])]
            index = st.selectbox("Select the income to update:", range(len(incomes)), format_func=lambda x: incomes[x])
            amount = st.number_input("Enter new amount:", min_value=0.0, step=0.01)
            description = st.text_input("Enter new description:")
            date = st.date_input("Enter date:")
            if st.button("Update Income"):
                manager.update_income(index, amount, description, date)
                st.success("Income updated successfully!")

        elif sub_choice == "Delete":
            st.subheader("Delete Income")
            incomes = [f"{idx + 1}. {inc['description']} - {inc['amount']} VND - {inc['date']}" for idx, inc in enumerate(manager.data['income'])]
            index = st.selectbox("Select the income to delete:", range(len(incomes)), format_func=lambda x: incomes[x])
            if st.button("Delete Income"):
                manager.delete_income(index)
                st.success("Income deleted successfully!")

        elif sub_choice == "View":
            st.subheader("List Income")
            manager.list_income()

            st.subheader("View Income by Month")
            month = st.selectbox("Select month:", [f"{datetime.now().year}-{str(i).zfill(2)}" for i in range(1, 13)])
            if st.button("View Income"):
                incomes_by_month = [inc for inc in manager.data['income'] if inc['date'][:7] == month]
                for income in incomes_by_month:
                    st.write(f"{income['description']} - {income['amount']} VND - {income['date']}")

    elif choice == "Category of Expenses":
        sub_menu = ["Add", "Update", "Delete"]
        sub_choice = st.sidebar.selectbox("Category Menu", sub_menu)
        
        if sub_choice == "Add":
            st.subheader("Add Category")
            category = st.text_input("Enter category name:")
            description = st.text_input("Enter category description:")
            if st.button("Add Category"):
                manager.add_category(category, description)
                st.success("Category added successfully!")

        elif sub_choice == "Update":
            st.subheader("Update Category")
            if all(isinstance(cat, dict) and 'name' in cat for cat in manager.data['categories']):
                old_category = st.selectbox("Select the category to update:", [cat['name'] for cat in manager.data['categories']])
                new_category = st.text_input("Enter new category name:")
                new_description = st.text_input("Enter new category description:")
                if st.button("Update Category"):
                    manager.update_category(old_category, new_category, new_description)
                    st.success("Category updated successfully!")
            else:
                st.error("Categories data is invalid.")

        elif sub_choice == "Delete":
            st.subheader("Delete Category")
            if all(isinstance(cat, dict) and 'name' in cat for cat in manager.data['categories']):
                category = st.selectbox("Select the category to delete:", [cat['name'] for cat in manager.data['categories']])
                if st.button("Delete Category"):
                    manager.delete_category(category)
                    st.success("Category deleted successfully!")
            else:
                st.error("Categories data is invalid.")

    elif choice == "Expenses":
        sub_menu = ["Add", "Update", "Delete"]
        sub_choice = st.sidebar.selectbox("Expenses Menu", sub_menu)
        
        if sub_choice == "Add":
            st.subheader("Add Expense")
            amount = st.number_input("Enter amount:", min_value=0, step=1)
            description = st.text_input("Enter description:")
            date = st.date_input("Enter date:")
            if all(isinstance(cat, dict) and 'name' in cat for cat in manager.data['categories']):
                category = st.selectbox("Select category:", [cat['name'] for cat in manager.data['categories']])
                if st.button("Add Expense"):
                    manager.add_expense(amount, description, category, date)
                    st.success("Expense added successfully!")
            else:
                st.error("Categories data is invalid.")

        elif sub_choice == "Update":
            st.subheader("Update Expense")
            expenses = [f"{idx + 1}. {exp['description']} - {exp['amount']} VND - {exp['category']} - {exp['date']}" for idx, exp in enumerate(manager.data['expenses'])]
            index = st.selectbox("Select the expense to update:", range(len(expenses)), format_func=lambda x: expenses[x])
            amount = st.number_input("Enter new amount:", min_value=0.0, step=0.01)
            description = st.text_input("Enter new description:")
            date = st.date_input("Enter date:")
            if all(isinstance(cat, dict) and 'name' in cat for cat in manager.data['categories']):
                category = st.selectbox("Select new category:", [cat['name'] for cat in manager.data['categories']])
                if st.button("Update Expense"):
                    manager.update_expense(index, amount, description, category, date)
                    st.success("Expense updated successfully!")
            else:
                st.error("Categories data is invalid.")

        elif sub_choice == "Delete":
            st.subheader("Delete Expense")
            expenses = [f"{idx + 1}. {exp['description']} - {exp['amount']} VND - {exp['category']} - {exp['date']}" for idx, exp in enumerate(manager.data['expenses'])]
            index = st.selectbox("Select the expense to delete:", range(len(expenses)), format_func=lambda x: expenses[x])
            if st.button("Delete Expense"):
                manager.delete_expense(index)
                st.success("Expense deleted successfully!")

    elif choice == "Summarize and Plot Summary":
        sub_menu = ["List Expenses", "Plot Line Summary", "Plot Pie Summary"]
        sub_choice = st.sidebar.selectbox("Summary Menu", sub_menu)
        
        if sub_choice == "List Expenses":
            st.subheader("List Expenses")
            date_period = st.date_input("Select date (for day) or month (for month):")
            period = st.selectbox("Select period type:", ["day", "month"])
            if period == "day":
                specific_period = date_period.strftime('%Y-%m-%d')
            elif period == "month":
                specific_period = date_period.strftime('%Y-%m')
            manager.list_expenses(specific_period)

        elif sub_choice == "Plot Line Summary":
            st.subheader("Plot Line Summary")
            period = st.selectbox("Plot summary by:", ["day", "month"])
            specific_period = None

            if period == 'day':
                specific_period = st.date_input("Select date:").strftime('%Y-%m-%d')
            elif period == 'month':
                specific_period = st.selectbox("Select month:", [f"{datetime.now().year}-{str(i).zfill(2)}" for i in range(1, 13)])

            if st.button("Plot"):
                manager.plot_line_summary(period, specific_period)

        elif sub_choice == "Plot Pie Summary":
            st.subheader("Plot Pie Summary")
            period = st.selectbox("Plot summary by:", ["day", "month"])
            specific_period = None

            if period == 'day':
                specific_period = st.date_input("Select date:").strftime('%Y-%m-%d')
            elif period == 'month':
                specific_period = st.selectbox("Select month:", [f"{datetime.now().year}-{str(i).zfill(2)}" for i in range(1, 13)])

            if st.button("Plot"):
                manager.plot_pie_summary(period, specific_period)

if __name__ == "__main__":
    main()
