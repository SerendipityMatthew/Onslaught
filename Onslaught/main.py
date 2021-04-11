import uiautomator2 as uiautomator2
import adbutils as adbutils
import Device as Device
import subprocess as subprocess
import time as time

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
            device_id = devices_id_record.split("\t")[0]
            is_online = devices_id_record.split("\t")[1]
            print("is online = " + str(is_online))
            key_is_online = True
            if is_online.__contains__("offline"):
                key_is_online = False

            adb_prop_cmd = "adb -s " + device_id + " shell getprop"
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

            android_device = Device.Android_Device(device_id, product_model,
                                                   build_version_release, key_is_online,
                                                   product_locale_language)
            device_dict[android_device.deviceId] = android_device
    return device_dict


def connect_to_wifi(wifi_name, wifi_password):
    pass


if __name__ == '__main__':
    device_dict = get_device()
    for device in device_dict.values():
        print("current test device model: " + device.model + ", is online: " + str(device.isOnline()))
        if not device.isOnline():
            continue
        connected_device = uiautomator2.connect_usb(serial=device.deviceId)

        # 启动到 WiFi 界面
        connected_device.app_start(package_name=settings_package,
                                   activity=rom_settings_wifi_activity)
        time.sleep(2)
        if not connected_device(text=wifi_name).exists:
            connected_device.swipe(300, 900, 300, 200)

        connected_device(text=wifi_name).click()
        connected_device.send_keys(wifi_password, clear=True)
        if connected_device(text="连接").exists():
            connected_device(text="连接").click()
        if connected_device(text="Connect").exists():
            connected_device(text="Connect").click()
        time.sleep(3)
