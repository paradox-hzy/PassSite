import os

class Simple:
    def __init__(self, para):
        self.para = para

    def predict(self):
        res = ''
        for (key, val) in self.para.items():
            res += str(key) + ': ' + str(val) + '\n'
        f = open(os.path.abspath(os.path.join('result', str(self.para['id'])+'.txt')), 'w')
        f.write(res)
        f.close()