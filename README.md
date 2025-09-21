# Expense_Tracker-Django-
A full-fledged Expense Tracker web application built with Django. Includes user authentication, transaction management, categories, budgets, reports, and analytics with charts. Designed to help users efficiently manage and track their personal finances.

# 💰 Expense Tracker

A full-fledged Expense Tracker web application built with **Django** that helps users manage their finances effectively.  
Track your income and expenses, set budgets, view reports, and analyze spending habits with ease.

---

## 🚀 Features
- **User Authentication** – Sign up, login, and secure access.
- **Dashboard** – Overview of income, expenses, and balance.
- **Add/Edit/Delete Transactions** – Manage income and expense records.
- **Category Management** – Organize transactions with categories.
- **Budget Setting with Alerts** – Define monthly budgets and get notified when exceeded.
- **Recurring Transactions** – Support for repeat expenses/incomes.
- **Reports & Analytics** – Visual insights with interactive charts.
- **Search & Filter** – Quickly find specific transactions.
- **Export/Import Data** – Download or upload transactions in CSV format.

---

## 🛠️ Tech Stack
- **Backend:** Django (Python)
- **Database:** SQLite (default) / PostgreSQL (optional)
- **Frontend:** HTML, CSS, Bootstrap
- **Charts & Reports:** Chart.js / Matplotlib
- **Authentication:** Django Authentication System

---

## 📦 Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/expense-tracker.git
   cd expense-tracker

2.Create and activate a virtual environment:

     python -m venv venv
    source venv/bin/activate   # On Linux/Mac
    venv\Scripts\activate      # On Windows

3. Install dependencies:
   
        pip install -r requirements.txt

5. Run migrations:
    
          python manage.py migrate
 
7. Create a superuser:

       python manage.py createsuperuser
 
    
9. Start the server:

        python manage.py runserver

      
11. Open in browser:

        http://127.0.0.1:8000/

