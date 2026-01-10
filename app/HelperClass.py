from random import randint,shuffle,choice
from string import digits,ascii_letters

class EncoderDecoder:
    def __init__(self):
        self.__Alphabets = list(digits + ascii_letters)
        self.__minShifting = 10
        self.__maxShifting = 30
        self.__minLength = 5
        self.__maxLength = 8
        for _ in range(randint(self.__minShifting,self.__maxShifting)): shuffle(self.__Alphabets)
        self.__MAP = {}

    def _getCode(self):
        return "".join(choice(self.__Alphabets) for _ in range(randint(self.__minLength,self.__maxLength)))

    def shortenUrl(self, long_Url):
        short_code = self._getCode()
        while short_code in self.__MAP:
            short_code = self._getCode()
        self.__MAP[short_code] = long_Url
        return short_code