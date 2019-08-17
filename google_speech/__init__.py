#!/usr/bin/env python2

import argparse
import collections
import logging
import os
import unicodedata
import re
import string
import subprocess
import sys
import threading
import urllib

import appdirs
import requests

from google_speech import colored_logging


SUPPORTED_LANGUAGES = ("af", "ar", "bn", "bs", "ca", "cs", "cy", "da", "de", "el", "en", "en-au", "en-ca", "en-gb",
                       "en-gh", "en-ie", "en-in", "en-ng", "en-nz", "en-ph", "en-tz", "en-uk", "en-us", "en-za", "eo",
                       "es", "es-es", "es-us", "et", "fi", "fr", "fr-ca", "fr-fr", "hi", "hr", "hu", "hy", "id", "is",
                       "it", "ja", "jw", "km", "ko", "la", "lv", "mk", "ml", "mr", "my", "ne", "nl", "no", "pl", "pt",
                       "pt-br", "pt-pt", "ro", "ru", "si", "sk", "sq", "sr", "su", "sv", "sw", "ta", "te", "th", "tl",
                       "tr", "uk", "vi", "zh-cn", "zh-tw")

PRELOADER_THREAD_COUNT = 1


class PreloaderThread(threading.Thread):

  """ Thread to pre load (download) audio data of a segment. """

  def run(self):
    try:
      for segment in self.segments:
        acquired = segment.preload_mutex.acquire(blocking=False)
        if acquired:
          try:
            segment.preLoad()
          finally:
            segment.preload_mutex.release()
    except Exception as e:
      logging.getLogger().error("%s: %s" % (e.what, e))


class Speech:

  """ Text to be read. """

  CLEAN_MULTIPLE_SPACES_REGEX = re.compile("\s{2,}")
  MAX_SEGMENT_SIZE = 100

  def __init__(self, text, lang):
    self.text = self.cleanSpaces(text)
    self.lang = lang

  def __iter__(self):
    """ Get an iterator over speech segments. """
    return self.__next__()

  def __next__(self):
    """ Get a speech segment, splitting text by taking into account spaces, punctuation, and maximum segment size. """
    if self.text == "-":
      if sys.stdin.isatty():
        logging.getLogger().error("Stdin is not a pipe")
        return
      while True:
        new_line = sys.stdin.readline()
        if not new_line:
          return
        segments = Speech.splitText(new_line)
        for segment_num, segment in enumerate(segments):
          yield SpeechSegment(segment, self.lang, segment_num, len(segments))

    else:
      segments = Speech.splitText(self.text)
      for segment_num, segment in enumerate(segments):
        yield SpeechSegment(segment, self.lang, segment_num, len(segments))

  @staticmethod
  def findLastCharIndexMatching(text, func):
    """ Return index of last character in string for which func(char) evaluates to True. """
    for i in range(len(text) - 1, -1, -1):
      if func(text[i]):
        return i

  @staticmethod
  def splitText(text):
    """ Split text into sub segments of size not bigger than MAX_SEGMENT_SIZE. """
    segments = []
    remaining_text = Speech.cleanSpaces(text)

    while len(remaining_text) > Speech.MAX_SEGMENT_SIZE:
      cur_text = remaining_text[:Speech.MAX_SEGMENT_SIZE]

      # try to split at punctuation
      split_idx = __clSpeechass__.findLastCharIndexMatching(cur_text,
                                                      # https://en.wikipedia.org/wiki/Unicode_character_property#General_Category
                                                      lambda x: unicodedata.category(x) in ("Ps", "Pe", "Pi", "Pf", "Po"))
      if split_idx is None:
        # try to split at whitespace
        split_idx = Speech.findLastCharIndexMatching(cur_text,
                                                        lambda x: unicodedata.category(x).startswith("Z"))
      if split_idx is None:
        # try to split at anything not a letter or number
        split_idx = Speech.findLastCharIndexMatching(cur_text,
                                                        lambda x: not (unicodedata.category(x)[0] in ("L", "N")))
      if split_idx is None:
        # split at the last char
        split_idx = Speech.MAX_SEGMENT_SIZE - 1

      new_segment = cur_text[:split_idx + 1].rstrip()
      segments.append(new_segment)
      remaining_text = remaining_text[split_idx + 1:].lstrip(string.whitespace + string.punctuation)

    if remaining_text:
      segments.append(remaining_text)

    return segments

  @staticmethod
  def cleanSpaces(dirty_string):
    """ Remove consecutive spaces from a string. """
    return Speech.CLEAN_MULTIPLE_SPACES_REGEX.sub(" ",
                                                     dirty_string.replace("\n", " ").replace("\t", " ").strip())

  def play(self, sox_effects=()):
    """ Play a speech. """

    # build the segments
    preloader_threads = []
    if self.text != "-":
      segments = list(self)
      # start preloader thread(s)
      preloader_threads = [PreloaderThread(name="PreloaderThread-%u" % (i)) for i in range(PRELOADER_THREAD_COUNT)]
      for preloader_thread in preloader_threads:
        preloader_thread.segments = segments
        preloader_thread.start()
    else:
      segments = iter(self)

    # play segments
    for segment in segments:
      segment.play(sox_effects)

    if self.text != "-":
      # destroy preloader threads
      for preloader_thread in preloader_threads:
        preloader_thread.join()

  def save(self, path):
    """ Save audio data to an MP3 file. """
    with open(path, "wb") as f:
      self.savef(f)

  def savef(self, file):
    """ Write audio data into a file object. """
    for segment in self:
      file.write(segment.getAudioData())


