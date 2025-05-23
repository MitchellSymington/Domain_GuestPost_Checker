import tkinter as tk
from tkinter import filedialog, messagebox
import os
import csv
import time
import random

# Cores utilizadas na interface
BG_COLOR = "#e6f0ff"
HEADER_COLOR = "#0073e6"
BUTTON_COLOR = "#3399ff"
HOVER_COLOR = "#66b3ff"
HOVER_RED = "#ff4d4d"
CLICK_COLOR = "#1a75ff"
TEXT_COLOR = "#ffffff"
STATUS_BLUE = "#0073e6"
STATUS_BLACK = "#000000"
STATUS_GREEN = "#28a745"
STATUS_RED = "#dc3545"

# Classe responsável pelos tooltips exibidos ao passar o mouse sobre campos
class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.label = None
        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.label or not self.text:
            return
        x = self.widget.winfo_rootx() - self.widget.master.winfo_rootx() + 10
        y = self.widget.winfo_rooty() - self.widget.master.winfo_rooty() + self.widget.winfo_height() + 2
        self.label = tk.Label(self.widget.master, text=self.text, bg="yellow", fg="black",
                              font=("Arial", 8), relief="solid", borderwidth=1)
        self.label.place(x=x, y=y)

    def hide_tooltip(self, event=None):
        if self.label:
            self.label.destroy()
            self.label = None

