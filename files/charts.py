import matplotlib.pyplot as plt
from matplotlib import rcParams
from PIL import Image
from datetime import datetime


# Class for drawing and saving all charts
class MyChart:

    def __init__(self, table, name, directory, chart_type, company_type=''):

        self.mytable = table
        self.name = name
        self.directory = directory
        self.type = chart_type
        if company_type:
            self.company_type = company_type
        self.year_label = {1000: 'thous.',
                           100: 'hundr.'}
        self.rounder = ''
        self.months = {1: 'Jan',  2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                       7: 'Jul',  8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

    # Function for save chart
    def save(self, size, name_diagram='', income='', companies=''):
        if not companies:
            plt.savefig(self.directory + name_diagram + income + self.name, transparent=True)
            plt.close()
            self.set_size(size, name_diagram, income)
        else:
            plt.savefig(self.directory + 'all.png', transparent=True)
            plt.close()
            self.set_size(size, name_diagram, income, companies=companies)

    # Function for save chart
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

    # Function for incomes in month
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

    # Function for draw diagram (Profit / Spending)
    def draw_diagram(self):
        rcParams['font.size'] = 20.0
        rcParams['font.family'] = 'Roboto'
        rcParams['text.color'] = 'w'

        fig = plt.figure()
        ax = fig.add_subplot(111)
        d = self.mytable.get_sum("Доход")
        r = self.mytable.get_sum("Итого")

        colors = ('#ff5497', '#464c7a')
        if d - r < 0:
            values = (r, 0)
            ax.pie(values, colors=colors[::-1], wedgeprops=dict(width=0.15))
        else:
            values = (d - r, r)
            ax.pie(values, colors=colors, wedgeprops=dict(width=0.15))

        self.save((120, 120), 'diagram_')

    # Function for draw diagram costs
    def draw_costs_diagram(self):
        rcParams['font.size'] = 20.0
        rcParams['font.family'] = 'Roboto'
        rcParams['text.color'] = 'w'

        fig = plt.figure()
        ax = fig.add_subplot(111)
        cols = sorted(list(set([col.strip() for col in self.mytable.cols()])), key=lambda x: -self.mytable.get_sum(x))

        values = ([self.mytable.get_sum(col.strip()) for col in cols])
        colors = ['#ff5497', '#ffa05d', '#465bca', '#3ef3d3', '#9d3171', '#cc804a', '#3f46a3']

        ax.pie(values, colors=colors, wedgeprops=dict(width=0.16))
        self.save((150, 150), 'diagram_costs_')

        return cols, colors[:len(cols)], values

    # Function for draw diagram spending in year
    def draw_year_chart(self, save=(290, 180)):

        fig = plt.figure()
        ax = fig.add_subplot(111, facecolor='#2c396c')
        x_data = list(self.mytable.table.columns)
        try:
            x_data.remove('Итого')
            y_data = [self.mytable.table[col][0] for col in self.mytable.table.columns
                      if col not in ['Итого', 'Unnamed: 0', 'День']]
            while y_data[0] == 0 and len(y_data) > 3 and \
                    x_data[0][:3].lower() != self.months[datetime.now().month].lower():
                y_data = y_data[1:]
                x_data = x_data[1:]

            while y_data[-1] == 0 and len(y_data) > 3 and \
                    x_data[-1][:3].lower() != self.months[datetime.now().month].lower():
                y_data = y_data[:-1]
                x_data = x_data[:-1]

            if self.type == 'hiss':
                ax.bar(x_data, y_data, color='#3b6fea')
            else:
                ax.plot(x_data, y_data, color='#3b6fea')
        except ValueError:
            return
        try:
            y_min = min([item for item in ax.get_yticks() if int(item) > 0])
            index = int('1' + str(int(y_min))[1:])
            while index > 1000:
                index //= 10
            while index < 100:
                index *= 10
        except ValueError:
            index = 1

        ax.set_yticklabels([round(elem) / index for elem in ax.get_yticks()],
                           fontfamily='Roboto', fontsize=18, color='w', verticalalignment='center')
        ax.set_xticklabels([item[:3].capitalize() for item in x_data],
                           fontfamily='Roboto', fontsize=18, color='w', verticalalignment='top', rotation=315)
        self.save(save)
        try:
            self.rounder = self.year_label[index]
        except KeyError:
            self.rounder = 'None'

    # Function for resize or excision images
    def set_size(self, size, name_diagram='', income='', companies=''):
        if not companies:
            im = Image.open(self.directory + name_diagram + income + self.name + '.png')
            if not name_diagram:
                im2 = im.resize(size)
                im2.save(self.directory + name_diagram + income + self.name + '.png')
            else:
                im.crop((180, 90, 480, 395)).resize(size).save(self.directory + name_diagram + self.name + '.png')
        else:
            im = Image.open(self.directory + 'all.png')
            im2 = im.resize(size)
            im2.save(self.directory + 'all.png')

    # Function for draw one or some company
    def draw_company(self, my_type='Month', companies=''):
        fig = plt.figure()
        ax = fig.add_subplot(111)

        data = list(self.mytable.table['Цена'])
        index_last = -1
        if my_type == 'Month':
            index_first = len(data) - 31

        elif my_type == 'Year':
            index_first = len(data) - 365

        elif my_type == '5 Years':
            index_first = int(len(data) - 365 * 3.7)

        else:
            index_first = 0
        if index_last != -1:
            y_data = [i for i in range(len(data[index_first:index_last]))]
            data = data[index_first:index_last]
        else:
            y_data = [i for i in range(len(data))]

        if not companies:
            ax.plot(y_data, data, color='#3ef3d3')
            f = ''
        else:
            colors = ['#ff5497', '#ffa05d', '#465bca', '#3ef3d3']
            for i, company in enumerate(companies):
                data = list(company.mytable.table['Цена'])
                y_data = [i for i in range(len(data))]
                ax.plot(y_data, data, color=colors[i])
            f = '12'

        y = [round(elem, 3) for elem in ax.get_yticks()]
        x = [round(elem, 3) for elem in ax.get_xticks()]

        index = int('1' + ''.join(['0' for _ in str(int(min(y)))[1:]]))

        while index > 1000:
            index //= 10
        while index < 100:
            index *= 10
        if my_type == 'Year' and index_first >= 0:
            x = [0] + [value for value in self.months.values()][::3]
        elif my_type == '5 Years' and index_first >= 0:
            x = [0] + [i for i in range(2015, 2021)][::2]
        elif my_type == 'Max' and len(data) > 100:
            x = [0] + [i for i in range(2005, 2021)][::4] + [2020]
        ax.set_yticklabels([round(float(elem) / index, 2) for elem in y], fontfamily='Roboto', fontsize=18, color='w',
                           verticalalignment='center')
        ax.set_xticklabels(x, fontfamily='Roboto', fontsize=18, color='w', verticalalignment='top')
        if not f:
            self.save((360, 220), companies=f)
        else:
            self.save((330, 250), companies=f)

        self.rounder = self.year_label[index]
        return data[-1]

    # Function for draw currency chart
    def draw_exchange_rates(self, currency, my_type='Month'):
        fig = plt.figure()
        ax = fig.add_subplot(111)
        try:
            data = list(self.mytable.table[currency.strip()])
        except KeyError:
            return
        index_last = -1
        if my_type == 'Month':
            index_first = len(data) - 31

        elif my_type == 'Year':
            index_first = len(data) - 365

        elif my_type == '5 Years':
            index_first = int(len(data) - 365 * 3.7)

        else:
            index_first = 0

        if index_last != -1:
            y_data = [i for i in range(len(data[index_first:index_last]))]
            data = data[index_first:index_last]
        else:
            y_data = [i for i in range(len(data[index_first:]))]
            data = data[index_first:]

        ax.plot(y_data, data, color='#3ef3d3')

        y = [round(elem, 3) for elem in ax.get_yticks()]
        x = [round(elem, 3) for elem in ax.get_xticks()]
        if my_type == 'Year':
            x = [0] + [value for value in self.months.values()][::3]
        elif my_type == '5 Years':
            x = [0] + [i for i in range(2015, 2021)][::2]
        elif my_type == 'Max':
            x = [0] + [i for i in range(2005, 2021)][::4] + [2020]
        ax.set_yticklabels(y, fontfamily='Roboto', fontsize=18, color='w', verticalalignment='center')
        ax.set_xticklabels(x, fontfamily='Roboto', fontsize=18, color='w', verticalalignment='top')
        self.save((360, 220))
        return data[-1]

    # Function for change type chart
    def change_type(self, new_type):
        self.type = new_type
