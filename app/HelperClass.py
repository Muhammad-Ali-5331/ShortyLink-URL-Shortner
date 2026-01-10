import random
from string import digits,ascii_letters

class EncoderDecoder:
    def __init__(self):
        self.Alphabets = list(digits + ascii_letters)
        for _ in range(random.randint(10,20)):
            random.shuffle(self.Alphabets)
        self.MAP = {}

    def getCode(self):
        return "".join(random.choice(self.Alphabets) for _ in range(random.randint(5,8)))

    def encodeUrl(self,long_Url):
        short_code = self.getCode()
        while short_code in self.MAP:
            short_code = self.getCode()
        self.MAP[short_code] = long_Url
        return short_code