# Classe principal da aplicação
class DomainCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)  # Remove barra padrão
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.99)
        self.center_window(400, 280)
        self.root.configure(bg=BG_COLOR)

        # Variáveis de estado
        self.query_path = tk.StringVar()
        self.domains_path = tk.StringVar()
        self.status_text = tk.StringVar(value="Waiting for file selection...")

        # Inicializa layout
        self.setup_title_bar()
        self.setup_interface()
        self.setup_status_bar()

    def center_window(self, width, height):
        # Centraliza a janela na tela
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def setup_title_bar(self):
        # Cria barra de título customizada com botões
        title_bar = tk.Frame(self.root, bg=HEADER_COLOR, relief="raised", bd=0, height=30)
        title_bar.pack(fill=tk.X, side=tk.TOP)

        def start_move(event): self.root.x = event.x; self.root.y = event.y
        def do_move(event):
            x, y = event.x_root - self.root.x, event.y_root - self.root.y
            self.root.geometry(f"+{x}+{y}")

        title_bar.bind("<Button-1>", start_move)
        title_bar.bind("<B1-Motion>", do_move)

        def on_click(btn):
            orig = btn.cget("bg")
            btn.config(bg=CLICK_COLOR)
            btn.after(150, lambda: btn.config(bg=orig))

        # Botões da barra
        btn_close = tk.Label(title_bar, text=" X ", bg=HEADER_COLOR, fg=TEXT_COLOR, cursor="hand2")
        btn_help  = tk.Label(title_bar, text=" ? ", bg=HEADER_COLOR, fg=TEXT_COLOR, cursor="hand2")
        btn_min   = tk.Label(title_bar, text=" - ", bg=HEADER_COLOR, fg=TEXT_COLOR, cursor="hand2")

        # Eventos dos botões
        btn_close.bind("<Enter>", lambda e: btn_close.config(bg=HOVER_RED))
        btn_close.bind("<Leave>", lambda e: btn_close.config(bg=HEADER_COLOR))
        btn_close.bind("<Button-1>", lambda e: (on_click(btn_close), self.root.destroy()))
        btn_min.bind("<Enter>", lambda e: btn_min.config(bg=HOVER_COLOR))
        btn_min.bind("<Leave>", lambda e: btn_min.config(bg=HEADER_COLOR))
        btn_min.bind("<Button-1>", lambda e: self.minimize_window(btn_min))
        btn_help.bind("<Enter>", lambda e: btn_help.config(bg=HOVER_COLOR))
        btn_help.bind("<Leave>", lambda e: btn_help.config(bg=HEADER_COLOR))
        btn_help.bind("<Button-1>", lambda e: (on_click(btn_help), self.show_help()))

        for btn in [btn_close, btn_help, btn_min]:
            btn.pack(side=tk.RIGHT, padx=2)

    def setup_interface(self):
        # Área principal com botões e campos
        frame = tk.Frame(self.root, bg=BG_COLOR)
        frame.pack(expand=True, fill=tk.BOTH, padx=20, pady=20)

        self.create_file_selector(frame, self.query_path, 0, "Select the query file containing '{{domain}}'", label_text="Query")
        self.create_file_selector(frame, self.domains_path, 1, "Select the file with the list of domains", label_text="Domain")

        start_btn = tk.Button(frame, text="Start Check", bg=BUTTON_COLOR, fg=TEXT_COLOR,
                              activebackground=HOVER_COLOR, relief=tk.FLAT, command=self.start_check)
        start_btn.grid(row=2, column=0, columnspan=2, pady=20, sticky="ew")
        start_btn.bind("<Enter>", lambda e: start_btn.config(bg=HOVER_COLOR))
        start_btn.bind("<Leave>", lambda e: start_btn.config(bg=BUTTON_COLOR))
        start_btn.bind("<Button-1>", lambda e: start_btn.config(bg=CLICK_COLOR))

    def setup_status_bar(self):
        # Barra inferior com texto de status
        self.status_label = tk.Label(self.root, textvariable=self.status_text, bg=BG_COLOR, fg=STATUS_BLUE,
                                     anchor="w", justify="left")
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(0, 5))

    def update_status(self, text, color):
        # Atualiza mensagem e cor da barra de status
        self.status_text.set(text)
        self.status_label.config(fg=color)

    def create_file_selector(self, frame, path_var, row, tooltip_text, label_text="Escolher arquivo"):
        # Cria botão de seleção de arquivo e campo ao lado
        def on_enter(e): file_btn.config(bg=HOVER_COLOR)
        def on_leave(e): file_btn.config(bg=BUTTON_COLOR)
        def on_click_effect(e):
            orig = file_btn.cget("bg")
            file_btn.config(bg=CLICK_COLOR)
            file_btn.after(150, lambda: file_btn.config(bg=orig))

        file_btn = tk.Button(frame, text=label_text, bg=BUTTON_COLOR, fg=TEXT_COLOR,
                             activebackground=HOVER_COLOR, relief=tk.FLAT,
                             command=lambda: self.select_file(path_var), height=1, width=10)
        file_btn.grid(row=row, column=0, sticky="w", pady=(0, 5))

        file_btn.bind("<Enter>", on_enter)
        file_btn.bind("<Leave>", on_leave)
        file_btn.bind("<Button-1>", on_click_effect)

        path_display = tk.Label(frame, textvariable=path_var, bg="white", fg="#333", width=25,
                                anchor="w", justify="left", relief="sunken", height=1)
        path_display.grid(row=row, column=1, sticky="w", padx=(10, 0))
        Tooltip(path_display, tooltip_text)

    def select_file(self, path_var):
        # Abre diálogo para selecionar arquivos
        filepath = filedialog.askopenfilename()
        if filepath:
            path_var.set(os.path.basename(filepath))
            if path_var == self.query_path:
                self.full_query_path = filepath
            else:
                self.full_domains_path = filepath

    def show_help(self, event=None):
        # Exibe janela com instruções de uso
        help_text = (
        "📘 How to Use Domain Guest Post Checker\n\n"
        "🔹 1. Click the 'Query' button and select a .txt file containing a Google-style search template.\n"
        "     Example: site:{{domain}} guest post\n\n"
        "🔹 2. Click the 'Domain' button and select a .txt file with one domain per line.\n"
        "     Example:\n"
        "       - example.com\n"
        "       - nytimes.com\n\n"
        "🔹 3. Click 'Start Check'. The tool will simulate a search and generate 'results.csv'.\n"
        "     Each domain will be marked as:\n"
        "       ✅ Y: Likely accepts guest posts\n"
        "       ❌ N: No indication found\n"
        "       ⚠️ ISSUE: There was an error during check\n\n"
        "ℹ️ No internet or Google search is actually performed — results are mocked for privacy and testing."
    )
        messagebox.showinfo("Help", help_text)

    def minimize_window(self, btn):
        # Minimiza a janela com workaround por causa do overrideredirect
        def on_click(b):
            orig = b.cget("bg")
            b.config(bg=CLICK_COLOR)
            b.after(150, lambda: b.config(bg=orig))
        on_click(btn)
        self.root.overrideredirect(False)
        self.root.iconify()
        self.root.after(200, lambda: self.root.overrideredirect(True))

    def start_check(self):
        # Executa a verificação com base nos arquivos selecionados
        self.update_status("Processing...", STATUS_BLACK)
        self.root.update_idletasks()

        try:
            with open(self.full_query_path, "r") as f:
                query_template = f.read().strip()
            with open(self.full_domains_path, "r") as f:
                domains = [line.strip() for line in f if line.strip()]
        except Exception as e:
            self.update_status("Error reading files.", STATUS_RED)
            messagebox.showerror("Error", f"Failed to read files: {e}")
            return

        results = []
        for domain in domains:
            query = query_template.replace("{{domain}}", domain)
            try:
                time.sleep(random.uniform(1, 2))
                if "fake" in domain:
                    status = "ISSUE"
                elif "nytimes" in domain:
                    status = "Y"
                else:
                    status = "N"
            except:
                status = "ISSUE"
            results.append((domain, status))

        try:
            with open("results.csv", "w", newline="") as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(["Domain", "Status"])
                for domain, status in results:
                    writer.writerow([domain, status])
            self.update_status("Check completed successfully.", STATUS_GREEN)
            messagebox.showinfo("Done", "Check complete. Results saved to results.csv")
        except Exception as e:
            self.update_status("Error saving results.", STATUS_RED)
            messagebox.showerror("Error", f"Failed to save results: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DomainCheckerApp(root)
    root.mainloop()
