import numpy as np
import tensorflow as tf
from tensorflow.keras import models
from collections import defaultdict
import time
import os

#tf2.0版本

class LSTM:
    def __init__(self,para_dict):
        #para_dict 包含'model':'bestLSTM_model.h5',这里要求模型和代码在相同路径
        # 'out_path':'LSTM_GEN.txt','thre':'1e-9'
        self.para=para_dict
        self.thre=10**(-int(para_dict['prob']))
        self.min_len=int(para_dict['len'])
        self.target_num=int(para_dict['num'])
    '''
    @pre:当前的密码片段 例如'abc' 'pass'
    @model:使用的模型
    @max_char:时间步
    return:返回下一个字符的概率向量 例如[0.1,0.3,0.5,0.1]
    '''

    def NNET(self,pre, model, max_char):
        index = len(pre)  # 下一个字符的下标
        x = np.zeros((1, max_char, 98))
        for i in range(len(pre)):
            if pre[i] == chr(2):
                x[0, i, 0] = 1
            elif pre[i] == chr(3):
                x[0, i, 98 - 2] = 1
            else:
                x[0, i, ord(pre[i]) - 32 + 1] = 1
        for j in range(len(pre), max_char):
            x[0, j, 98 - 1] = 1

        a = list(model.predict(x)[0, index - 1])
        # predict返回的是x对应的下一个状态的密码矩阵 选取对应index个字符的概率向量并返回
        return a

    def predict(self):
        model = models.load_model(os.path.abspath('module/LSTM/bestLSTM_model.h5'))
        '''
        初始时 prefix栈中只存放起始字符 LUT存放片段对应概率，起始字符对应为1
        每次都要将prefix栈中片段全部遍历弹出，然后清空LUT表
        '''
        prefix = [chr(2)]  # 用于存放当前片段
        LUT = defaultdict(int)
        LUT[chr(2)] = 1  # 设置起始概率为1
        total_num = 0
        out_path = os.path.abspath(os.path.join('result', str(self.para['id'])+'.txt'))

        with open(out_path, 'w') as f:
            depth = 1  # 表示遍历的深度
            while 1:
                # print('当前深度%d' % depth)
                # 首先判断prefix栈中是否还有剩余的片段
                if len(prefix) == 0:
                    break
                # 如果有则要将存在栈中的前缀全部弹出 将所有后缀先全部存入两个列表中
                temp1 = []  # 存放当前片段
                temp2 = []  # 存放对应概率
                '''
                下面开始遍历prefix栈，每次弹出一个前缀，遍历该前缀对应的所有的下一个字符
                遇到满足条件的结束字符就生成口令 大于概率阈值的片段就放入暂存列表
                这里需要注意 栈中每次存放的片段都是长度相同并且按照概率排序的
                例如[abc,123,bcd,mnj...] [0.6,0.5,0.4...]
                '''
                stamp1 = time.time()
                while len(prefix) > 0:
                    cur_pre = prefix[0]
                    del prefix[0]

                    next_prob = self.NNET(cur_pre, model, 18)  # 获得下一个字符的概率
                    num = 1
                    while num < 98 - 1:  # 用于遍历概率向量对应的每一个字符 这里跳过了起始和空字符
                        pro = next_prob[num]
                        # 如果当前字符串已经到达长度上限了 只去考虑结束字符
                        if len(cur_pre) > 30:
                            num = 98 - 2  # 设置num为遍历结束 保证不会有下一次遍历
                            pro = next_prob[num]  # 更新概率
                        if pro * LUT[cur_pre] > self.thre:
                            if num == 98 - 2:  # 遇到终止字符
                                if len(cur_pre) - 1 >= self.min_len:  # 大于最低长度的可以生成
                                    f.write(cur_pre[1:] + '\n')
                                    #f.write(str(LUT[cur_pre] * pro) + '\n')
                                    total_num += 1
                                    # if (total_num % 1e2 == 0):
                                    #     print(total_num, '\t', cur_pre[1:])
                                    if total_num>self.target_num:
                                        return
                            else:
                                # 其他情况下 将新的片段和对应概率分别存放到两个列表中 同时要对应
                                # LUT[cur_pre + chr(num + 31)] = LUT[cur_pre] * pro  # 更新当前概率
                                temp1.append(cur_pre + chr(num + 31))
                                temp2.append(LUT[cur_pre] * pro)
                                # prefix.append(cur_pre + chr(num + 31))  # 将新的片段放入prefix中 注意要放到列表头部
                        num += 1
                stamp2 = time.time()
                # print('当前深度结束 遍历用时%f' % (stamp2 - stamp1))
                # 此时prefix栈中所有前缀弹出 后缀已经全部存入两个列表中
                LUT.clear()  # 先将LUT表清空，释放空间
                # 接下来将暂存表按照概率排序 只保留前beam_size个再次放入栈中
                new_pre = list(zip(temp2, temp1))
                new_pre.sort(key=lambda x: x[0], reverse=True)
                stamp3 = time.time()
                # print('排序结束 排序用时%f' % (stamp3 - stamp2))
                # 接下来选取前beam_size个项再放入prefix栈中
                # beamsize的设置可以根据深度进行变化 也就是根据口令长度分布进行变化
                if depth < 4:
                    beam_size = 100
                elif 4 <= depth <= 7:
                    beam_size = 150
                elif 8 <= depth <= 10:
                    beam_size = 200
                elif 11 <= depth <= 13:
                    beam_size = 100
                elif depth > 13:
                    beam_size = 500
                search_size = beam_size if beam_size < len(new_pre) else len(new_pre)
                for i in range(search_size):
                    item = new_pre[i]  # item为一个元组 第一个存放概率 第二个存放片段
                    prefix.append(item[1])  # 注意这里是逆序放入 这样prefix每次pop的都是高概率片段
                    LUT[item[1]] = item[0]
                new_pre = []
                depth += 1


# if __name__ == '__main__':
#     #para_dict= {'model':'bestLSTM_model.h5','out_path':'LSTM_GEN.txt','thre':'1e-9'}
#     para={
#         'id': '1000000',
#         'module': 'lstm',
#         'type': 'gen',
#         'email': 'test@11.com',
#         'epoch': '0',
#         'prob': '7',#1e-7
#         'num': '1000',
#         'len': '8',#最低长度为4
#     }
#     LSTM_model=LSTM(para)
#     LSTM_model.predict()