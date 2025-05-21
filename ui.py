import tkinter as tk
from tkinter import messagebox, filedialog
import csv

# Global list to hold the asset tags
asset_tags = []

def ui_print(message):
    messagebox.showinfo("Info", message)

def validate_asset_tag(asset_tag):
    return asset_tag not in asset_tags

def import_from_csv():
    try:
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if file_path:
            with open(file_path, newline='') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    asset_tag = row[0].strip()
                    if validate_asset_tag(asset_tag):
                        asset_tags.append(asset_tag)
                update_asset_tag_display()
    except Exception as e:
        messagebox.showerror("Import Error", f"Failed to import from CSV: {str(e)}")

def update_asset_tag_display():
    listbox.delete(0, tk.END)
    for tag in asset_tags:
        listbox.insert(tk.END, tag)

def add_asset_tag():
    asset_tag = asset_tag_entry.get().strip()
    if not asset_tag:
        return
    if not validate_asset_tag(asset_tag):
        messagebox.showwarning("Duplicate Entry", f"Asset tag {asset_tag} has already been entered.")
        asset_tag_entry.delete(0, tk.END)
        return
    asset_tags.append(asset_tag)
    update_asset_tag_display()
    asset_tag_entry.delete(0, tk.END)

def submit():
    prestage_input = prestage_entry.get().strip()
    if not prestage_input:
        messagebox.showwarning("Input Error", "Please enter a PreStage name or ID.")
        return
    root.quit()

def run_ui(token):
    global root, asset_tag_entry, listbox, prestage_entry

    root = tk.Tk()
    root.title("Asset Tag Input")

    frame = tk.Frame(root)
    frame.pack(padx=10, pady=10)

    tk.Label(frame, text="Enter Asset Tag:").grid(row=0, column=0)
    asset_tag_entry = tk.Entry(frame, width=25)
    asset_tag_entry.grid(row=0, column=1)
    asset_tag_entry.bind("<Return>", lambda event: add_asset_tag())

    add_button = tk.Button(frame, text="Add", command=add_asset_tag)
    add_button.grid(row=0, column=2, padx=10)

    listbox = tk.Listbox(frame, height=10, width=40)
    listbox.grid(row=1, column=0, columnspan=3, pady=10)

    import_button = tk.Button(root, text="Import from CSV", command=import_from_csv)
    import_button.pack(pady=5)

    tk.Label(root, text="Enter Destination PreStage (Name or ID):").pack(padx=10, pady=10)
    prestage_entry = tk.Entry(root, width=50)
    prestage_entry.pack(pady=5)

    submit_button = tk.Button(root, text="Submit", command=submit)
    submit_button.pack(pady=20)

    root.mainloop()

    return asset_tags, prestage_entry.get().strip()
def get_client_credentials():
    credentials = {}

    def submit_credentials():
        client_id = client_id_entry.get().strip()
        client_secret = client_secret_entry.get().strip()
        if not client_id or not client_secret:
            messagebox.showwarning("Input Error", "Please enter both Client ID and Client Secret.")
            return
        credentials["client_id"] = client_id
        credentials["client_secret"] = client_secret
        cred_window.quit()

    cred_window = tk.Tk()
    cred_window.title("Jamf API Credentials")

    tk.Label(cred_window, text="Client ID:").grid(row=0, column=0, padx=10, pady=5)
    client_id_entry = tk.Entry(cred_window, width=40)
    client_id_entry.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(cred_window, text="Client Secret:").grid(row=1, column=0, padx=10, pady=5)
    client_secret_entry = tk.Entry(cred_window, width=40, show="*")
    client_secret_entry.grid(row=1, column=1, padx=10, pady=5)

    submit_btn = tk.Button(cred_window, text="Submit", command=submit_credentials)
    submit_btn.grid(row=2, column=0, columnspan=2, pady=15)

    cred_window.mainloop()

    return credentials["client_id"], credentials["client_secret"]
