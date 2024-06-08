from tkinter import ttk, messagebox, scrolledtext
from random import choice, shuffle
import database as data
import tkinter as tk
import sys

# TODO: Write up Readme
# TODO: Build login window, think of hashing login password, locking database, and email recovery of account
# TODO: Change visual design to look.... better..
# TODO: Implement a list of predefined websites to choose from who have urls built in & make option to add more
# TODO: Delete selected button


def add_password(event=None):
    """Adds an Entry to the database. Must include a website, email and password for function to work"""

    # Deals with empty fields case, all fields need to be filled or else database will throw error
    if website.get() == "" or email.get() == "" or password.get() == "":
        return messagebox.showinfo("Missing fields", "Information missing")

    # Deals with unique website case, each website must be different or else database throws unique error, websites also
    # Need to be unique as we use them for keeping track of entries, editing and deleting.
    with data.app.app_context():
        db_entries = data.db.session.scalars(data.db.select(data.Passwords)).all()
        websites = [entry.website for entry in db_entries]
        if website.get() in websites:
            return messagebox.showinfo("Already exists", f"An email and password already exists for {website.get()}")

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
        # email.delete(0, tk.END)
        password.delete(0, tk.END)


def generate():
    """Automatically generates a password and displays it in the password entry box in the main window"""

    ls1= ['a','b','c','d','e','f','g','h','j','k','l','p','o','i','u','y','t','r','w','q','s','z','x,','v','n','m']
    ls2=['1','2','3','4','5','6','7','8','9','0']
    ls3=['!','#','$','%','&','*','?','(',')','.']
    generated = []
    for i in range(3):
        generated.extend([choice(ls1), choice(ls1).capitalize(), choice(ls2), choice(ls3)])
        shuffle(generated)
    gen_pass = "".join(generated)

    return pass_variable.set(gen_pass)


def manage_passwords():
    """Window that Reads, Updates and Deletes Passwords, most of the database management is reached from this window"""

    window.deiconify()
    frame = tk.Frame(window, pady=5, padx=5)
    frame.grid(column=0, row=0)
    tk.Label(frame, text="List of Passwords", font=("Arial", 24, 'bold')).grid(column=0, row=0, columnspan=8)

    # Creates the view box for all database entries to render in
    tree_box = ttk.Treeview(frame, columns=("1", '2', '3'), show='headings', selectmode="browse")
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree_box.yview)
    tree_box.configure(yscrollcommand=scrollbar.set)
    # Creates Scrollbar
    scrollbar.grid(column=9, row=1, sticky="N S E W")
    tree_box.grid(column=0, row=1, columnspan=8)

    tree_box.heading('1', text="Website")
    tree_box.heading('2', text="Email")
    tree_box.heading('3', text="Password")

    # Reads all entries in the passwords database and inputs them all into a scrollable text box on screen.
    with data.app.app_context():
        for entry in data.db.session.scalars(data.db.select(data.Passwords).order_by(data.Passwords.website)).all():
            tree_box.insert('', 'end', values=(entry.website, entry.email, entry.password))

    (ttk.Button(frame, text="Edit", command=lambda: edit_selection(tree_box.item(tree_box.focus())['values']))
     .grid(column=0, row=5))
    (ttk.Button(frame, text="Delete", command=lambda: delete(tree_box.item(tree_box.focus())['values']))
     .grid(column=2, row=5))


# Prevents multiple instances of the "Manage passwords" window from appearing by hiding the window on exit. Without this
# If a user was to click the manage passwords button while the window was already up it would open another window
def manage_passwords_event():
    """Hides the password manager window, usually called when another window has been activated"""
    window.withdraw()
    pass


