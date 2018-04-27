# __author__ = 'luoys'
import ConfigParser


class Ini:
    # def __init__(self, section, key):
    #     self.section = section
    #     self.key = key

    def getConfigValue(self, section, key):
        config = ConfigParser.ConfigParser()
        config.read('..\\config.ini')
        value = config.get(section, key)
        return value
