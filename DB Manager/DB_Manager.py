import tkinter as tk
import sqlite3

conn = sqlite3.connect("tutorial.db")
cursor = conn.cursor()


add_user_query = """CREATE TABLE IF NOT EXISTS users (
                            id integer PRIMARY KEY AUTOINCREMENT,
                            name text NOT NULL,
                            password text NOT NULL,
                            email text NOT NULL,
                            age integer,
                            gender text,
                            address text
                ); """  
cursor.execute(add_user_query)
conn.commit()


def center_window(width, height):
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')


class WelcomeWindow(tk.Frame):
    def __init__(self, master):
        super().__init__()
        self.master = master
        self.master.title("Welcome")
        center_window(240, 120)
        
        login_button = tk.Button(self, text="Login", width=10, command=self.open_login_window)
        login_button.pack(padx=20, pady=(20, 10))
        
        register_button = tk.Button(self, text="Register", width=10, command=self.open_register_window)
        register_button.pack(pady=10)
        self.pack()
        
    def open_login_window(self):
        for widget in self.winfo_children(): 
            widget.destroy()
        self.destroy()
        LoginWindow(self.master)
        
    def open_register_window(self):
        for widget in self.winfo_children(): 
            widget.destroy()
        self.destroy()
        RegisterWindow(self.master)


class LoginWindow(tk.Frame):
    def __init__(self, master):
        super().__init__()
        self.master = master
        self.master.title("Login")
        self.master.resizable(False, False)
        center_window(240, 150)
        
        tk.Label(self, text="Username:").grid(row=0, column=0)
        self.username_entry = tk.Entry(self)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)
        
        tk.Label(self, text="Password:").grid(row=1, column=0)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)
        
        submit_button = tk.Button(self, text="Submit", width=8, command=self.submit)
        submit_button.grid(row=2, column=1, sticky="e", padx=10, pady=(10, 0))

        submit_button = tk.Button(self, text="Back", width=8, command=self.back)
        submit_button.grid(row=2, column=0, sticky="w", padx=10, pady=(10, 0))
        self.pack()
            
    def submit(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        cursor.execute("SELECT * FROM users WHERE name=? AND password=?", (username, password))
        user = cursor.fetchone()

        if user:
            # Logged in
            (self.master)
            self.destroy()
        else:
            print("You have typed in the wrong details")
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)


    def back(self):
        for widget in self.winfo_children(): 
            widget.destroy()
        self.destroy()
        WelcomeWindow(self.master)


class RegisterWindow(tk.Frame):
    def __init__(self, master):
        super().__init__()
        self.master = master
        self.master.title("Register")
        self.master.resizable(False, False)
        center_window(320, 350)
        
        tk.Label(self, text="Name:").grid(row=0, column=0, sticky="w")
        self.first_name_entry = tk.Entry(self, width=26)
        self.first_name_entry.grid(row=0, column=1, padx=10, pady=10, sticky="e")
        
        tk.Label(self, text="Password:").grid(row=2, column=0, sticky="w")
        self.password_entry = tk.Entry(self, show="*", width=26)
        self.password_entry.grid(row=2, column=1, padx=10, pady=10, sticky="e")
        
        tk.Label(self, text="Email:").grid(row=3, column=0, sticky="w")
        self.email_entry = tk.Entry(self, width=26)
        self.email_entry.grid(row=3, column=1, padx=10, pady=10, sticky="e")
        
        tk.Label(self, text="Gender:").grid(row=4, column=0, sticky="w")
        self.gender_entry = tk.Entry(self, width=10)
        self.gender_entry.grid(row=4, column=1, padx=10, pady=10, sticky="e")
        
        tk.Label(self, text="Age:").grid(row=5, column=0, sticky="w")
        self.age_entry = tk.Entry(self, width=10)
        self.age_entry.grid(row=5, column=1, padx=10, pady=10, sticky="e")
        
        tk.Label(self, text="Address:").grid(row=6, column=0, sticky="w")
        self.address_entry = tk.Text(self, width=20, height=3)
        self.address_entry.grid(row=6, column=1, padx=10, pady=10, sticky="e")
        
        submit_button = tk.Button(self, text="Submit", width=8, command=self.submit)
        submit_button.grid(row=7, column=1, padx=10, pady=10, sticky="e")

        submit_button = tk.Button(self, text="Back", width=8, command=self.back)
        submit_button.grid(row=7, column=0, sticky="w", padx=10, pady=(10, 10))
        self.pack()
        
    def submit(self):
        insert_user_data = """INSERT INTO users(name, password, email, age, gender, address)
                              VALUES (?, ?, ?, ?, ?, ?)"""
        
        user_data = (self.first_name_entry.get().strip(), 
                    self.password_entry.get().strip(), 
                    self.email_entry.get().strip(), 
                    self.age_entry.get().strip(),
                    self.gender_entry.get().strip(), 
                    self.address_entry.get(1.0, tk.END).strip())
        
        cursor.execute(insert_user_data, user_data)
        conn.commit()

        self.destroy()
        MainWindow(self.master)


    def back(self):
        for widget in self.winfo_children(): 
            widget.destroy()
        self.destroy()
        WelcomeWindow(self.master)


class MainWindow(tk.Frame):
    def __init__(self, master):
        super().__init__()
        self.master = master
        center_window(600, 400)

        self.generateUserList()
        self.pack()

    def generateUserList(self):
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()

        columns = ["ID", "Name", "Password", "Email", "Age", "Gender", "Address"]
        column_widths = [5, 10, 10, 30, 5, 10, 20]
        for col_index, col_name in enumerate(columns):
            label = tk.Label(self, text=col_name, padx=5, pady=5)
            label.grid(row=0, column=col_index)

        # Iterate over users and create Entry widgets
        for row_index, user in enumerate(users):
            for col_index, value in enumerate(user):
                entry = tk.Entry(self, width=column_widths[col_index], disabledforeground="black")
                entry.grid(row=row_index + 1, column=col_index)
                entry.insert(0, str(value))  # Insert user data into Entry widget
                entry.configure(state="disabled")


root = tk.Tk()
root.eval('tk::PlaceWindow . center')
WelcomeWindow(root)
root.mainloop()