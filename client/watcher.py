import os
import socket
import threading
import tkinter as tk
import uuid
import time

import requests
import socketio


# ============================================================
# CONFIG
# ============================================================

SERVER_URL = "http://127.0.0.1:5000"
ADMIN_TOKEN = "WATCHER-ADMIN-2026"

WINDOW_WIDTH = 280
WINDOW_HEIGHT = 150

BACKGROUND = "#000000"
TEXT_COLOR = "#eeeeee"
DIM_COLOR = "#777777"

CLIENT_ID = str(uuid.uuid4())

sio = socketio.Client(reconnection=True)


# ============================================================
# WATCHER
# ============================================================

class Watcher:

    def __init__(self):
        self.root = tk.Tk()

        self.root.title("The Watcher")

        # Không viền
        self.root.overrideredirect(True)

        # Hạn chế xuất hiện như cửa sổ bình thường trên taskbar
        try:
            self.root.wm_attributes("-toolwindow", True)
        except Exception:
            pass

        # Luôn nằm trên
        self.root.attributes("-topmost", True)

        self.root.configure(bg=BACKGROUND)

        self.center_window()

        self.troll_running = False
        self.message_id = 0

        # ====================================================
        # MAIN FRAME
        # ====================================================

        self.frame = tk.Frame(
            self.root,
            bg=BACKGROUND
        )

        self.frame.pack(
            fill="both",
            expand=True
        )

        # ====================================================
        # DOT
        # ====================================================

        self.dot = tk.Label(
            self.frame,
            text="●",
            fg=TEXT_COLOR,
            bg=BACKGROUND,
            font=("Consolas", 24)
        )

        self.dot.place(
            relx=0.5,
            rely=0.30,
            anchor="center"
        )

        # Không click nữa.
        # Watcher tự bắt đầu sự kiện sau khi mở.

        # ====================================================
        # MESSAGE
        # ====================================================

        self.message = tk.Label(
            self.frame,
            text="",
            fg=TEXT_COLOR,
            bg=BACKGROUND,
            font=("Consolas", 10),
            wraplength=240,
            justify="center"
        )

        self.message.place(
            relx=0.5,
            rely=0.67,
            anchor="center"
        )

        # ====================================================
        # FAKE CLOSE BUTTON
        # ====================================================

        self.fake_close = tk.Label(
            self.frame,
            text="×",
            fg=TEXT_COLOR,
            bg=BACKGROUND,
            font=("Arial", 11)
        )

        self.fake_close.place(
            relx=0.94,
            rely=0.12,
            anchor="center"
        )

        # Không bind.
        # Đây chỉ là nút X giả.

        # ====================================================
        # REAL CLOSE BUTTON
        # ====================================================

        self.real_close = tk.Label(
            self.frame,
            text="×",
            fg=BACKGROUND,
            bg=BACKGROUND,
            font=("Arial", 7)
        )

        self.real_close.place(
            relx=0.97,
            rely=0.94,
            anchor="se"
        )

        self.real_close.bind(
            "<Button-1>",
            self.close
        )

        # ====================================================
        # START
        # ====================================================

        self.blink()

        # Tự động bắt đầu sau 2 giây
        self.root.after(
            2000,
            self.start_troll
        )

        # Kết nối server
        threading.Thread(
            target=self.connect_server,
            daemon=True
        ).start()

    # ========================================================
    # CENTER WINDOW
    # ========================================================

    def center_window(self):

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2

        self.root.geometry(
            f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}"
        )

    # ========================================================
    # BLINK
    # ========================================================

    def blink(self):

        self.dot.config(
            fg=TEXT_COLOR
        )

        self.root.after(
            1200,
            self.blink_off
        )

    def blink_off(self):

        self.dot.config(
            fg=BACKGROUND
        )

        self.root.after(
            300,
            self.blink
        )

    # ========================================================
    # TYPEWRITER
    # ========================================================

    def typewriter(
        self,
        text,
        message_id,
        callback=None,
        index=0
    ):

        if message_id != self.message_id:
            return

        if index <= len(text):

            self.message.config(
                text=text[:index]
            )

            self.root.after(
                25,
                lambda: self.typewriter(
                    text,
                    message_id,
                    callback,
                    index + 1
                )
            )

        else:

            if callback:
                self.root.after(
                    500,
                    callback
                )

    # ========================================================
    # TROLL START
    # ========================================================

    def start_troll(self):

        if self.troll_running:
            return

        self.troll_running = True

        self.message_id += 1

        current_id = self.message_id

        self.typewriter(
            "I noticed something.",
            current_id,
            lambda: self.troll_step_2(current_id)
        )

    # ========================================================
    # STEP 2
    # ========================================================

    def troll_step_2(self, message_id):

        if message_id != self.message_id:
            return

        self.typewriter(
            "Virus scan initiated...",
            message_id,
            lambda: self.troll_step_3(message_id)
        )

    # ========================================================
    # STEP 3
    # ========================================================

    def troll_step_3(self, message_id):

        self.typewriter(
            "Checking paths...",
            message_id,
            lambda: self.troll_step_4(message_id)
        )

    # ========================================================
    # STEP 4
    # ========================================================

    def troll_step_4(self, message_id):

        self.typewriter(
            "Scanning local directories...",
            message_id,
            lambda: self.troll_step_5(message_id)
        )

    # ========================================================
    # STEP 5
    # ========================================================

    def troll_step_5(self, message_id):

        self.typewriter(
            "Preparing file...",
            message_id,
            lambda: self.troll_download(message_id)
        )

    # ========================================================
    # FAKE DOWNLOAD
    # ========================================================

    def troll_download(self, message_id):

        if message_id != self.message_id:
            return

        self.download_progress = 0

        self.update_download(
            message_id
        )

    # ========================================================
    # DOWNLOAD PROGRESS
    # ========================================================

    def update_download(self, message_id):

        if message_id != self.message_id:
            return

        # Dừng ở 99% lâu hơn
        if self.download_progress >= 99:

            self.message.config(
                text=(
                    "Downloading...\n"
                    "watcher_log_0000.txt\n"
                    "[█████████░] 99%"
                )
            )

            self.root.after(
                3000,
                lambda: self.finish_download(
                    message_id
                )
            )

            return

        self.download_progress += 3

        if self.download_progress > 99:
            self.download_progress = 99

        total_blocks = 10

        filled = int(
            self.download_progress / 100 * total_blocks
        )

        empty = total_blocks - filled

        bar = (
            "█" * filled +
            "░" * empty
        )

        self.message.config(
            text=(
                "Downloading...\n"
                "watcher_log_0000.txt\n"
                f"[{bar}] {self.download_progress}%"
            )
        )

        self.root.after(
            120,
            lambda: self.update_download(
                message_id
            )
        )

    # ========================================================
    # FINISH DOWNLOAD
    # ========================================================

    def finish_download(self, message_id):

        if message_id != self.message_id:
            return

        self.create_safe_file()

        self.message.config(
            text="Download complete."
        )

        self.root.after(
            1800,
            lambda: self.return_to_initial(
                message_id
            )
        )

    # ========================================================
    # SAFE LOCAL FILE
    # ========================================================

    def create_safe_file(self):

        try:

            downloads = os.path.join(
                os.path.expanduser("~"),
                "Downloads"
            )

            os.makedirs(
                downloads,
                exist_ok=True
            )

            path = os.path.join(
                downloads,
                "watcher_log_0000.txt"
            )

            content = """WATCHER LOG 0000

Observation started.

Automatic event detected.

I was already watching.

This file was created by The Watcher.

Nothing was downloaded from the internet.

Observation continues...
"""

            with open(
                path,
                "w",
                encoding="utf-8"
            ) as file:

                file.write(content)

        except Exception:
            pass

    # ========================================================
    # RETURN
    # ========================================================

    def return_to_initial(self, message_id):

        if message_id != self.message_id:
            return

        self.message.config(
            text=""
        )

        self.troll_running = False

    # ========================================================
    # SERVER CONNECTION
    # ========================================================

    def connect_server(self):

        try:

            @sio.event
            def connect():

                try:

                    hostname = socket.gethostname()

                    sio.emit(
                        "identify",
                        {
                            "client_id": CLIENT_ID,
                            "hostname": hostname,
                            "version": "1.0"
                        }
                    )

                except Exception:
                    pass

            @sio.event
            def watcher_message(data):

                try:

                    message = data.get(
                        "message",
                        ""
                    )

                    duration = data.get(
                        "duration",
                        5
                    )

                    effect = data.get(
                        "effect",
                        "normal"
                    )

                    self.root.after(
                        0,
                        lambda: self.show_remote_message(
                            message,
                            duration,
                            effect
                        )
                    )

                except Exception:
                    pass

            sio.connect(
                SERVER_URL,
                transports=[
                    "websocket",
                    "polling"
                ]
            )

            while True:

                try:

                    sio.emit(
                        "heartbeat",
                        {
                            "client_id": CLIENT_ID
                        }
                    )

                except Exception:
                    pass

                time.sleep(10)

        except Exception:
            pass

    # ========================================================
    # REMOTE MESSAGE
    # ========================================================

    def show_remote_message(
        self,
        text,
        duration,
        effect
    ):

        self.message_id += 1

        current_id = self.message_id

        if effect == "blink":

            self.show_blink_message(
                text,
                current_id
            )

        elif effect == "slow":

            self.typewriter(
                text,
                current_id
            )

        else:

            self.message.config(
                text=text
            )

        self.root.after(
            int(duration * 1000),
            lambda: self.clear_remote_message(
                current_id
            )
        )

    # ========================================================
    # BLINK MESSAGE
    # ========================================================

    def show_blink_message(
        self,
        text,
        message_id
    ):

        if message_id != self.message_id:
            return

        self.message.config(
            text=text
        )

        self.root.after(
            350,
            lambda: self.hide_blink_message(
                text,
                message_id
            )
        )

    def hide_blink_message(
        self,
        text,
        message_id
    ):

        if message_id != self.message_id:
            return

        self.message.config(
            text=""
        )

        self.root.after(
            350,
            lambda: self.show_blink_message(
                text,
                message_id
            )
        )

    # ========================================================
    # CLEAR
    # ========================================================

    def clear_remote_message(
        self,
        message_id
    ):

        if message_id != self.message_id:
            return

        self.message.config(
            text=""
        )

    # ========================================================
    # CLOSE
    # ========================================================

    def close(self, event=None):

        try:
            sio.disconnect()
        except Exception:
            pass

        self.root.destroy()

    # ========================================================
    # RUN
    # ========================================================

    def run(self):

        self.root.mainloop()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    watcher = Watcher()

    watcher.run()