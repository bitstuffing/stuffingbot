from pydub import AudioSegment
import logger

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

	@staticmethod
	def mp3ToWav(audioFileName):
		logger.debug(audioFileName[len(audioFileName)-4:])
		if '.mp3' == audioFileName[len(audioFileName)-4:].lower():
			sound = AudioSegment.from_mp3(audioFileName)
			audioFileName = audioFileName[:len(audioFileName)-4] + '.wav'
			sound.export(audioFileName, format="wav")
			logger.debug("converted file to wav")
			return audioFileName

	@staticmethod
	def wavToMp3(audioFileName):
		logger.debug(audioFileName[len(audioFileName)-4:])
		if '.wav' == audioFileName[len(audioFileName)-4:].lower():
			sound = AudioSegment.from_wav(audioFileName)
			audioFileName = audioFileName[:len(audioFileName)-4] + '.mp3'
			sound.export(audioFileName, format="mp3")
			logger.debug("converted file to mp3")
			return audioFileName

	@staticmethod
	def oggToWav(audioFileName):
		logger.debug(audioFileName[len(audioFileName)-4:])
		if '.ogg' == audioFileName[len(audioFileName)-4:].lower() or '.oga' == audioFileName[len(audioFileName)-4:].lower():
			sound = AudioSegment.from_ogg(audioFileName)
			audioFileName = audioFileName[:len(audioFileName)-4] + '.wav'
			sound.export(audioFileName, format="wav")
			logger.debug("converted file to wav")
			return audioFileName
