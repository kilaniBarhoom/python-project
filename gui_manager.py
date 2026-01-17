import tkinter 
from tkinter import messagebox, ttk, scrolledtext
from db import DatabaseManager

class LoginWindow:
    def __init__(self):
        self.window = tkinter.Tk()
        self.window.title("Smart Records System - Login")
        self.window.geometry("500x500")

        tkinter.Label(self.window, text="Smart Records System", font=("Arial", 18, "bold")).pack(pady=20)

        tkinter.Label(self.window, text="Username").pack()
        self.username = tkinter.Entry(self.window)
        self.username.pack()

        tkinter.Label(self.window, text="Password").pack()
        self.password = tkinter.Entry(self.window, show="*")
        self.password.pack()

        tkinter.Button(self.window, text="Login", command=self.login).pack(pady=10)
        tkinter.Button(self.window, text="Sign Up", command=self.open_signup).pack()
    
    def login(self):
        username = self.username.get().strip()
        password = self.password.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Fill all fields")
            return
        
        db = DatabaseManager()
        success, user_id, message = db.authenticate_user(username, password)
        
        if success:
            messagebox.showinfo("Success", message)
            self.window.destroy()
            DashboardWindow(user_id, username)
        else:
            messagebox.showerror("Login Failed", message)
            self.password.delete(0, tkinter.END)

    def open_signup(self):
        SignUpWindow(self.window)

    def run(self):
        self.window.mainloop()


class SignUpWindow:
    def __init__(self, parent):
        self.window = tkinter.Toplevel(parent)
        self.window.title("Sign Up")
        self.window.geometry("400x400")
        self.window.grab_set()
        
        tkinter.Label(self.window, text="Create Account", font=("Arial", 14, "bold")).pack(pady=10)

        tkinter.Label(self.window, text="Full Name").pack()
        self.fullname = tkinter.Entry(self.window, width=30)
        self.fullname.pack(pady=5)

        tkinter.Label(self.window, text="Username").pack()
        self.username = tkinter.Entry(self.window, width=30)
        self.username.pack(pady=5)

        tkinter.Label(self.window, text="Password").pack()
        self.password = tkinter.Entry(self.window, show="*", width=30)
        self.password.pack(pady=5)

        tkinter.Label(self.window, text="Confirm Password").pack()
        self.confirm_password = tkinter.Entry(self.window, show="*", width=30)
        self.confirm_password.pack(pady=5)

        tkinter.Button(self.window, text="Create", command=self.create_account, width=20, bg="#4CAF50", fg="white").pack(pady=10)
        tkinter.Button(self.window, text="Cancel", command=self.window.destroy, width=20).pack()

    def create_account(self):
        fullname = self.fullname.get().strip()
        username = self.username.get().strip()
        password = self.password.get()
        confirm = self.confirm_password.get()
        
        if not all([fullname, username, password, confirm]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        if len(username) < 4:
            messagebox.showerror("Error", "Username must be at least 4 characters")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match!")
            return
        
        db = DatabaseManager()
        success, message = db.create_user(username, password, fullname)
        
        if success:
            messagebox.showinfo("Success", message)
            self.window.destroy()
        else:
            messagebox.showerror("Error", message)


class DashboardWindow:
    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username
        self.window = tkinter.Tk()
        self.window.title("Smart Records System - Dashboard")
        self.window.geometry("900x600")

        top_frame = tkinter.Frame(self.window, bg="#4CAF50", height=60)
        top_frame.pack(fill='x')
        top_frame.pack_propagate(False)

        tkinter.Label(
            top_frame,
            text=f"Welcome, {username}!",
            font=("Arial", 14, "bold"),
            bg="#4CAF50",
            fg="white"
        ).pack(side='left', padx=20, pady=15)

        tkinter.Button(
            top_frame,
            text="Logout",
            font=("Arial", 10),
            bg="white",
            command=self.logout
        ).pack(side='right', padx=20)

        button_frame = tkinter.Frame(self.window, bg="#f5f5f5")
        button_frame.pack(fill='x', pady=10)

        tkinter.Button(
            button_frame, 
            text="➕ Add Record",
            font=("Arial", 10, "bold"),
            bg="#4CAF50",
            fg="white",
            cursor="hand2",
            command=self.show_add_record
        ).pack(side="left", padx=10)
        
        tkinter.Button(
            button_frame, 
            text="✏️ Edit Record",
            bg="#2196F3", 
            fg="white",
            font=("Arial", 10),
            cursor="hand2",
            command=self.show_edit_record
        ).pack(side="left", padx=5)
        
        tkinter.Button(
            button_frame, 
            text="🗑️ Delete Record",
            bg="#f44336", 
            fg="white",
            font=("Arial", 10),
            cursor="hand2",
            command=self.delete_record
        ).pack(side="left", padx=5)

        tkinter.Button(
            button_frame, 
            text="🔄 Refresh",
            font=("Arial", 10),
            cursor="hand2",
            command=self.load_records
        ).pack(side="left", padx=5)

        table_frame = tkinter.Frame(self.window)
        table_frame.pack(fill='both', expand=True, padx=20, pady=10)

        columns = ('ID', 'Title', 'Description', 'Category', 'Date', 'Status')
        
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show='headings',
            height=15
        )

        self.tree.heading('ID', text='ID')
        self.tree.heading('Title', text='Title')
        self.tree.heading('Description', text='Description')
        self.tree.heading('Category', text='Category')
        self.tree.heading('Date', text='Date Added')
        self.tree.heading('Status', text='Status')

        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Title', width=150)
        self.tree.column('Description', width=250)
        self.tree.column('Category', width=100)
        self.tree.column('Date', width=120, anchor='center')
        self.tree.column('Status', width=100, anchor='center')

        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        status_frame = tkinter.Frame(self.window, bg="#e0e0e0", height=25)
        status_frame.pack(fill='x', side='bottom')
        status_frame.pack_propagate(False)

        self.status_label = tkinter.Label(
            status_frame,
            text="Ready",
            bg="#e0e0e0",
            font=("Arial", 9)
        )
        self.status_label.pack(side='left', padx=10)

        self.load_records()

        self.window.mainloop()

    def load_records(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        db = DatabaseManager()
        records = db.read_all_records(self.user_id)
        
        for record in records:
            date_str = record[4][:10] if len(record[4]) > 10 else record[4]
            desc_short = record[2][:50] + '...' if len(record[2]) > 50 else record[2]
            
            self.tree.insert('', 'end', values=(
                record[0],
                record[1],
                desc_short,
                record[3],
                date_str,
                record[5]
            ))

        self.status_label.config(text=f"Loaded {len(records)} records")

    def show_add_record(self):
        AddRecordWindow(self.window, self.user_id, self.load_records)

    def show_edit_record(self):
        selected_item = self.tree.selection()

        if not selected_item:
            messagebox.showwarning("Warning", "Please select a record to edit")
            return

        item_id = selected_item[0]
        record_values = self.tree.item(item_id, 'values')

        EditRecordWindow(
            parent=self.window,
            tree=self.tree,
            item_id=item_id,
            record_values=record_values,
            user_id=self.user_id,
            callback=self.load_records
        )

    def delete_record(self):
        selected_item = self.tree.selection()

        if not selected_item:
            messagebox.showwarning("Warning", "Please select a record to delete")
            return

        item = self.tree.item(selected_item[0])
        record_id = item['values'][0]
        record_title = item['values'][1]

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete '{record_title}'?"
        )

        if confirm:
            db = DatabaseManager()
            success, message = db.delete_record(record_id)
            
            if success:
                messagebox.showinfo("Success", message)
                self.load_records()
            else:
                messagebox.showerror("Error", message)

    def logout(self):
        confirm = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if confirm:
            self.window.destroy()
            LoginWindow().run()


