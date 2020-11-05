import matplotlib.pyplot as plt
from matplotlib import rcParams
from PIL import Image
from datetime import datetime


class MyChart:
    def __init__(self, table, name, directory, type):
        self.mytable = table
        self.name = name
        self.directory = directory
        self.type = type
        self.year_label = {1000: 'thous.',
                           100: 'hundr.'}
        self.rounder = ''
        self.months = {1: 'Jan',  2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                       7: 'Jul',  8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

    def save(self, size, name_diagram='', income=''):
        plt.savefig(self.directory + name_diagram + income + self.name, transparent=True)
        plt.close()
        self.set_size(size, name_diagram, income)

    def draw_month_chart(self):
        days = [31 if i % 2 == 1 else 30 for i in range(1, 13)]
        days[8::2] = [30] * 2
        days[7::2] = [31] * 3
        days[1] = 28 if datetime.now().year % 4 != 0 else 29
        index = [key - 1 for key, value in self.months.items()
                 if value.lower() == self.mytable.file_name.split('/')[-1].split('.')[0][:3].lower()]

        days = days[index[0]]
        fig = plt.figure()
        ax = fig.add_subplot(111)
        x_data = list(self.mytable.table["День"][:days])
        y_data = list(self.mytable.table["Итого"][:days])
        if self.type == 'hiss':
            ax.bar(x_data, y_data, color='#3b6fea', alpha=1, align='center')
        else:
            ax.plot(x_data, y_data, color='#3b6fea')
        y = [round(elem) for elem in ax.get_yticks()]
        x = [round(elem) for elem in ax.get_xticks()]
        ax.set_yticklabels(y, fontfamily='Roboto', fontsize=18, color='w', verticalalignment='center')
        ax.set_xticklabels(x, fontfamily='Roboto', fontsize=18, color='w', verticalalignment='top')
        self.save((310, 200))

    def draw_month_income(self):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        days = [31 if i % 2 == 1 else 30 for i in range(1, 13)]
        days[8::2] = [30] * 2
        days[7::2] = [31] * 3
        days[1] = 28 if datetime.now().year % 4 != 0 else 29
        index = [key - 1 for key, value in self.months.items()
                 if value.lower() == self.mytable.file_name.split('/')[-1].split('.')[0][:3].lower()]

        days = days[index[0]]

        x_data = list(self.mytable.table["День"][:days])
        y_data = list(self.mytable.table["Доход"][:days])
        if self.type == 'hiss':
            ax.bar(x_data, y_data, color='#3b6fea', alpha=1, align='center')
        else:
            ax.plot(x_data, y_data, color='#3b6fea')
        y = [round(elem) for elem in ax.get_yticks()]
        x = [round(elem) for elem in ax.get_xticks()]
        ax.set_yticklabels(y, fontfamily='Roboto', fontsize=18, color='w', verticalalignment='center')
        ax.set_xticklabels(x, fontfamily='Roboto', fontsize=18, color='w', verticalalignment='top')
        self.save((310, 200), income='income')

    def draw_diagram(self):
        rcParams['font.size'] = 20.0
        rcParams['font.family'] = 'Roboto'
        rcParams['text.color'] = 'w'

        fig = plt.figure()
        ax = fig.add_subplot(111)
        d = self.mytable.get_sum("Доход")
        r = self.mytable.get_sum("Итого")

        values = (d - r, r)
        colors = ('#ff5497', '#464c7a')
        ax.pie(values, colors=colors, wedgeprops=dict(width=0.15))

        self.save((120, 120), 'diagram_')

    def draw_costs_diagram(self):
        rcParams['font.size'] = 20.0
        rcParams['font.family'] = 'Roboto'
        rcParams['text.color'] = 'w'

        fig = plt.figure()
        ax = fig.add_subplot(111)
        cols = sorted(list(set([col.strip() for col in self.mytable.cols()])), key=lambda x: -self.mytable.get_sum(x))

        values = ([self.mytable.get_sum(col) for col in cols])
        colors = ['#ff5497', '#ffa05d', '#465bca', '#3ef3d3', '#9d3171', '#cc804a', '#3f46a3']

        ax.pie(values, colors=colors, wedgeprops=dict(width=0.16))
        self.save((150, 150), 'diagram_costs_')

        return cols, colors[:len(cols)], values

    def draw_year_chart(self, save=(290, 180)):

        fig = plt.figure()
        ax = fig.add_subplot(111, facecolor='#2c396c')
        x_data = list(self.mytable.table.columns)
        x_data.remove('Итого')
        y_data = [self.mytable.table[col][0] for col in self.mytable.table.columns
                  if col not in ['Итого', 'Unnamed: 0', 'День']]
        while y_data[0] == 0 and len(y_data) > 3 and x_data[0] != datetime.now().month:
            y_data = y_data[1:]
            x_data = x_data[1:]
        while y_data[-1] == 0 and len(y_data) > 3 and x_data[0] != datetime.now().month:
            y_data = y_data[:-1]
            x_data = x_data[:-1]

        if self.type == 'hiss':
            ax.bar(x_data, y_data, color='#3b6fea')
        else:
            ax.plot(x_data, y_data, color='#3b6fea')
        y_min = min([item for item in ax.get_yticks() if int(item) > 0])
        index = int('1' + str(int(y_min))[1:])
        while index > 1000:
            index //= 10
        while index < 100:
            index *= 10

        ax.set_yticklabels([round(elem) / index for elem in ax.get_yticks()],
                           fontfamily='Roboto', fontsize=18, color='w', verticalalignment='center')
        ax.set_xticklabels([self.months[item + 1] for item in [round(elem) for elem in ax.get_xticks()]],
                           fontfamily='Roboto', fontsize=18, color='w', verticalalignment='top', rotation=315)
        self.save(save)
        self.rounder = self.year_label[index]

    def set_size(self, size, name_diagram='', income=''):
        im = Image.open(self.directory + name_diagram + income + self.name + '.png')
        if not name_diagram:
            im2 = im.resize(size)
            im2.save(self.directory + name_diagram + income + self.name + '.png')
        else:
            im.crop((180, 90, 480, 395)).resize(size).save(self.directory + name_diagram + self.name + '.png')

    def draw_exchange_rates(self, mytype='Month'):
        fig = plt.figure()
        ax = fig.add_subplot(111)

        dollar_data = list(self.mytable.table["dollar"])
        evro_data = list(self.mytable.table["euro"])
        index_last = -1
        if mytype == 'Month':
            index_first = len(dollar_data) - 31

        elif mytype == 'Year':
            index_first = len(dollar_data) - 365

        elif mytype == '5 Years':
            index_first = int(len(dollar_data) - 365 * 3.7)

        elif mytype == 'Max':
            index_first = 0

        y_data = [i for i in range(len(dollar_data[index_first:index_last]))]
        dollar_data = dollar_data[index_first:index_last]
        evro_data = evro_data[index_first:index_last]
        if mytype == 'Year':
            x = [value for value in self.months.values()]
        elif mytype == '5 Years':
            x = [i for i in range(2015, 2021)]
        elif mytype == 'Max':
            x = [i for i in range(2015, 2021)]
        else:
            x = [-5, 0, 5, 10, 15, 20, 25, 30]
        if self.type == 'hiss':
            ax.bar(y_data, dollar_data, color='#3b6fea', alpha=1, align='center')
        else:
            ax.plot(y_data, dollar_data, color='#3b6fea')

        if self.type == 'hiss':
            ax.bar(y_data, evro_data, color='#3ef3d3', alpha=1, align='center')
        else:
            ax.plot(y_data, evro_data, color='#3ef3d3')
        y = [round(elem) for elem in ax.get_yticks()]
        x = [round(elem) for elem in ax.get_xticks()]
        if mytype == 'Year':
            x = [0] + [value for value in self.months.values()][::3]
        elif mytype == '5 Years':
            x = [0] + [i for i in range(2015, 2021)][::2]
        elif mytype == 'Max':
            x = [0] + [i for i in range(2015, 2021)][::2]
        ax.set_yticklabels(y, fontfamily='Roboto', fontsize=18, color='w', verticalalignment='center')
        ax.set_xticklabels(x, fontfamily='Roboto', fontsize=18, color='w', verticalalignment='top')
        self.save((310, 190))

    def change_type(self, new_type):
        self.type = new_type