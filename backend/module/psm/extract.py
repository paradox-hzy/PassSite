import re
from collections import defaultdict
import os
import numpy
pattern_re = re.compile(r'([a-zA-Z]+)|([0-9]+)|[^a-zA-Z0-9]+')
# 利用正则表达式进行片段匹配
L, D, S = 'L', 'D', 'S'
LEN_MAX, LEN_MIN = 40, 4  # 数据长度范围
structure = defaultdict(int)  # 存放密码结构和对应出现次数
digit = defaultdict(int)
letter = defaultdict(int)
special = defaultdict(int)


def check(str_):
    for i in range(len(str_)):
        if ord(str_[i]) > 126 or ord(str_[i]) < 32:
            return 0
    return 1


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


# 模式识别
def process(struc, groups, count):
    struct=''
    global structure
    for i in range(len(struc)):
        type = struc[i][0]
        length = struc[i][1]
        struct += type+str(length)
        content = groups[i]
        if type == 'L':
            letter[content] += count
        elif type == 'D':
            digit[content] += count
        else:
            special[content] += count

    structure[struct] += count


def process_dict(diction, type):
    total = defaultdict(int)  # 存放不同长度的总次数
    def de_dict():
        return defaultdict(int)
    final = defaultdict(de_dict)  # 每个长度对应一个字典 存放对应的片段和出现次数
    for k, v in diction.items():
        # k为对应片段 v为对应次数
        final[len(k)][k] += v
        total[len(k)] += v
    del diction
    for k, dic in final.items():
        # k为长度 dic为片段和次数的字典
        # 同一长度下按照概率排序
        dic = sorted(dic.items(), key=lambda d: d[1], reverse=1)
        with open((r'结构化提取结果/'+type + str(k) + '.txt'), 'w') as f:
            for s, v in dic:
                s1 = s+'\t'+str(v/total[len(s)])+'\n'
                f.write(s1)
    # del dic


def process_structure():  # 将结构和对应的概率输出到文本
    total = 0  # 总结构数目
    global structure
    for key, count in structure.items():
        total += count
    structure = sorted(structure.items(), key=lambda d: d[1], reverse=1)
    with open(r'./结构化提取结果/structure.txt', 'w') as f:
        for key, count in structure:  # key是L6D2的结构 count是对应出现次数
            ans = (key) +'\t'+str(count/total)+'\n'
            f.write(ans)
    del structure


# train_data = r'train_password_withcount.txt'
train_data = r'pcfg\rockyou-withcount.txt'
batch_size = 1e6
f = open(train_data, encoding='UTF-8', mode='r')
# 下面开始先进行口令结构化的提取 并记录对应次数
while 1:
    num = 0
    password = defaultdict(int)  # 存放不同密码以及对应次数
    while num <= batch_size:
        lines_1 = (f.readline().rstrip('\n'))
        if lines_1 == '':
            break
        if len(lines_1) < 8 or lines_1[7] != ' ':  # 0-6为次数 7为空格 8之后为密码 不满足此格式的跳过
            continue
        if check(lines_1) == 0:
            continue
        if len(lines_1[8:]) > LEN_MAX or len(lines_1[8:]) < LEN_MIN:  # 如果长度不符合要求则跳过
            continue
        pwd = lines_1[8:]
        count = int(lines_1[:7])
        s, groups = patterns(pwd)
        # structure为[(L,1),(D,6)]的格式  groups为['a','123456']的格式,count为频数
        process(s, groups, count)
    if num == 0:
        break
    # 对密码进行结构化提取 并计算概率

# 此时letter等片段字典中存放着不同片段以及对应的出现次数 structure存放着结构化口令以及对应出现次数


# 将提取结果以文本形式输出
if not os.path.isdir('结构化提取结果'):
    os.makedirs(os.path.join('结构化提取结果'))
process_dict(letter, 'letter')
process_dict(digit, 'digit')
process_dict(special, 'special')
process_structure()

