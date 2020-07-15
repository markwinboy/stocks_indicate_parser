import requests
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd

#Константы
lst_name_stocks = []
dic = {}
# name = "MAIL"
main_lst = []
lst_index = ["net_assets","assets","revenue","net_income","p_e","p_bv","p_s","roe","roa","ev_ebitda","debt_ebitda"]
lst_name_index = ["Капитал","Активы","Выручка","Чистая прибыль","P/E(Price/Earnings)","P/B(Price/Book value)",
                  "P/S(Price/Sales)","ROE(Reurn on Equal),%","ROA(Return on Assets),%","EV/EBITDA","NetDebt/EBITDA"]

# Функция перебора строчек со значениями lst_index
def parse_table(name,table):
  global main_lst
  index = table.find('tr', {'field': name})
  if index != None:
    value_index = index.find_all('td')
    try:
      value_index.remove(index.find("td", {'class': "ltm_spc"}))
    except ValueError:
      print("Отсутствует пустой столбец")
    value_index = [i.text.strip().replace("%","") for i in value_index[1:]]
  else:
    value_index = ["" for i in range(len(year))]
  main_lst.append(value_index)

def request_smartlab(url):
  # url = 'https://smart-lab.ru/q/%s/f/y/' % (name)# url страницы
  headers = {'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"}
  r = requests.get(url, headers = headers)
  r.encoding = 'utf8'
  return r

def main_page(r):
  global dic
  soup = BeautifulSoup(r.text,"html.parser")
  tables = soup.find_all('table', {'class': 'simple-little-table little trades-table'})
  # print(tables[0].find_all('a'))
  for i in tables[0].find_all('a'):
    # print(i.text)
    if "forum" in i.get("href"):
      # print(i.get("href").split("/")[-1]
      dic[i.text] = i.get("href").split("/")[-1]


def parse_stocks(r):
  global year
  soup = BeautifulSoup(r.text,"html.parser") #Отправляем полученную страницу в библиотеку для парсинга
  tables=soup.find_all('table', {'class': 'simple-little-table financials'})
  header = tables[0].find('tr', {'class': 'header_row'})
  year = header.find_all('strong')
  year = [i.text for i in year]
  for item in lst_index:
    # print(item)
    parse_table(item,tables[0])


def create_tables_indicators():
  global main_lst
  df = pd.DataFrame(main_lst,columns=year,index=lst_name_index)
  main_lst = []
  df = df.astype(object).replace({'': np.nan, '-': np.nan})
  df.apply(pd.to_numeric, errors='ignore')
  df=df.T.copy()
  df["Обязательства"] = df["Активы"].astype('float64')-df["Капитал"].astype('float64')
  print(df.T)

def write_excel(df,name):
  writer = pd.ExcelWriter("stocks/"+name+ ".xlsx", engine='xlsxwriter')
  df.to_excel(writer,"Индексы")
  writer.save()

def main():
  url = "https://smart-lab.ru/q/shares_fundamental/"
  request = request_smartlab(url)
  main_page(request)
  url = 'https://smart-lab.ru/q/%s/f/y/' % ("ALRS")
  request = request_smartlab(url)
  parse_stocks(request)
  create_tables_indicators()
  # for i in dic:
  #   url = 'https://smart-lab.ru/q/%s/f/y/' % (dic.get(i))
  #   request = request_smartlab(url)
  #   parse_stocks(request)
  #   create_tables_indicators(i)



if __name__ == '__main__':
  main()