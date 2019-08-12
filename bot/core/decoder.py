class Decoder():

    @staticmethod
    def extract(fromString, toString, data):
        newData = data[data.find(fromString) + len(fromString):]
        newData = newData[0:newData.find(toString)]
        return newData

    @staticmethod
    def rExtract(fromString, toString, data):
        newData = data[0:data.rfind(toString)]
        newData = newData[newData.rfind(fromString) + len(fromString):]
        return newData

    @staticmethod
    def extractWithRegex(fromString, toString, data):
        newData = data[data.find(fromString):]
        newData = newData[0:newData.find(toString) + len(toString)]
        return newData

    @staticmethod
    def rExtractWithRegex(fromString, toString, data):
        newData = data[0:data.rfind(toString) + len(toString)]
        newData = newData[newData.rfind(fromString):]
        return newData
