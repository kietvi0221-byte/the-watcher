import tkinter as tk
from tkinter import ttk, messagebox
import requests


# ============================================================
# CONFIG
# ============================================================

SERVER_URL = "http://127.0.0.1:5000"

ADMIN_TOKEN = "WATCHER-ADMIN-2026"

BG = "#070707"
PANEL = "#0D0D0D"
PANEL_2 = "#111111"

TEXT = "#D8D8D8"
DIM = "#666666"
GREEN = "#777777"
BORDER = "#1A1A1A"


# ============================================================
# CONTROL PANEL
# ============================================================

class ControlPanel:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "The Watcher"
        )

        self.root.geometry(
            "700x560"
        )

        self.root.configure(
            bg=BG
        )

        self.root.minsize(
            650,
            520
        )

        self.selected_client = None
        self.client_data = []

        self.build_style()
        self.build_ui()

        self.refresh_clients()

    # ========================================================
    # STYLE
    # ========================================================

    def build_style(self):

        style = ttk.Style()

        try:
            style.theme_use(
                "clam"
            )
        except Exception:
            pass

        style.configure(
            "Watcher.TCombobox",
            fieldbackground=PANEL_2,
            background=PANEL_2,
            foreground=TEXT,
            bordercolor=BORDER,
            lightcolor=BORDER,
            darkcolor=BORDER
        )

    # ========================================================
    # UI
    # ========================================================

    def build_ui(self):

        # ----------------------------------------------------
        # HEADER
        # ----------------------------------------------------

        header = tk.Frame(
            self.root,
            bg=BG
        )

        header.pack(
            fill="x",
            padx=35,
            pady=(25, 10)
        )

        title = tk.Label(
            header,
            text="●  THE WATCHER",
            font=("Consolas", 18),
            fg=TEXT,
            bg=BG
        )

        title.pack(
            anchor="w"
        )

        subtitle = tk.Label(
            header,
            text="CONTROL",
            font=("Consolas", 9),
            fg=DIM,
            bg=BG
        )

        subtitle.pack(
            anchor="w",
            pady=(3, 0)
        )

        # ----------------------------------------------------
        # SEPARATOR
        # ----------------------------------------------------

        separator = tk.Frame(
            self.root,
            bg=BORDER,
            height=1
        )

        separator.pack(
            fill="x",
            padx=35,
            pady=10
        )

        # ----------------------------------------------------
        # WATCHERS
        # ----------------------------------------------------

        label = tk.Label(
            self.root,
            text="WATCHERS",
            font=("Consolas", 9),
            fg=DIM,
            bg=BG
        )

        label.pack(
            anchor="w",
            padx=35,
            pady=(10, 5)
        )

        list_frame = tk.Frame(
            self.root,
            bg=PANEL
        )

        list_frame.pack(
            fill="x",
            padx=35
        )

        self.client_list = tk.Listbox(
            list_frame,
            bg=PANEL,
            fg=TEXT,
            selectbackground="#202020",
            selectforeground=TEXT,
            font=("Consolas", 10),
            height=7,
            borderwidth=0,
            highlightthickness=0,
            activestyle="none"
        )

        self.client_list.pack(
            fill="x",
            padx=8,
            pady=8
        )

        self.client_list.bind(
            "<<ListboxSelect>>",
            self.select_client
        )

        # ----------------------------------------------------
        # MESSAGE
        # ----------------------------------------------------

        label = tk.Label(
            self.root,
            text="MESSAGE",
            font=("Consolas", 9),
            fg=DIM,
            bg=BG
        )

        label.pack(
            anchor="w",
            padx=35,
            pady=(18, 5)
        )

        self.message = tk.Text(
            self.root,
            height=5,
            bg=PANEL,
            fg=TEXT,
            insertbackground=TEXT,
            font=("Consolas", 10),
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=BORDER,
            highlightcolor="#333333",
            padx=12,
            pady=10,
            wrap="word"
        )

        self.message.pack(
            fill="x",
            padx=35
        )

        # ----------------------------------------------------
        # OPTIONS
        # ----------------------------------------------------

        options = tk.Frame(
            self.root,
            bg=BG
        )

        options.pack(
            fill="x",
            padx=35,
            pady=15
        )

        # Effect

        tk.Label(
            options,
            text="EFFECT",
            font=("Consolas", 8),
            fg=DIM,
            bg=BG
        ).pack(
            side="left"
        )

        self.effect = ttk.Combobox(
            options,
            values=[
                "typewriter",
                "instant",
                "glitch",
                "fade"
            ],
            state="readonly",
            width=13,
            style="Watcher.TCombobox"
        )

        self.effect.set(
            "typewriter"
        )

        self.effect.pack(
            side="left",
            padx=(8, 25)
        )

        # Duration

        tk.Label(
            options,
            text="DURATION",
            font=("Consolas", 8),
            fg=DIM,
            bg=BG
        ).pack(
            side="left"
        )

        self.duration = ttk.Combobox(
            options,
            values=[
                "3",
                "5",
                "10",
                "15",
                "30",
                "60"
            ],
            state="readonly",
            width=6,
            style="Watcher.TCombobox"
        )

        self.duration.set(
            "5"
        )

        self.duration.pack(
            side="left",
            padx=8
        )

        # ----------------------------------------------------
        # SEND BUTTON
        # ----------------------------------------------------

        self.send_button = tk.Button(
            self.root,
            text="SEND",
            command=self.send_message,
            font=("Consolas", 10),
            fg=TEXT,
            bg="#151515",
            activebackground="#252525",
            activeforeground=TEXT,
            relief="flat",
            borderwidth=0,
            cursor="hand2"
        )

        self.send_button.pack(
            pady=5,
            ipadx=50,
            ipady=9
        )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        self.status = tk.Label(
            self.root,
            text="Watching.",
            font=("Consolas", 8),
            fg=DIM,
            bg=BG
        )

        self.status.pack(
            pady=(8, 15)
        )

    # ========================================================
    # GET CLIENTS
    # ========================================================

    def get_clients(self):

        try:

            response = requests.get(
                f"{SERVER_URL}/api/clients",
                headers={
                    "X-Watcher-Token":
                        ADMIN_TOKEN
                },
                timeout=3
            )

            if response.status_code != 200:

                return []

            data = response.json()

            return data.get(
                "clients",
                []
            )

        except Exception:

            self.status.config(
                text="Server unavailable."
            )

            return []

    # ========================================================
    # REFRESH
    # ========================================================

    def refresh_clients(self):

        clients = self.get_clients()

        previous = self.selected_client

        self.client_list.delete(
            0,
            tk.END
        )

        self.client_data = []

        for client in clients:

            if client["status"] == "online":

                status = "●"

            else:

                status = "○"

            text = (
                f"{status}  "
                f"{client['client_id']}   "
                f"{client['hostname']}"
            )

            self.client_list.insert(
                tk.END,
                text
            )

            self.client_data.append(
                client
            )

        # Try to preserve selection

        if previous:

            for i, client in enumerate(
                self.client_data
            ):

                if (
                    client["client_id"]
                    ==
                    previous["client_id"]
                ):

                    self.client_list.selection_set(
                        i
                    )

                    self.selected_client = client

                    break

        self.root.after(
            3000,
            self.refresh_clients
        )

    # ========================================================
    # SELECT
    # ========================================================

    def select_client(self, event):

        selection = (
            self.client_list.curselection()
        )

        if not selection:
            return

        index = selection[0]

        self.selected_client = (
            self.client_data[index]
        )

        self.status.config(
            text=
            "Selected  "
            +
            self.selected_client[
                "client_id"
            ]
        )

    # ========================================================
    # SEND
    # ========================================================

    def send_message(self):

        if not self.selected_client:

            messagebox.showwarning(
                "The Watcher",
                "Select a Watcher first."
            )

            return

        if (
            self.selected_client["status"]
            !=
            "online"
        ):

            messagebox.showwarning(
                "The Watcher",
                "This Watcher is offline."
            )

            return

        message = self.message.get(
            "1.0",
            tk.END
        ).strip()

        if not message:

            messagebox.showwarning(
                "The Watcher",
                "Message is empty."
            )

            return

        effect = self.effect.get()

        duration = int(
            self.duration.get()
        )

        try:

            response = requests.post(
                f"{SERVER_URL}/api/send",

                headers={
                    "X-Watcher-Token":
                        ADMIN_TOKEN
                },

                json={
                    "client_id":
                        self.selected_client[
                            "client_id"
                        ],

                    "message":
                        message,

                    "effect":
                        effect,

                    "duration":
                        duration
                },

                timeout=5
            )

            data = response.json()

            if response.status_code == 200:

                self.status.config(
                    text="Message sent."
                )

                self.message.delete(
                    "1.0",
                    tk.END
                )

            else:

                self.status.config(
                    text=
                    data.get(
                        "error",
                        "Send failed."
                    )
                )

        except Exception:

            self.status.config(
                text="Server unavailable."
            )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = ControlPanel(
        root
    )

    root.mainloop()