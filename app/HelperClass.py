from random import randint,shuffle,choice
from string import digits,ascii_letters

class EncoderDecoder:
    def __init__(self):
        self.Alphabets = list(digits + ascii_letters)
        for _ in range(randint(10,50)): shuffle(self.Alphabets)
        self.MAP = {}

    def getCode(self):
        return "".join(choice(self.Alphabets) for _ in range(randint(5,8)))

    def encodeUrl(self,long_Url):
        short_code = self.getCode()
        while short_code in self.MAP:
            short_code = self.getCode()
        self.MAP[short_code] = long_Url
        return short_code