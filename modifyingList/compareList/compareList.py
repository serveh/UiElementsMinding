import pandas as pd

myApp=[]
theirApp=[]
sameApp=[]
cheker = None
df = pd.read_excel('/home/srwe/Desktop/comparedList.xlsx')
for i in range(len(df['L1'])):
    cheker=False
    s1 = str(df['L1'][i])
    for j in range(len(df['L2'])):
        s2=str(df['L2'][j])
        if (not s1=='nan' and not s2=='nan'):
            if ((s1 in s2) or (s2 in s1)):
                cheker=True
    if not cheker and not s1=='nan':
        myApp.append(s1)
pd.DataFrame(myApp).to_excel('natanLeft.xlsx', header=False, index=False)

for i in range(len(df['L2'])):
    cheker=False
    s1 = str(df['L2'][i])
    for j in range(len(df['L1'])):
        s2=str(df['L1'][j])
        if (not s1=='nan' and not s2=='nan'):
            if ((s1 in s2) or (s2 in s1)):
                cheker=True
    if not cheker:
        theirApp.append(s1)

pd.DataFrame(theirApp).to_excel('myLeft.xlsx', header=False, index=False)



'''
result = df[df['L2'].isin(list(df['L1']))]
writer = ExcelWriter('pythonExport.xlsx')
result.to_excel(writer,'Sheet1',index=False)
writer.save()
'''