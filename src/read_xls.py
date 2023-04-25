# https://xlrd.readthedocs.io/en/latest/

import xlrd

book = xlrd.open_workbook("../example1/Kaseta_2v1 BOM.xls")
print("The number of worksheets is {0}".format(book.nsheets))
print("Worksheet name(s): {0}".format(book.sheet_names()))
sh = book.sheet_by_index(0)
print("Name:{0} Rows:{1} Cols:{2}".format(sh.name, sh.nrows, sh.ncols))

for rx in range(sh.nrows):
    print(sh.row(rx))
