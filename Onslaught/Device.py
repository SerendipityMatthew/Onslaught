class Android_Device(object):
    # device_id 设备的 device id
    # model 设备的 model name
    # version 设备的android 版本
    def __init__(self, device_id, model, version, is_online, language):
        self.deviceId = device_id
        self.model = model
        self.version = version
        self.language = language
        self.is_online = is_online

    def isConnectByWifi(self):
        if str(self.deviceId).__contains__("192.168"):
            return True
        return False

    def isOnline(self):
        return self.is_online
