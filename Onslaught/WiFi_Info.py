class WiFi_Info(object):
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password

    def is_WiFi_2_4(self):
        if str(self.ssid).__contains__("2.4G"):
            return True

    def __str__(self):
        return str(self.__dict__)
