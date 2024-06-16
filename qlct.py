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
            st.error("Chi muc khong hop le")

    def delete_income(self, index):
        if 0 <= index < len(self.data['income']):
            del self.data['income'][index]
            self.save_data()
        else:
            st.error("Chi muc khong hop le")

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
        st.error("Danh muc khong ton tai!")

    def delete_category(self, category_name):
        self.data['categories'] = [cat for cat in self.data['categories'] if cat['name'] != category_name]
        self.data['expenses'] = [expense for expense in self.data['expenses'] if expense['category'] != category_name]
        self.save_data()

    def add_expense(self, amount, description, category, date):
        if category not in [cat['name'] for cat in self.data['categories'] if isinstance(cat, dict)]:
            st.error("Danh muc khong ton tai!")
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
            st.error("Chi muc khong hop le")

    def delete_expense(self, index):
        if 0 <= index < len(self.data['expenses']):
            del self.data['expenses'][index]
            self.save_data()
        else:
            st.error("Chi muc khong hop le")

    def list_expenses(self, period=None):
        if period == 'Toan bo':
            table_data = []
            sorted_expenses = sorted(self.data['expenses'], key=lambda x: x['date'])  
            for idx, expense in enumerate(sorted_expenses):
                table_data.append([idx + 1, expense['description'], expense['amount'], expense['category'], expense['date']])
            st.table(pd.DataFrame(table_data, columns=['So thu tu', 'Ghi chu', 'So tien (VND)', 'Danh muc', 'Ngay']))

        elif period == 'Ngay':
            selected_date = st.date_input("Ngay:")
            expenses_by_day = [expense for expense in self.data['expenses'] if expense['date'] == selected_date.strftime('%Y-%m-%d')]
            if expenses_by_day:
                table_data = []
                for idx, expense in enumerate(expenses_by_day):
                    table_data.append([idx + 1, expense['description'], expense['amount'], expense['category'], expense['date']])
                st.table(pd.DataFrame(table_data, columns=['So thu tu', 'Ghi chu', 'So tien (VND)', 'Danh muc', 'Ngay']))
            else:
                st.write("Khong tim thay thong tin chi tieu trong ngay duoc chon.")
        
        elif period == 'Thang':
            selected_year = st.selectbox("Nam:", list(set(expense['date'][:4] for expense in self.data['expenses'])))
            expenses_by_year = [expense for expense in self.data['expenses'] if expense['date'][:4] == selected_year]
            selected_month = st.selectbox("Thang:", [str(i).zfill(2) for i in range(1, 13)])
            expenses_by_month = [expense for expense in expenses_by_year if expense['date'][5:7] == selected_month]
            sorted_expenses_by_month = sorted(expenses_by_month, key=lambda x: x['date'])  
            if sorted_expenses_by_month:
                table_data = []
                for idx, expense in enumerate(sorted_expenses_by_month):
                    table_data.append([idx + 1, expense['description'], expense['amount'], expense['category'], expense['date']])
                st.table(pd.DataFrame(table_data, columns=['So thu tu', 'Ghi chu', 'So tien (VND)', 'Danh muc', 'Ngay']))
            else:
                st.write("Khong tim thay thong tin chi tieu trong thang duoc chon.")

        elif period == 'Nam':
            selected_year = st.selectbox("Nam:", list(set(expense['date'][:4] for expense in self.data['expenses'])))
            expenses_by_year = [expense for expense in self.data['expenses'] if expense['date'][:4] == selected_year]
            sorted_expenses_by_year = sorted(expenses_by_year, key=lambda x: x['date'])  
            if sorted_expenses_by_year:
                table_data = []
                for idx, expense in enumerate(sorted_expenses_by_year):
                    table_data.append([idx + 1, expense['description'], expense['amount'], expense['category'], expense['date']])
                st.table(pd.DataFrame(table_data, columns=['So thu tu', 'Ghi chu', 'So tien (VND)', 'Danh muc', 'Ngay']))
            else:
                st.write("Khong tim thay thong tin chi tieu trong nam duoc chon.")

        else:
            st.error("Giai doan duoc chon khong hop le.")

    def list_income(self, period=None):
        if period == 'Toan bo':
            table_data = []
            sorted_income = sorted(self.data['income'], key=lambda x: x['date'])  
            for idx, income in enumerate(sorted_income):
                table_data.append([idx + 1, income['description'], income['amount'], income['date']])
            st.table(pd.DataFrame(table_data, columns=['So thu tu', 'Loai thu nhap', 'So tien (VND)', 'Ngay']))
        
        elif period == 'Thang':
            selected_year = st.selectbox("Thang:", list(set(income['date'][:4] for income in self.data['income'])))
            incomes_by_year = [income for income in self.data['income'] if income['date'][:4] == selected_year]
            selected_month = st.selectbox("Nam:", [str(i).zfill(2) for i in range(1, 13)])
            incomes_by_month = [income for income in incomes_by_year if income['date'][5:7] == selected_month]
            sorted_incomes_by_month = sorted(incomes_by_month, key=lambda x: x['date'])  
            if sorted_incomes_by_month:
                table_data = []
                for idx, income in enumerate(sorted_incomes_by_month):
                    table_data.append([idx + 1, income['description'], income['amount'], income['date']])
                st.table(pd.DataFrame(table_data, columns=['So thu tu', 'Loai thu nhap', 'So tien (VND)', 'Ngay']))
            else:
                st.write("Khong tim thay thong tin thu nhap trong thang duoc chon.")

        elif period == 'Nam':
            selected_year = st.selectbox("Nam:", list(set(income['date'][:4] for income in self.data['income'])))
            incomes_by_year = [income for income in self.data['income'] if income['date'][:4] == selected_year]
            sorted_incomes_by_year = sorted(incomes_by_year, key=lambda x: x['date'])  
            if sorted_incomes_by_year:
                table_data = []
                for idx, income in enumerate(sorted_incomes_by_year):
                    table_data.append([idx + 1, income['description'], income['amount'], income['date']])
                st.table(pd.DataFrame(table_data, columns=['So thu tu', 'Loai thu nhap', 'So tien (VND)', 'Ngay']))
            else:
                st.write("Khong tim thay thong tin thu nhap trong nam duoc chon.")

        else:
            st.error("Giai doan duoc chon khong hop le.")

    def summarize_expenses(self, period):
        summary = {}
        for expense in self.data['expenses']:
            date = datetime.strptime(expense['date'], '%Y-%m-%d')
            if period == 'Ngay':
                key = date.strftime('%Y-%m-%d')
            elif period == 'Thang':
                key = date.strftime('%Y-%m')

            if key not in summary:
                summary[key] = 0
            summary[key] += expense['amount']
        
        return summary

    def summarize_income(self, period):
        summary = {}
        for income in self.data['income']:
            date = datetime.strptime(income['date'], '%Y-%m-%d')
            if period == 'Ngay':
                key = date.strftime('%Y-%m-%d')
            elif period == 'Thang':
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

        sorted_expense_summary = sorted(expense_summary.items(), key=lambda x: x[0])
        sorted_income_summary = sorted(income_summary.items(), key=lambda x: x[0])

        dates = [item[0] for item in sorted_expense_summary]
        expense_amounts = [item[1] for item in sorted_expense_summary]
        income_amounts = [income_summary.get(date, 0) for date in dates]

        plt.figure(figsize=(10, 5))
        plt.plot(dates, expense_amounts, marker='o', label='Chi tieu')
        plt.plot(dates, income_amounts, marker='o', label='Thu nhap')
        plt.xlabel(f'Thoi gian ({period})')
        plt.ylabel('So tien (VND)')
        plt.title(f'Thong ke chi tieu và thu nhap theo {period.capitalize()}')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(plt)


    def plot_pie_summary(self, period, specific_period):
        category_summary = {}
        for expense in self.data['expenses']:
            date = datetime.strptime(expense['date'], '%Y-%m-%d')
            if period == 'Ngay' and specific_period == date.strftime('%Y-%m-%d'):
                key = expense['category']
            elif period == 'Thang' and specific_period == date.strftime('%Y-%m'):
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
            plt.title(f'Thong ke chi tieu theo danh muc ({period.capitalize()})')
            st.pyplot(plt)

