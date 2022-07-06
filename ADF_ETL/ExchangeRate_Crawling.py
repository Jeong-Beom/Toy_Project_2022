# 사용할 패키지 경로 지정
import sys
sys.path.append('C:\\Users\\Bestc\\anaconda3\\Lib\\site-packages')

# 필요 패키지 로드
# RPA
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
# Crawling
import pandas as pd


# 크롬 개발자 버전 에러 메세지 삭제
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])

# 한국무역협회 사이트 접속
URL = "https://www.kita.net/cmmrcInfo/ehgtGnrlzInfo/rltmEhgt.do"
driver = webdriver.Chrome('C:\\Workspace\\python\\Toy_Project_2022\\MBTI\\chrome\\chromedriver.exe', options = options)
driver.get(URL)
time.sleep(15) # 로딩시간에 맞게 적정히 수정

# 통화별 환율관련 수치 가공 후 리스트로 저장
import re

data_01 = driver.find_element(By.XPATH, f'//*[@id="contents"]/div[3]/div[2]').text
data_02 = re.sub('[^0-9a-zA-Z.\n ]', '', data_01) 
data_03 = data_02.replace(',', '')
data_04 = data_03.replace(',', '')
data_05 = data_04.split("\n")[1:]

# 날짜 데이터 추출 후 리스트에 날짜 추가
date = driver.find_element(By.XPATH, f'//*[@id="contents"]/div[3]/div[1]/div[1]').text
date_01 = date.split('\n')
date_02 = date_01[0].replace('년', '-')
date_03 = date_02.replace('월', '-')
date_04 = date_03.replace('일', '')
time.sleep(5) # 로딩시간에 맞게 적정히 수정
driver.close()

# 데이터 프레임에 넣기
df_01 = pd.DataFrame({'Date' : [], 'Currency' : [], 
              'Exchange_rate' : [], 'Day_to_day' :[],
              'Rise_and_fall' : [],
              'Buy' : [], 'Sell' : [],
              'To_Transfer' : [], 'Receive' : []})
for i in range(len(data_05)):
    df_01.loc[len(df_01)] = [date_04] + data_05[i].split()

info = pd.read_csv("C:\Workspace\python\Toy_Project_2022\ADF_ETL\info\sqlinfo.txt", sep=":")

import pyodbc

server = info.loc[0][0] + '.database.windows.net' # sql 서버 이름
database = info.loc[0][3] # sql db이름
username = info.loc[0][1] # sql 서버 관리자 ID
password = info.loc[0][2] # sql 서버 관리자 PW
cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()
# Insert Dataframe into SQL Server:
for index, row in df_01.iterrows():
     cursor.execute("INSERT INTO dbo.Exchange_rate_test (Date,Currency,Exchange_rate,Day_to_day,Rise_and_fall,Buy,Sell,To_Transfer,Receive) values(?,?,?,?,?,?,?,?,?)", 
                     row.Date, row.Currency, row.Exchange_rate, row.Day_to_day, row.Rise_and_fall, row.Buy, row.Sell, row.To_Transfer, row.Receive)
cnxn.commit()
cursor.close()