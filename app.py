import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
from src.pipeline import CogniHireEngine
from src.loader import load_candidates
from src.config import TARGET_JD
import time

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG = "#f5efe6"
PAPER = "#fffaf2"
PANEL = "#fffdf8"
SURFACE = "#fffdf8"
SURFACE_ALT = "#f9f3e9"
SURFACE_ELEV = "#fffaf2"
BORDER = "#cfc3b2"
BORDER_STRONG = "#b8a28e"
ACCENT = "#7b5c42"
ACCENT_SOFT = "#e6d8ca"
ACCENT_WARM = "#d8c4ae"
TEXT = "#111111"
MUTED = "#6f6a63"
SUCCESS = "#4f6f52"

class CogniHireApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CogniHire | Predictive Talent Intelligence Engine")
        self.geometry("1280x700")
        self.minsize(1280, 700)
        self.configure(fg_color=BG)

        self.candidates = None
        self.engine = None
        self.last_results = None
        self.selected_file = None

        self.setup_ui()
        self.initialize_system()

    def setup_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=320, corner_radius=0, fg_color=PAPER, border_width=1, border_color=BORDER)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)

        # Brand Header
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(40, 30))
        
        ctk.CTkLabel(
            brand_frame,
            text="CogniHire",
            font=ctk.CTkFont(family="Georgia", size=32, weight="bold"),
            text_color=ACCENT,
            anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            brand_frame,
            text="Predictive Talent Intelligence Engine",
            font=ctk.CTkFont(size=13, slant="italic"),
            text_color=MUTED,
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        # Control Section
        ctrl_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        ctrl_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))

        # Dataset Card - Now more integrated
        self.dataset_card = ctk.CTkFrame(ctrl_frame, fg_color=SURFACE_ALT, corner_radius=16, border_width=1, border_color=BORDER)
        self.dataset_card.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(self.dataset_card, text="SOURCE DATASET", font=ctk.CTkFont(size=10, weight="bold"), text_color=MUTED).pack(anchor="w", padx=20, pady=(15, 5))
        self.file_label = ctk.CTkLabel(self.dataset_card, text="No file selected", font=ctk.CTkFont(size=13), wraplength=220, justify="left", text_color=TEXT)
        self.file_label.pack(anchor="w", padx=20, pady=(0, 10))
        self.browse_btn = ctk.CTkButton(self.dataset_card, text="Browse JSONL", command=self.browse_file, height=36, fg_color=ACCENT, hover_color=ACCENT_WARM, text_color="white", font=ctk.CTkFont(size=13, weight="bold"), corner_radius=8)
        self.browse_btn.pack(anchor="w", padx=20, pady=(0, 15))

        # Action Buttons - Grouped as a "Command Center"
        actions_frame = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        actions_frame.pack(fill="x")

        self.run_btn = ctk.CTkButton(actions_frame, text="Execute Ranking Pipeline", command=self.run_pipeline, height=50, font=ctk.CTkFont(size=14, weight="bold"), fg_color=ACCENT, hover_color=ACCENT_WARM, text_color="white", corner_radius=12)
        self.run_btn.pack(fill="x", pady=(0, 10))

        self.export_btn = ctk.CTkButton(actions_frame, text="Export Results", command=self.export_csv, height=40, fg_color="transparent", border_width=1, border_color=BORDER_STRONG, text_color=TEXT, state="disabled", corner_radius=12)
        self.export_btn.pack(fill="x", pady=(0, 10))

        self.clear_btn = ctk.CTkButton(actions_frame, text="Clear Dashboard", command=self.clear_results, height=40, fg_color="transparent", text_color=MUTED, hover_color=SURFACE_ALT, state="disabled", corner_radius=12)
        self.clear_btn.pack(fill="x")

        # Status Card - Moved to bottom of sidebar
        self.status_card = ctk.CTkFrame(self.sidebar, fg_color=SURFACE_ALT, corner_radius=16, border_width=1, border_color=BORDER)
        self.status_card.grid(row=6, column=0, sticky="ew", padx=20, pady=(0, 30))
        
        ctk.CTkLabel(self.status_card, text="SYSTEM STATUS", font=ctk.CTkFont(size=10, weight="bold"), text_color=MUTED).pack(anchor="w", padx=20, pady=(15, 5))
        self.status_chip = ctk.CTkLabel(self.status_card, text="System ready", font=ctk.CTkFont(size=13, weight="bold"), text_color=SUCCESS)
        self.status_chip.pack(anchor="w", padx=20, pady=(0, 5))
        
        self.artifacts_label = ctk.CTkLabel(self.status_card, text="Artifacts Loaded", font=ctk.CTkFont(size=12), text_color=MUTED)
        self.artifacts_label.pack(anchor="w", padx=20, pady=(2, 0))
        self.faiss_label = ctk.CTkLabel(self.status_card, text="FAISS Ready", font=ctk.CTkFont(size=12), text_color=MUTED)
        self.faiss_label.pack(anchor="w", padx=20, pady=(2, 0))
        
        self.metric_label = ctk.CTkLabel(self.status_card, text="Awaiting dataset selection", font=ctk.CTkFont(size=12), text_color=MUTED)
        self.metric_label.pack(anchor="w", padx=20, pady=(0, 15))

        # --- MAIN CONTENT ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=BG, border_width=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)

        # Top Header - More dramatic spacing
        header_bar = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_bar.grid(row=0, column=0, sticky="ew", padx=50, pady=(50, 30))
        header_bar.columnconfigure(0, weight=1)

        self.header_title = ctk.CTkLabel(header_bar, text="Candidate Intelligence Dashboard", font=ctk.CTkFont(family="Georgia", size=36, weight="bold"), text_color=TEXT, anchor="w")
        self.header_title.grid(row=0, column=0, sticky="w")
        self.status_label = ctk.CTkLabel(header_bar, text="Loading AI models…", font=ctk.CTkFont(size=15), text_color=MUTED, anchor="w")
        self.status_label.grid(row=1, column=0, sticky="w", pady=(8, 0))

        # Content Area
        self.content_area = ctk.CTkFrame(self.main_frame, corner_radius=0, fg_color="transparent")
        self.content_area.grid(row=2, column=0, sticky="nsew", padx=50, pady=(0, 50))
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(3, weight=1)

        # Progress Section - More refined
        self.progress_container = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.progress_container.grid(row=0, column=0, sticky="w", pady=(0, 12))
        
        self.progress_bar = ctk.CTkProgressBar(self.progress_container, height=12, width=400, progress_color=ACCENT)
        self.progress_bar.pack(side="left", padx=(0, 10))
        self.progress_bar.set(0)
        
        self.progress_text = ctk.CTkLabel(self.progress_container, text="0%", font=ctk.CTkFont(family="Courier", size=12, weight="bold"), text_color=TEXT)
        self.progress_text.pack(side="left")

        self.step_header = ctk.CTkLabel(self.content_area, text="Pipeline progress", font=ctk.CTkFont(size=14, weight="bold"), text_color=TEXT, anchor="w")
        self.step_header.grid(row=1, column=0, sticky="w", pady=(0, 12))

        self.step_frame = ctk.CTkFrame(self.content_area, fg_color=SURFACE_ALT, corner_radius=14, border_width=1, border_color=BORDER)
        self.step_frame.grid(row=2, column=0, sticky="ew", pady=(0, 25))
        self.step_frame.grid_columnconfigure(0, weight=1)
        self.stage_names = [
            "Loading Candidates",
            "Precomputation",
            "Sieve 1",
            "Sieve 2",
            "Sieve 3",
            "Ranking Complete",
        ]
        self.stage_labels = []
        for i, stage in enumerate(self.stage_names):
            label = ctk.CTkLabel(
                self.step_frame,
                text=stage,
                font=ctk.CTkFont(size=12),
                fg_color=SURFACE_ALT,
                text_color=MUTED,
                corner_radius=12,
                anchor="center",
                pady=12,
            )
            label.grid(row=0, column=i, padx=(0 if i == 0 else 12, 0), sticky="ew")
            self.step_frame.grid_columnconfigure(i, weight=1)
            self.stage_labels.append(label)

        self.summary_frame = ctk.CTkFrame(self.content_area, fg_color=SURFACE_ALT, corner_radius=14, border_width=1, border_color=BORDER)
        self.summary_frame.grid(row=2, column=0, sticky="ew", pady=(0, 25))
        self.summary_frame.grid_remove()
        
        self.summary_title = ctk.CTkLabel(self.summary_frame, text="Ranking Complete", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT, anchor="w")
        self.summary_title.grid(row=0, column=0, sticky="w", padx=25, pady=(20, 10))
        
        self.summary_details = ctk.CTkLabel(self.summary_frame, text="", font=ctk.CTkFont(size=14), text_color=MUTED, anchor="w", justify="left")
        self.summary_details.grid(row=1, column=0, sticky="w", padx=25, pady=(0, 20))

        self.table_container = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.table_container.grid(row=3, column=0, sticky="nsew")
        self.table_container.grid_columnconfigure(0, weight=1)
        self.table_container.grid_rowconfigure(1, weight=1)

        self.table_header = ctk.CTkFrame(self.table_container, fg_color=SURFACE_ELEV, corner_radius=14, border_width=1, border_color=BORDER)
        self.table_header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.table_header.columnconfigure(0, weight=0, minsize=60)
        self.table_header.columnconfigure(1, weight=0, minsize=200)
        self.table_header.columnconfigure(2, weight=0, minsize=130)
        self.table_header.columnconfigure(3, weight=2)

        ctk.CTkLabel(self.table_header, text="RANK", font=ctk.CTkFont(size=11, weight="bold"), width=60, text_color=MUTED, anchor="center").grid(row=0, column=0, padx=10, pady=15, sticky="ew")
        ctk.CTkLabel(self.table_header, text="CANDIDATE", font=ctk.CTkFont(size=11, weight="bold"), width=200, text_color=MUTED, anchor="w").grid(row=0, column=1, padx=10, pady=15, sticky="w")
        ctk.CTkLabel(self.table_header, text="SCORE", font=ctk.CTkFont(size=11, weight="bold"), width=130, text_color=MUTED, anchor="center").grid(row=0, column=2, padx=(25,15), pady=15, sticky="ew")
        ctk.CTkLabel(self.table_header, text="REASONING", font=ctk.CTkFont(size=11, weight="bold"), text_color=MUTED, anchor="center").grid(row=0, column=3, padx=10, pady=15, sticky="ew")

        self.table_body = ctk.CTkScrollableFrame(self.table_container, fg_color="transparent", border_width=0)
        self.table_body.grid(row=1, column=0, sticky="nsew")
        self.table_body.grid_columnconfigure(0, weight=1)

        self._show_empty_state()

    def update_progress_stage(self, index):
        total = len(self.stage_labels) - 1
        progress = index / total
        self.progress_bar.set(progress)
        self.progress_text.configure(text=f"{int(progress * 100)}%")
        for i, label in enumerate(self.stage_labels):
            if i < index:
                label.configure(fg_color="#ead9c2", text_color=TEXT)
            elif i == index:
                label.configure(fg_color=ACCENT, text_color="#fffaf2")
            else:
                label.configure(fg_color=SURFACE_ALT, text_color=MUTED)
        self.step_header.configure(text=f"{self.stage_names[index]}...")

    def show_summary(self, total_time_s, results_df, precompute_time=0, ranking_time=0):
        minutes = total_time_s / 60
        precompute_mins = precompute_time / 60
        ranking_mins = ranking_time / 60
        
        summary_text = f" Total Execution Time: {total_time_s:.2f}s ({minutes:.2f} mins) | Precompute: {precompute_time:.2f}s ({precompute_mins:.2f} mins) | Rank: {ranking_time:.2f}s ({ranking_mins:.2f} mins)"
        
        self.progress_container.grid_remove()
        self.step_frame.grid_remove()
        self.step_header.configure(text="Ranking Complete")
        self.summary_details.configure(text=summary_text)
        self.summary_frame.grid()

    def reset_progress(self):
        self.summary_frame.grid_remove()
        self.progress_container.grid()
        self.step_frame.grid()
        self.step_header.configure(text="Pipeline progress")
        self.update_progress_stage(0)

    def initialize_system(self):
        try:
            self.update_status("Loading AI models…", "#fbbf24")
            self.progress_bar.start()
            self.update_idletasks()
            self.engine = CogniHireEngine()
            self.update_status("Ready to review candidate pools", "#4ade80")
            self.progress_bar.stop()
            self.progress_bar.set(1)
        except Exception as e:
            messagebox.showerror("Initialization Error", f"Failed to load models: {e}")
            self.update_status("Initialization failed", "#f87171")
            self.progress_bar.stop()

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Candidates Dataset",
            filetypes=[("JSONL Files", "*.jsonl"), ("All Files", "*.*")],
        )
        if file_path:
            self.selected_file = file_path
            self.file_label.configure(text=os.path.basename(file_path))
            self.metric_label.configure(text="Dataset ready for ranking")
            self.status_chip.configure(text="Dataset loaded", text_color="#4ade80")
            self.update_status("Dataset selected. Ready to rank.", "#dfe8f5")

    def _show_empty_state(self):
        for widget in self.table_body.winfo_children():
            widget.destroy()

        empty_card = ctk.CTkFrame(self.table_body, fg_color=PANEL, corner_radius=18, border_width=1, border_color=BORDER)
        empty_card.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(empty_card, text="No ranking results yet", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT, anchor="w").pack(anchor="w", padx=18, pady=(16, 8))
        ctk.CTkLabel(empty_card, text="Select a dataset and run the ranking pipeline to surface your best-fit candidates.", font=ctk.CTkFont(size=12), justify="left", text_color=MUTED).pack(anchor="w", padx=18, pady=(0, 16))

    def display_results(self, df):
        for widget in self.table_body.winfo_children():
            widget.destroy()

        if df is None or df.empty:
            self._show_empty_state()
            return

        self.metric_label.configure(text=f"{len(df)} candidates shortlisted")

        for idx, row in df.iterrows():
            rank = idx + 1
            candidate_id = str(row["candidate_id"])
            score = row["score"]
            reason = str(row.get("reasoning", ""))

            row_frame = ctk.CTkFrame(self.table_body, fg_color=PANEL, corner_radius=14, border_width=1, border_color=BORDER)
            row_frame.pack(fill="x", pady=(0, 8))
            # Match header min sizes so columns line up exactly
            row_frame.grid_columnconfigure(0, weight=0, minsize=60)
            row_frame.grid_columnconfigure(1, weight=0, minsize=200)
            row_frame.grid_columnconfigure(2, weight=0, minsize=130)
            row_frame.grid_columnconfigure(3, weight=2)

            row_frame.bind("<Enter>", lambda event, f=row_frame: f.configure(fg_color="#f3e8db"))
            row_frame.bind("<Leave>", lambda event, f=row_frame: f.configure(fg_color=PANEL))

            ctk.CTkLabel(row_frame, text=f"#{rank}", font=ctk.CTkFont(size=12, weight="bold"), width=60, text_color=ACCENT, anchor="center").grid(row=0, column=0, padx=10, pady=12, sticky="ew")
            ctk.CTkLabel(row_frame, text=candidate_id, font=ctk.CTkFont(size=12), width=200, text_color=TEXT, anchor="w", wraplength=200).grid(row=0, column=1, padx=10, pady=12, sticky="w")
            ctk.CTkLabel(row_frame, text=str(score), font=ctk.CTkFont(size=12, weight="bold"), width=130, anchor="center", text_color=SUCCESS).grid(row=0, column=2, padx=(25,15), pady=12, sticky="ew")
            reason_label = ctk.CTkLabel(row_frame, text=reason, font=ctk.CTkFont(size=12), justify="left", wraplength=1200, text_color=MUTED, anchor="w")
            reason_label.configure(justify="left")
            reason_label.grid(row=0, column=3, padx=10, pady=12, sticky="w")
            if hasattr(ctk, "CTkToolTip"):
                ctk.CTkToolTip(reason_label, text=reason)

    def run_pipeline(self):
        if not hasattr(self, "selected_file") or not self.selected_file:
            messagebox.showwarning("No File", "Please select a .jsonl dataset first.")
            return

        jd_text = TARGET_JD

        self.run_btn.configure(state="disabled")
        self.export_btn.configure(state="disabled")
        self.update_status("Processing candidate shortlist…", "#fbbf24")
        self.reset_progress()
        self.progress_bar.start()
        self.update_idletasks()

        threading.Thread(target=self._execute_pipeline_thread, args=(jd_text,), daemon=True).start()

    def update_status(self, text, color="white"):
        self.after(0, lambda: self.status_label.configure(text=text, text_color=color))

    def clear_results(self):
        self.last_results = None
        self._show_empty_state()
        self.export_btn.configure(state="disabled")
        self.clear_btn.configure(state="disabled")
        self.metric_label.configure(text="Results cleared")
        self.status_chip.configure(text="Results cleared", text_color=MUTED)
        self.update_status("Results cleared", ACCENT)

    def _execute_pipeline_thread(self, jd_text):
        start_time = time.time()
        try:
            self.update_status("Loading candidates…", "#fbbf24")
            self.after(0, lambda: self.update_progress_stage(0))
            self.candidates = load_candidates(self.selected_file)
            if not self.candidates:
                raise ValueError("Failed to load candidates from the selected file.")

            self.after(0, lambda: self.update_progress_stage(1))
            self.update_status("Precomputing embeddings…", "#fbbf24")
            pre_start = time.time()
            self.engine.precompute_on_fly(self.candidates)
            precompute_time = time.time() - pre_start
            
            # Update status labels with ticks after precomputation
            self.after(0, lambda: self.artifacts_label.configure(text="Artifacts Loaded ✓", text_color=SUCCESS))
            self.after(0, lambda: self.faiss_label.configure(text="FAISS Ready ✓", text_color=SUCCESS))

            self.after(0, lambda: self.update_progress_stage(2))
            self.update_status("Preparing semantic recall…", "#fbbf24")
            self.after(0, lambda: self.update_progress_stage(3))
            self.update_status("Applying intelligence filters…", "#fbbf24")
            self.after(0, lambda: self.update_progress_stage(4))
            self.update_status("Performing precision rerank…", "#fbbf24")
            rank_start = time.time()
            results_df = self.engine.run_pipeline(self.candidates, jd_text)
            ranking_time = time.time() - rank_start

            total_time_s = time.time() - start_time
            self.after(0, lambda: self.update_progress_stage(5))
            self.after(0, lambda: self.show_summary(total_time_s, results_df, precompute_time, ranking_time))
            self.after(0, lambda: self._finalize_pipeline(results_df, total_time_s))

        except Exception as e:
            self.after(0, lambda: self._handle_pipeline_error(e))

    def _finalize_pipeline(self, results_df, total_time_s):
        self.display_results(results_df)
        self.last_results = results_df
        self.update_status("Ready", "#4ade80")
        self.export_btn.configure(state="normal")
        self.clear_btn.configure(state="normal")
        self.run_btn.configure(state="normal")
        self.progress_bar.stop()
        self.progress_bar.set(1)
        self.status_chip.configure(text="Ready", text_color="#4ade80")
        
        # Update System Status card with detailed metrics
        total_processed = len(self.candidates) if self.candidates else 0
        shortlisted = len(results_df) if results_df is not None else 0
        top_score = results_df.iloc[0]["score"] if results_df is not None and not results_df.empty else 0.0
        avg_top_100 = results_df["score"].head(100).mean() if results_df is not None and not results_df.empty else 0.0
        
        metrics_text = (
            f"Candidates Processed: {total_processed:,}\n"
            f"Candidates Shortlisted: {shortlisted:,}\n"
            f"Top Candidate Score: {top_score:.3f}\n"
            f"Avg Top-100 Score: {avg_top_100:.3f}"
        )
        self.metric_label.configure(text=metrics_text)

    def _handle_pipeline_error(self, e):
        messagebox.showerror("Pipeline Error", str(e))
        self.update_status("Execution failed", "#f87171")
        self.run_btn.configure(state="normal")
        self.progress_bar.stop()
        self.progress_bar.set(0)
        self.status_chip.configure(text="Execution failed", text_color="#f87171")

    def export_csv(self):
        if self.last_results is not None:
            save_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                initialfile="cognihire_results.csv",
                title="Save Ranking Results",
            )
            if save_path:
                self.last_results.to_csv(save_path, index=False)
                messagebox.showinfo("Success", f"Results exported to:\n{save_path}")

if __name__ == "__main__":
    app = CogniHireApp()
    app.mainloop()
