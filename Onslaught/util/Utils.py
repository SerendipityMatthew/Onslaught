import subprocess as subprocess
import socket

import Device

key_build_version_release = "ro.build.version.release"
key_product_model = "ro.product.model"
key_product_locale_language = "ro.product.locale.language"


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
    print("=========== : switch_on_device_screen: " + str(is_screen_on))
    if is_screen_on:

        print("+++++++++++++++")
    else:
        print("------------   " + switch_on_cmd)
        subprocess.getstatusoutput(switch_on_cmd)
