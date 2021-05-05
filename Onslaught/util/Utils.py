import json
import os
import subprocess as subprocess
import socket
import uiautomator2 as uiautomator2
import Device
from WiFi_Info import WiFi_Info
from main import onslaughtapp_package, onslaughtapp_resource_id

key_build_version_release = "ro.build.version.release"
key_product_model = "ro.product.model"
key_product_locale_language = "ro.product.locale.language"


def get_wifi_ssid(device_serial: str):
    dump_wifi_cmd = "adb -s " + device_serial + " shell dumpsys wifi"
    wifi_ssid = ""
    dump_wifi_cmd_result = subprocess.getstatusoutput(dump_wifi_cmd)
    wifi_sys__info = dump_wifi_cmd_result[1].split("\n")
    for line in wifi_sys__info:
        if str(line).__contains__("mWifiInfo SSID: "):
            if line.__contains__("Supplicant state: COMPLETED"):
                print("line = " + line)
                wifi_info = line.split(",")
                for info in wifi_info:
                    if info.__contains__("mWifiInfo SSID:"):
                        wifi_ssid = info.split(":")[1]
                    else:
                        pass
        else:
            pass
    if wifi_ssid.__eq__(""):
        print("have not get the wifi ssid which device had been connected: " + " the device: " + device_serial)
    else:
        print("get the wifi ssid which device had been connected, wifi ssid: " + wifi_ssid + " the device: " + device_serial)
    return wifi_ssid


def is_net_ok():
    test_server = ("www.baidu.com", 443)
    s = socket.socket()
    s.settimeout(5_000)
    try:
        status = s.connect_ex(test_server)
        if status == 0:
            s.close()
            return True
        else:
            return False
    except Exception as exception:
        return False


def get_device_info(device_serial, is_online):
    adb_prop_cmd = "adb -s " + device_serial + " shell getprop"
    adb_prop_cmd_result = subprocess.getstatusoutput(adb_prop_cmd)
    product_model = ""
    build_version_release = ""
    product_locale_language = ""
    if adb_prop_cmd_result[0] == 0:
        for prop in adb_prop_cmd_result[1].split("\n"):
            if prop.__contains__(key_product_model):
                product_model = strip_str_for_prop(prop.split(":")[1])

            if prop.__contains__(key_build_version_release):
                build_version_release = strip_str_for_prop(prop.split(":")[1])

            if prop.__contains__(key_product_locale_language):
                product_locale_language = strip_str_for_prop(prop.split(":")[1])

    android_device = Device.Android_Device(device_serial, product_model,
                                           build_version_release,
                                           product_locale_language, is_online)
    return android_device


def strip_str_for_prop(prop):
    return prop.strip(" ").replace("[", "").replace("]", "")


def is_device_online(device_serial: str):
    is_online = False
    if device_serial == "":
        return is_online
    adb_device_cmd = "adb devices"
    cmd_result = subprocess.getstatusoutput(adb_device_cmd)
    if cmd_result.__len__() > 1:
        device_serial_list = cmd_result[1].split("\n")
        length = device_serial_list.__len__()
        for index in range(device_serial_list.__len__()):
            if 0 < index < length - 1:
                device_info = device_serial_list[index].split("\t")

                if device_info[0].strip(" ").__eq__(device_serial):
                    if device_info[1].strip(" ").__eq__("device"):
                        is_online = True
                    else:
                        is_online = False
    return is_online


def is_device_screen_on(device_serial: str):
    screen_state_cmd = ""
    if device_serial.__eq__(""):
        screen_state_cmd = "adb shell dumpsys deviceidle "
    else:
        screen_state_cmd = "adb -s " + device_serial + " shell dumpsys deviceidle "
    screen_state_cmd_result = subprocess.getstatusoutput(screen_state_cmd)
    result_list = screen_state_cmd_result[1].split("\n")
    for line in result_list:
        if line.__contains__("mScreenOn"):
            line_list = line.split("=")
            if line_list[1].lower().__eq__("false"):
                return False
            elif line_list[1].lower().__eq__("true"):
                return True
            else:
                return False


