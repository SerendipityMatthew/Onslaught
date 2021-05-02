class Apk_Info(object):
    def __init__(self, package_name, version_name, version_code):
        self.package_name = package_name
        self.version_name = version_name
        self.version_code = version_code

    def __str__(self):
        return str(self.__dict__)
