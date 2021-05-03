import asyncio
import os
import subprocess as subprocess
import threading
import time as time

import uiautomator2 as uiautomator2
from uiautomator2 import UiObjectNotFoundError

import Apk_Info as Apk_Info
import util.Utils as Utils
from Device import Android_Device
from TestCase import TestCase

adb_devices_cmd = "adb devices"
key_build_version_release = "ro.build.version.release"
key_product_model = "ro.product.model"
key_product_locale_language = "ro.product.locale.language"
deye_package = "com.deye"
current_test_package = deye_package

settings_package = "com.android.settings"
nexus_settings_activity = "com.android.settings.Settings"
rom_settings_activity = "com.android.settings.MainSettings"
rom_settings_wifi_activity = "com.android.settings.Settings$WifiSettingsActivity"
wifi_connect_resource_id = "android:id/button1"
onslaughtapp_package = "me.xuwanjin.onslaughtapp"
onslaughtapp_resource_id = onslaughtapp_package + ":id/"
wifi_219_password = "785174509I350"
wifi_219_name = "219"
wifi_matthew_name = "Matthew_2.4G"
wifi_matthew_password = "785174509"
wifi_switch_widget_resource_id = "com.android.settings:id/switch_widget"
wifi_name = wifi_219_name
wifi_password = wifi_219_password
is_start_test_parallel = True


def strip_str_for_prop(prop):
    return prop.strip(" ").replace("[", "").replace("]", "")


def get_device():
    adb_devices_result = subprocess.getstatusoutput(adb_devices_cmd)
    print("list all android device: " + str(adb_devices_result))
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

            device_dict[android_device.device_serial] = android_device
    return device_dict


def connect_to_wifi(device_serial: str, wifi_name, wifi_password):
    uiAuto = uiautomator2.connect_usb(serial=device_serial)
    uiAuto.app_start(package_name=settings_package,
                     activity=rom_settings_wifi_activity)
    time.sleep(2)
    if not uiAuto(text=wifi_name).exists:
        uiAuto.swipe(300, 900, 300, 200)

    uiAuto(text=wifi_name).click()
    """
        在某些情况下, 这个设备已经连接过这个 WiFi 了, 执行 sendkeys 会报错, 
    """
    try:
        uiAuto.send_keys(wifi_password, clear=True)
    except UiObjectNotFoundError as error:
        print(error)
    finally:
        if uiAuto(text="连接").exists():
            uiAuto(text="连接").click()
        if uiAuto(text="Connect").exists():
            uiAuto(text="Connect").click()
        if uiAuto(text="CONNECT").exists():
            uiAuto(text="CONNECT").click()
    time.sleep(3)


def connect_to_wifi_with_app(uiauto_device: Android_Device, wifi_name, wifi_password):
    is_existed = Utils.is_onslaught_app_installed(uiauto_device.device_serial)
    current_ssid = Utils.get_wifi_ssid(uiauto_device.device_serial)
    print("the wifi which " + uiauto_device.device_serial + " had been connected to wifi " + current_ssid)
    if current_ssid.__eq__(wifi_name):
        return
    save_setting_id = "com.android.settings:id/save"
    if is_existed:
        uiautomator = uiautomator2.connect_usb(serial=uiauto_device.device_serial)
        uiautomator.app_start(package_name=onslaughtapp_package)
        uiautomator(resourceId=onslaughtapp_resource_id + "wifi_ssid").clear_text()
        uiautomator(resourceId=onslaughtapp_resource_id + "wifi_ssid").set_text(wifi_name)
        uiautomator(resourceId=onslaughtapp_resource_id + "wifi_password").send_keys(wifi_password)
        uiautomator(resourceId=onslaughtapp_resource_id + "connect_to_wifi").click()
        print("the android version of current test device is : " + uiauto_device.version)
        """
         对于 android 11 以及以上的系统, 会出现一个系统的弹窗让用户需选择
        """
        version = str(uiauto_device.version)
        if version.__contains__("."):
            ver = version.split(".")[0]
            if int(ver) >= 11:
                uiautomator(resourceId=save_setting_id).click()
        elif int(uiauto_device.version) >= 11:
            uiautomator(resourceId=save_setting_id).click()
        time.sleep(6)


