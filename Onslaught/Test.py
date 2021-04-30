import util.Utils as Utils
import time

# Utils.get_wifi_ssid("")
# print(Utils.is_net_ok())

# hello = Utils.is_device_screen_on("")
# hello = Utils.switch_off_device_screen("")

# time.sleep(5)
# Utils.switch_on_device_screen("")
is_online = Utils.is_device_online("31a9dd05")
print(is_online)
