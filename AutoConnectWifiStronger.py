import subprocess
import time

def get_wifi_list():
    result = subprocess.run(["nmcli", "-t", "-f", "SSID,SIGNAL", "dev", "wifi"], capture_output=True, text=True)
    wifi_networks = result.stdout.strip().split("\n")
    wifi_list = []
    
    for wifi in wifi_networks:
        if wifi:
            ssid, signal = wifi.split(":")
            wifi_list.append((ssid, int(signal)))

    #sort down by rate 
    wifi_list.sort(key=lambda x: x[1], reverse=True)
    return wifi_list

def get_current_wifi():
    result = subprocess.run(["nmcli", "-t", "-f", "ACTIVE,SSID", "con", "show"], capture_output=True, text=True)
    for line in result.stdout.strip().split("\n"):
        if line.startswith("yes:"):
            return line.split(":")[1]  #return current ssid 
    return None

def connect_to_wifi(ssid):
    print(f"Đang kết nối tới {ssid} ...")
    result = subprocess.run(["nmcli", "dev", "wifi", "connect", ssid], capture_output=True, text=True)
    if "successfully" in result.stdout:
        print(f"Kết nối thành công đến {ssid}")
    else:
        print(f"Lỗi khi kết nối {ssid}: {result.stderr}")

def auto_connect_best_wifi():
    current_wifi = get_current_wifi()
    wifi_list = get_wifi_list()

    print(f"WiFi hiện tại: {current_wifi}")
    print("Danh sách WiFi khả dụng:")
    for ssid, signal in wifi_list:
        print(f" - {ssid}: {signal} dBm")

    if wifi_list and (not current_wifi or wifi_list[0][0] != current_wifi):
        best_wifi = wifi_list[0][0]
        print(f"Kết nối tới WiFi mạnh nhất: {best_wifi}")
        connect_to_wifi(best_wifi)

if __name__ == "__main__":
    while True:
        auto_connect_best_wifi()
        time.sleep(30) 