class AddRecordWindow:
    def __init__(self, parent, user_id, callback):
        self.user_id = user_id
        self.callback = callback
        self.window = tkinter.Toplevel(parent)
        self.window.title("Add New Record")
        self.window.geometry("500x450")
        self.window.resizable(False, False)
        self.window.grab_set()
        
        tkinter.Label(
            self.window,
            text="Add New Record",
            font=("Arial", 16, "bold")
        ).pack(pady=20)
        
        form_frame = tkinter.Frame(self.window)
        form_frame.pack(padx=30, pady=10, fill='both', expand=True)
        
        tkinter.Label(form_frame, text="Title:", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky='w', pady=10)
        self.title_entry = tkinter.Entry(form_frame, font=("Arial", 11), width=35)
        self.title_entry.grid(row=0, column=1, pady=10, sticky='ew')
        
        tkinter.Label(form_frame, text="Description:", font=("Arial", 11, "bold")).grid(row=1, column=0, sticky='nw', pady=10)
        self.description_text = scrolledtext.ScrolledText(form_frame, font=("Arial", 10), width=35, height=10)
        self.description_text.grid(row=1, column=1, pady=10, sticky='ew')
        
        tkinter.Label(form_frame, text="Category:", font=("Arial", 11, "bold")).grid(row=2, column=0, sticky='w', pady=10)
        self.category_var = tkinter.StringVar()
        category_combo = ttk.Combobox(
            form_frame,
            textvariable=self.category_var,
            font=("Arial", 11),
            width=33,
            values=["General", "Important", "Personal", "Work", "Other"]
        )
        category_combo.grid(row=2, column=1, pady=10, sticky='ew')
        category_combo.set("General")
        
        form_frame.columnconfigure(1, weight=1)
        
        btn_frame = tkinter.Frame(self.window)
        btn_frame.pack(pady=20)
        
        tkinter.Button(
            btn_frame,
            text="Save Record",
            font=("Arial", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            width=15,
            cursor="hand2",
            command=self.save_record
        ).pack(side='left', padx=5)
        
        tkinter.Button(
            btn_frame,
            text="Cancel",
            font=("Arial", 11),
            width=15,
            cursor="hand2",
            command=self.window.destroy
        ).pack(side='left', padx=5)
    
    def save_record(self):
        title = self.title_entry.get().strip()
        description = self.description_text.get('1.0', tkinter.END).strip()
        category = self.category_var.get()
        
        if not title:
            messagebox.showerror("Error", "Title is required!")
            return
        
        if not description:
            messagebox.showerror("Error", "Description is required!")
            return
        
        db = DatabaseManager()
        success, message = db.create_record(self.user_id, title, description, category)
        
        if success:
            messagebox.showinfo("Success", message)
            self.callback()
            self.window.destroy()
        else:
            messagebox.showerror("Error", message)


class EditRecordWindow:
    def __init__(self, parent, tree, item_id, record_values, user_id, callback):
        self.tree = tree
        self.item_id = item_id
        self.record_id = record_values[0]
        self.user_id = user_id
        self.callback = callback

        self.window = tkinter.Toplevel(parent)
        self.window.title("Edit Record")
        self.window.geometry("500x500")
        self.window.resizable(False, False)
        self.window.grab_set()

        tkinter.Label(
            self.window,
            text="Edit Record",
            font=("Arial", 16, "bold")
        ).pack(pady=20)

        form_frame = tkinter.Frame(self.window)
        form_frame.pack(padx=30, pady=10, fill='both', expand=True)

        tkinter.Label(form_frame, text="Title:", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky='w', pady=10)
        self.title_entry = tkinter.Entry(form_frame, font=("Arial", 11), width=35)
        self.title_entry.grid(row=0, column=1, pady=10, sticky='ew')
        self.title_entry.insert(0, record_values[1])

        tkinter.Label(form_frame, text="Description:", font=("Arial", 11, "bold")).grid(row=1, column=0, sticky='nw', pady=10)
        self.description_text = scrolledtext.ScrolledText(form_frame, font=("Arial", 10), width=35, height=10)
        self.description_text.grid(row=1, column=1, pady=10, sticky='ew')
        self.description_text.insert('1.0', record_values[2])

        tkinter.Label(form_frame, text="Category:", font=("Arial", 11, "bold")).grid(row=2, column=0, sticky='w', pady=10)
        self.category_var = tkinter.StringVar(value=record_values[3])
        category_combo = ttk.Combobox(
            form_frame,
            textvariable=self.category_var,
            font=("Arial", 11),
            width=33,
            values=["General", "Important", "Personal", "Work", "Other"]
        )
        category_combo.grid(row=2, column=1, pady=10, sticky='ew')

        tkinter.Label(form_frame, text="Status:", font=("Arial", 11, "bold")).grid(row=3, column=0, sticky='w', pady=10)
        self.status_var = tkinter.StringVar(value=record_values[5])
        status_combo = ttk.Combobox(
            form_frame,
            textvariable=self.status_var,
            font=("Arial", 11),
            width=33,
            values=["Active", "Inactive", "Completed"]
        )
        status_combo.grid(row=3, column=1, pady=10, sticky='ew')

        form_frame.columnconfigure(1, weight=1)

        btn_frame = tkinter.Frame(self.window)
        btn_frame.pack(pady=20)

        tkinter.Button(
            btn_frame,
            text="Update Record",
            font=("Arial", 11, "bold"),
            bg="#2196F3",
            fg="white",
            width=15,
            cursor="hand2",
            command=self.update_record
        ).pack(side='left', padx=5)

        tkinter.Button(
            btn_frame,
            text="Cancel",
            font=("Arial", 11),
            width=15,
            cursor="hand2",
            command=self.window.destroy
        ).pack(side='left', padx=5)

    def update_record(self):
        title = self.title_entry.get().strip()
        description = self.description_text.get('1.0', tkinter.END).strip()
        category = self.category_var.get()
        status = self.status_var.get()

        if not title or not description:
            messagebox.showerror("Error", "All fields are required")
            return

        db = DatabaseManager()
        success, message = db.update_record(self.record_id, title, description, category, status)
        
        if success:
            messagebox.showinfo("Success", message)
            self.callback()
            self.window.destroy()
        else:
            messagebox.showerror("Error", message)


LoginWindow().run()