def edit_selection(selected):
    """Edits the selected entry in the database"""
    # Checks for no selection
    if selected == '':
        return messagebox.showinfo("Nothing Selected", "Select an entry to edit")

    # Mostly just window generation for the edit view
    manage_passwords_event()
    edit_window.deiconify()
    frame = tk.Frame(edit_window, pady=5, padx=5)
    frame.grid(column=0, row=0)

    tk.Label(frame, text="Edit or Delete Entry").grid(column=1, row=2, sticky="W E")
    tk.Label(frame, text="Website").grid(column=0, row=3)
    tk.Label(frame, text="Email").grid(column=1, row=3)
    tk.Label(frame, text="Password").grid(column=2, row=3)

    edit_website = tk.Entry(frame)
    edit_email = tk.Entry(frame)
    edit_password = tk.Entry(frame)

    edit_website.insert(tk.END, selected[0])
    edit_email.insert(tk.END, selected[1])
    edit_password.insert(tk.END, selected[2])

    edit_website.grid(column=0, row=4)
    edit_email.grid(column=1, row=4)
    edit_password.grid(column=2, row=4)

    (ttk.Button(frame, text="Confirm", command=lambda: confirm_edit(selected, edit_website, edit_email, edit_password))
     .grid(column=0, row=5))

    edit_window.bind('<Return>', lambda event: confirm_edit(selected, edit_website, edit_email, edit_password))
    edit_window.protocol("WM_DELETE_WINDOW", edit_window_event)


# window operates.
def confirm_edit(selected, edit_website, edit_email, edit_password, event=None):
    """Deals with confirming the changes to the database entry"""
    with data.app.app_context():
        entry = data.db.session.scalar(data.db.select(data.Passwords).where(data.Passwords.website == selected[0]))
        entry.id = entry.id
        entry.website = edit_website.get()
        entry.email = edit_email.get()
        entry.password = edit_password.get()
        data.db.session.commit()
        return edit_window_event()


# hides edit window and un hides manager window, this is a better option then destroying and re-creating these windows
def edit_window_event():
    """Identical to the manage passwords view, but for the edit window, hides it if not in use."""
    edit_window.withdraw()
    return manage_passwords()


def delete(selected):
    """Deletes the selected entry in the database"""
    if selected == '':
        return messagebox.showinfo("No selection", "No entry selected")

    with data.app.app_context():
        entry = data.db.session.scalar(data.db.select(data.Passwords).where(data.Passwords.website == selected[0]))
        data.db.session.delete(entry)
        data.db.session.commit()

        manage_passwords_event()
        manage_passwords()


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
edit_window = tk.Toplevel(root)
edit_window.withdraw()
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
image = tk.PhotoImage(file='mk-logo-copy.png')
canvas.create_image(350, 270, image=image)

mainframe = ttk.Frame(root, width=1000, height=1000, padding=20)
mainframe.grid(column=0, row=0)

ttk.Label(mainframe, text="Enter website: ").grid(column=0, row=0, sticky="W")
ttk.Label(mainframe, text="Enter email/username: ").grid(column=0, row=1, sticky="W")
ttk.Label(mainframe, text="Enter password: ").grid(column=0, row=2, sticky="W")

website = ttk.Entry(mainframe)
email = ttk.Entry(mainframe)
pass_variable = tk.StringVar()
password = ttk.Entry(mainframe, textvariable=pass_variable)

website.grid(column=1, row=0, columnspan=2)
email.grid(column=1, row=1, columnspan=2)
password.grid(column=1, row=2, columnspan=2)
(ttk.Button(mainframe, text="Add", command=add_password)).grid(column=1, row=3)
ttk.Button(mainframe, text="Passwords", command=manage_passwords).grid(column=2, row=3)
ttk.Button(mainframe, text="Generate Random Password", command=generate).grid(column=1, columnspan=2, row=4)

# For building purposes, this is turned off until finished
# root.withdraw()

# Lets you confirm an entry with the enter key
root.bind('<Return>', add_password)
window.protocol("WM_DELETE_WINDOW", manage_passwords_event)
root.mainloop()
