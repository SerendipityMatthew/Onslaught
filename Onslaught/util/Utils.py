import subprocess as subprocess


def get_wifi_ssid(device_serial: str):
    dump_wifi_cmd = "adb shell " + device_serial + "dumpsys wifi"
    wifi_ssid = ""
    dump_wifi_cmd_result = subprocess.getstatusoutput(dump_wifi_cmd)
    wifi_sys__info = dump_wifi_cmd_result[1].split("\n")
    for line in wifi_sys__info:
        if str(line).__contains__("mWifiInfo SSID: "):
            if line.__contains__("Supplicant state: COMPLETED"):
                wifi_info = line.split(",")
                for info in wifi_info:
                    if info.__contains__("mWifiInfo SSID:"):
                        wifi_ssid = info.split(":")[1]
                    else:
                        pass
        else:
            pass
    if wifi_ssid.__eq__(""):
        print("have not get the wifi ssid which device had been connected: ")
    else:
        print("get the wifi ssid which device had been connected, wifi ssid: " + wifi_ssid)
    return wifi_ssid