def catch_device_log(device: Android_Device, package_name: str):
    if not device.isOnline():
        return
    """
    再次检查一下设备是否在线
    """
    realTimeDevice = get_device()[device.device_serial]
    print("check the device is online: " + str(realTimeDevice.isOnline()))
    if not realTimeDevice.isOnline():
        return

    # log 的路径  包名 /  日期
    current_test_date = time.strftime("%Y-%m-%d_%H", time.localtime())
    print("the current test date: " + str(current_test_date))
    current_path = os.getcwd()
    """
     路径保持为 包名/设备model名称/设备的device_serial/当前日期的+ 小时.log
    """
    log_path = current_path + os.sep + package_name + os.sep + device.model + os.sep + device.device_serial

    if not os.path.exists(log_path):
        os.makedirs(log_path)

    log_file_path = log_path + "/" + current_test_date + ".log"

    print("the log path which we want to save: " + log_file_path)
    logcat_cmd = "adb -s " + realTimeDevice.device_serial + " logcat -b all"
    log_file = open(log_file_path, "w")
    result = subprocess.Popen(logcat_cmd, shell=True, stdout=subprocess.PIPE)
    for line in iter(result.stdout.readline, "b"):
        current_date = time.strftime("%Y-%m-%d_%H", time.localtime())
        if current_date.__eq__(current_test_date):
            log_file.write(line.decode('utf-8', 'ignore'))
            log_file.flush()
        else:
            print("进入下一个小时的, 收集手机 log 的阶段")
            catch_device_log(device, package_name)


def get_app_info(connected_device: uiautomator2, package_name: str):
    if package_name is None:
        return

    package = package_name.split(".")

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

    print("the app info: " + str(app_info))
    return app_info


def execute_cmd(func):
    def wrapper():
        print("%s is running" % func.__name__)
        return func()  # 把 foo 当做参数传递进来时，执行func()就相当于执行foo()

    return wrapper


def start_and_stop_app(device_serial: str, package_name: str):
    uiautomator = uiautomator2.connect_usb(serial=device_serial)
    is_app_installed = Utils.is_app_installed(device_serial, package_name)
    if not is_app_installed:
        return False
    uiautomator.app_start(package_name=package_name)
    time.sleep(5)
    uiautomator.app_stop(package_name=package_name)
    return True


def start_device_test(device: Android_Device):
    if not device.isOnline():
        return

    connected_device = uiautomator2.connect_usb(serial=device.device_serial)
    Utils.set_device_never_sleep(device.device_serial)
    # 2. 获取 app 信息
    app_info = get_app_info(connected_device, current_test_package)
    # 3. 执行收集手机log的任务
    """
        暂时以线程的方式实现
    """
    thread = threading.Thread(target=catch_device_log, args=(device, current_test_package))
    thread.start()
    # 4. 切换设备的 WiFi
    wifi_list = Utils.parse_wifi_list_json()
    for wifi_item in wifi_list:
        # connect_to_wifi(wifi_item.ssid, wifi_item.password)
        print("the current test wifi item: " + str(wifi_item))
        connect_to_wifi_with_app(device, wifi_item.ssid, wifi_item.password)
        connected_device.press("home")
        for i in range(4):
            time.sleep(3)
            test_result = execute_cmd(start_and_stop_app(device.device_serial, current_test_package))
            test_case = TestCase(device, app_info, test_result="pass",
                                 wifi_info=wifi_item, failed_reason="")
            test_case_list.append(test_case)
            print("the test result: " + str(test_result))

        print(connected_device.device_info)


if __name__ == '__main__':
    """
     1. 获取设备信息
     2. 获取 app 信息
     3. 执行收集手机log的任务
     4. 切换设备的 WiFi 
     5. 对 app 执行操作 (执行配网操作/执行登录退出 等等)
     6. 输出当前的操作的结果
     7. 回到第二步第四步骤
     8. 把所有的测试结果写到 html 文件当中.
    """
    # 1. 获取设备信息
    all_device_dict = get_device()
    test_case_list = []
    for test_device in all_device_dict.values():
        print("current test device model: " + test_device.model + ", is online: " + str(test_device.isOnline()))

        if is_start_test_parallel:
            device_thread = threading.Thread(target=start_device_test, args={test_device})
            device_thread.start()
        else:
            start_device_test(test_device)

    for case in test_case_list:
        print("   " + str(case))
