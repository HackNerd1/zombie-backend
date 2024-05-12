'''
TODO 数据接口
该文件下
'''
import os
import pandas as pd
from itertools import combinations, permutations# 用于排列组合
from sklearn.ensemble import RandomForestClassifier# 随机森林
from sklearn.externals import joblib
'''
读取文件
'''
fileArry = []
# 存放路径
data_source_path = '/app/upload_tmp/'# 对应服务器接收到的文件目录
model_path = '/app/model/'# 对应服务器接模型, 训练集数据 存放位置
output_path = '/app/model/output/'# 对应服务器模型输出路径

RForest =  joblib.load("/app/model/RForest.m")

# 遍历目录 将文件路径存到fileArry
for dirname, _, filenames in os.walk(data_source_path):
    for filename in filenames:
        print(filename)
        fileArry.append(os.path.join(data_source_path, filename))

# 在文件夹中查找year_report.csv
def find_year_rep(fileArry):
    for filepath in fileArry:
        # df = pd.read_csv(filepath,encoding = 'GB2312')
        df = pd.read_csv(filepath,encoding = 'utf-8')
        if '净利润' and '纳税总额' in df.columns:
            return df
    return 1

# 在文件夹中查找base.csv
def find_base(fileArry):
    for filepath in fileArry:
        # df = pd.read_csv(filepath,encoding = 'GB2312')
        df = pd.read_csv(filepath,encoding = 'utf-8')
        if '行业' in df.columns:
            return df
    return 1

# 读取year_report.csv 到两个地址
df = find_year_rep(fileArry)# 用于比较差异
base = find_base(fileArry)
dataframe = find_year_rep(fileArry)# 最终结果

'''
数据处理

思路：
    先将所有缺失的year向上填充,因为存在某几个单元格,他们的位置正好处于两个年份的交汇处
    比如 这种情况：
        ID：11111 year：2015
        ID：11112 year：None <---
        ID：11113 year：2016
    此时ID11112本因该为2016 却被向上填充成了2015 所以需要单独查找该单元格 使其向下填充为2016 然后再将剩余的所以年份向上填充
    因为异常的单元格已经被处理 所以得出的dataframe不再会出现数据长度不一致的情况

    本次用到difference函数来实现本操作
'''
# 对年份的空值处理
def fill_na_year(inputdf):
    inputdf["year"] = inputdf['year'].fillna(method="pad")
    df_year_2015 = inputdf[inputdf.year == 2015].reset_index().drop(['index'],axis =1)
    df_year_2016 = inputdf[inputdf.year == 2016].reset_index().drop(['index'],axis =1)
    df_year_2017 = inputdf[inputdf.year == 2017].reset_index().drop(['index'],axis =1)
    return df_year_2015,df_year_2016,df_year_2017

df_year_2015,df_year_2016,df_year_2017 = fill_na_year(df)

# 对dataframe中指定单元格年份进行填充 i是传入的需要修改行的ID
def re_fill_na_year(i):
    temp_index = dataframe[(dataframe['ID']==i) & (dataframe['year'].isnull())].index# 条件：ID== i & year == None  
    dataframe.loc[temp_index,'year'] = dataframe.loc[temp_index,'year'].fillna(dataframe.loc[temp_index+1,'year'].values[0])# 向下填充

df_array = list(combinations([df_year_2015,df_year_2016,df_year_2017], 2))# 将dataframe对象进行排列组合

for df in df_array:
    # 比较各组合之间的差异 set函数返回一个元组 通过for来遍历差异值
    diff1 = set(df[0]["ID"]).difference(df[1]["ID"])
    diff2 = set(df[1]["ID"]).difference(df[0]["ID"])
    # 当返回元组不为空时
    if len(diff1) !=0:
        for i in diff1:
            try:
                re_fill_na_year(i)# 填充空值
            except:
                pass
    elif len(diff2) != 0:
        for i in diff2:
            try:
                re_fill_na_year(i)
            except:
                pass

df_year_2015,df_year_2016,df_year_2017 = fill_na_year(dataframe)

df_year_2016 = df_year_2016.drop(['ID'],axis =1)# 去掉df_year_2016，df_year_2017 的 ID 不然target会出现三列ID
df_year_2017 = df_year_2017.drop(['ID'],axis =1)

'''
建模：

说明：
    这里将target先保存后读取，是因为输出为csv可以将dataframe中名字相同列名作出区分
    比如：
        原本的列名为：      --->       输出为csv的列名：
        净利润 净利润 净利润           净利润 净利润.1 净利润.2
'''
target = pd.concat([df_year_2015,df_year_2016,df_year_2017], axis=1)# 合并数据
target.to_csv(output_path+'/target.csv',encoding="GB2312",index =False)

target = pd.read_csv(output_path+'/target.csv',encoding = 'GB2312')# 用于预测
# train = pd.read_csv(model_path+'/train.csv',encoding = 'GB2312')# 用于训练模型


output = target.loc[:,['ID','净利润']]# 输出
output = output.rename(columns={'净利润':'flag'})# 多读取一列方便操作
target = target.loc[:,['净利润', '净利润.1','净利润.2','纳税总额','纳税总额.1','纳税总额.2']]# 选取特征

# 缺失值用众数填充 这里填充后的值为0
for val in target.columns:
    target[val] = target[val].fillna(target[val].mode()[0])

'''随机森林'''
# x = train.drop(['flag'],axis=1)
# y = train.loc[:,['flag']]
# RForest = RandomForestClassifier(n_jobs=2,n_estimators=10)
# RForest.fit(x,y)
flag = RForest.predict(target)
output['flag'] = flag
output = output.sort_values(by='ID').reset_index().drop(['index'], axis=1)
output.to_csv(output_path+'/output.csv',encoding="GB2312",index =False)

local_data = pd.concat([ base, output.drop('ID', axis=1)], axis= 1)
local_data.to_csv(output_path+'/local_data.csv',encoding="GB2312",index =False)
# 删除target.csv文件
if(os.path.exists(output_path+"/target.csv")):
    os.remove(output_path+"/target.csv")
    print('sucessfully delete target.csv')