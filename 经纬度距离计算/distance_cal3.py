import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt, ceil
import math
import time


def geodistance(lng1, lat1, lng2, lat2):
    lng1, lat1, lng2, lat2 = map(radians, [float(lng1), float(lat1), float(lng2), float(lat2)]) # 经纬度转换成弧度
    dlon = lng2-lng1
    dlat = lat2-lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    distance = 2*asin(sqrt(a))*6371*1000  # 地球平均半径，6371km
    distance = round(distance,0)
    return distance


minx_diff = pd.read_csv(r'D:\python\geo\minx_diff.csv', sep='\t')
minx_mile = int(input('请输入你要计算的最小距离（100、200、300、500、800、1000）：'))

for i in range(6):
    if minx_diff['minx_mile'][i]==minx_mile:
        diff_lon = minx_diff['diff_lon'][i]
        diff_lat = minx_diff['diff_lat'][i]
        print(diff_lon, diff_lat)
        break
else:
    print('抱歉，暂不支持该最小距离计算，请重新输入')

starttime = time.time()
file_name = r'D:\python\geo\distance_cal3\sTable.csv'
df1=pd.read_csv(file_name)
count_a = df1['name'].count() 

file_name2 = r'D:\python\geo\distance_cal3\tTable.csv'
df2=pd.read_csv(file_name2)
count_b = df2['name2'].count()

pieces = ceil(count_a * count_b / 10000000)   # 计算量上限为1000万
print(pieces)
linesPerFile = ceil(count_a / pieces)+1
print(linesPerFile)

with open(file_name, 'r') as f:
    csv_file = f.readlines()
print(len(csv_file))

filecount = 1
# 以0为起点，文件行数为终点，分片大小为间隔，循环遍历文件，每次遍历行数即为分片大小，而不是每行遍历一次，处理效率极高，但是比较吃内存
for i in range(0, len(csv_file), linesPerFile):
    # 打开目标文件准备写入，不存在则创建
    with open(file_name[:-4] + '_' + str(filecount) + '.csv', 'w+') as f:
        # 判断是否为第一个文件，不是的话需要先写入标题行
        if filecount > 1:
            f.write(csv_file[0])
        # 批量写入i至i+分片大小的多行数据，效率极高
        f.writelines(csv_file[i:i+linesPerFile])
    # 完成一个文件写入之后，文件编号增加1
    filecount += 1

distance = pd.DataFrame(columns=('name','lon','lat','name2', 'lon2', 'lat2', 'distance'))
for i in range(1, filecount):
    df_temp = pd.read_csv(file_name[:-4] + '_' + str(i) + '.csv')
    m = pd.concat([pd.concat([df_temp]*len(df2)).sort_index().reset_index(drop=True),
               pd.concat([df2]*len(df_temp)).reset_index(drop=True)], 1)
    # 避免链式赋值
    x = m[abs(m.lon-m.lon2) < diff_lon]
    n = x[abs(x.lat-x.lat2) < diff_lat]
    nn = n.copy()
    nn['distance'] = nn.apply(lambda ser: geodistance(ser['lon'], ser['lat'], ser['lon2'], ser['lat2']), axis=1)
    distance = distance.append(nn[nn.distance <= minx_mile])
distance.to_csv('D:/python/geo/distance_result.csv')
endtime=time.time()
cost_time = endtime - starttime
print('处理完成，程序运行时间： {}秒'.format(float('%.2f' % cost_time)))
