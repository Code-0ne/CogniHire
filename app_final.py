# gui.py
import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import os
from src.pipeline import CogniHireEngine
from src.loader import load_candidates

# Set the appearance and theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class CogniHireApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. Window Configuration
        self.title("CogniHire Talent Intelligence Engine - Production Mode")
        self.geometry("1200x700")

        # 2. State Management
        self.candidates = None
        self.engine = None
        self.last_results = None

        # 3. Initialize Application
        self.setup_ui()
        self.initialize_system()

    def setup_ui(self):
        """Configures the modern layout of the application."""
        # Grid Layout: Sidebar (0) and Main View (1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=320, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Logo and Header
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="CogniHire AI", 
            font=ctk.CTkFont(size=26, weight="bold")
        )
        self.logo_label.pack(pady=(30, 10), padx=20)
        
        self.sub_label = ctk.CTkLabel(
            self.sidebar, 
            text="Dynamic Ranking System", 
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.sub_label.pack(pady=(0, 30), padx=20)

        # Dataset Selection
        self.data_label = ctk.CTkLabel(self.sidebar, text="Candidate Dataset (.jsonl):", font=("Arial", 14, "bold"))
        self.data_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        self.file_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.file_frame.pack(pady=5, padx=20, fill="x")
        
        self.file_label = ctk.CTkLabel(self.file_frame, text="No file selected", font=("Arial", 11), wraplength=200)
        self.file_label.pack(side="left", padx=(0, 10))
        
        self.browse_btn = ctk.CTkButton(
            self.file_frame, 
            text="Browse", 
            width=80, 
            command=self.browse_file
        )
        self.browse_btn.pack(side="right")

        # JD Input Section
        self.jd_label = ctk.CTkLabel(self.sidebar, text="Target Job Description:", font=("Arial", 14, "bold"))
        self.jd_label.pack(pady=(20, 5), padx=20, anchor="w")
        
        self.jd_text = ctk.CTkTextbox(self.sidebar, width=260, height=250, font=("Arial", 12))
        self.jd_text.pack(pady=10, padx=20)
        # Use the official TARGET_JD from config for consistency
        from src.config import TARGET_JD
        self.jd_text.insert("0.0", TARGET_JD)

        # Action Buttons
        self.run_btn = ctk.CTkButton(
            self.sidebar, 
            text="Execute Ranking Pipeline", 
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#1f6aa5", 
            hover_color="#144870",
            command=self.run_pipeline
        )
        self.run_btn.pack(pady=30, padx=20)

        self.export_btn = ctk.CTkButton(
            self.sidebar, 
            text="Export Results to CSV", 
            fg_color="transparent", 
            border_width=2,
            command=self.export_csv, 
            state="disabled"
        )
        self.export_btn.pack(pady=10, padx=20)

        # --- MAIN DISPLAY AREA ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=20)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        # Status Bar
        self.status_label = ctk.CTkLabel(
            self.main_frame, 
            text="Ready. Please select a dataset.", 
            font=("Arial", 14),
            text_color="white"
        )
        self.status_label.grid(row=0, column=0, pady=20)

        # Results Table
        self.results_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="Ranking Results")
        self.results_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.setup_results_table()

    def initialize_system(self):
        """Initializes the AI engine without loading a specific dataset first."""
        try:
            self.status_label.configure(text="Loading AI Models...", text_color="yellow")
            self.update_idletasks()
            self.engine = CogniHireEngine()
            self.status_label.configure(text="Ready. Please select a dataset.", text_color="white")
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to load models: {e}")
            self.status_label.configure(text="Initialization failed", text_color="red")

    def browse_file(self):
        """Allows user to select a .jsonl file."""
        file_path = filedialog.askopenfilename(
            title="Select Candidates Dataset",
            filetypes=[("JSONL Files", "*.jsonl"), ("All Files", "*.*")]
        )
        if file_path:
            self.selected_file = file_path
            self.file_label.configure(text=os.path.basename(file_path))
            self.status_label.configure(text="Dataset selected. Ready to rank.", text_color="white")

    def setup_results_table(self):
        """Creates the header for the results table."""
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        headers = ["Rank", "Candidate ID", "Score", "Reasoning"]
        for i, header in enumerate(headers):
            lbl = ctk.CTkLabel(self.results_frame, text=header, font=("Arial", 12, "bold"))
            lbl.grid(row=0, column=i, padx=10, pady=5, sticky="w")

    def display_results(self, df):
        """Populates the results table with DataFrame content."""
        self.setup_results_table()
        
        for idx, row in df.iterrows():
            rank = idx + 1
            cid = row["candidate_id"]
            score = str(row['score'])
            reason = row["reasoning"]

            ctk.CTkLabel(self.results_frame, text=str(rank)).grid(row=rank, column=0, padx=10, pady=2, sticky="w")
            ctk.CTkLabel(self.results_frame, text=cid).grid(row=rank, column=1, padx=10, pady=2, sticky="w")
            ctk.CTkLabel(self.results_frame, text=score).grid(row=rank, column=2, padx=10, pady=2, sticky="w")
            
            reason_lbl = ctk.CTkLabel(self.results_frame, text=reason, font=("Arial", 11), wraplength=600, justify="left")
            reason_lbl.grid(row=rank, column=3, padx=10, pady=2, sticky="w")

    def run_pipeline(self):
        """Main pipeline execution flow: Load -> Precompute -> Rank."""
        if not hasattr(self, 'selected_file') or not self.selected_file:
            messagebox.showwarning("No File", "Please select a .jsonl dataset first.")
            return

        jd_text = self.jd_text.get("1.0", "end-1c").strip()
        if not jd_text:
            messagebox.showwarning("No JD", "Please enter a target job description.")
            return

        self.run_btn.configure(state="disabled")
        self.status_label.configure(text="🚀 Processing... Please wait.", text_color="yellow")
        self.update_idletasks()

        try:
            self.candidates = load_candidates(self.selected_file)
            if not self.candidates:
                raise ValueError("Failed to load candidates from the selected file.")

            self.status_label.configure(text="⚙️  Precomputing embeddings & index...", text_color="yellow")
            self.update_idletasks()
            self.engine.precompute_on_fly(self.candidates)

            self.status_label.configure(text="🧠 Ranking and generating reasoning...", text_color="yellow")
            self.update_idletasks()
            results_df = self.engine.run_pipeline(self.candidates, jd_text)
            
            self.display_results(results_df)
            self.last_results = results_df
            self.status_label.configure(text="✅ Ranking Complete!", text_color="green")
            self.export_btn.configure(state="normal")
            
        except Exception as e:
            messagebox.showerror("Pipeline Error", str(e))
            self.status_label.configure(text="❌ Execution failed", text_color="red")
        finally:
            self.run_btn.configure(state="normal")

    def export_csv(self):
        if self.last_results is not None:
            save_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                initialfile="cognihire_results.csv",
                title="Save Ranking Results"
            )
            if save_path:
                self.last_results.to_csv(save_path, index=False)
                messagebox.showinfo("Success", f"Results exported to:\n{save_path}")

if __name__ == "__main__":
    app = CogniHireApp()
    app.mainloop()
