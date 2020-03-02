"""
    Module for taiji chiper
"""
import numpy as np
from functools import reduce

from model.taiji.util import subt_expansion
from model.taiji.util import subt_compression
from model.taiji.util import shift_row
from model.taiji.util import mix_col
from model.taiji.util import subt_box

from model.taiji.constant import R_BOX
from model.taiji.constant import VEC_INIT
from model.taiji.constant import BLOCK_SIZE
from model.taiji.constant import ECB_MODE
from model.taiji.constant import CBC_MODE 
from model.taiji.constant import CFB_MODE
from model.taiji.constant import OFB_MODE

class TaijiChiper:
    def __init__(self, key, mode=CBC_MODE):
        self.mode = mode
        self._n_iter = 13

        self._round_keys = self._generate_round_keys(key)
        self._encryption_map = {
            ECB_MODE: self._ecb_encryption,
            CBC_MODE: self._cbc_encryption,
            CFB_MODE: self._cfb_encryption,
            OFB_MODE: self._ofb_encryption
        }

        self._decryption_map = {
            ECB_MODE: self._ecb_decryption,
            CBC_MODE: self._cbc_decryption,
            CFB_MODE: self._cfb_decryption,
            OFB_MODE: self._ofb_decryption,
        }

    def _generate_round_keys(self, key):
        N = 4
        copy_key = np.copy(key)
        w_vec = [np.reshape(key, (N, N)), np.reshape(copy_key, (N, N))]
        for i in range(4):
            rev_i = N - 1 - i
            w_vec[0][i] = subt_box(w_vec[0][i], i)
            w_vec[1][i] = subt_box(w_vec[1][i], rev_i)

        K = []
        for i in range(self._n_iter - 1):
            K_round = []
            for j in range(2):
                res_vec = subt_expansion(np.roll(w_vec[j][i % N], i // N + 1))
                if i >= N:
                    res_vec = subt_box(res_vec ^ K[i - 1][j], i % N)
                if i >= N and i % 2 == 0:
                    res_vec = (res_vec + R_BOX[j, (i - N) // 2]) % 256
                K_round.append(res_vec) 
            K.append(K_round)
        K = np.array(K)

        K_final_round = np.array([[
            mix_col(reduce(lambda a, b: a ^ b, K[:len(K), 0])) ^ R_BOX[0, N - 1],
            mix_col(reduce(lambda a, b: a ^ b, K[:len(K), 1])) ^ R_BOX[1, N - 1],
        ]])
        K = np.vstack([K, K_final_round])
        return K

    def _f_func(self, data_block, key):
        l_data, r_data = np.split(data_block, 2)
        lsub_data = subt_expansion(l_data)
        rsub_data = subt_expansion(r_data)

        lshiftr_data = shift_row(lsub_data)
        rshiftr_data = shift_row(rsub_data)

        lxorr_data = lshiftr_data ^  rshiftr_data
        raddl_data = (rshiftr_data + lshiftr_data) % 256

        laddk_data = (lxorr_data + key[0]) % 256
        rxork_data = raddl_data ^ key[0]

        lxork_data = laddk_data ^ key[1]
        raddk_data = (rxork_data + key[1]) % 256

        lmixc_data = mix_col(lxork_data)
        rmixc_data = mix_col(raddk_data)

        lcom_data = subt_compression(rmixc_data)
        rcom_data = subt_compression(lmixc_data)
        return np.concatenate((np.ravel(lcom_data), np.ravel(rcom_data)))
    
    def _iter_encryption(self, data_block):
        round_data = data_block
        for i in range(self._n_iter):
            left_block, right_block = np.split(round_data, 2)
            new_left_block = right_block
            new_right_block = left_block ^ self._f_func(right_block, self._round_keys[i])
            round_data = np.concatenate((new_left_block, new_right_block))
        return round_data

    def _iter_decryption(self, data_block):
        round_data = data_block
        for i in range(self._n_iter):
            left_block, right_block = np.split(round_data, 2)
            new_right_block = left_block
            new_left_block = right_block ^ self._f_func(left_block, self._round_keys[-1 - i])
            round_data = np.concatenate((new_left_block, new_right_block))
        return round_data

    def _ecb_encryption(self, data_block, prev_block):
        y_data = prev_block ^ prev_block ^ data_block
        chiper_block =  self._iter_encryption(y_data)
        return chiper_block, chiper_block

    def _ecb_decryption(self, data_block, prev_block):
        y_data = prev_block ^ prev_block ^ data_block
        plain_block =  self._iter_decryption(y_data)
        return plain_block, plain_block

    def _cbc_encryption(self, data_block, prev_block):
        y_data = prev_block ^ data_block
        chiper_block = self._iter_encryption(y_data)
        return chiper_block, chiper_block

    def _cbc_decryption(self, data_block, prev_block):
        y_data = self._iter_decryption(data_block)
        plain_block = prev_block ^ y_data
        return plain_block, data_block

    def _cfb_encryption(self, data_block, prev_block):
        y_data = prev_block
        chiper_block = data_block ^ self._iter_encryption(y_data)
        return chiper_block, chiper_block

    def _cfb_decryption(self, data_block, prev_block):
        y_data = prev_block
        plain_block = data_block ^ self._iter_decryption(y_data)
        return plain_block, data_block

    def _ofb_encryption(self, data_block, prev_block):
        y_data = self._iter_encryption(prev_block)
        chiper_block = data_block ^ y_data
        return chiper_block, y_data

    def _ofb_decryption(self, data_block, prev_block):
        y_data = self._iter_decryption(prev_block)
        plain_block = data_block ^ y_data
        return plain_block, y_data

    def _create_blocks(self, data):
        n_data = len(data)
        n_remain = -(n_data % BLOCK_SIZE) % BLOCK_SIZE
        padding_data = np.array([0] * n_remain, dtype='int')
        new_data = np.concatenate((data, padding_data))
        return np.split(new_data, len(new_data) // BLOCK_SIZE)

    def _process(self, data, opt='ENC'):
        data_blocks = self._create_blocks(data)
        chiper_mode = self._encryption_map[self.mode] if opt == 'ENC' else self._decryption_map[self.mode]
        prev_block = np.copy(VEC_INIT)
        res_data = []
        for i in range(len(data_blocks)):
            res_block, prev_block = chiper_mode(data_blocks[i], prev_block)
            res_data.append(res_block)
        return np.ravel(res_data)

    def encrypt(self, data):
        chiper_data = self._process(data, opt='ENC')
        return bytearray(list(chiper_data))

    def decrypt(self, data):
        plain_data = self._process(data, opt='DEC')
        return bytearray(list(plain_data))