class SpeechSegment:

  """ Text segment to be read. """

  BASE_URL = "https://translate.google.com/translate_tts"

  session = requests.Session()

  def __init__(self, text, lang, segment_num, segment_count=None):
    self.text = text
    self.lang = lang
    self.segment_num = segment_num
    self.segment_count = segment_count
    self.preload_mutex = threading.Lock()

  def __str__(self):
    return self.text

  def preLoad(self):
    logging.getLogger().debug("Preloading segment '%s'" % (self))
    real_url = self.buildUrl()
    audio_data = self.download(real_url)
    assert(audio_data)

  def getAudioData(self):
    """ Fetch the audio data. """
    with self.preload_mutex:
      real_url = self.buildUrl()
      audio_data = self.download(real_url)
      assert(audio_data)
    return audio_data

  def play(self, sox_effects=()):
    """ Play the segment. """
    audio_data = self.getAudioData()
    logging.getLogger().info("Playing speech segment (%s): '%s'" % (self.lang, self))
    cmd = ["sox", "-q", "-t", "mp3", "-"]
    if sys.platform.startswith("win32"):
      cmd.extend(("-t", "waveaudio"))
    cmd.extend(("-d", "trim", "0.1", "reverse", "trim", "0.07", "reverse"))  # "trim", "0.25", "-0.1"
    cmd.extend(sox_effects)
    logging.getLogger().debug("Start player process")
    p = subprocess.Popen(cmd,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.DEVNULL)
    p.communicate(input=audio_data)
    if p.returncode != 0:
      raise RuntimeError()
    logging.getLogger().debug("Done playing")

  def buildUrl(self):
    """
    Construct the URL to get the sound from Goggle API.
    """
    params = collections.OrderedDict()
    params["client"] = "tw-ob"
    params["ie"] = "UTF-8"
    params["idx"] = str(self.segment_num)
    if self.segment_count is not None:
      params["total"] = str(self.segment_count)
    params["textlen"] = str(len(self.text))
    params["tl"] = self.lang
    lower_text = self.text.lower()
    params["q"] = lower_text
    return "%s?%s" % (SpeechSegment.BASE_URL, urllib.quote_plus(params))

  def download(self, url):
    """ Download a sound file. """
    logging.getLogger().debug("Downloading '%s'..." % (url))
    response = SpeechSegment.session.get(url,
                                     headers={"User-Agent": "Mozilla/5.0"},
                                     timeout=3.1)
    response.raise_for_status()
    return response.content


def cl_main():
  # parse args
  arg_parser = argparse.ArgumentParser(description="Google Speech v%s.%s" % (__version__, __doc__),
                                       formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  arg_parser.add_argument("speech",
                          help="Text to play")
  arg_parser.add_argument("-l",
                          "--lang",
                          choices=SUPPORTED_LANGUAGES,
                          default="en",
                          dest="lang",
                          help="Language")
  arg_parser.add_argument("-e",
                          "--sox-effects",
                          default=(),
                          nargs="+",
                          dest="sox_effects",
                          help="SoX effect command to pass to SoX's play")
  arg_parser.add_argument("-v",
                          "--verbosity",
                          choices=("warning", "normal", "debug"),
                          default="normal",
                          dest="verbosity",
                          help="Level of logging output")
  arg_parser.add_argument("-o",
                          "--output",
                          default=None,
                          dest="output",
                          help="Outputs audio data to this file instead of playing it")
  args = arg_parser.parse_args()

  # setup logger
  logging_level = {"warning": logging.WARNING,
                   "normal": logging.INFO,
                   "debug": logging.DEBUG}
  logging.getLogger().setLevel(logging_level[args.verbosity])
  logging.getLogger("requests").setLevel(logging.ERROR)
  logging.getLogger("urllib2").setLevel(logging.ERROR)
  if logging_level[args.verbosity] == logging.DEBUG:
    fmt = "%(asctime)s %(threadName)s: %(message)s"
  else:
    fmt = "%(message)s"
  logging_formatter = colored_logging.ColoredFormatter(fmt=fmt)
  logging_handler = logging.StreamHandler()
  logging_handler.setFormatter(logging_formatter)
  logging.getLogger().addHandler(logging_handler)

  if (args.output is not None) and args.sox_effects:
    logging.getLogger().debug("Effects are not supported when saving to a file")
    exit(1)

  # do the job
  speech = Speech(args.speech, args.lang)
  if args.output:
    speech.save(args.output)
  else:
    speech.play(args.sox_effects)


if __name__ == "__main__":
  cl_main()
