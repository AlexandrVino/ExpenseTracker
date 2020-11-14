from datetime import datetime
import sqlite3

# import classes from my files
from files import analysis_tables
from files import charts

MyTable, CurrencyTable, CompanyTable = analysis_tables.MyTable, \
                                       analysis_tables.CurrencyTable, \
                                       analysis_tables.CompanyTable
MyChart = charts.MyChart

DATABASE = {}

MONTHS = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
          7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
DATE = datetime


def get_default_date_base(username):
    year_file_name = 'sources/' + username + '/DataBases/Tables/years/2020.xlsx'

    for key, value in MONTHS.items():
        month_file_name = 'sources/DataBases/Tables/months/' + \
                          MONTHS[key].lower() + '_costs.xlsx'
        DATABASE[value] = MyChart(MyTable(month_file_name),
                                  value,
                                  'sources/images/', 'hiss')
    DATABASE['currency'] = MyChart(CurrencyTable(username), 'exchange_rates_month',
                                   'sources/images/', 'chart')

    DATABASE[DATE.year] = MyChart(MyTable(year_file_name),
                                  str(DATE.year),
                                  'sources/images/', 'chart')

    update_tables(username)
    save_constants()
    return DATABASE


def update_tables(username):
    list_months = ['sources/' + username + '/DataBases/Tables/months/' + value.lower() + '_costs.xlsx'
                   for key, value in MONTHS.items()]
    for file_directory in list_months:
        t = MyTable(file_directory)
        t.save_table()
        del t

    DATABASE[DATE.year].mytable.update_year_table(list_months)


# Function parse strings to my classes
def get_date_base(username):

    con = sqlite3.connect('sources/' + username + '/DataBases/dbFiles/database.db')
    cur = con.cursor()

    text = [list(item) for item in cur.execute("""SELECT * FROM database_table""")]

    for line in text:
        key = line[0]
        table_directory = line[1]
        name = line[2]
        directory = line[3]
        my_type = line[4]
        if key in MONTHS.values() or key == '2020':
            DATABASE[key] = MyChart(MyTable(table_directory),
                                    name, directory, my_type)

        else:
            DATABASE[key] = MyChart(CurrencyTable(username), name, directory, my_type)

    text = [list(item) for item in cur.execute("""SELECT * FROM companies""")]
    for line in text:
        name = line[1]
        table_directory = line[2]
        directory_img = line[3]
        type_chart = line[4]
        type_company = line[5]
        DATABASE[name] = MyChart(CompanyTable(table_directory, name, username),
                                 name, directory_img, type_chart, type_company)
    return DATABASE
