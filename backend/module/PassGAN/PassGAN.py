from collections import defaultdict
import tensorflow as tf
import numpy as np
import  os


class PassGAN:
    def __init__(self,para):
        self.para=para
        self.generator = tf.saved_model.load(os.path.abspath("module/PassGAN/model/generator"))
        self.discriminator = tf.saved_model.load(os.path.abspath("module/PassGAN/model/discriminator"))
        # 构造字符对应字典
        charmap = defaultdict(int)
        charmap[chr(2)] = 0
        inv_charmap = [chr(2)]
        for i in range(32, 127):
            charmap[chr(i)] = i - 31
            inv_charmap.append(chr(i))
        self.charmap=charmap
        self.inv_charmap=inv_charmap
        self.output=self.out_path = os.path.abspath(os.path.join('result', str(self.para['id'])+'.txt'))
        self.passwords=defaultdict(int)
        self.MIN_LEN=int(para['len'])

    def gene(self):
        total = 0
        pwd = []

        while total <int(self.para['num']) :
            # 声明噪音
            z = tf.random.normal([64, 128], dtype=tf.float32)
            # 通过生成器获得密码 注意此时密码是独热码形式 先通过argmax转换为下标形式
            samples = self.generator(noise=z, training=False)
            samples = np.argmax(samples, axis=2)
            decoded_samples = []
            for i in range(len(samples)):
                decoded = []
                for j in range(len(samples[i])):
                    decoded.append(self.inv_charmap[samples[i][j]])
                decoded_samples.append(tuple(decoded))
            pwd.extend(decoded_samples)
            if len(pwd) > 1e2 :
                #with open(self.output, 'a') as f:
                for s in pwd:
                    s = "".join(s).replace(chr(2), '')
                    if len(s)<self.MIN_LEN:
                        continue
                    self.passwords[s]+=1
                    total = len(self.passwords)
                    # if total % 100 == 0 and total != 0:
                    #     print('当前生成口令总数：%d' % total)
                    if total >= int(self.para['num']):
                        break
                pwd = []

    def out(self):
        self.passwords=sorted(self.passwords.items(),key=lambda x:x[1],reverse=True)
        with open(self.output,'w') as f:
            for pwd,cnt in self.passwords:
                f.write(pwd+'\n')
        #with open('info_'+(self.para['id'])+'.txt','w') as f:
           # f.write('id:'+(self.para['id'])+'\n')
            #f.write('email:' + (self.para['email']) + '\n')

    def predict(self):
        self.gene()
        self.out()
# if __name__ == '__main__':
#     para={
#         'id': '1',
#         'module': 'gan',
#         'type': 'gen',
#         'email': 'test@11.com',
#         'iter': '0',
#         'num': '1000',
#         'len': '4',
#     }
#     PassGAN_model=PassGAN(para)
#     PassGAN_model.predict()
