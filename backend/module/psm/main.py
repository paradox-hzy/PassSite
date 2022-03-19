import os
import numpy as np
import re
import time


cur_path = os.getcwd()  # 获取当前的路径
# file = cur_path + "/data.txt"  # 攻击模型生成的口令及其对应的频率
# samples = cur_path + "/samples.txt"  # 样本
file_dic = os.path.join(cur_path, "module/psm/pwd/dictionary.txt")  # 攻击模型生成的口令及其对应的频率
dict1 = {}
# dict_struct = {}
pattern_re = re.compile(r'([a-zA-Z]+)|([0-9]+)|[^a-zA-Z0-9]+')
pattern_up = re.compile(r'([a-z]+)|([A-Z]+)|[^a-zA-Z]+')
# 利用正则表达式进行片段匹配
L, D, S = 'L', 'D', 'S'
L_BIG, L_SMALL, DS = 'L_BIG', 'L_SMALL', 'DS'
score_count = []
type_count = 0
prob__ = 0


class PSM:
    def __init__(self, password):
        self.password = password
        self.sample_path = os.path.join(cur_path, "module/psm/samples/samples.txt")
        self.score = 60
        self.score1 = 60
        self.score2 = 60
        self.type_num = 0

    def evaluate(self):
        time.sleep(1)
        load_prob(file_dic)
        get_prob(self.password)  # 计算的到prob__
        # 将score_count的值累加并赋给score2
        self.score2 = sum(score_count)
        score_count.clear()  # 清空数组
        if prob__ == -1:
            self.score1 = self.score2
        elif prob__ != -1:
            arrA = create_A(self.sample_path)
            arrC = create_C(arrA)
            j = get_index(arrA, prob__)
            self.score1 = int(strength(arrC[j]))
        if self.score1 > 100:
            self.score1 = 100
        self.score = self.score1 * 0.5 + self.score2 * 0.5
        return str(self.score)


# 加载攻击模型生成的口令，并返回数组
def load_prob(path):
    with open(path, 'r') as f:
        data = f.readlines()
        for line in data:
            pwd1 = line.split('\t')[0]
            dict1[pwd1] = '{:0.22f}'.format(float(line.split('\t')[1]))


def get_prob(pwd2):
    # 1 对密码长度的赋分规则
    if len(pwd2) <= 6:
        score_count.append(0)
    elif 7 <= len(pwd2) <= 8:
        score_count.append(10)
    elif len(pwd2) >= 9:
        score_count.append(25)

    # 第一部分，对所有类型的口令都要进行口令规则赋分
    # 数字和特殊符号识别
    para1 = patterns(pwd2)
    para2 = process_struct(para1[0], para1[1])
    para3 = load_struct()
    # 大小写识别
    para4 = patterns_upper(pwd2)
    process_struct_upper(para4[0])
    # 字符类型识别赋分
    type_score()

    # 第二部分，对口令集中的进行强度值的计算
    if pwd2 in dict1:
        # return float(dict1[pwd2])  # 返回概率
        global prob__
        prob__ = float(dict1[pwd2])
    elif para2[0] in para3:
        p1 = para3[para2[0]]
        p2 = 1
        for i in range(len(para2[1])):
            p2 = p2 * para2[1][i]
        prob__ = p1 * p2 / 10
    else:
        prob__ = -1


# 创建数组A，其已经按照概率降序排列
def create_A(path):
    lines = []
    with open(path, 'r') as f:
        data = f.readlines()
        for line in data:
            prob = line.split()
            # prob = prob[:-1]
            # prob = prob[:0]
            lines.append(prob)
        A_array = np.array(lines)
        A_array = A_array.astype(float)
    return A_array


# 创建数组C,按照公式
def create_C(A):
    n = len(A)
    temp = 0
    c_temp = []
    for i in range(n):
        for j in range(i + 1):
            temp += 1 / A[j]
        temp = temp / n
        c_temp.append(temp)
    c_temp[-1] = c_temp[-2]
    C = np.array(c_temp)
    C = C.astype(float)
    # print(c_temp)
    return C