def switch_off_device_screen(device_serial: str):
    """
    adb shell input keyevent 26
    :param device_serial:
    :param switch_on:
    :return:
    """
    if device_serial.__eq__(""):
        switch_on_cmd = "adb shell input keyevent 26"
    else:
        switch_on_cmd = "adb -s " + device_serial + " shell input keyevent 26"
    if is_device_screen_on(device_serial):
        subprocess.getstatusoutput(switch_on_cmd)


def switch_on_device_screen(device_serial: str):
    """
    adb shell input keyevent 26
    :param device_serial:
    :param switch_on:
    :return:
    """
    switch_on_cmd = ""
    if device_serial.__eq__(""):
        switch_on_cmd = "adb shell input keyevent 26"
    else:
        switch_on_cmd = "adb -s " + device_serial + " shell input keyevent 26"
    is_screen_on = is_device_screen_on(device_serial)
    print("the current device " + device_serial + ", the screen is " + str(is_screen_on))

    if is_screen_on:
        pass
    else:
        subprocess.getstatusoutput(switch_on_cmd)

def get_running_app_pid(package_name: str, device_serial: str):
    """
    获取设备上特定包名的进程pid
    :param package_name: 包名
    :param device_serial: 所在设备的 device serial
    :return: 返回进程的 pid, 如果没有在运行当中返回 0
    """
    adb_pid_cmd = "adb -s " + device_serial + " shell dumpsys activity processes"
    result = subprocess.getstatusoutput(adb_pid_cmd)
    process_key_word = ": ProcessRecord{"
    pid: int = 0
    for line in result[1].split("\n"):
        if line.__contains__(process_key_word):
            if line.__contains__("PID #"):
                process_info = line.split(":")
                if process_info[2].__contains__(package_name):
                    package_uid = process_info[2]
                    if package_uid.__contains__("/"):
                        if package_uid.split("/")[0].__eq__(package_name):
                            pid = int(process_info[0].split("#")[1])

    print("the current package " + package_name + ", the pid is " + pid)
    return pid


def is_onslaught_app_installed(device_serial):
    package_name = "me.xuwanjin.onslaughtapp"
    package_location_cmd = "adb -s " + device_serial + " shell pm path " + package_name
    result = subprocess.getstatusoutput(package_location_cmd)
    if result[1].__contains__(package_name):
        return True
    return False


def is_app_installed(device_serial: str, package_name: str):
    package_location_cmd = "adb -s " + device_serial + " shell pm path " + package_name
    result = subprocess.getstatusoutput(package_location_cmd)
    if result[1].__contains__(package_name):
        return True
    return False


def set_device_never_sleep(device_serial: str):
    """
    设置设备永不睡眠的模式
    :param device_serial:
    :return:
    """
    never_sleep_cmd = "adb -s " + device_serial + " shell settings put system screen_off_timeout 2147483647"
    subprocess.getstatusoutput(never_sleep_cmd)


def parse_wifi_list_json():
    wifi_list = []
    current_path = os.getcwd()
    print("the current path " + str(current_path))
    with open(file="wifi_list") as wifi_json_file:
        line = wifi_json_file.readline()
        while line:
            wifi_info_group = line.split(",")
            if wifi_info_group.__len__() == 2:
                ssid = wifi_info_group[0].split("=")[1]
                password = wifi_info_group[1].split("=")[1].replace("\n", "")
                wifi_info = WiFi_Info(ssid, password)
                wifi_list.append(wifi_info)
                line = wifi_json_file.readline()
    return wifi_list


def switch_on_wifi(device_serial: str):
    # adb shell svc wifi enable
    switch_on_wifi_cmd = "adb -s " + device_serial + " shell svc wifi enable"
    subprocess.getstatusoutput(switch_on_wifi_cmd)


def switch_off_wifi(device_serial: str):
    # adb shell svc wifi disable
    switch_off_wifi_cmd = "adb -s " + device_serial + " shell svc wifi disable"
    subprocess.getstatusoutput(switch_off_wifi_cmd)
