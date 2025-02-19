import subprocess
import time

def get_available_wifi():
    """Lấy danh sách WiFi khả dụng"""
    output = subprocess.check_output("nmcli -t -f SSID dev wifi list", shell=True).decode()
    available_networks = output.strip().split("\n")
    return [ssid for ssid in available_networks if ssid]

def get_saved_wifi():
    """Lấy danh sách WiFi đã từng kết nối"""
    output = subprocess.check_output("nmcli -t -f NAME connection show", shell=True).decode()
    saved_networks = output.strip().split("\n")
    return [ssid for ssid in saved_networks if ssid]

def connect_to_wifi(ssid):
    """Kết nối tới WiFi"""
    print(f"🔄 Đang kết nối {ssid} ...")
    result = subprocess.run(["nmcli", "connection", "up", ssid], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Đã kết nối thành công {ssid}!")
    else:
        print(f"Không thể kết nối {ssid}. Lỗi:\n{result.stderr}")

def check_and_reconnect():
    """Kiểm tra và kết nối lại WiFi nếu mất kết nối"""
    while True:
        try:
            result = subprocess.run(["ping", "-c", "2", "8.8.8.8"], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(" Internet vẫn hoạt động, không cần kết nối lại.")
            else:
                print("⚠️ Mất kết nối! Đang tìm mạng WiFi khả dụng...")

                available_wifi = get_available_wifi()
                saved_wifi = get_saved_wifi()
                
                # Tìm mạng WiFi đã lưu trong danh sách khả dụng
                for wifi in saved_wifi:
                    if wifi in available_wifi:
                        connect_to_wifi(wifi)
                        break
                else:
                    print("Không tìm thấy mạng WiFi nào đã lưu.")
            
            time.sleep(30)

        except KeyboardInterrupt:
            print(" Dừng chương trình.")
            break

check_and_reconnect()