# 通过二分查找获取数组a和c中的索引j
def get_index(A, value):
    num = len(A)
    head = 0
    while (num - head) != 1:
        if value >= A[int((head + num) / 2)]:
            num = int((head + num) / 2)
            # print(head, num)
        elif value < A[int((head + num) / 2)]:
            head = int((head + num) / 2)
            # print(head, num, value)
    return head


def strength(num):
    return int(pow(num / 1e+05, 1/3))


# 口令不在口令集中的情况
# 将struct加载到dict中
def load_struct():
    dict_struct = {}
    with open(os.path.abspath('module/psm/结构化提取结果/structure.txt'), 'r') as f:
        data = f.readlines()
        for line in data:
            struct1 = line.split('\t')[0]
            dict_struct[struct1] = float(line.split('\t')[1])
    return dict_struct


# 加载数字段
def load_digit(num):
    dict_struct = {}
    with open(os.path.abspath('module/psm/结构化提取结果/digit{}.txt'.format(num)), 'r') as f:
        data = f.readlines()
        for line in data:
            struct1 = line.split('\t')[0]
            dict_struct[struct1] = float(line.split('\t')[1])
    return dict_struct


# 加载字母段
def load_letter(num):
    dict_struct = {}
    with open(os.path.abspath('module/psm/结构化提取结果/letter{}.txt'.format(num)), 'r') as f:
        data = f.readlines()
        for line in data:
            struct1 = line.split('\t')[0]
            dict_struct[struct1] = float(line.split('\t')[1])
    return dict_struct


# 加载特殊字符段
def load_special(num):
    dict_struct = {}
    with open(os.path.abspath('module/psm/结构化提取结果/special{}.txt'.format(num)), 'r') as f:
        data = f.readlines()
        for line in data:
            struct1 = line.split('\t')[0]
            dict_struct[struct1] = float(line.split('\t')[1])
    return dict_struct


def patterns(w):
    structure, groups = [], []
    # match每次遍历的是匹配的片段
    for match in pattern_re.finditer(w):
        L_pat, D_pat = match.groups()  # 是否有对应可匹配的片段
        pat_t = L if L_pat else D if D_pat else S
        group = match.group()  # 匹配的内容
        structure.append((pat_t, len(group)))  # 记录L,3这样的格式
        groups.append(group)  # 记录对应内容
    return tuple(structure), groups
    # structure为[(L,1),(D,6)]的格式  groups为['a','123456']的格式


# 用于大小写的模式识别
def patterns_upper(w):
    structure, groups = [], []
    # match每次遍历的是匹配的片段
    for match in pattern_up.finditer(w):
        small_pat, big_pat = match.groups()  # 是否有对应可匹配的片段
        pat_t = L_BIG if big_pat else L_SMALL if small_pat else DS
        group = match.group()  # 匹配的内容
        structure.append((pat_t, len(group)))  # 记录L,3这样的格式
        groups.append(group)  # 记录对应内容
    return tuple(structure), groups
    # structure为[(L_BIG,1),(L_SMALL,6)]的格式  groups为['A','abcde']的格式


# 模式识别
def process_struct(struct_, groups):
    struct = ''
    prob_ = []
    # global structure

    # 表示数字和特殊字符类型的个数
    num_d = 0
    num_s = 0
    for i in range(len(struct_)):
        type_ = struct_[i][0]
        length = struct_[i][1]
        struct += type_ + str(length)
        type_num = 0
        # content = groups[i]
        # tmp = {}
        if type_ == 'L':
            tmp = load_letter(length)
            if groups[i] in tmp:
                prob_.append(float(tmp[groups[i]]))
            else:
                prob_.append(float(1 / pow(len(tmp), 2)))
        elif type_ == 'D':
            num_d = num_d + length
            tmp = load_digit(length)
            if groups[i] in tmp:
                prob_.append(float(tmp[groups[i]]))
            else:
                prob_.append(float(1 / pow(len(tmp), 2)))
        else:
            num_s = num_s + length
            tmp = load_special(length)
            if groups[i] in tmp:
                prob_.append(float(tmp[groups[i]]))
            else:
                prob_.append(float(1 / pow(len(tmp), 2)))
    # 3 对数字个数的模式识别
    if num_d == 0:
        score_count.append(0)
        global type_count
        type_count = type_count + 1
        # print('d长度等于0加分0')
    elif 1 <= num_d <= 6:
        score_count.append(5)
        # print('d长度1-6加分5')
    elif num_d > 6:
        score_count.append(10)
        # print('d长度大于6加分10')

    # 4 对特殊符号个数的模式识别
    if num_s == 0:
        score_count.append(0)
        type_count = type_count + 1
        # print('s长度等于0加分0')
    elif num_s == 1:
        score_count.append(10)
        # print('s长度等于1加分20')
    elif num_s > 1:
        score_count.append(20)
        # print('s长度大于1加分20')

    return struct, prob_


