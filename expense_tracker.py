import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import sv_ttk
class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("1100x600")
        
        # Apply modern theme
        sv_ttk.set_theme("dark")
        
        # Initialize database
        self.create_database()
        
        # Main container
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            self.main_frame,
            text="Expense Tracker",
            font=("Helvetica", 24)
        )
        title_label.pack(pady=20)
        
        # Input Frame
        input_frame = ttk.LabelFrame(self.main_frame, text="Add New Expense", padding="10")
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Description
        ttk.Label(input_frame, text="Description:").grid(row=0, column=0, padx=5, pady=5)
        self.description_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.description_var).grid(row=0, column=1, padx=5, pady=5)
        
        # Amount
        ttk.Label(input_frame, text="Amount:").grid(row=0, column=2, padx=5, pady=5)
        self.amount_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.amount_var).grid(row=0, column=3, padx=5, pady=5)
        
        # Category
        ttk.Label(input_frame, text="Category:").grid(row=0, column=4, padx=5, pady=5)
        self.category_var = tk.StringVar()
        categories = ["Food", "Transport", "Entertainment", "Bills", "Other"]
        ttk.Combobox(input_frame, textvariable=self.category_var, values=categories).grid(row=0, column=5, padx=5, pady=5)
        
        # Add Button
        ttk.Button(input_frame, text="Add Expense", command=self.add_expense).grid(row=0, column=6, padx=5, pady=5)
        
        # Treeview for expenses
        self.tree = ttk.Treeview(self.main_frame, columns=("ID", "Date", "Description", "Amount", "Category"), show="headings")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Category", text="Category")
        
        # Column widths
        self.tree.column("ID", width=50)
        self.tree.column("Date", width=100)
        self.tree.column("Description", width=200)
        self.tree.column("Amount", width=100)
        self.tree.column("Category", width=100)
        
        # Buttons Frame
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_expense).pack(side=tk.LEFT, padx=5)
        self.update_button = ttk.Button(button_frame, text="Update Selected", command=self.update_expense)
        self.update_button.pack(side=tk.LEFT, padx=5)
        
        # Load expenses
        self.load_expenses()

    def create_database(self):
        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS expenses
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     date TEXT,
                     description TEXT,
                     amount REAL,
                     category TEXT)''')
        conn.commit()
        conn.close()

    def add_expense(self):
        description = self.description_var.get()
        try:
            amount = float(self.amount_var.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid amount")
            return
        category = self.category_var.get()
        
        if not description or not category:
            messagebox.showerror("Error", "Please fill all fields")
            return
            
        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute("INSERT INTO expenses (date, description, amount, category) VALUES (?, ?, ?, ?)",
                 (datetime.now().strftime("%Y-%m-%d"), description, amount, category))
        conn.commit()
        conn.close()
        
        self.clear_inputs()
        self.load_expenses()

    def load_expenses(self):
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute("SELECT * FROM expenses ORDER BY date DESC")
        expenses = c.fetchall()
        
        for expense in expenses:
            self.tree.insert("", "end", values=expense)
            
        conn.close()

    def delete_expense(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an expense to delete")
            return
            
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this expense?"):
            expense_id = self.tree.item(selected_item)['values'][0]
            conn = sqlite3.connect('expenses.db')
            c = conn.cursor()
            c.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
            conn.commit()
            conn.close()
            self.load_expenses()

    def update_expense(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select an expense to update")
            return
            
        expense = self.tree.item(selected_item)['values']
        self.description_var.set(expense[2])
        self.amount_var.set(expense[3])
        self.category_var.set(expense[4])
        
        # Delete the old entry
        self.delete_expense()

    def clear_inputs(self):
        self.description_var.set("")
        self.amount_var.set("")
        self.category_var.set("")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop() 