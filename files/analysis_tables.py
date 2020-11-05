from pandas import read_excel, DataFrame
import requests  # Модуль для обработки URL
from bs4 import BeautifulSoup  # Модуль для работы с HTML
from datetime import datetime


class MyTable:
    def __init__(self, file_name):
        self.file_name = file_name
        self.list_of_none_col = ['Итого', 'Unnamed: 0', 'День', 'Доход']
        try:
            self.table = read_excel(self.file_name)
        except FileNotFoundError:
            self.table = DataFrame({'День': [i for i in range(1, 32)],
                                    'Еда': [0 for _ in range(31)],
                                    'Одежда': [0 for _ in range(31)],
                                    'Путешествия': [0 for _ in range(31)],
                                    'Развлечения': [0 for _ in range(31)],
                                    'Транспорт': [0 for _ in range(31)]})
            self.table['Итого'] = sum([self.table[col] for col in self.table.columns
                                       if col not in self.list_of_none_col])
        self.table['Итого'] = sum([self.table[col] for col in self.table.columns
                                   if col not in self.list_of_none_col])
        try:
            del self.table['Unnamed: 0']
        except KeyError:
            pass
        self.save_table()

    def get_table(self):
        return self.table

    def set_table_name(self, newname):
        try:
            self.file_name = newname
            self.table = read_excel(self.file_name)
            return True
        except FileNotFoundError:
            return 'файл не найден'

    def create_year_table(self, months):
        if len(self.table) == 0:  # checking table is empty
            year_table = DataFrame({0: [0]})
            for i, file_name in enumerate(months):
                month = file_name.split('/')[-1].split('.')[0].split('_')[0]
                table = read_excel(file_name)
                year_table[month] = sum(list(table['Итого'][:30]))
            del year_table[0]
            self.table = year_table
            self.table['Итого'] = sum([self.table[col] for col in self.table.columns
                                       if col not in self.list_of_none_col])
            self.save_table()

    def update_year_table(self, months):  # how create_year_table(), but it change, create_year_table() - create
        year_table = DataFrame({0: [0]})
        for i, file_name in enumerate(months):
            month = file_name.split('/')[-1].split('.')[0].split('_')[0]
            table = read_excel(file_name)
            year_table[month] = sum(list(table['Итого'][:30]))
        del year_table[0]
        self.table = year_table
        self.table['Итого'] = sum([self.table[col] for col in self.table.columns
                                   if col not in self.list_of_none_col])
        self.save_table()

    def __str__(self):
        return str(self.table)

    def add_column(self, column_name, values):
        self.table[column_name] = values

    def save_table(self):
        self.table.to_excel(self.file_name,  columns=[col for col in self.table.columns])

    def sort(self):
        total = self.table['Итого']
        new_table = DataFrame(self.table['День'])
        for key in sorted(self.table.columns):
            if key not in ['Итого', 'День']:
                new_table[key] = self.table[key]
        self.table = new_table
        self.table['Итого'] = total
        self.save_table()

    def get_sum(self, col):
        try:
            return sum(list(self.table[col]))
        except KeyError:
            return -1

    def add_payment(self, title, prise, day):
        try:
            self.table[title] = [int(item) + int(prise) if i + 1 == day else item for i, item in
                                 enumerate(self.table[title])]
        except KeyError:
            self.table[title] = [0 for _ in range(len(self.table['День']))]
            self.table[title] = [int(item) + int(prise) if i + 1 == day else item for i, item in
                                 enumerate(self.table[title])]
        self.save_table()

    def cols(self):
        return [col for col in list(self.table.columns) if col not in self.list_of_none_col]


