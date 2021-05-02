from Device import Android_Device
from Apk_Info import Apk_Info
from TestDuration import TestDuration
from WiFi_Info import WiFi_Info


class TestCase(object):
    """

    """
    def __init__(self, device: Android_Device, app_info: Apk_Info,
                 test_result: bool, testDuration: TestDuration,
                 wifi_info: WiFi_Info):
        """
        :param device: 测试的设备
        :param app_info: 测试的 app 信息
        :param test_result: 测试的结果
        :param testDuration: 测试的开始时间, 结束时间
        :param wifi_info: 测试的当前 WiFi 信息
        """
        self.device = device
        self.app_info = app_info
        self.test_result = test_result
        self.testDuration = testDuration
        self.wifi_info = wifi_info

    def __str__(self):
        return str(self.__dict__)
