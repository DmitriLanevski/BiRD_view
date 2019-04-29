import xmltodict
import pandas as pd

#Class for storing and selecting data
class DataContainer:
    def __init__(self, data):
        self.uploadedData = data
        self.readData()

    #Parses data
    def readData(self):
        d = xmltodict.parse(self.uploadedData)
        self.dic = d['catalog']
        self.head = self.dic['head']
        self.data = self.dic['data']
        self.df = pd.read_csv(pd.compat.StringIO(self.data['values']), header=None)

    #Selects data according to key variation
    def data_by_key_variation(self, pol): #does not work for all variables yet
        key_variation = self.data['key_variation']
        var_list = self.list_maker(key_variation, 0)
        y = []
        j = 0
        for i in var_list:
            values = self.df.iloc[j]
            values.pop(0)
            j += 1
            if pol is not None:
                pol_list = self.list_maker('polarization', pol)
                for v, p in zip(values, pol_list):
                    if p == pol:
                        y.append(v)
            else:
                for v in values:
                    y.append(v)
        return y

    def y_axis_by_key_variation(self, length):
        key_variation = self.data['key_variation']
        var_list = self.list_maker(key_variation, 0)
        num = length//len(var_list)
        y = []
        j = 0
        for i in var_list:
            k = [i] * num
            y.append(k)

        w = [i for x in y for i in x]
        return w

    def x_axis_by_variable(self, name, pol, length):
        var_list = self.list_maker(name, 1)
        num = length//len(var_list)
        var_list = self.list_maker(name, 0)
        y = []

        if pol is not None:
            pol_list = self.list_maker('polarization', pol)
            for v, p in zip(var_list, pol_list):
                if p == pol:
                    y.append(v)
        else:
            for v in var_list:
                y.append(v)

        w = y * num
        return w

    #Reads data from DataContainer into list
    def list_maker(self, value, u):
        string = self.data[value]
        list1 = string.split(',')
        if u == 1:
            list1 = list(set(list1))
        return list1
