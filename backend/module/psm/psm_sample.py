import time

class PSM:
    def __init__(self, password):
        self.password = password
    
    def evaluate(self):
        time.sleep(1)
        self.score = int(2.5*len(self.password))
        if self.score > 100:
            self.score = 100
        return str(self.score)