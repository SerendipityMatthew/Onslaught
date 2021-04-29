import os
import subprocess as subprocess
import time as time

import uiautomator2 as uiautomator2
from uiautomator2 import UiObjectNotFoundError

import Apk_Info as Apk_Info
import util.Utils as Utils
from Device import Android_Device

adb_devices_cmd = "adb devices"
key_build_version_release = "ro.build.version.release"
key_product_model = "ro.product.model"
key_product_locale_language = "ro.product.locale.language"
deye_package = "com.23"
current_test_package = deye_package

settings_package = "com.android.settings"
nexus_settings_activity = "com.android.settings.Settings"
rom_settings_activity = "com.android.settings.MainSettings"
rom_settings_wifi_activity = "com.android.settings.Settings$WifiSettingsActivity"
wifi_connect_resource_id = "android:id/button1"
wifi_219_password = "785174509I350"
wifi_219_name = "219"
wifi_matthew_name = "Matthew_2.4G"
wifi_matthew_password = "785174509"
wifi_switch_widget_resource_id = "com.android.settings:id/switch_widget"
wifi_name = wifi_219_name
wifi_password = wifi_219_password


def strip_str_for_prop(prop):
    return prop.strip(" ").replace("[", "").replace("]", "")


def get_device():
    adb_devices_result = subprocess.getstatusoutput(adb_devices_cmd)
    print(adb_devices_result)
    device_dict = {}
    if adb_devices_result[0] == 0:
        split_result = adb_devices_result[1].split("\n")
        devices_list = split_result[1:split_result.__len__() - 1]
        for devices_id_record in devices_list:
            serial = devices_id_record.split("\t")[0]
            is_online = devices_id_record.split("\t")[1]
            print("is online = " + str(is_online))
            key_is_online = True
            if is_online.__contains__("offline"):
                key_is_online = False

            android_device = Utils.get_device_info(serial, key_is_online)

            device_dict[android_device.deviceId] = android_device
    return device_dict


def connect_to_wifi(wifi_name, wifi_password):
    connected_device.app_start(package_name=settings_package,
                               activity=rom_settings_wifi_activity)
    time.sleep(2)
    if not connected_device(text=wifi_name).exists:
        connected_device.swipe(300, 900, 300, 200)

    connected_device(text=wifi_name).click()
    """
        在某些情况下, 这个设备已经连接过这个 WiFi 了, 执行 sendkeys 会报错, 
    """
    try:
        connected_device.send_keys(wifi_password, clear=True)
    except UiObjectNotFoundError as error:
        print(error)
    finally:
        if connected_device(text="连接").exists():
            connected_device(text="连接").click()
        if connected_device(text="Connect").exists():
            connected_device(text="Connect").click()
        if connected_device(text="CONNECT").exists():
            connected_device(text="CONNECT").click()
    time.sleep(3)


def catch_device_log(device: Android_Device, package_name: str):
    if not device.isOnline():
        return
    # 再次检查一下设备是否在线
    realTimeDevice = get_device()[device.deviceId]
    print("-----------------" + str(realTimeDevice.isOnline()))
    if not realTimeDevice.isOnline():
        return

    # log 的路径  包名 /  日期
    date = time.strftime("%Y-%m-%d_%H", time.localtime())
    current_path = os.getcwd()

    log_path = current_path + "/" + package_name
    if not os.path.exists(log_path):
        os.makedirs(log_path)

    log_file_path = log_path + "/" + date + ".log"

    print(log_file_path)
    logcat_cmd = "adb -s " + realTimeDevice.deviceId + " logcat -b all"
    log_file = open(log_file_path, "w")
    print("==========")
    result = subprocess.Popen(logcat_cmd, shell=True, stdout=subprocess.PIPE)
    for line in iter(result.stdout.readline, "b"):
        log_file.write(line.decode('utf-8', 'ignore'))
        log_file.flush()


def get_app_info(connected_device: uiautomator2, package_name: str):
    if package_name is None:
        return

    package = package_name.split(".")

    print("======== ", str(package.__len__()))
    if package.__len__() < 2:
        return

    if package.__len__() >= 2 and package[1].__eq__(""):
        return
    app_info = ""
    from uiautomator2 import BaseError
    try:
        package_info = connected_device.app_info(package_name)
        app_info = Apk_Info.Apk_Info(package_info["packageName"], package_info["versionName"],
                                     package_info["versionCode"])
    except BaseError:
        print("not found any app in device " + str(connected_device.device_info["model"] + ", device serial  " +
                                                   str(connected_device.device_info["serial"])))

    print("the app info " + app_info)
    return app_info


if __name__ == '__main__':
    device_dict = get_device()
    for device in device_dict.values():
        print("current test device model: " + device.model + ", is online: " + str(device.isOnline()))
        if not device.isOnline():
            continue
        connected_device = uiautomator2.connect_usb(serial=device.deviceId)
        get_app_info(connected_device, current_test_package)
        connect_to_wifi("Matthew_5G","785714509")
        print(connected_device.device_info)
        # asyncio.run(catch_device_log(device, current_test_package))
        # catch_device_log(device, current_test_package)
