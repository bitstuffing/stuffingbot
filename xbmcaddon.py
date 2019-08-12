
def Addon(id):
	dummy = Dummy()
	return dummy


class Dummy():
	def getLocalizedString(value):
		return value
	def getString(value):
		return value
	def getSetting(self,name):
		return name
	def getAddonInfo(self,name):
		return name
