import tkinter as tk
from tkinter import ttk
from eventlog import EventLogCollector

def display_logs(logs):
    def filter_logs(event=None):
        search_text = search_entry.get().lower()
        selected_property = property_var.get()
        if selected_property == "All Properties":
            filtered_logs = [log for log in logs if search_text in str(log).lower()]
        else:
            filtered_logs = [log for log in logs if search_text in str(log[selected_property]).lower()]
        refresh_tree(filtered_logs)

    def refresh_tree(filtered_logs):
        tree.delete(*tree.get_children())
        for idx, log in enumerate(filtered_logs):
            tree.insert("", "end", text=str(idx), values=(log['Record No.'], log['Level'], log['Generated Time'], log['Event ID'], log['Source'], log['User ID'], log['Channel']))

    root = tk.Tk()
    root.title("Event Logs")

    search_frame = tk.Frame(root)
    search_frame.pack(padx=10, pady=5, fill="x")

    properties = ["All Properties", "Record No.", "Level", "Generated Time", "Event ID", "Source", "User ID", "Channel"]
    property_var = tk.StringVar(root)
    property_var.set(properties[0])

    property_dropdown = tk.OptionMenu(search_frame, property_var, *properties)
    property_dropdown.pack(side=tk.LEFT, padx=5)

    search_entry = tk.Entry(search_frame, width=50)
    search_entry.pack(side=tk.LEFT, pady=10)

    search_button = tk.Button(search_frame, text="Search", command=filter_logs)
    search_button.pack(side=tk.LEFT, pady=5, padx=5)

    tree = ttk.Treeview(root)
    tree["columns"] = ("Record No.", "Level", "Generated Time", "Event ID", "Source", "User ID", "Channel")
    tree.heading("#0", text="Index")
    tree.column("#0", minwidth=0, width=50, stretch=tk.NO)
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, minwidth=0, width=150, stretch=tk.NO)

    for idx, log in enumerate(logs):
        tree.insert("", "end", text=str(idx), values=(log['Record No.'], log['Level'], log['Generated Time'], log['Event ID'], log['Source'], log['User ID'], log['Channel']))

    tree.pack(expand=True, fill="both")
    search_entry.bind("<Return>", filter_logs)

    root.mainloop()

def show():
    collector = EventLogCollector(result_path="C:\\Windows\\Users", system_root="C:\\Windows", version="Windows 7,8,10", UTC=9)
    event_logs = collector.extract_logs(log_names=["Application", "System", "Security", "Setup"])
    display_logs(event_logs)