# 模式识别, 大小写
def process_struct_upper(struct_):
    struct = ''
    # 表示数字和特殊字符类型的个数
    num_big = 0
    num_small = 0
    for i in range(len(struct_)):
        type_ = struct_[i][0]
        length = struct_[i][1]
        struct += type_ + str(length)
        if type_ == 'L_BIG':
            num_big = num_big + length
            # print('有大写')
        elif type_ == 'L_SMALL':
            num_small = num_small + length
            # print('有小写')

    # 3 对字母个数以及大小写的模式识别

    if num_big == 0 or num_small == 0:
        global type_count
        type_count = type_count + 1
        if (num_big + num_small) == 0:
            score_count.append(0)
            type_count = type_count + 1
            # print('大小写都没有')
        else:
            score_count.append(10)
            # print('大小写有一个')
    elif num_big != 0 and num_small != 0:
        score_count.append(25)
        # print('大小写都有')
    return struct


# def get_prob_out(pwd2):
#     para1 = patterns(pwd2)
#     # print(para1)
#     para2 = process_struct(para1[0], para1[1])
#     para3 = load_struct()
#     if para2[0] in para3:
#         p1 = para3[para2[0]]
#         p2 = 1
#         for i in range(len(para2[1])):
#             p2 = p2 * para2[1][i]
#         return p1 * p2


# 5 对于字符种类部分的赋分
def type_score():
    global type_count
    if type_count == 0:
        score_count.append(20)
        # print('复杂系数4')
    elif type_count == 1:
        score_count.append(10)
        # print('复杂系数3')
    elif type_count == 2:
        score_count.append(5)
        # print('复杂系数2')
    type_count = 0


# if __name__ == '__main__':
#     sample_path = cur_path + "\\samples\\samples.txt"
#     load_prob(file_dic)
#     tag = 0
#     while tag == 0:
#         pwd_str = input("请输入口令：")
#         get_prob(pwd_str)
#         print('口令%s的概率为：' % pwd_str, prob__)
#         # print(score_count)
#         score2 = sum(score_count)
#         score_count.clear()
#         # print('score2分数为：{}'.format(score2))
#         if prob__ == -1:
#             score1 = score2
#         elif prob__ != -1:
#             arrA = create_A(sample_path)
#             arrC = create_C(arrA)
#             j = get_index(arrA, prob__)
#             print(j)
#             print('口令%s的强度值为：' % pwd_str, arrC[j])
#             score1 = int(strength(arrC[j]))
#             if score1 > 100:
#                 score1 = 100
#             print(strength(arrC[j]))
#         score = score1 * 0.5 + score2 * 0.5
#         print(score)
#         tag_str = input("是否继续？")
#         if tag_str == "否":
#             tag = 1
    # sample_path = cur_path + "\\samples\\samples.txt"
    # load_prob(file_dic)
    # # pwd_str = input()
    # # pwd = PSM(pwd_str)
    # pwd_prob = get_prob(pwd_str)
    # arrA = create_A(sample_path)
    # arrC = create_C(arrA)
    # j = get_index(arrA, pwd_prob)
    # strength(arrC[j])
# load_prob(file_dic)
#         get_prob(self.password)  # 计算的到prob__
        # 将score_count的值累加并赋给score2
        # self.score2 = sum(score_count)
        # score_count.clear()  # 清空数组
