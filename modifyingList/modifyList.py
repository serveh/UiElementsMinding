import pandas as pd

df = pd.read_excel('/home/srwe/Desktop/nataniList.xlsx')
list=[]

for i in range(len(df['L1'])):
    s1 = str(df['L1'][i])
    s1 = s1[40:]
    print(s1)
    list.append(s1)
pd.DataFrame(list).to_excel('nataniModified.xlsx', header=False, index=False)