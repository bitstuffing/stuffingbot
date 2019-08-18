from __future__ import print_function
import json
from os.path import join, dirname
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
import threading
from bot.core.config import Config
import logger

SPEECH_KEY = Config.getConfig()['IBM_SPEECH_KEY']

class SpeechToText():

    def __init__(self):
        # If service instance provides API key authentication
        self.service = SpeechToTextV1(
            ## url is optional, and defaults to the URL below. Use the correct URL for your region.
            url='https://gateway-lon.watsonplatform.net/speech-to-text/api',
            iam_apikey=SPEECH_KEY)

        #self.service = SpeechToTextV1(
        #    username='email',
        #    password='password',
        #    url='https://gateway-lon.watsonplatform.net/speech-to-text/api')

        self.model = self.service.get_model('es-ES_BroadbandModel').get_result()
        #logger.debug(json.dumps(self.model, indent=2))

    def getAllModels():
        models = self.service.list_models().get_result()
        #TODO extract es-ES_BroadbandModel from language: es-ES
        logger.debug(json.dumps(models, indent=2))

    def transcribe(self,wavFile):
        transcription = ""
        logger.debug("transcribe %s file"%wavFile)
        with open(join(dirname(__file__), wavFile),
                  'rb') as audio_file:
            transcription = str(json.dumps(
                self.service.recognize(
                    audio=audio_file,
                    model=self.model["name"],
                    content_type='audio/wav',
                    timestamps=True,
                    word_confidence=True).get_result(),
                indent=2))
        logger.debug("transcribed %s file: %s"%(wavFile,transcription))

        # Example using threads in a non-blocking way
        #mycallback = MyRecognizeCallback()
        #audio_file = open(join(dirname(__file__), wavFile), 'rb')
        #audio_source = AudioSource(audio_file)
        #recognize_thread = threading.Thread(
        #    target=self.service.recognize_using_websocket,
        #    args=(audio_source, "audio/l16; rate=44100", mycallback))
        #recognize_thread.start()

        return transcription

# Example using websockets (for async non-blocking way)
class MyRecognizeCallback(RecognizeCallback):
    def __init__(self):
        RecognizeCallback.__init__(self)

    def on_transcription(self, transcript):
        logger.debug(transcript)

    def on_connected(self):
        logger.debug('Connection was successful')

    def on_error(self, error):
        logger.debug('Error received: {}'.format(error))

    def on_inactivity_timeout(self, error):
        logger.debug('Inactivity timeout: {}'.format(error))

    def on_listening(self):
        logger.debug('Service is listening')

    def on_hypothesis(self, hypothesis):
        logger.debug(hypothesis)

    def on_data(self, data):
        logger.debug(data)
