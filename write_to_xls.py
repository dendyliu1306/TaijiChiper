import xlwt
from xlwt import Workbook
from model.taiji.constant import *

def main():
    wb = Workbook()
    sheet1 = wb.add_sheet('Sheet 1')
    sheet2 = wb.add_sheet('Sheet 2')
    sheet3 = wb.add_sheet('Sheet 3')
    sheet4 = wb.add_sheet('Sheet 4')
    sheets = [sheet1, sheet2, sheet3, sheet4]
    for sheet_idx in range(len(sheets)):
        curr_box = np.reshape(S_BOX[sheet_idx], (16, 16))
        for i in range(len(curr_box)):
            for j in range(len(curr_box[i])):
                el_hex = bytearray([curr_box[i, j]]).hex()
                sheets[sheet_idx].write(i + 1, j, el_hex)
    wb.save('S_Box.xls')

if __name__ == '__main__':
    main()