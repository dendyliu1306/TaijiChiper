import tkinter as tk
import random as rd
from tkinter.filedialog import askopenfilename
from model.taiji.chiper import TaijiChiper

def calculate_precentage(changed_chiper, chiper):
    counter = 0
    for i in range(len(chiper)):
        if changed_chiper[i] == chiper[i]:
            counter += 1

    precentage = 100 - (counter / len(chiper) * 100)
    print('Same byte: ', counter)
    print('Diff percentage: ', precentage)

def test_diffusion(data, key, n):
    print('TEST DIFFUSON =====================================')
    n_data = len(data)
    datas = []
    rd_idx = rd.sample(range(n_data), n)

    tj = TaijiChiper(key)
    chiper = tj.encrypt(data)
    for i in range(n):
        idata = bytearray(data)
        idata[rd_idx[i]] = (idata[rd_idx[i]] + 1) % 256
        tj = TaijiChiper(key)
        changed_chiper = tj.encrypt(idata)
        print(i)
        print('Bit post: ', rd_idx[i])
        calculate_precentage(changed_chiper, chiper)

def test_confusion(data, key, n):
    print('TEST CONFUSION =====================================')
    n_key = len(key)
    keys = []
    rd_idx = rd.sample(range(n_key), n)    
    for i in range(n):
        ikey = bytearray(key)
        ikey[rd_idx[i]] = (ikey[rd_idx[i]] + 1) % 256
        keys.append(ikey)

    tj = TaijiChiper(key)
    chiper = tj.encrypt(data)
    for i in range(len(keys)):
        key_text = keys[i].decode()
        tj = TaijiChiper(keys[i])
        changed_chiper = tj.encrypt(data)
        print(i)
        print('Key: ', key_text)
        calculate_precentage(changed_chiper, chiper)

def main():
    filename = askopenfilename()
    with open(filename, 'rb') as f:
        data = bytearray(f.read())
    key = bytearray('kript ografitaiji'.encode())
    n
    n = 5
    print(len(data))
    test_confusion(data, key, n)
    test_diffusion(data, key, n)

if __name__ == '__main__':
    main()