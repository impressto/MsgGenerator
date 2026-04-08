#!/usr/bin/env python3
"""
GUI Interface for MsgGenerator
Creates .msg files using a simple graphical interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os

class MsgGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MSG File Generator")
        self.root.geometry("600x500")
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame with padding
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Create MSG File", font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        # Sender Email
        ttk.Label(main_frame, text="Sender Email:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.sender_email = ttk.Entry(main_frame, width=50)
        self.sender_email.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        self.sender_email.insert(0, "dev@example.com")
        
        # Sender Name
        ttk.Label(main_frame, text="Sender Name:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.sender_name = ttk.Entry(main_frame, width=50)
        self.sender_name.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        self.sender_name.insert(0, "Linux Developer")
        
        # Subject
        ttk.Label(main_frame, text="Subject:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.subject = ttk.Entry(main_frame, width=50)
        self.subject.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        self.subject.insert(0, "Generated Email")
        
        # Recipient Email
        ttk.Label(main_frame, text="Recipient Email:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.recipient_email = ttk.Entry(main_frame, width=50)
        self.recipient_email.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        self.recipient_email.insert(0, "client@example.com")
        
        # Recipient Name
        ttk.Label(main_frame, text="Recipient Name:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.recipient_name = ttk.Entry(main_frame, width=50)
        self.recipient_name.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)
        self.recipient_name.insert(0, "Client Name")
        
        # Body
        ttk.Label(main_frame, text="Email Body:").grid(row=6, column=0, sticky=(tk.W, tk.N), pady=5)
        body_frame = ttk.Frame(main_frame)
        body_frame.grid(row=6, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.body = tk.Text(body_frame, width=50, height=8, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(body_frame, orient=tk.VERTICAL, command=self.body.yview)
        self.body.configure(yscrollcommand=scrollbar.set)
        
        self.body.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        body_frame.columnconfigure(0, weight=1)
        body_frame.rowconfigure(0, weight=1)
        
        self.body.insert(1.0, "This .msg file was created on Linux without Outlook.")
        
        # Output file
        ttk.Label(main_frame, text="File Name:").grid(row=7, column=0, sticky=tk.W, pady=5)
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=7, column=1, sticky=(tk.W, tk.E), pady=5)
        
        self.output_file = ttk.Entry(output_frame, width=40)
        self.output_file.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.output_file.insert(0, "Success.msg")
        
        # Note about save location
        note_label = ttk.Label(main_frame, text="Files will be saved to: msg_files/", 
                               font=('Arial', 9), foreground='gray')
        note_label.grid(row=7, column=1, sticky=tk.W, pady=(0, 5))
        
        browse_btn = ttk.Button(output_frame, text="Browse", command=self.browse_file)
        browse_btn.grid(row=0, column=1, padx=(5, 0))
        
        output_frame.columnconfigure(0, weight=1)
        
        # Generate button
        generate_btn = ttk.Button(main_frame, text="Generate MSG File", command=self.generate_msg)
        generate_btn.grid(row=9, column=0, columnspan=2, pady=20)
        
        # Configure row weights for body text expansion
        main_frame.rowconfigure(6, weight=1)
    
    def browse_file(self):
        """Open file dialog to choose output location"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".msg",
            filetypes=[("MSG files", "*.msg"), ("All files", "*.*")],
            initialfile=self.output_file.get()
        )
        if filename:
            self.output_file.delete(0, tk.END)
            self.output_file.insert(0, filename)
    
    def generate_msg(self):
        """Call the C# MsgGenerator with the provided arguments"""
        # Get values from form
        sender_email = self.sender_email.get().strip()
        sender_name = self.sender_name.get().strip()
        subject = self.subject.get().strip()
        recipient_email = self.recipient_email.get().strip()
        recipient_name = self.recipient_name.get().strip()
        body = self.body.get(1.0, tk.END).strip()
        output_file = self.output_file.get().strip()
        
        # Validate inputs
        if not all([sender_email, sender_name, subject, recipient_email, recipient_name, body, output_file]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Build command - use dotnet run with -- to pass arguments
        cmd = [
            "dotnet", "run", "--project", script_dir, "--",
            sender_email, sender_name, subject, 
            recipient_email, recipient_name, body, output_file
        ]
        
        try:
            # Run the C# program
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=script_dir
            )
            
            if result.returncode == 0:
                messagebox.showinfo("Success", f"MSG file created successfully!\n\n{result.stdout}")
            else:
                messagebox.showerror("Error", f"Failed to generate MSG file:\n\n{result.stderr}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to run MsgGenerator:\n\n{str(e)}")

def main():
    root = tk.Tk()
    app = MsgGeneratorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
