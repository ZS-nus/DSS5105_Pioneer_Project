import pandas as pd

# 读取表格
df = pd.read_csv('../processed_files/apple2/table_18.csv ')

# 查看第二列的数据类型
second_column_dtype = df.iloc[:, 1].dtype
print(f"The data type of the second column is: {second_column_dtype}")