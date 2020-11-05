from datetime import datetime

# import classes from my files
from files import analysis_tables
from files import charts

MyTable, CurrencyTable = analysis_tables.MyTable, analysis_tables.CurrencyTable
MyChart = charts.MyChart

DATABASE = {}

MONTHS = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
          7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
DATE = datetime


def get_default_date_base():
    year_file_name = 'sources/DataBases/Tables/years/2020.xlsx'

    for key, value in MONTHS.items():
        month_file_name = 'sources/DataBases/Tables/months/' + \
                          MONTHS[key].lower() + '_costs.xlsx'
        DATABASE[value] = MyChart(MyTable(month_file_name),
                                  value,
                                  'sources/images/', 'hiss')
    DATABASE['currency'] = MyChart(CurrencyTable(), 'exchange_rates_month',
                                   'sources/images/', 'chart')

    DATABASE[DATE.year] = MyChart(MyTable(year_file_name),
                                  str(DATE.year),
                                  'sources/images/', 'chart')

    update_tables()
    save_constants()
    return DATABASE


def update_tables():
    list_months = ['sources/DataBases/Tables/months/' + value.lower() + '_costs.xlsx'
                   for key, value in MONTHS.items()]
    for file_directory in list_months:
        t = MyTable(file_directory)
        t.save_table()
        del t

    DATABASE[DATE.year].mytable.update_year_table(list_months)


def save_constants(db=DATABASE):
    file = open('sources/DataBases/txtFiles/database.txt', 'w', encoding='utf8')
    for key, value in db.items():
        if key != 2020:
            file.write(str(key) + ' ' + value.mytable.file_name + ' ' +
                       value.name + ' ' + value.directory + ' ' + value.type)
            file.write('\n')
        else:
            file.write(str(key) + ' ' + value.mytable.file_name + ' ' +
                       value.name + ' ' + value.directory + ' ' + value.type)


def get_date_base():
    file = open('sources/DataBases/txtFiles/database.txt', 'r', encoding='utf8').readlines()
    for line in file:
        line = line.split()
        key = line[0]
        table_directory = line[1]
        name = line[2]
        directory = line[3]
        my_type = line[4]
        if key in MONTHS.values() or key == '2020':
            DATABASE[key] = MyChart(MyTable(table_directory),
                                            name,
                                            directory,
                                            my_type)
        else:
            DATABASE[key] = MyChart(CurrencyTable(),
                                    name,
                                    directory,
                                    my_type)
    return DATABASE

