import requests
from bs4 import BeautifulSoup
import pandas as pd
import sqlite3
from datetime import date, timedelta


page = requests.get("https://www.worldometers.info/coronavirus/")
soup = BeautifulSoup(page.content, 'html.parser')
rawTable = soup.find('table', id="main_table_countries_yesterday")
yesterday = date.today() - timedelta(days=1)

def tableDataText(table):
    rows = []
    trs = table.find_all('tr')
    headerRow = [td.get_text(strip=True) for td in trs[0].find_all('th')]
    if headerRow:
        rows.append(headerRow)
        trs = trs[1:]
    for tr in trs:
        rows.append([td.get_text(strip=True) for td in tr.find_all('td')])
    return rows

table = tableDataText(rawTable)
columns = ["Number", "Country_or_Other", "TotalCases", "NewCases", "TotalDeaths", "NewDeaths", "TotalRecovered", "ActiveCases",
           "Serious_or_Critical", "Tot_Cases_per_1M_pop", "Deaths_per_1M_pop", "TotalTests", "Tests_per_1M_pop",
           "Population", "Continent"]

df = pd.DataFrame(table[1:], columns=columns)
df['Date'] = yesterday
del df["Number"]
del df["Population"]

conn = sqlite3.connect('corona.db')

c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS coronadata ({})".format(', '.join(df.columns)))

for row in df.iterrows():
    sql = 'INSERT INTO coronadata ({}) VALUES ({})'.format(' ,'.join(df.columns), ','.join(['?']*len(df.columns)))
    c.execute(sql, tuple(row[1]))
conn.commit()
