import  numpy as np
from copy import  deepcopy
from collections import  defaultdict
import os
import time
import pickle

import tensorflow as tf
from tensorflow.keras import models
'''
片段类包含了
next_seg指向下一个要填充的片段 从0开始
content当前填充内容['abc','123']
length总结构数目3
struct结构列表['L3','D3','S1']
prob初始化为结构概率 之后填充后不断更新
'''
class segment():
    def __init__(self,struct,leng,pro):
        self.next_seg=0
        self.content=[]
        self.length=leng
        self.struct=struct
        self.prob=pro





'''
返回一个结构化口令填充之后的长度 注意没有计算起始字符
@pwd:口令片段list['chr(2)','L1','D2']
return  1+2=3
'''
def struct_length(pwd):
    i=1
    length=0
    while i<len(pwd):
        if pwd[i][1:]=='' or pwd[i][1:]==' ' :
            a=1
        #这里需要考虑 P和N的结构 使用平均长度
        if pwd[i][0]=='P':
            length +=6
        elif pwd[i][0]=='N':
            length +=4
        elif pwd[i][0]=='d':
            length +=7
        elif pwd[i][0] == 'E':
            length += 10
        else:
            length+=int(pwd[i][1:])
        i+=1

    return length

'''
检查是否有连续相同属性的片段出现 仅针对考虑长度的片段 即PDN不考虑
@cur:口令片段list['chr(2)','L1','D2']
@item:结构化片段D3
return 1代表出现 0不出现
'''
def check_fun1(cur,item):
    if item[0]=='K' or item[0]=='W' :
        return 0
    new=cur[-1]#指向最后一个结构
    #判断首字母是否相同
    return 1 if item[0]==new[0] else 0



