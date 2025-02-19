import subprocess
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import time

def get_current_wifi():
    """Lấy mạng WiFi hiện tại đang kết nối"""
    result = subprocess.run(["nmcli", "-t", "-f", "ACTIVE,SSID", "con", "show"], capture_output=True, text=True)
    for line in result.stdout.strip().split("\n"):
        if line.startswith("yes:"):
            return line.split(":")[1]  
    return None

def get_wifi_list():
    """Lấy danh sách WiFi khả dụng và tín hiệu của chúng"""
    result = subprocess.run(["nmcli", "-t", "-f", "SSID,SIGNAL", "dev", "wifi"], capture_output=True, text=True)
    wifi_networks = result.stdout.strip().split("\n")
    wifi_list = []
    
    for wifi in wifi_networks:
        if wifi:
            ssid, signal = wifi.split(":")
            wifi_list.append((ssid, int(signal)))

    # Sắp xếp danh sách theo tín hiệu mạnh nhất
    wifi_list.sort(key=lambda x: x[1], reverse=True)
    return wifi_list

def connect_to_wifi(ssid):
    """Kết nối tới WiFi bằng nmcli"""
    print(f"Kết nối tới {ssid} ...")
    result = subprocess.run(["nmcli", "dev", "wifi", "connect", ssid], capture_output=True, text=True)
    if "successfully" in result.stdout:
        print(f"Kết nối thành công {ssid}")
    else:
        print(f"Lỗi kết nối {ssid}: {result.stderr}")

def auto_reconnect_wifi():
    """Tự động tìm WiFi mạnh nhất và kết nối nếu mất mạng"""
    while True:
        current_wifi = get_current_wifi()
        if not current_wifi:
            print("Mất kết nối, tìm WiFi mới...")
            wifi_list = get_wifi_list()
            if wifi_list:
                best_wifi = wifi_list[0][0]
                print(f"Kết nối tới WiFi mạnh nhất: {best_wifi}")
                connect_to_wifi(best_wifi)
        
        time.sleep(10) 

def run_aws_command():
    """Chạy AWS CLI command từ input"""
    aws_command = aws_command_text.get("1.0", tk.END).strip()
    if not aws_command:
        messagebox.showerror("Lỗi", "Vui lòng nhập lệnh AWS CLI!")
        return
    
    def execute():
        try:
            process = subprocess.Popen(aws_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for line in process.stdout:
                log_text.insert(tk.END, line)
                log_text.yview(tk.END) 
            
            for line in process.stderr:
                log_text.insert(tk.END, "LỖI: " + line)
                log_text.yview(tk.END)

        except Exception as e:
            log_text.insert(tk.END, f"Lỗi khi chạy lệnh: {e}\n")

    threading.Thread(target=execute, daemon=True).start()

#  GUI với Tkinter
root = tk.Tk()
root.title("AWS CLI Downloader")

tk.Label(root, text="Nhập AWS CLI command:").pack(pady=5)

aws_command_text = scrolledtext.ScrolledText(root, width=80, height=5)
aws_command_text.pack(padx=10, pady=5)

run_button = tk.Button(root, text="Chạy AWS CLI", command=run_aws_command)
run_button.pack(pady=5)

tk.Label(root, text="Log:").pack(pady=5)

log_text = scrolledtext.ScrolledText(root, width=80, height=10)
log_text.pack(padx=10, pady=5)

# Chạy auto reconnect WiFi trong luồng riêng
threading.Thread(target=auto_reconnect_wifi, daemon=True).start()

root.mainloop()
