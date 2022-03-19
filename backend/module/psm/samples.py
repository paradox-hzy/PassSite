import os
import numpy as np
import random
import math
import heapq

# 加载攻击模型生成的口令，并生成一系列样本

cur_path = os.getcwd()  # 获取当前的路径
# file = cur_path + "/pwd/dictionary.txt"  # 攻击模型生成的口令及其对应的频率
file = cur_path + "/pwd/csdn_gen.txt"
sample_path = cur_path + "\\samples\\"  # 样本
num = 0  # 用于记录生成的样本个数
dict1 = {}
dict2_k = {}
k_arr = []
r_arr = []
sample_num = 1000


# 快速排序
def quickSort(arr, left=None, right=None):
    left = 0 if not isinstance(left, (int, float)) else left
    right = len(arr)-1 if not isinstance(right, (int, float)) else right
    if left < right:
        partitionIndex = partition(arr, left, right)
        quickSort(arr, left, partitionIndex-1)
        quickSort(arr, partitionIndex+1, right)
    return arr


def partition(arr, left, right):
    pivot = left
    index = pivot+1
    i = index
    while i <= right:
        if arr[i] < arr[pivot]:
            swap(arr, i, index)
            index += 1
        i += 1
    swap(arr, pivot, index-1)
    return index-1


def swap(arr, i, j):
    arr[i], arr[j] = arr[j], arr[i]


# 加载攻击模型生成的口令，并返回数组
# def load_prob(path):
#     lines = []
#     with open(path, 'r') as f:
#         # with open(samples, 'w') as t:
#             data = f.readlines()
#             for line in data:
#                 pwd1 = line.split('\t')[0]
#                 dict1[pwd1] = line.split('\t')[1]
#                 prob = line.split('\t')[1]
#                 lines.append(prob)
#                 prob_array = np.array(lines)
#                 prob_array = prob_array.astype(float)
#     return prob_array

# 加载攻击模型生成的口令，并返回数组
def load_prob(path, m):
    # lines = []
    with open(path, 'r') as f:
        # with open(samples, 'w') as t:
            data = f.readlines()
            i = 0
            for line in data:
                pwd1 = line.split('\t')[0]
                dict1[pwd1] = line.split('\t')[1]
                prob = line.split('\t')[1]
                # lines.append(prob)
                k = pow(random.uniform(0, 1), (1 / (10000 * float(prob))))
                # print(k)
                k_arr.append(k)
                dict2_k[k] = pwd1
                if i <= m:
                    # r_arr.append(k)
                    heapq.heappush(r_arr, k)
                else:
                    heapq.heappushpop(r_arr, k)
                    # kt = r_arr1cc
                    # if k > kt:
                    #     r_arr[0] = k
                i = i + 1
                if i >= 100000:
                    break
            # prob_array = np.array(lines)
            # prob_array = prob_array.astype(float)
    # return prob_array


def get_prob(pwd2):
    return dict1[pwd2]


# # 生成多个样本
# def gen_samples(pwd_array, path):
#     # sample_array = []
#     for j in range(100):
#         sample_array = []
#         for i in range(100):
#             # sample_array[i] = pwd_array[2]
#             a = pwd_array[random.randint(0, 9999)]
#             sample_array.append(a)
#         sample_array.sort(reverse=True)
#         with open(os.path.join(path, 'samples_{}.txt').format(j), 'w') as t:
#             for i in range(100):
#                 # sample_array[i] = pwd_array[2]
#                 # a = pwd_array[random.randint(2, 5)]
#                 # sample_array.append(a)
#                 t.writelines(str('{:0.22f}'.format(sample_array[i]).lstrip('[').rstrip(']'))+'\n')
#     # return sample_array

# 生成多个样本
def gen_samples(path, m):
    t_arr = []
    for i in range(m):
        t_arr.append(dict1[dict2_k[r_arr[i]]])
    t_arr.sort(key=float, reverse=True)
    with open(os.path.join(path, 'samples.txt'), 'w') as t:
        for i in range(m):
            t.writelines(str('{:0.22f}'.format(float(t_arr[i])))+'\n')
    # return sample_array


if __name__ == '__main__':
    load_prob(file, sample_num)
    gen_samples(sample_path, sample_num)
    print(r_arr)
    # li = '12fd34'
    # print(int(li[:3]))