class PL:
    def __init__(self,para):
        # para_dict 包含'model':''P_LSTM.h5'',这里要求模型和代码在相同路径
        # 'VEC_LEN':VEC_LEN,'thre':thre
        self.para=para
        #self.VEC_LEN=para['VEC_LEN']
        self.mid_path=os.path.abspath('module/PL/mid_gen.txt')
        self.mid_thre=10**(-int(self.para['struct_prob']))
        self.out_path=os.path.abspath(os.path.join('result', str(self.para['id'])+'.txt'))
        self.thre=10**(-int(para['final_prob']))#最终口令概率
        #self.struc_to_index=struc_to_index
        #elf.index_to_struc=index_to_struc
        self.total=0#记录总生成口令数目
        self.gene_list=defaultdict(float)#存放生成口令
        self.batch_size=500
        # 读取一些初始值
        f1 = open(os.path.abspath('module/PL/index.pickle'), 'rb')
        self.index_to_struc = pickle.load(f1)
        self.VEC_LEN = len(self.index_to_struc) + 3  # +3表示起始字符 结束字符 空字符
        self.index_to_struc[0] = chr(2)  # 起始字符
        self.index_to_struc[self.VEC_LEN - 2] = chr(3)  # VEC_LEN-2是结束字符           VEC_LEN-1下标对应的是补全字符
        # 获取下标对应结构的字典
        self.struc_to_index = dict(zip(self.index_to_struc.values(), self.index_to_struc.keys()))
        self.MIN_LEN=int(para['gen_len'])


    def NNET(self,pre, model, max_char, VEC_LEN):
        index = len(pre[0]) - 1
        x = np.zeros((len(pre), max_char, VEC_LEN))
        for i in range(len(pre)):
            start = len(pre[i]) - max_char if len(pre[i]) - max_char > 0 else 0
            for j in range(start, len(pre[i])):  # 这里每次只取对应时间步的
                if pre[i][j] == chr(2):
                    x[i, j, 0] = 1
                else:
                    x[i, j, self.struc_to_index[''.join(pre[i][j])]] = 1
            # 添加补全字符
        for i in range(len(pre)):
            for j in range(len(pre[i]), max_char):
                x[i, j, VEC_LEN - 1] = 1

        a = model.predict(x)  # 输出为batch*veclen
        a = a[:, index, :]  # 获得batch*vec_len的矩阵
        # predict返回的是x对应的下一个状态的密码矩阵 选取对应index个字符的概率向量并返回
        return a
    #生成structure
    def gene(self):
        with open(os.path.abspath('module/PL/结构化提取结果/不同片段数目.txt'), 'r') as f:
            lines = f.readlines()
            max_word = int(lines[0].strip('\n')) + 2
        max_char=max_word
        model=models.load_model(os.path.abspath('module/PL/P_LSTM.h5'))
        total_num = 0
        prefix = [[chr(2)]]  # 用于存放当前片段
        LUT = {chr(2): 1}
        outpath =self.mid_path
        with open(outpath, 'w') as f:
            depth = 1  # 表示遍历的深度
            while 1:
                # print('当前深度%d' % depth)
                # 首先判断prefix栈中是否还有剩余的片段
                if len(prefix) == 0:
                    break
                temp1 = []  # 存放当前片段
                temp2 = []  # 存放对应概率
                stamp1 = time.time()
                while len(prefix) > 0:  # 遍历每个首字符
                    select_num = self.batch_size if self.batch_size < len(prefix) else len(prefix)  # 放入模型的字符串数目
                    prefix_batch = prefix[:select_num]
                    prefix = prefix[select_num:] if select_num != len(prefix) else []
                    next_batch_prob = self.NNET(prefix_batch, model, max_char,self.VEC_LEN)  # batch_size*VEC_LEN 代表每个字符串的下一个字符概率
                    for i in range(select_num):
                        prob_i = next_batch_prob[i]  # 获得第i个字符串对应的下一个字符的概率向量
                        num = 1
                        while num < self.VEC_LEN - 1:  # 用于遍历概率向量对应的每一个字符 这里跳过了起始和空字符
                            # 判断是否出现连续相同结构
                            if check_fun1(prefix_batch[i], self.index_to_struc[num]):
                                num += 1
                                continue
                            pro = prob_i[num]
                            if LUT[''.join(prefix_batch[i])] * pro > self.mid_thre:
                                if num == self.VEC_LEN - 2:  # 遇到终止字符
                                    # if struct_length(prefix_batch[i]) >= 4:  # 大于最低长度的可以生成
                                    f.write(''.join(prefix_batch[i][1:]) + '\t')
                                    f.write(str(LUT[''.join(prefix_batch[i])] * pro) + '\n')
                                    total_num += 1
                                    # if total_num % 1e4 == 0:
                                    #     print(total_num, '\t', ''.join(prefix_batch[i][1:]))

                                else:
                                    # 添加新结构后超出上限 则去寻找其他可行的结构
                                    if struct_length(prefix_batch[i] + [self.index_to_struc[num]]) > 15:
                                        num += 1
                                        continue
                                    # 其他情况下 将新的片段和对应概率分别存放到两个列表中 同时要对应
                                    temp1.append(prefix_batch[i] + [self.index_to_struc[num]])
                                    temp2.append(LUT[''.join(prefix_batch[i])] * pro)

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

                for i in range(len(new_pre)):
                    item = new_pre[i]  # item为一个元组 第一个存放概率 第二个存放片段
                    prefix.append(item[1])  # 注意这里是逆序放入 这样prefix每次pop的都是高概率片段
                    LUT[''.join(item[1])] = item[0]

                depth += 1
                if depth > 20:
                    break

    #读取提取的片段内容：
    def read_content(self):
        # 将结构化内容直接读取在内存中
        # 使用字典存放对应内容  digit的key为数字片段长度  value为对应长度下片段列表 每个元素是(pwd,prob)组成的元组
        digit = defaultdict(list)
        letter = defaultdict(list)
        special = defaultdict(list)
        kp = defaultdict(list)
        words = defaultdict(list)
        date = []
        email = []
        path = os.path.abspath("module/PL/结构化提取结果")
        for curDir, dirs, files in os.walk(path):
            for file in files:
                if file[0] == 'L':
                    length = int(file[1:-4])
                    with open(os.path.join(path, file), 'r') as f:
                        while 1:
                            line = f.readline().rstrip('\n')
                            if line == "":
                                break
                            ind = line.index('\t')
                            pwd = line[:ind]
                            prob = float(line[ind + 1:])
                            letter[length].append((pwd, prob))


                elif file[0] == 'D':
                    length = int(file[1:-4])
                    with open(os.path.join(path, file), 'r') as f:
                        while 1:
                            line = f.readline().rstrip('\n')
                            if line == "":
                                break
                            ind = line.index('\t')
                            pwd = line[:ind]
                            prob = float(line[ind + 1:])
                            digit[length].append((pwd, prob))

                elif file[0] == 'S':
                    length = int(file[1:-4])
                    with open(os.path.join(path, file), 'r') as f:
                        while 1:
                            line = f.readline().rstrip('\n')
                            if line == "":
                                break
                            ind = line.index('\t')
                            pwd = line[:ind]
                            prob = float(line[ind + 1:])
                            special[length].append((pwd, prob))

                elif file[0] == 'K':
                    length = int(file[1:-4])
                    with open(os.path.join(path, file), 'r') as f:
                        while 1:
                            line = f.readline().rstrip('\n')
                            if line == "":
                                break
                            ind = line.index('\t')
                            pwd = line[:ind]
                            prob = float(line[ind + 1:])
                            kp[length].append((pwd, prob))
                elif file[0] == 'W':
                    length = int(file[1:-4])
                    with open(os.path.join(path, file), 'r') as f:
                        while 1:
                            line = f.readline().rstrip('\n')
                            if line == "":
                                break
                            ind = line.index('\t')
                            pwd = line[:ind]
                            prob = float(line[ind + 1:])
                            words[length].append((pwd, prob))
                elif file[0] == 'd':
                    with open(os.path.join(path, file), 'r') as f:
                        while 1:
                            line = f.readline().rstrip('\n')
                            if line == "":
                                break
                            ind = line.index('\t')
                            pwd = line[:ind]
                            prob = float(line[ind + 1:])
                            date.append((pwd, prob))
                elif file[0] == 'E':
                    with open(os.path.join(path, file), 'r') as f:
                        while 1:
                            line = f.readline().rstrip('\n')
                            if line == "":
                                break
                            ind = line.index('\t')
                            pwd = line[:ind]
                            prob = float(line[ind + 1:])
                            email.append((pwd, prob))
        self.digit=digit
        self.letter=letter
        self.special=special
        self.kp=kp
        self.words=words
        self.date=date
        self.email=email
    #进行内容填充
    '''
    seg_list:包含segment对象的列表
    f写入生成口令
    '''

    def fill(self,seg_list):
        while len(seg_list) > 0:
            seg = seg_list.pop()
            if seg.next_seg == seg.length:  # 如果填充结束 就直接生成
                # 这里没有判断概率因为 在之前的结构已经判断了
                pwd = ''.join(seg.content)
                if len(pwd)<self.MIN_LEN:
                    continue
                self.gene_list[pwd] += seg.prob

                # if len(self.gene_list) % 1e3 == 0 and len(self.gene_list) != 0:
                #     print(len(self.gene_list), '\t', ''.join(seg.content), '\t', ''.join(seg.struct), '\t', str(seg.prob))
                continue

            struct = seg.struct[seg.next_seg]  # 当前要填充的结构 例如'L5'
            if struct[0] != 'P' and struct[0] != 'N' and struct[0] != 'd' and struct[0] != 'E':
                leng = int(struct[1:])  # 读取长度
            contents = []

            if struct[0] == 'L':
                contents = self.letter[leng]
            elif struct[0] == 'D':
                contents = self.digit[leng]
            elif struct[0] == 'S':
                contents = self.special[leng]
            elif struct[0] == 'K':
                contents = self.kp[leng]
            elif struct[0] == 'W':
                contents = self.words[leng]
            elif struct[0] == 'd':
                contents = self.date
            elif struct[0] == 'E':
                contents = self.email
            for item in contents:
                content = item[0]
                prob = item[1]
                if prob * seg.prob >= self.thre:  # 如果填充后的片段概率大于阈值 就新建一个segment放入队列中
                    n_seg = deepcopy(seg)
                    n_seg.content.append(content)
                    n_seg.prob *= prob
                    n_seg.next_seg += 1
                    seg_list.append(n_seg)
                else:  # 如果概率小于阈值
                    break

    #生成最终结果
    def gene2(self):
        self.read_content()#首先读取片段内容
        f = open(self.mid_path, 'r')
        f1 = open(self.out_path, 'w')
        seg_list = []

        while 1:
            pwd = f.readline()  # pwd是结构化口令并附带概率
            if pwd == "":
                break
            pwd = pwd.rstrip('\n')
            index = pwd.index('\t')
            i = 0
            st = []  # 用于存放结构化密码的每个结构片段
            cur = ''
            while i < len(pwd[:index]):
                if pwd[i].isalpha():
                    cur = pwd[i]
                    i += 1
                    while i < len(pwd) and pwd[i].isdigit():
                        cur += pwd[i]
                        i += 1
                st.append(cur)

            prob = float(pwd[index + 1:])

            new_seg = segment(struct=st, leng=len(st), pro=prob)
            seg_list.append(new_seg)
            self.fill(seg_list)
        #完成填充之后，排序
        # 完成对所有的结构提取后 将字典中口令写入文本
        # 这里直接对字典进行排序 然后生成
        gene_pwd = sorted(self.gene_list.items(), key=lambda x: x[1], reverse=True)  # 从大到小排序
        save_num = int(self.para['num'])
        num = 0
        for item in gene_pwd:
            f1.write(item[0] + '\n')
            num += 1
            if num >= save_num:
                break
        #f2=open('info_'+(self.para['id'])+'.txt','w')
       # f2.write('id:'+(self.para['id'])+'\n')
        #f2.write('email:' + (self.para['email']) + '\n')

    def predict(self):
        self.gene()  # 注意要先生成base structure
        self.gene2()  # 再生成最终口令
# if __name__ == '__main__':


#     #设置为0的表述用不到的
#     para={
#         'id': '1000000',
#         'module': 'pl',
#         'type': 'gen',
#         'email': 'test@11.com',
#         'extract_len':'6',
#         'epoch':'0',
#         'struct_prob':'5',
#         'final_prob':'6',
#         'num': '1000',
#         'gen_len': '4',
#     }
#     #para={'max_char':max_word,'thre':1e-8,'model':'P_LSTM.h5'}
#     #生成模型
#     PL_model=PL(para)
#     PL_model.predict()

