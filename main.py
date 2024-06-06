import sys
from tkinter import ttk, messagebox, scrolledtext
import tkinter as tk
import database as data


# TODO: Actually makes this something I like, because currently its design is ver undesirable.
# TODO: Deal with unique website entries
def add_password(event=None):
    if website.get() == "" or email.get() == "" or password.get() == "":
        return messagebox.showinfo("Missing fields", "Information missing")

    new_entry = data.Passwords(
        website=website.get().lower(),
        email=email.get().lower(),
        password=password.get()
    )
    with data.app.app_context():
        data.db.session.add(new_entry)
        data.db.session.commit()

        # Clears the inputs after commiting a password
        website.delete(0, tk.END)
        email.delete(0, tk.END)
        password.delete(0, tk.END)


# TODO: GIGA SPAGHETTI CODES!!!! NEEDS SERIOUS REFACTORING, CLEANING, COMBINING... But... it works at the moment
# TODO: Handle when nothing is selected and user clicks on edit
# TODO: Add edit password feature
def edit(id):
    if id == '':
        return messagebox.showinfo("Missing fields", "Information missing")

    # TODO: Find a way not to destory the window everytime I confirm a edit, but just hide the window, like the how the
    # window operates.
    def second_event(event=None):
        with data.app.app_context():
            entry = data.db.session.scalar(data.db.select(data.Passwords).where(data.Passwords.website == id[0]))
            entry.id = entry.id
            entry.website = website.get()
            entry.email = email.get()
            entry.password = password.get()
            data.db.session.commit()
            window.destroy()
            return manage_passwords()

    # Destroys edit window and replaces it with manager window
    def edit_event():
        window.destroy()
        return manage_passwords()

    disable_event()
    window = tk.Toplevel()
    frame = tk.Frame(window, pady=5, padx=5)
    frame.grid(column=0, row=0)

    tk.Label(frame, text="Edit or Delete Entry").grid(column=1, row=2, sticky="W E")
    tk.Label(frame, text="Website").grid(column=0, row=3)
    tk.Label(frame, text="Email").grid(column=1, row=3)
    tk.Label(frame, text="Password").grid(column=2, row=3)

    website = tk.Entry(frame)
    email = tk.Entry(frame)
    password = tk.Entry(frame)

    website.insert(tk.END, id[0])
    email.insert(tk.END, id[1])
    password.insert(tk.END, id[2])

    website.grid(column=0, row=4)
    email.grid(column=1, row=4)
    password.grid(column=2, row=4)

    ttk.Button(frame, text="Confirm", command=second_event).grid(column=0, row=5)

    window.protocol("WM_DELETE_WINDOW", edit_event)
    window.bind('<Return>', second_event)

# TODO: Hand the case when delete is clicked but an entry isnt selected.
def delete(website):
    if id == '':
        return messagebox.showinfo("Missing fields", "Information missing")

    with data.app.app_context():
        entry = data.db.session.scalar(data.db.select(data.Passwords).where(data.Passwords.website == website))
        data.db.session.delete(entry)
        data.db.session.commit()

        disable_event()
        manage_passwords()


# Prevents multiple instances of the "Manage passwords" window from appearing by hiding the window on exit. Without this
# If a user was to click the manage passwords button while the window was already up it would open another window
def disable_event():
    window.withdraw()
    pass


# TODO: once this is fully functional, think of a way to imporve its design... its labouress at the moment.
def manage_passwords():
    """Reads, Updates and Deletes Passwords"""

    window.deiconify()
    frame = tk.Frame(window, pady=5, padx=5)
    frame.grid(column=0, row=0)
    tk.Label(frame, text="List of Passwords", font=("Arial", 24, 'bold')).grid(column=0, row=0, columnspan=8)

    tree_box = ttk.Treeview(frame, columns=("1", '2', '3'), show='headings', selectmode="browse")
    tree_box.grid(column=0, row=1, columnspan=8)

    tree_box.heading('1', text="Website")
    tree_box.heading('2', text="Email")
    tree_box.heading('3', text="Password")

    # TODO: SORT passwords to display in alphabetical order
    # Reads all entries in the passwords database and inputs them all into a scrollable text box on screen.
    with data.app.app_context():
        for entry in data.db.session.scalars(data.db.select(data.Passwords)).all():
            tree_box.insert('', 'end', values=(entry.website, entry.email, entry.password))

    ttk.Button(frame, text="Edit", command=lambda: edit(tree_box.item(tree_box.focus())['values'])).grid(column=0, row=5)
    ttk.Button(frame, text="Delete", command=lambda: delete(tree_box.item(tree_box.focus())['values'][0])).grid(column=2, row=5)

# For login features, currently disabled while building out the database functions
# def login():
#     if entry1.get() == 'user' and entry2.get() == 'asdf':
#         root.deiconify()
#         top.destroy()
#
#
# def close():
#     top.destroy()
#     root.destroy()
#     sys.exit()


# ----------------------------------------GUI--------------------------------------------
root = tk.Tk()
window = tk.Toplevel(root)
window.withdraw()

# top = tk.Toplevel()
# top.title("Login to MK-Pass")
root.title("MK - Password Manager")

# LOGIN WINDOW--------------------------------------
# login_canvas = tk.Canvas(top, height=200, width=200)
# login_canvas.grid(column=0, row=0)
#
# login_frame = ttk.Frame(top, width=1000, height=1000, padding=20)
# login_frame.grid(column=0, row=0)
#
# ttk.Label(login_frame, text="Enter Username", padding=5).grid(column=0, row=0, sticky="W")
# ttk.Label(login_frame, text="Enter Password", padding=5).grid(column=0, row=2, sticky="W")
# entry1= ttk.Entry(login_frame)
# entry2= ttk.Entry(login_frame)
# button1 = ttk.Button(login_frame, text="Login", command=login)
# button2 = tk.Button(login_frame, text="Close", command=close)
#
# entry1.grid(column=0, row=1, columnspan=2)
# entry2.grid(column=0, row=3, columnspan=2)
# button1.grid(column=0, row=4, sticky="W")
# button2.grid(column=1, row=4)

# MAIN WINDOW------------------------------------------
canvas = tk.Canvas(height=555, width=700)
canvas.grid(column=0, row=0)
image = tk.PhotoImage(file='') #mk-logo-copy.png
canvas.create_image(350, 270, image=image)

mainframe = ttk.Frame(root, width=1000, height=1000, padding=20)
mainframe.grid(column=0, row=0)

ttk.Label(mainframe, text="Enter website: ").grid(column=0, row=0, sticky="W")
ttk.Label(mainframe, text="Enter email/username: ").grid(column=0, row=1, sticky="W")
ttk.Label(mainframe, text="Enter password: ").grid(column=0, row=2, sticky="W")

website = ttk.Entry(mainframe)
email = ttk.Entry(mainframe)
password = ttk.Entry(mainframe)

website.grid(column=1, row=0, columnspan=2)
email.grid(column=1, row=1, columnspan=2)
password.grid(column=1, row=2, columnspan=2)
(ttk.Button(mainframe, text="Add", command=add_password)).grid(column=1, row=3)
ttk.Button(mainframe, text="Passwords", command=manage_passwords).grid(column=2, row=3)

# For building purposes, this is turned off until finished
# root.withdraw()

# Lets you confirm an entry with the enter key
root.bind('<Return>', add_password)
window.protocol("WM_DELETE_WINDOW", disable_event)
root.mainloop()
