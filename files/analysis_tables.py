from pandas import read_excel, DataFrame
import requests  # Модуль для обработки URL
from bs4 import BeautifulSoup  # Модуль для работы с HTML
from datetime import datetime


# Base table for drawing charts
class MyTable:

    def __init__(self, file_name):
        self.file_name = file_name
        self.list_of_none_col = ['Итого', 'Unnamed: 0', 'День', 'Доход']
        try:
            self.table = read_excel(self.file_name)
        except FileNotFoundError:
            if '2020' not in self.file_name:
                self.table = DataFrame({'День': [i for i in range(1, 32)],
                                        'Доход': [0 for _ in range(31)]})
            else:
                self.table = DataFrame({'January': [0],
                                        'February': [0],
                                        'March': [0],
                                        'April': [0],
                                        'May': [0],
                                        'June': [0],
                                        'July': [0],
                                        'September': [0],
                                        'October': [0],
                                        'November': [0],
                                        'December': [0]
                                        })
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

    # Function for set directory table
    def set_table_name(self, new_name):
        try:
            self.file_name = new_name
            self.table = read_excel(self.file_name)
            return True
        except FileNotFoundError:
            return 'файл не найден'

    # Function creating year table
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

    # Function updating year table
    def update_year_table(self, months):  # how create_year_table(), but it change, create_year_table() - create
        year_table = DataFrame({0: [0]})
        for i, file_name in enumerate(months):
            month = file_name.split('/')[-1].split('.')[0].split('_')[0]
            table = read_excel(file_name)
            year_table[month] = sum(list(table['Итого'][:30]))
        del year_table[0]
        self.table = year_table
        if type(self) is not CurrencyTable:
            self.table['Итого'] = sum([self.table[col] for col in self.table.columns
                                       if col not in self.list_of_none_col])
        self.save_table()

    def __str__(self):
        return str(self.table)

    # Function add column
    def add_column(self, column_name, values):
        self.table[column_name] = values

    # Function saving table
    def save_table(self):
        if type(self) == MyTable:
            self.table['Итого'] = sum([self.table[col] for col in self.table.columns
                                       if col not in self.list_of_none_col])
        self.table.to_excel(self.file_name,  columns=[col for col in self.table.columns])

    # Function sorting table by titles
    def sort(self):
        total = self.table['Итого']
        new_table = DataFrame(self.table['День'])
        for key in sorted(self.table.columns):
            if key not in ['Итого', 'День']:
                new_table[key] = self.table[key]
        self.table = new_table
        self.table['Итого'] = total
        self.save_table()

    # Function return sum all items col
    def get_sum(self, col):
        try:
            return sum(list(self.table[col]))
        except KeyError:
            return 0

    # insert payment in table
    def add_payment(self, title, prise, day):
        title = title.strip()
        try:
            self.table[title] = [int(item) + int(prise) if i + 1 == day else item for i, item in
                                 enumerate(self.table[title])]
        except KeyError:
            self.table[title] = [0 for _ in range(len(self.table['День']))]
            self.table[title] = [int(item) + int(prise) if i + 1 == day else item for i, item in
                                 enumerate(self.table[title])]
        self.sort()
        self.save_table()

    def update_table(self):
        self.table = read_excel(self.file_name)
        try:
            del self.table['Unnamed: 0']
        except KeyError:
            pass

    # Function return cols table
    def cols(self):
        return [col for col in list(self.table.columns) if col not in self.list_of_none_col]


# Table for drawing currency charts
class CurrencyTable(MyTable):

    def __init__(self, user_name):

        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3)' +
                                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}

        self.file_name = 'sources/currency.xlsx'
        self.table = read_excel(self.file_name)
        self.user_name = user_name
        try:
            del self.table['Unnamed: 0']
        except KeyError:
            pass
        self.cols = self.table.columns
        self.check_currency()

    def save_table(self):
        self.table.to_excel(self.file_name,  columns=[col for col in self.cols])

    # Function for parsing currencies in table
    def check_currency(self):
        try:
            date = open('sources/last_day_currency.txt').read().split('\n')[0]
            if date != str(datetime.now()).split()[0]:
                currency_names = [col for col in self.cols if col not in ['Unnamed: 0']]
                currency_values = {col: list(self.table[col]) for col in currency_names}
                currency_values['Дата'] += ['-'.join(str(datetime.now()).split()[0].split('-')[::-1])]
                for name in currency_names[1:]:
                    name_url = f'https://www.google.com/search?q=Курс+{"+".join(name.split())}&oq=курс+' \
                               f'{"+".join(name.split())}&aqs=chrome.0.69i59j0i10l7.2527j1j7&sourceid=chrome&ie=UTF-8'
                    full_page = requests.get(name_url, headers=self.headers)
                    soup = BeautifulSoup(full_page.content, 'html.parser')
                    convert = soup.findAll("span", class_="DFlfde SwHCTb")
                    try:
                        currency_values[name].append('.'.join(convert[0].text.split(',')))
                    except IndexError:
                        continue
                min_len = len(min(list(currency_values.values()), key=lambda x: len(x)))
                currency_values = {key: value[:min_len] for key, value in currency_values.items()}
                columns = DataFrame(currency_values)
                self.table = columns
                self.save_table()
                date = open('sources/last_day_currency.txt', 'w')
                date.write(str(datetime.now()).split()[0])
                date.close()
        except requests.exceptions.ConnectionError as exception:
            return exception


# Table for drawing companies charts
class CompanyTable(MyTable):

    def __init__(self, file_name, company, user_name):

        self.file_name = file_name
        self.table = read_excel(file_name)
        self.company = company
        self.cols = self.table.columns
        self.user_name = user_name

        self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3)' +
                                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/'
                                  'webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
                        }

    # Function for parsing companies in table
    def check_company(self, dollar):
        try:
            date = open('sources/' + self.user_name + '/DataBases/txtFiles/last_day_company.txt').read().split('\n')[0]
            if date != str(datetime.now()).split()[0]:
                s = requests.Session()

                url = f'https://www.google.com/search?q=исторические+цены+на+акции+компании+' \
                      f'{"+".join(self.company.split())}&oq=курс+{"+".join(self.company.split())}' \
                      f'&aqs=chrome.0.69i59j0i10l7.2527j1j7&sourceid=chrome&ie=UTF-8'

                answer = s.get(url, headers=self.headers)
                hrefs = BeautifulSoup(answer.content, 'html.parser').findAll('div', class_='yuRUbf')

                href = hrefs[0].find('a')['href']
                answer = s.get(href, headers=self.headers)
                span = BeautifulSoup(answer.content, 'html.parser').find('span', id='last_last').text
                span = float('.'.join(''.join(span.split('.')).split(',')))
                curr = BeautifulSoup(answer.content, 'html.parser').find('div',
                                                                         class_='bottom lighterGrayFont arial_11')
                curr = curr.findAll('span', class_='bold')[-1].text
                if curr != 'USD':
                    span = round(span / dollar, 2)

                company_names = [col for col in self.cols if col not in ['Unnamed: 0']]
                company_values = {col: list(self.table[col]) for col in company_names}
                company_values['Дата'] += ['-'.join(str(datetime.now()).split()[0].split('-')[::-1])]
                company_values['Цена'] += [span]

                tb = DataFrame(company_values)
                tb.to_excel(f'sources/' + self.user_name + f'/DataBases/companies/{self.company}.xlsx')
                self.update_table()

        except requests.exceptions.ConnectionError as exception:
            return exception
