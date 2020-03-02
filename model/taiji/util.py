import numpy as np
from functools import reduce

from model.taiji.constant import *
from model.taiji.constant import S_BOX
from model.taiji.constant import MIX_BOX

def subt_expansion(data):
    expand_data = np.zeros((4, 4), dtype='int')
    for r in range(4):
        for c in range(4):
            base_i, base_j = r // 2 * 2, c // 2 * 2
            base_idx = r // 2 * 2 + c // 2
            curr_idx = (r - base_i) * 2 + (c - base_j)
            box_idx = (base_idx + curr_idx) % 4
            val = data[curr_idx]
            expand_data[r, c] = (S_BOX[box_idx, val] + expand_data[base_i, base_j]) % 256
    return expand_data

def shift_row(data):
    R, C = data.shape
    shifted_data = np.zeros(data.shape, dtype='int')
    for r in range(len(data)):
        prev_r = (r - 1) % R
        prev_c = (r - 1) % C
        shifted_data[r] = np.roll(data[r], data[prev_r, prev_c])
    return shifted_data

def xor_multiply(data):
    Rd, Cd = data.shape
    Rb, Cb = MIX_BOX.shape
    M = Rd = Cb
    xmulti_data = np.zeros((Rb, Cd), dtype='int')
    for r in range(Rb):
        for c in range(Cd):
            multi_data = [(MIX_BOX[r, i] * data[i, c]) % 256 for i in range(M)]
            xmulti_data[r, c] = reduce(lambda a, b: a ^ b, multi_data)
    return np.reshape(xmulti_data, (-1,))

def mix_col(data):
    R, C = data.shape
    mixed_data = np.zeros(data.shape, dtype='int')
    for c in range(C):
        col_data = np.reshape(data[:, c], (-1, 1))
        mixed_data[:, c] = xor_multiply(col_data)
    return mixed_data

def subt_compression(data):
    compressed_data = np.zeros((2, 2), dtype='int')
    for r in range(2):
        for c in range(2):
            ex_r, ex_c = r * 2, c * 2
            val_0 = data[ex_r, ex_c]
            val_1 = data[ex_r, ex_c + 1]
            val_2 = data[ex_r + 1, ex_c]
            val_3 = data[ex_r + 1, ex_c + 1]
            idx_0 = r * 2 + c
            idx_1 = (idx_0 + 1) % 4
            idx_2 = (idx_0 + 2) % 4
            idx_3 = (idx_0 + 3) % 4
            sub_data = [S_BOX[idx_0, val_0], S_BOX[idx_1, val_1], S_BOX[idx_2, val_2], S_BOX[idx_3, val_3]]
            compressed_data[r, c] = reduce(lambda a, b: a ^ b, sub_data)
    return compressed_data

def subt_box(data, box_idx):
    ori_shape = data.shape
    flat_data = np.ravel(data)
    for i in range(len(flat_data)):
        flat_data[i] = S_BOX[box_idx, flat_data[i]]
    return np.reshape(flat_data, ori_shape)
