import time

class PSM:
    def __init__(self, password):
        self.password = password
    
    def evaluate(self):
        time.sleep(1)
        self.score = int(5.7*len(self.password))
        if self.score > 100:
            self.score = 100
        return str(self.score)