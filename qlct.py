import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import streamlit as st
import calendar
import pandas as pd

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
            'amount': round(amount, 2),
            'description': description,
            'date': date.strftime('%Y-%m-%d')
        })
        self.save_data()

    def update_income(self, index, amount, description, date):
        if 0 <= index < len(self.data['income']):
            self.data['income'][index].update({
                'amount': round(amount, 2),
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
            'amount': round(amount, 2),
            'description': description,
            'category': category,
            'date': date.strftime('%Y-%m-%d')
        })
        self.save_data()

    def update_expense(self, index, amount, description, category, date):
        if 0 <= index < len(self.data['expenses']):
            self.data['expenses'][index].update({
                'amount': round(amount, 2),
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
        if period == 'all':
            table_data = []
            sorted_expenses = sorted(self.data['expenses'], key=lambda x: x['date'])  # Sắp xếp theo ngày tăng dần
            for idx, expense in enumerate(sorted_expenses):
                table_data.append([idx + 1, expense['description'], expense['amount'], expense['category'], expense['date']])
            st.table(pd.DataFrame(table_data, columns=['Index', 'Description', 'Amount (VND)', 'Category', 'Date']))

        elif period == 'day':
            selected_date = st.date_input("Select date:")
            expenses_by_day = [expense for expense in self.data['expenses'] if expense['date'] == selected_date.strftime('%Y-%m-%d')]
            if expenses_by_day:
                table_data = []
                for idx, expense in enumerate(expenses_by_day):
                    table_data.append([idx + 1, expense['description'], expense['amount'], expense['category'], expense['date']])
                st.table(pd.DataFrame(table_data, columns=['Index', 'Description', 'Amount (VND)', 'Category', 'Date']))
            else:
                st.write("No expenses found for selected date.")
        
        elif period == 'month':
            selected_year = st.selectbox("Select year:", list(set(expense['date'][:4] for expense in self.data['expenses'])))
            expenses_by_year = [expense for expense in self.data['expenses'] if expense['date'][:4] == selected_year]
            selected_month = st.selectbox("Select month:", [str(i).zfill(2) for i in range(1, 13)])
            expenses_by_month = [expense for expense in expenses_by_year if expense['date'][5:7] == selected_month]
            sorted_expenses_by_month = sorted(expenses_by_month, key=lambda x: x['date'])  # Sắp xếp theo ngày tăng dần
            if sorted_expenses_by_month:
                table_data = []
                for idx, expense in enumerate(sorted_expenses_by_month):
                    table_data.append([idx + 1, expense['description'], expense['amount'], expense['category'], expense['date']])
                st.table(pd.DataFrame(table_data, columns=['Index', 'Description', 'Amount (VND)', 'Category', 'Date']))
            else:
                st.write("No expenses found for selected month.")

        elif period == 'year':
            selected_year = st.selectbox("Select year:", list(set(expense['date'][:4] for expense in self.data['expenses'])))
            expenses_by_year = [expense for expense in self.data['expenses'] if expense['date'][:4] == selected_year]
            sorted_expenses_by_year = sorted(expenses_by_year, key=lambda x: x['date'])  
            if sorted_expenses_by_year:
                table_data = []
                for idx, expense in enumerate(sorted_expenses_by_year):
                    table_data.append([idx + 1, expense['description'], expense['amount'], expense['category'], expense['date']])
                st.table(pd.DataFrame(table_data, columns=['Index', 'Description', 'Amount (VND)', 'Category', 'Date']))
            else:
                st.write("No expenses found for selected year.")

        else:
            st.error("Invalid period selection.")

    def list_income(self, period=None):
        if period == 'all':
            table_data = []
            sorted_income = sorted(self.data['income'], key=lambda x: x['date'])  # Sắp xếp theo ngày tăng dần
            for idx, income in enumerate(sorted_income):
                table_data.append([idx + 1, income['description'], income['amount'], income['date']])
            st.table(pd.DataFrame(table_data, columns=['Index', 'Description', 'Amount (VND)', 'Date']))
        
        elif period == 'month':
            selected_year = st.selectbox("Select year:", list(set(income['date'][:4] for income in self.data['income'])))
            incomes_by_year = [income for income in self.data['income'] if income['date'][:4] == selected_year]
            selected_month = st.selectbox("Select month:", [str(i).zfill(2) for i in range(1, 13)])
            incomes_by_month = [income for income in incomes_by_year if income['date'][5:7] == selected_month]
            sorted_incomes_by_month = sorted(incomes_by_month, key=lambda x: x['date'])  # Sắp xếp theo ngày tăng dần
            if sorted_incomes_by_month:
                table_data = []
                for idx, income in enumerate(sorted_incomes_by_month):
                    table_data.append([idx + 1, income['description'], income['amount'], income['date']])
                st.table(pd.DataFrame(table_data, columns=['Index', 'Description', 'Amount (VND)', 'Date']))
            else:
                st.write("No income found for selected month.")

        elif period == 'year':
            selected_year = st.selectbox("Select year:", list(set(income['date'][:4] for income in self.data['income'])))
            incomes_by_year = [income for income in self.data['income'] if income['date'][:4] == selected_year]
            sorted_incomes_by_year = sorted(incomes_by_year, key=lambda x: x['date'])  # Sắp xếp theo ngày tăng dần
            if sorted_incomes_by_year:
                table_data = []
                for idx, income in enumerate(sorted_incomes_by_year):
                    table_data.append([idx + 1, income['description'], income['amount'], income['date']])
                st.table(pd.DataFrame(table_data, columns=['Index', 'Description', 'Amount (VND)', 'Date']))
            else:
                st.write("No income found for selected year.")

        else:
            st.error("Invalid period selection.")

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

    def plot_line_summary(self, period, date_range):
        start_period, end_period = date_range
        expense_summary = self.summarize_expenses(period)
        income_summary = self.summarize_income(period)

        if start_period and end_period:
            expense_summary = {k: v for k, v in expense_summary.items() if start_period <= k <= end_period}
            income_summary = {k: v for k, v in income_summary.items() if start_period <= k <= end_period}

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
            period = st.selectbox("Select period:", ["all", "month", "year"])
            manager.list_income(period)

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
            period = st.selectbox("Select period:", ["all", "day", "month", "year"])
            manager.list_expenses(period)

        elif sub_choice == "Plot Line Summary":
            st.subheader("Plot Line Summary")
            start_year = st.selectbox("Select start year:", [str(year) for year in range(2000, datetime.now().year + 1)])
            start_month = st.selectbox("Select start month:", [f"{start_year}-{str(i).zfill(2)}" for i in range(1, 13)])
            end_year = st.selectbox("Select end year:", [str(year) for year in range(2000, datetime.now().year + 1)])
            end_month = st.selectbox("Select end month:", [f"{end_year}-{str(i).zfill(2)}" for i in range(1, 13)])

            if st.button("Plot"):
                date_range = (start_month, end_month)
                manager.plot_line_summary('month', date_range)

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
