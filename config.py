import json

CONFIGURATION_FILE = 'configuration.json'

class Config():

    @staticmethod
    def getConfig():
        config = {}
        with open(CONFIGURATION_FILE, 'r') as json_file:
            config = json.load(json_file)

        return config
