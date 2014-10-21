import os
import hashlib
import requests
from bs4 import BeautifulSoup
import pandas as pd

if not os.path.exists('.cache-ec'):
    os.makedirs('.cache-ec')

ua = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36'
session = requests.Session()


def get(url):
    '''Return cached lxml tree for url'''
    url_e=url.encode('utf-8')
    path = os.path.join('.cache-ec', hashlib.md5(url_e).hexdigest() + '.html')
    if not os.path.exists(path):
        print (url)
        response = session.get(url, headers={'User-Agent': ua})
        with open(path, 'w') as fd:
            fd.write(response.text)
    return BeautifulSoup(open(path), 'html.parser')


def eci(url, code):
    soup = get(url)
    data = soup.find_all('table')[5].find_all('table')[1].find_all('table')[0]
    state = data.find('td').text[0:-14]
    result = []
    for tr in data.find_all('tr')[4:]:
        cells  = [td.text.strip() for td in tr.find_all('td')]
        cells += [state, code]
        result.append(cells)
    return result


result=[]
codes = ['S07', 'S13']
ranges = {}
ranges['S07'] = 8
ranges['S13'] = 28
for code in codes:
    url = "http://eciresults.nic.in/statewise"+code+".htm"
    result += eci(url, code)
    for const in range(1, ranges[code]+1):
        url = "http://eciresults.nic.in/statewise"+code+str(const)+".htm"
        result += eci(url, code)
result = result[:-1]

data = pd.DataFrame(result)
data.columns = ['Constituency','Constituency-code','Leading Candidate','Leading Party','Trailing Candidate','Trailing Party','Margin','Status','State','State-code']
data.to_csv('eci-2014-states-constituency-wise.csv', index=False, encoding='utf-8')
