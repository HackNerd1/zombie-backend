import pandas as pd
import json
import numpy as np
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)

class Visualization():
    '''数据可视化'''
    def __init__(self, local_data_path:str, save_path:str):
        self.local_data = pd.read_csv(local_data_path, encoding='GB2312')
        self.save_path = save_path
        self.data_length = len(self.local_data['flag'])
        self.columns_with_flag = {'RadarmapIndustry':'行业', 'PieplotIndustryType':'企业类型', 'Roseplot': '区域','BarplotPeople':'控制人类型'}
        self.columns_with_no_flag = {'RingplotZombie':'flag', 'RadarmapArea':'区域'}
        self.map_data = [{"name":"湖北","confirm":1},{"name":"广东","confirm":1},{"name":"浙江","confirm":1},{"name":"河南","confirm":1},{"name":"湖南","confirm":1},{"name":"江西","confirm":1},{"name":"安徽","confirm":1},{"name":"重庆","confirm":1},{"name":"江苏","confirm":1},{"name":"山东","confirm":1},{"name":"四川","confirm":1},{"name":"北京","confirm":1},{"name":"上海","confirm":1},{"name":"福建","confirm":1},{"name":"黑龙江","confirm":1},{"name":"陕西","confirm":1},{"name":"广西","confirm":1},{"name":"河北","confirm":1},{"name":"云南","confirm":1},{"name":"海南","confirm":1},{"name":"辽宁","confirm":1},{"name":"山西","confirm":1},{"name":"天津","confirm":1},{"name":"贵州","confirm":1},{"name":"甘肃","confirm":1},{"name":"吉林","confirm":1},{"name":"内蒙古","confirm":1},{"name":"宁夏","confirm":1},{"name":"新疆","confirm":1},{"name":"香港","confirm":1},{"name":"青海","confirm":1},{"name":"台湾","confirm":1},{"name":"澳门","confirm":1},{"name":"西藏","confirm":1}]

    def save_file(self):
        file = open(self.save_path, 'w',encoding='utf-8')
        data = self._postprocess()
        json.dump(data,file,ensure_ascii=False)
        file.close()
    def to_json(self, x, y):
        '''转换成json对象
        
        Arguments:
            x, y
        Returns:
            json data
        '''
        
        output = {"x" : x, "y" : y}

        return output
    def loc_data_no_flag(self, column_name:str):
        '''单单是某一列的数据统计
        Argumenst:
            column_name
        return:
            json数组
        '''

        colmuns =  pd.DataFrame( self.local_data[ column_name ].value_counts() ).T.columns
        data = self.local_data[ column_name ].value_counts()
        output = []
        for col in colmuns:
            json_data = self.to_json( col, data[col] )
            output.append(json_data)

        return output
    def loc_data_with_flag(self, column_name:str):
        '''僵尸企业中,各列数据的占比

        Argumenst:
            column_name
        return:
            json数组
        '''
        data = self.local_data[ self.local_data['flag'] == 1 ].loc[ : , column_name].value_counts()
        colmuns =  pd.DataFrame( data ).T.columns
        output = []
        for col in colmuns:
            json_data = self.to_json( col, data[col] )
            output.append(json_data)

        return output

    def _postprocess(self):
        '''将所有数据整合到一个json对象中

        Returns:
            json数据

        '''
        processeddata = {}
        for i in self.columns_with_flag:
            processeddata[i] = self.loc_data_with_flag(self.columns_with_flag[i])
        for i in self.columns_with_no_flag:
            processeddata[i] = self.loc_data_no_flag(self.columns_with_no_flag[i])
        # 僵尸企业总数
        processeddata['LiquidplotZombie'] = self.local_data['flag'].value_counts()[0]
        # 非僵尸企业总数
        processeddata['not_zomboe_sum'] = self.local_data['flag'].value_counts()[1]
        # 企业总数
        processeddata['data_len'] = self.data_length

        processeddata['ProvincesMapZombie'] = self.ProvincesMapZombie()
        
        processeddata = json.dumps(processeddata, cls=NpEncoder)

        return processeddata
    def ProvincesMapZombie(self):
        '''对地图数据进行处理

        Returns:
            json数据

        '''
        origin_data = self.loc_data_with_flag('区域')
        output = self.map_data

        for i in origin_data:
            for j in output:
                if i['x'] == j['name']:
                    j['confirm'] = i['y']

        return output

if __name__ == '__main__':
    output_path = '/app/model/output'# 对应服务器模型输出路径
    V = Visualization(output_path+'./local_data.csv', output_path+'./plot_data.json')
    V.save_file()
    # a = V.ProvincesMapZombie()
    # a = V.loc_data_no_flag('flag')
    # print(data)