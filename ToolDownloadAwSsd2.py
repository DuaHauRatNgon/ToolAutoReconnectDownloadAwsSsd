import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
import threading
import time
import re
import speedtest
import os

root = tk.Tk()
root.title("AWS S3 Download Manager")
root.geometry("700x400")

progress = ttk.Progressbar(root, length=500, mode="determinate")
progress.pack(pady=10)

wifi_status_label = tk.Label(root, text="Mạng: Đang kiểm tra...", font=("Arial", 12))
wifi_status_label.pack()

output_text = scrolledtext.ScrolledText(root, height=10, width=85)
output_text.pack()


def check_wifi_speed():
    while True:
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            download_speed = st.download() / 1_000_000  # Mbps

            if download_speed >= 10:
                color = "green"
                status_text = f"Mạng: Tốt ({download_speed:.2f} Mbps)"
            elif 1 <= download_speed < 10:
                color = "yellow"
                status_text = f"Mạng: Yếu ({download_speed:.2f} Mbps)"
            else:
                color = "red"
                status_text = "Mạng: Mất kết nối!"

            wifi_status_label.config(text=status_text, fg=color)

        except:
            wifi_status_label.config(text="Mạng: Không có kết nối!", fg="red")

        time.sleep(10)  


def run_aws_command(command):
    """Chạy lệnh AWS CLI và hiển thị tiến trình tải"""
    try:
        aws_access_key = re.search(r"export AWS_ACCESS_KEY_ID=(.*)", command)
        aws_secret_key = re.search(r"export AWS_SECRET_ACCESS_KEY=(.*)", command)
        aws_session_token = re.search(r"export AWS_SESSION_TOKEN=(.*)", command)

        if aws_access_key and aws_secret_key:
            aws_env = {
                "AWS_ACCESS_KEY_ID": aws_access_key.group(1).strip(),
                "AWS_SECRET_ACCESS_KEY": aws_secret_key.group(1).strip(),
                "AWS_SESSION_TOKEN": aws_session_token.group(1).strip() if aws_session_token else "",
            }
        else:
            messagebox.showerror("Lỗi", "Không tìm thấy thông tin AWS_ACCESS_KEY_ID hoặc AWS_SECRET_ACCESS_KEY")
            return

        aws_s3_command = re.search(r"aws s3 cp .*", command)
        if not aws_s3_command:
            messagebox.showerror("Lỗi", "Không tìm thấy lệnh 'aws s3 cp'")
            return

        process = subprocess.Popen(
            aws_s3_command.group(0),
            shell=True,
            env={**aws_env, **dict(os.environ)},
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )

        for line in process.stdout:
            output_text.insert(tk.END, line)
            output_text.see(tk.END)

            match = re.search(r"(\d+)%", line)
            if match:
                progress["value"] = int(match.group(1))
                root.update_idletasks()

        process.wait()
        if process.returncode == 0:
            output_text.insert(tk.END, " Tải file hoàn tất!\n")
            progress["value"] = 100
        else:
            output_text.insert(tk.END, " Lỗi khi tải file!\n")

    except Exception as e:
        messagebox.showerror("Lỗi", str(e))


def start_download():
    """Nhận lệnh từ input và chạy"""
    command = output_text.get("1.0", tk.END).strip()
    if not command:
        messagebox.showerror("Lỗi", "Vui lòng nhập lệnh AWS CLI")
        return

    # Chạy trong luồng riêng để không làm lag giao diện
    threading.Thread(target=run_aws_command, args=(command,), daemon=True).start()


download_button = tk.Button(root, text="Tải file", command=start_download, font=("Arial", 12))
download_button.pack(pady=10)

# Chạy kiểm tra tốc độ mạng trong luồng riêng
threading.Thread(target=check_wifi_speed, daemon=True).start()

root.mainloop()