def main():
    manager = ExpenseManager()
    
    st.title("Quan li chi tieu")

    menu = ["Thu nhap", "Danh muc chi tieu", "Chi tieu", "Thong ke"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Thu nhap":
        sub_menu = ["Tao", "Cap nhat", "Xoa", "Xem danh sach thu nhap"]
        sub_choice = st.sidebar.selectbox("Cac chuc nang", sub_menu)
        
        if sub_choice == "Tao":
            st.subheader("Tao thu nhap")
            amount = st.number_input("So tien:", min_value=0, step=1)
            description = st.text_input("Loai thu nhap:")
            date = st.date_input("Ngay:")
            if st.button("Tao thu nhap"):
                manager.add_income(amount, description, date)
                st.success("Ban da tao thanh cong!")

        elif sub_choice == "Cap nhat":
            st.subheader("Cap nhat thu nhap")
            incomes = [f"{idx + 1}. {inc['description']} - {inc['amount']} VND - {inc['date']}" for idx, inc in enumerate(manager.data['income'])]
            index = st.selectbox("Thu nhap ban muon thay doi:", range(len(incomes)), format_func=lambda x: incomes[x])
            amount = st.number_input("So tien:", min_value=0.0, step=0.01)
            description = st.text_input("Loai thu nhap:")
            date = st.date_input("Ngay:")
            if st.button("Cap nhat thu nhap"):
                manager.update_income(index, amount, description, date)
                st.success("Ban da cap nhat thanh cong!")

        elif sub_choice == "Xoa":
            st.subheader("Xoa thu nhap")
            incomes = [f"{idx + 1}. {inc['description']} - {inc['amount']} VND - {inc['date']}" for idx, inc in enumerate(manager.data['income'])]
            index = st.selectbox("Thu nhap ban muon xoa:", range(len(incomes)), format_func=lambda x: incomes[x])
            if st.button("Xoa thu nhap"):
                manager.delete_income(index)
                st.success("Ban da xoa thanh cong!")

        elif sub_choice == "Xem danh sach thu nhap":
            st.subheader("Xem danh sach thu nhap")
            period = st.selectbox("Loc theo:", ["Toan bo", "Thang", "Nam"])
            manager.list_income(period)

    elif choice == "Danh muc chi tieu":
        sub_menu = ["Tao", "Cap nhat", "Xoa"]
        sub_choice = st.sidebar.selectbox("Cac chuc nang", sub_menu)
        
        if sub_choice == "Tao":
            st.subheader("Them danh muc")
            category = st.text_input("Ten danh muc:")
            description = st.text_input("Mo ta:")
            if st.button("Them danh muc"):
                manager.add_category(category, description)
                st.success("Ban da tao thanh cong!")

        elif sub_choice == "Cap nhat":
            st.subheader("Cap nhat danh muc")
            if all(isinstance(cat, dict) and 'name' in cat for cat in manager.data['categories']):
                old_category = st.selectbox("Danh muc ban muon thay doi:", [cat['name'] for cat in manager.data['categories']])
                new_category = st.text_input("Ten danh muc moi:")
                new_description = st.text_input("Mo ta cho danh muc moi:")
                if st.button("Cap nhat danh muc"):
                    manager.update_category(old_category, new_category, new_description)
                    st.success("Ban da cap nhat thanh cong!")
            else:
                st.error("Du lieu danh muc khong hop le.")

        elif sub_choice == "Xoa":
            st.subheader("Xoa danh muc")
            if all(isinstance(cat, dict) and 'name' in cat for cat in manager.data['categories']):
                category = st.selectbox("Chon danh muc de xoa:", [cat['name'] for cat in manager.data['categories']])
                if st.button("Xoa danh muc"):
                    manager.delete_category(category)
                    st.success("Ban da xoa thanh cong!")
            else:
                st.error("Du lieu danh muc khong hop le.")

    elif choice == "Chi tieu":
        sub_menu = ["Tao", "Cap nhat", "Xoa"]
        sub_choice = st.sidebar.selectbox("Cac chuc nang", sub_menu)
        
        if sub_choice == "Tao":
            st.subheader("Tao chi tieu")
            amount = st.number_input("So tien:", min_value=0, step=1)
            description = st.text_input("Ghi chu:")
            date = st.date_input("Ngay:")
            if all(isinstance(cat, dict) and 'name' in cat for cat in manager.data['categories']):
                category = st.selectbox("Chon danh muc:", [cat['name'] for cat in manager.data['categories']])
                if st.button("Tao chi tieu"):
                    manager.add_expense(amount, description, category, date)
                    st.success("Ban da tao thanh cong!")
            else:
                st.error("Du lieu danh muc khong hop le.")

        elif sub_choice == "Cap nhat":
            st.subheader("Cap nhat chi tieu")
            expenses = [f"{idx + 1}. {exp['description']} - {exp['amount']} VND - {exp['category']} - {exp['date']}" for idx, exp in enumerate(manager.data['expenses'])]
            index = st.selectbox("Chi tieu ban muon thay doi:", range(len(expenses)), format_func=lambda x: expenses[x])
            amount = st.number_input("So tien:", min_value=0.0, step=0.01)
            description = st.text_input("Ghi chu:")
            date = st.date_input("Ngay:")
            if all(isinstance(cat, dict) and 'name' in cat for cat in manager.data['categories']):
                category = st.selectbox("Danh muc:", [cat['name'] for cat in manager.data['categories']])
                if st.button("Cap nhat chi tieu"):
                    manager.update_expense(index, amount, description, category, date)
                    st.success("Ban da cap nhat thanh cong!")
            else:
                st.error("Du lieu danh muc khong hop le.")

        elif sub_choice == "Xoa":
            st.subheader("Xoa chi tieu")
            expenses = [f"{idx + 1}. {exp['description']} - {exp['amount']} VND - {exp['category']} - {exp['date']}" for idx, exp in enumerate(manager.data['expenses'])]
            index = st.selectbox("Chi tieu ban muon xoa:", range(len(expenses)), format_func=lambda x: expenses[x])
            if st.button("Xoa chi tieu"):
                manager.delete_expense(index)
                st.success("Ban da xoa thanh cong!")

    elif choice == "Thong ke":
        sub_menu = ["Danh sach chi tieu", "Thong ke thu nhap va chi tieu theo thoi gian", "Thong ke chi tieu theo danh muc"]
        sub_choice = st.sidebar.selectbox("Cac chuc nang", sub_menu)
        
        if sub_choice == "Danh sach chi tieu":
            st.subheader("Danh sach chi tieu")
            period = st.selectbox("Loc theo:", ["Toan bo", "Ngay", "Thang", "Nam"])
            manager.list_expenses(period)

        elif sub_choice == "Thong ke thu nhap va chi tieu theo thoi gian":
            st.subheader("Thong ke thu nhap va chi tieu theo thoi gian")
            start_year = st.selectbox("Bat dau tu nam:", [str(year) for year in range(2000, datetime.now().year + 1)])
            start_month = st.selectbox("Bat dau tu thang:", [f"{start_year}-{str(i).zfill(2)}" for i in range(1, 13)])
            end_year = st.selectbox("Ket thuc o nam:", [str(year) for year in range(2000, datetime.now().year + 1)])
            end_month = st.selectbox("Ket thuc o thang:", [f"{end_year}-{str(i).zfill(2)}" for i in range(1, 13)])

            if st.button("Hien thi"):
                date_range = (start_month, end_month)
                manager.plot_line_summary('Thang', date_range)

        elif sub_choice == "Thong ke chi tieu theo danh muc":
            st.subheader("Thong ke chi tieu theo danh muc")
            period = st.selectbox("Loc theo:", ["Ngay", "Thang"])
            specific_period = None

            if period == 'Ngay':
                specific_period = st.date_input("Ngay:").strftime('%Y-%m-%d')
            elif period == 'Thang':
                specific_period = st.selectbox("Thang:", [f"{datetime.now().year}-{str(i).zfill(2)}" for i in range(1, 13)])

            if st.button("Hien thi"):
                manager.plot_pie_summary(period, specific_period)

if __name__ == "__main__":
    main()
