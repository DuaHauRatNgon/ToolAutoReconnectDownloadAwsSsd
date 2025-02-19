import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess

def run_aws_command():
    command = text_input.get("1.0", tk.END).strip()
    if not command:
        messagebox.showerror("Lỗi", "Vui lòng nhập lệnh AWS CLI")
        return
    
    try:
        # Chạy lệnh AWS CLI
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output_text.delete("1.0", tk.END)  # Xóa kết quả cũ
        output_text.insert(tk.END, result.stdout if result.stdout else result.stderr)
    except Exception as e:
        messagebox.showerror("Lỗi thực thi", str(e))

root = tk.Tk()
root.title("AWS CLI Runner")

tk.Label(root, text="Nhập lệnh AWS CLI:").pack()
text_input = scrolledtext.ScrolledText(root, height=5, width=80)
text_input.pack()

tk.Button(root, text="Chạy Lệnh", command=run_aws_command).pack()

tk.Label(root, text="Kết quả:").pack()
output_text = scrolledtext.ScrolledText(root, height=10, width=80)
output_text.pack()

root.mainloop()
