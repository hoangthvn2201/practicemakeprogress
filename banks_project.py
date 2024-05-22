url = 'https://web.archive.org/web/20230908091635/https://en.wikipedia.org/wiki/List_of_largest_banks'
table_attrs = ['Name', 'MC_USD_Billion']
table_attrs_final = ['Name','MC_USD_Billion','MC_GBP_Billion','MC_EUR_Billion','MC_INR_Billion']
csv_path = './Largest_banks_data.csv'
db_name = 'Banks.db'
table_name = 'Largest_banks'
log_file = 'code_log.txt'

import pandas as pd  
import numpy as np 
import requests 
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime


def log_progress(message):
    timestamp_format = '%Y-%h-%d-%H-%M-%S'
    now = datetime.now()
    timestamp = now.strftime(timestamp_format)
    with open('code_log.txt','a') as f:
        f.write(timestamp+': '+message+'\n')
def extract(url, table_attrs):
    response = requests.get(url).text
    page = BeautifulSoup(response,'html.parser')
    table = page.find_all('tbody')
    rows = table[0].find_all('tr')
    df = pd.DataFrame(columns = table_attrs)
    for row in rows:
        col = row.find_all('td')
        if len(col) != 0:
            col_dict = {'Name': col[1].contents[2].text,
                        'MC_USD_Billion': float(col[2].text[0:-1])}
            df1 = pd.DataFrame(col_dict,index=[0])
            df = pd.concat([df,df1], ignore_index = True)
    return df 

def transform(df,csv_path):
    df_rate = pd.read_csv(csv_path)
    exchange_rate = df_rate.set_index('Currency').to_dict()['Rate']
    df['MC_EUR_Billion'] = [np.round(x*exchange_rate['EUR'],2) for x in df['MC_USD_Billion']]
    df['MC_GBP_Billion'] = [np.round(x*exchange_rate['GBP'],2) for x in df['MC_USD_Billion']]
    df['MC_INR_Billion'] = [np.round(x*exchange_rate['INR'],2) for x in df['MC_USD_Billion']]

    return df

def load_to_csv(df, csv_path):
    df.to_csv(csv_path)

def load_to_db(df, sql_connection, table_name):
    df.to_sql(table_name, sql_connection, if_exists='replace',index = False)

def run_queries(query_statement, sql_connection):
    print(query_statement)
    query = pd.read_sql(query_statement, sql_connection)
    print(query)

url = 'https://web.archive.org/web/20230908091635/https://en.wikipedia.org/wiki/List_of_largest_banks'
table_attrs = ['Name', 'MC_USD_Billion']
table_attrs_final = ['Name','MC_USD_Billion','MC_GBP_Billion','MC_EUR_Billion','MC_INR_Billion']
csv_path = './Largest_banks_data.csv'
db_name = 'Banks.db'
table_name = 'Largest_banks'
log_file = 'code_log.txt'

log_progress('Preliminaries complete. Initiating ETL process')

df = extract(url, table_attrs)

log_progress('Data extraction complete. Initiating Transformation process')

df = transform(df,'./exchange_rate.csv')

log_progress('Data transformation complete. Initiating Loading process')

load_to_csv(df,csv_path = './Largest_banks_data.csv')

log_progress('Data saved to CSV file')

conn = sqlite3.connect(db_name)

log_progress('SQL Connection initiated')

load_to_db(df, conn, table_name)

log_progress('Data loaded to Database as a table, Executing queries')