class CurrencyTable:
    def __init__(self):
        self.dollar_url = 'https://www.google.com/search?sxsrf=ALeKk01NWm6viYijAo3HXYOEQU' \
                          'yDEDtFEw%3A1584716087546&source=hp&ei=N9l0XtDXHs716QTcuaXoAg&q' \
                          '=%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1%80+%D0%BA+%D1%80%D1%83%D0%B' \
                          '1%D0%BB%D1%8E&oq=%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1%80+&gs_l=ps' \
                          'y-ab.3.0.35i39i70i258j0i131l4j0j0i131l4.3044.4178..5294...1.0.' \
                          '.0.83.544.7......0....1..gws-wiz.......35i39.5QL6Ev1Kfk4'

        self.evro_url = 'https://www.google.com/search?sxsrf=ALeKk01rKIvG3Ol0GFL7DqYLOlkw' \
                        'Q0zOFw%3A1602753572184&ei=JBSIX9TrCqznrgTAspi4BQ&q=%D0%B5%D0%B2%' \
                        'D1%80%D0%BE+%D0%BA+%D1%80%D1%83%D0%B1%D0%BB%D1%8E&oq=tdhj+%D0%BA' \
                        '+%D1%80%D1%83%D0%B1%D0%BB%D1%8E&gs_lcp=CgZwc3ktYWIQARgAMgQIABBDM' \
                        'gQIABAKMgQIABAKMgQIABAKMgQIABAKMgQIABAKMgQIABAKMgQIABAKMgQIABAKM' \
                        'gQIABAKOgQIABBHOgYIABAHEB46CAgAEAcQChAeOgoIABAHEAoQHhAqOgQIABANU' \
                        'PClH1jQrB9gjL4faABwA3gAgAGVAYgB_AOSAQM0LjGYAQCgAQGqAQdnd3Mtd2l6y' \
                        'AEIwAEB&sclient=psy-ab'

        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}
        self.table = read_excel('sources/DataBases/DollarEuro/table.xlsx')
        self.file_name = 'sources/DataBases/DollarEuro/table.xlsx'

        self.url_google = 'https://ru.investing.com/equities/google-inc-historical-data'

        try:
            del self.table['Unnamed: 0']
        except KeyError:
            pass

    def get_dollar_currency_price(self):
        full_page = requests.get(self.dollar_url, headers=self.headers)
        soup = BeautifulSoup(full_page.content, 'html.parser')
        convert = soup.findAll("span", {"class": "DFlfde", "class": "SwHCTb", "data-precision": 2})
        return convert[0].text

    def get_euro_currency_price(self):
        full_page = requests.get(self.evro_url, headers=self.headers)
        soup = BeautifulSoup(full_page.content, 'html.parser')
        convert = soup.findAll("span", {"class": "DFlfde", "class": "SwHCTb", "data-precision": 2})
        return convert[0].text

    def get_google_table(self):
        text = ''
        return text

    def check_currency(self):
        date = open('sources/DataBases/txtFiles/last_day.txt').read().split('\n')[0]
        if date != str(datetime.now()).split()[0]:
            new_table = DataFrame({'data': [0 for _ in range(len(list(self.table['euro'])) + 1)],
                                   'dollar': [0 for _ in range(len(list(self.table['euro'])) + 1)],
                                   'euro': [0 for _ in range(len(list(self.table['euro'])) + 1)]})
            some_list = list(self.table['data'])
            some_list.append(datetime.now())
            new_table['data'] = some_list
            currency = float(self.get_dollar_currency_price().replace(",", "."))
            some_list = list(self.table['dollar'])
            some_list.append(currency)
            new_table['dollar'] = some_list
            currency = float(self.get_euro_currency_price().replace(",", "."))
            some_list = list(self.table['euro'])
            some_list.append(currency)
            new_table['euro'] = some_list
            self.table = new_table
            self.save_table()
            date = open('sources/DataBases/txtFiles/last_day.txt', 'w')
            date.write(str(datetime.now()).split()[0])
            date.close()

    def get_table(self):
        return self.table

    def __str__(self):
        return str(self.table)

    def add_column(self, column_name, values):
        self.table[column_name] = values

    def save_table(self):
        self.table.to_excel(self.file_name,  columns=[col for col in self.table.columns])

    def get_sum(self, col):
        try:
            return sum(self.table[col])
        except KeyError:
            return -1

