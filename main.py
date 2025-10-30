import sys
import os

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    try:
        # Crée un 'faux' flux de sortie vers 'devnull' (le vide)
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
    except Exception:
        pass

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading 
import datetime
import sys

from network_tools import run_ping_test, run_speed_test

# (Configuration CTk... )
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class NetworkDiagnosticApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Netwok Diagnostics by xjapan")
        self.geometry("800x700") 
        
        self.log_file = "network_log.txt"
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Variables d'état ---
        self.is_pinging = False
        self.is_speedtesting = False
        self.current_ping_thread = None
        self.current_speedtest_thread = None
        
        # --- Sidebar (frame de gauche) ---
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        
        self.sidebar_frame.grid_rowconfigure(10, weight=1) 

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Network Diagnostics v 1.0", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)

        # --- Champ Ping ---
        self.ping_host_label = ctk.CTkLabel(self.sidebar_frame, text="Hôte à pinger :")
        self.ping_host_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.ping_host_entry = ctk.CTkEntry(self.sidebar_frame, placeholder_text="google.com")
        self.ping_host_entry.grid(row=2, column=0, padx=20, pady=(5, 10))
        self.ping_button = ctk.CTkButton(self.sidebar_frame, text="Lancer Ping", command=self.start_ping_thread)
        self.ping_button.grid(row=3, column=0, padx=20, pady=10)

        # --- Champs Vitesse Max ---
        self.dl_max_label = ctk.CTkLabel(self.sidebar_frame, text="Max Download (Mbps):")
        self.dl_max_label.grid(row=4, column=0, padx=20, pady=(10, 0), sticky="w")
        self.dl_max_entry = ctk.CTkEntry(self.sidebar_frame)
        self.dl_max_entry.insert(0, "10000") 
        self.dl_max_entry.grid(row=5, column=0, padx=20, pady=(5, 10))
        self.ul_max_label = ctk.CTkLabel(self.sidebar_frame, text="Max Upload (Mbps):")
        self.ul_max_label.grid(row=6, column=0, padx=20, pady=(10, 0), sticky="w")
        self.ul_max_entry = ctk.CTkEntry(self.sidebar_frame)
        self.ul_max_entry.insert(0, "5000") 
        self.ul_max_entry.grid(row=7, column=0, padx=20, pady=(5, 10))
        
        # --- Boutons du bas (rangées ajustées) ---
        self.speedtest_button = ctk.CTkButton(self.sidebar_frame, text="Lancer Speedtest", command=self.start_speedtest_thread)
        self.speedtest_button.grid(row=8, column=0, padx=20, pady=10) 
        
        self.clear_log_button = ctk.CTkButton(self.sidebar_frame, text="Effacer le Log", command=self.clear_log_display)
        self.clear_log_button.grid(row=9, column=0, padx=20, pady=10) 

        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Thème:", anchor="w")
        self.appearance_mode_label.grid(row=11, column=0, padx=20, pady=(10, 0)) 
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["System", "Dark", "Light"],
                                                             command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=12, column=0, padx=20, pady=(10, 20)) 

        # --- Main frame (droite) ---
        
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1) 
        self.gauge_frame = ctk.CTkFrame(self.main_frame)
        self.gauge_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        self.gauge_frame.grid_columnconfigure(1, weight=1)
        self.dl_label = ctk.CTkLabel(self.gauge_frame, text="Download (Mbps)", font=ctk.CTkFont(size=12))
        self.dl_label.grid(row=0, column=0, padx=(10, 5), pady=5, sticky="w")
        self.download_bar = ctk.CTkProgressBar(self.gauge_frame, orientation="horizontal", height=20)
        self.download_bar.set(0)
        self.download_bar.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.ul_label = ctk.CTkLabel(self.gauge_frame, text="Upload (Mbps)", font=ctk.CTkFont(size=12))
        self.ul_label.grid(row=1, column=0, padx=(10, 5), pady=5, sticky="w")
        self.upload_bar = ctk.CTkProgressBar(self.gauge_frame, orientation="horizontal", height=20)
        self.upload_bar.set(0)
        self.upload_bar.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.results_label = ctk.CTkLabel(self.main_frame, text="Résultats des Tests :", font=ctk.CTkFont(size=16, weight="bold"))
        self.results_label.grid(row=1, column=0, sticky="w", pady=(0, 10)) 
        self.results_textbox = ctk.CTkTextbox(self.main_frame, width=500, height=400, wrap="word") 
        self.results_textbox.grid(row=2, column=0, sticky="nsew") 
        self.results_textbox.insert("end", "Bienvenue ! Lancez un test pour voir les résultats ici.\n")
        self.results_textbox.configure(state="disabled") 
        
        # --- Lancement des fonctions au démarrage ---
        self._check_log_file()
        
     
    # --- Les fonctions de log, clear, change_appearance... ne changent pas ---
    def _check_log_file(self):
        if not os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.write(f"--- Log de diagnostic réseau - Démarré le {datetime.datetime.now().isoformat()} ---\n")
                self.log_to_display(f"Fichier de log '{self.log_file}' créé.\n")
            except Exception as e:
                self.log_to_display(f"Erreur lors de la création du fichier de log : {e}\n", error=True)
        else:
            self.log_to_display(f"Fichier de log '{self.log_file}' existant. \n", to_file=False)

    def log_to_display(self, message, error=False, to_file=True):
        timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
        display_message = f"{timestamp} {message}\n"
        self.results_textbox.configure(state="normal")
        self.results_textbox.insert("end", display_message)
        self.results_textbox.see("end") 
        self.results_textbox.configure(state="disabled")
        if to_file:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(display_message)
            except Exception as e:
                self.results_textbox.configure(state="normal")
                self.results_textbox.insert("end", f"ERREUR D'ÉCRITURE LOG : {e}\n")
                self.results_textbox.configure("disabled")

    def clear_log_display(self):
        if messagebox.askyesno("Confirmer", "Voulez-vous vraiment effacer le contenu affiché ?\n(Le fichier de log n'est pas effacé)"):
            self.results_textbox.configure(state="normal")
            self.results_textbox.delete("1.0", "end")
            self.results_textbox.insert("end", "Historique effacé.\n")
            self.results_textbox.configure(state="disabled")

    def change_appearance_mode_event(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    # (La section Ping )
    def start_ping_thread(self):
        if self.is_pinging:
            messagebox.showinfo("Attention", "Un test Ping est déjà en cours.")
            return
        host_to_ping = self.ping_host_entry.get()
        if not host_to_ping: host_to_ping = "google.com"
        self.is_pinging = True
        self.ping_button.configure(state="disabled", text="Ping en cours...")
        self.log_to_display(f"Lancement du test Ping vers {host_to_ping}...")
        self.current_ping_thread = threading.Thread(target=self._run_ping_in_background, args=(host_to_ping,))
        self.current_ping_thread.start()

    def _run_ping_in_background(self, host): 
        ping_result = run_ping_test(host=host) 
        self.after(0, self._process_ping_result, ping_result) 

    def _process_ping_result(self, ping_result):
        if ping_result["success"]:
            self.log_to_display(f"Ping réussi:\n{ping_result['output']}")
        else:
            self.log_to_display(f"Ping échoué: {ping_result['error']}\n{ping_result['output']}", error=True)
            if "Impossible de joindre le host" in ping_result["output"]:
                 messagebox.showerror("Erreur Ping", f"Hôte inconnu ou injoignable :\n{ping_result['error']}")
        self.is_pinging = False
        self.ping_button.configure(state="normal", text="Lancer Ping")

    # --- Section Speedtest ---
    def start_speedtest_thread(self):
        if self.is_speedtesting:
            messagebox.showinfo("Attention", "Un test Speedtest est déjà en cours.")
            return

        self.is_speedtesting = True
        self.speedtest_button.configure(state="disabled", text="Speedtest en cours...")
        
        self.download_bar.set(0)
        self.upload_bar.set(0)
        self.download_bar.configure(mode="indeterminate")
        self.upload_bar.configure(mode="indeterminate")
        self.download_bar.start()
        self.upload_bar.start()
        
        # On n'a plus besoin de passer d'ID
        self.current_speedtest_thread = threading.Thread(target=self._run_speedtest_in_background)
        self.current_speedtest_thread.start()

    # Accepte plus d'argument
    def _run_speedtest_in_background(self):
        log_from_thread = lambda msg: self.after(0, self.log_to_display, msg)
        
        speed_result = run_speed_test(log_callback=log_from_thread)
        
        self.after(0, self._process_speedtest_result, speed_result) 

    # (La fonction _process_speedtest_result)
    def _process_speedtest_result(self, speed_result):
        self.download_bar.stop()
        self.upload_bar.stop()
        self.download_bar.configure(mode="determinate")
        self.upload_bar.configure(mode="determinate")
        self.download_bar.set(0) 
        self.upload_bar.set(0)

        if speed_result["success"]:
            dl_speed = speed_result['download']
            ul_speed = speed_result['upload']
            ping_val = speed_result['ping']
            self.log_to_display(f"Speedtest réussi:\n"
                                f"  Ping: {ping_val:.2f} ms\n"
                                f"  Téléchargement: {dl_speed:.2f} Mbps\n"
                                f"  Envoi: {ul_speed:.2f} Mbps")
            try:
                max_dl = float(self.dl_max_entry.get())
            except ValueError: max_dl = 1000.0 
            try:
                max_ul = float(self.ul_max_entry.get())
            except ValueError: max_ul = 500.0 
            dl_progress = min(dl_speed / max_dl, 1.0)
            ul_progress = min(ul_speed / max_ul, 1.0)
            self.animate_bar(self.download_bar, dl_progress)
            self.animate_bar(self.upload_bar, ul_progress)
        else:
            self.log_to_display(f"Speedtest échoué: {speed_result['error']}", error=True)
            messagebox.showerror("Erreur Speedtest", speed_result['error'])
        self.is_speedtesting = False
        self.speedtest_button.configure(state="normal", text="Lancer Speedtest")

    # (La fonction animate_bar)
    def animate_bar(self, bar, final_value, current_step=0, max_steps=50):
        if current_step >= max_steps:
            bar.set(final_value); return
        current_progress = bar.get()
        step_size = (final_value - current_progress) / (max_steps - current_step)
        new_value = bar.get() + step_size
        bar.set(new_value)
        self.after(20, self.animate_bar, bar, final_value, current_step + 1)


if __name__ == "__main__":
    app = NetworkDiagnosticApp()
    app.mainloop()