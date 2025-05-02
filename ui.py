import tkinter as tk
from tkinter import messagebox
import csv
import re

# Global list to hold the asset tags
asset_tags = []

def validate_asset_tag(asset_tag):
    # Check if the asset tag is already in the list
    if asset_tag in asset_tags:
        return False
    return True

# Function to handle CSV import
def import_from_csv():
    try:
        file_path = tk.filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            with open(file_path, newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    asset_tag = row[0].strip()
                    if validate_asset_tag(asset_tag):  # Check if it's not already added
                        asset_tags.append(asset_tag)
                update_asset_tag_display()
    except Exception as e:
        messagebox.showerror("Import Error", f"Failed to import from CSV: {str(e)}")

# Function to update the display of asset tags
def update_asset_tag_display():
    listbox.delete(0, tk.END)  # Clear the listbox
    for tag in asset_tags:
        listbox.insert(tk.END, tag)

# Function to handle adding a new asset tag
def add_asset_tag():
    asset_tag = asset_tag_entry.get().strip()
    if not asset_tag:
        return  # Empty input; ignore
    if not validate_asset_tag(asset_tag):
        messagebox.showwarning("Duplicate Entry", f"Asset tag {asset_tag} has already been entered.")
        asset_tag_entry.delete(0, tk.END)  # Clear the entry field
        return
    asset_tags.append(asset_tag)
    update_asset_tag_display()  # Update the list of asset tags displayed
    asset_tag_entry.delete(0, tk.END)  # Clear the input field

# Function to handle submission and passing information to main.py
def submit():
    prestage_input = prestage_entry.get().strip()
    if not prestage_input:
        messagebox.showwarning("Input Error", "Please enter a PreStage name or ID.")
        return
    # Return the asset tags and prestage input to the main program
    print("Asset Tags:", asset_tags)
    print("PreStage:", prestage_input)
    root.quit()  # Close the UI

# Function to create the UI
def run_ui(token):
    global root, asset_tag_entry, listbox, prestage_entry
    
    root = tk.Tk()
    root.title("Asset Tag Input")

    # Frame for asset tag input and list
    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    # Asset Tag Input
    tk.Label(frame, text="Enter Asset Tag:").grid(row=0, column=0)
    asset_tag_entry = tk.Entry(frame, width=25)
    asset_tag_entry.grid(row=0, column=1)
    asset_tag_entry.bind("<Return>", lambda event: add_asset_tag())  # Allow pressing Enter to add

    # Button to add asset tag
    add_button = tk.Button(frame, text="Add", command=add_asset_tag)
    add_button.grid(row=0, column=2, padx=10)

    # Listbox to display asset tags
    listbox = tk.Listbox(frame, height=10, width=40)
    listbox.grid(row=1, column=0, columnspan=3, pady=10)
    
    # Button to import asset tags from CSV
    import_button = tk.Button(root, text="Import from CSV", command=import_from_csv)
    import_button.pack(pady=5)

    # PreStage input
    tk.Label(root, text="Enter Destination PreStage (Name or ID):").pack(padx=10, pady=10)
    prestage_entry = tk.Entry(root, width=50)
    prestage_entry.pack(pady=5)

    # Submit button
    submit_button = tk.Button(root, text="Submit", command=submit)
    submit_button.pack(pady=20)

    root.mainloop()

    # Return the asset tags and prestage input for the next part of the program
    return asset_tags, prestage_entry.get().strip()

