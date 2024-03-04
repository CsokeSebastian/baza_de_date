import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3

conn = sqlite3.connect('materials.db')
c = conn.cursor()

def add_material():
    try:
        table_materials = (""" CREATE TABLE IF NOT EXISTS materials(
                           ID INTEGER PRIMARY KEY NOT NULL,
                           Name TEXT,
                           Unit TEXT, 
                           Price TEXT);""")
    
        c.execute(table_materials)
        c.execute("INSERT INTO materials VALUES (?, ?, ?, ?)",
                (None, name_entry.get(), unit_entry.get(), float(price_entry.get())))
        conn.commit()
        messagebox.showinfo("Success", "Material added successfully")
        clear_entries()
        refresh_materials()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Material already exists")
    except ValueError:
        messagebox.showerror("Error", "Invalid price")

def search_materials():
    search_term = search_entry.get()
    print("Searching for:", search_term)
    for item in tree.get_children():
        tree.delete(item)
    c.execute("SELECT * FROM materials WHERE Name LIKE '%' || ? || '%'", (search_term,))
    search_results = c.fetchall()
    for material in search_results:
        tree.insert('', tk.END, values=material)

def clear_entries():
    name_entry.delete(0, tk.END)
    unit_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)
    search_entry.delete(0, tk.END)
    new_price_entry.delete(0, tk.END)
    refresh_materials()

def refresh_materials():
    for item in tree.get_children():
        tree.delete(item)
    c.execute("SELECT ID, Name, Unit, Price FROM materials")
    for row in c.fetchall():
        tree.insert('', tk.END, values=row)
    tree.selection_remove(tree.selection())
    name_entry.delete(0, tk.END)
    unit_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)

def on_item_selected(event):
    name_entry.delete(0, tk.END)
    unit_entry.delete(0, tk.END)
    price_entry.delete(0, tk.END)
    for selected_item in tree.selection():
        item = tree.item(selected_item)
        ID, Name, Unit, Price = item['values']
        print(f"Selected ID: {ID}")
        name_entry.insert(tk.END, Name)
        unit_entry.insert(tk.END, Unit)
        price_entry.insert(tk.END, Price)

def update_selected_material():
    try:
        selected_item = tree.selection()[0]
        ID = tree.item(selected_item)['values'][0]
        updated_name = name_entry.get()
        updated_unit = unit_entry.get()
        updated_price = new_price_entry.get()
        update_sql = """UPDATE materials 
                                    SET Name = ?,
                                    Unit = ?,
                                    Price = ?
                                    WHERE ID = ?"""
        c.execute(update_sql, (updated_name, updated_unit, updated_price, ID))
        conn.commit()
        print(updated_name, updated_unit, updated_price, ID)
        refresh_materials()
        messagebox.showinfo("Success", "Material updated successfully") 
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

def delete_selected_material():
    selected_item = tree.selection()[0]
    ID = tree.item(selected_item)['values'][0]
    print(f"Deleting material with ID: {ID}")
    c.execute("DELETE FROM materials WHERE ID=?", (ID,))
    conn.commit()
    refresh_materials()
    messagebox.showinfo("Success", "Material deleted successfully")

# GUI setup
root = tk.Tk()
root.title("Materials Database")
root.geometry("1000x600")
root.resizable(True, True)
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(1, weight=1)
selected_id = tk.StringVar(root)

columns = ('ID', 'Name', 'Unit', 'Price')
tree = ttk.Treeview(root, columns=columns, show='headings')
tree.heading('ID', text='ID')
tree.heading('Name', text='Name')
tree.heading('Unit', text='Unit')
tree.heading('Price', text='Price')
tree.column('ID', width=80, anchor=tk.CENTER)
tree.column('Name', width=200, anchor=tk.W)
tree.column('Unit', width=100, anchor=tk.CENTER)
tree.column('Price', width=100, anchor=tk.E)
tree.bind('<<TreeviewSelect>>', on_item_selected)
selected_id = tk.StringVar(root)

root.grid_rowconfigure(6, weight=1)
root.grid_columnconfigure(1, weight=1)

scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=tree.yview)
scrollbar.grid(row=1, column=4, sticky='ns')
tree.configure(yscrollcommand=scrollbar.set)

name_label = tk.Label(root, text="Numele Materialului:")
name_label.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
name_entry = tk.Entry(root)
name_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=10)

unit_label = tk.Label(root, text="Unitate De Masura:")
unit_label.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
unit_entry = tk.Entry(root)
unit_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=10)

price_label = tk.Label(root, text="Pret:")
price_label.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
price_entry = tk.Entry(root)
price_entry.grid(row=2, column=1, sticky="ew", padx=10, pady=10)

add_button = tk.Button(root, text="Adauga Material", command=add_material)
add_button.grid(row=3, column=0, columnspan=2)

search_label = tk.Label(root, text="Cauta Material:")
search_label.grid(row=4, column=0, sticky="ew", padx=10, pady=10)
search_entry = tk.Entry(root)
search_entry.grid(row=4, column=1, sticky="ew", padx=10, pady=10)

search_button = tk.Button(root, text="Cauta", command=search_materials)
search_button.grid(row=5, column=0, columnspan=2)

tree.grid(row=6, column=0, columnspan=2, sticky='nsew')
scrollbar.grid(row=6, column=2, sticky='ns')

new_price_label = tk.Label(root, text="Pret Nou:")
new_price_label.grid(row=10, column=0, sticky="ew", padx=10, pady=10)
new_price_entry = tk.Entry(root)
new_price_entry.grid(row=10, column=1, sticky="ew", padx=10, pady=10)

update_button = tk.Button(root, text="Schimbati Pretul Materialului", command=update_selected_material)
update_button.grid(row=12, column=0, columnspan=2)

delete_button = tk.Button(root, text="Stergeti Materialul Selectat", command=delete_selected_material)
delete_button.grid(row=12, column=2, columnspan=2)

clear_button = tk.Button(root, text="Goleste Campuri", command=clear_entries)
clear_button.grid(row=14, column=0, columnspan=2)

refresh_materials()

root.mainloop()

conn.close()