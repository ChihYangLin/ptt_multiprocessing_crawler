#載入套件
import requests
import json
import os
from bs4 import BeautifulSoup
import time
t1 = time.time()
#建立PttCvs資料夾
resource_path = './PttCvs'
if not os.path.exists(resource_path):
    os.mkdir(resource_path)
#網址基本設定
User_Agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
headers = {'User-Agent':User_Agent}
url = 'https://www.ptt.cc/bbs/CVS/index.html'
count_n = 1
#設立每年的json list
json_CVS_2020 = list()
json_CVS_2019 = list()
json_CVS_2018 = list()
json_CVS_2017 = list()
json_CVS_2016 = list()
json_CVS_2015 = list()
json_CVS_2014 = list()
json_CVS_2013 = list()
json_CVS_2012 = list()
json_CVS_2011 = list()
json_CVS_2010 = list()
json_CVS_list  = [json_CVS_2020,json_CVS_2019,json_CVS_2018,json_CVS_2017,json_CVS_2016,json_CVS_2015,json_CVS_2014,json_CVS_2013,json_CVS_2012,json_CVS_2011,json_CVS_2010]
yesr_list = ['2020','2019','2018','2017','2016','2015','2014','2013','2012','2011','2010']

while True:
    # get每篇文章的網址list
    res = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    title_list = soup.select('div[class="title"]')
    # request進去每篇文章
    for n in title_list:
        article_dict = dict()
        title = n.text
        try :
            title_url = 'https://www.ptt.cc' + n.select('a')[0]['href']
            title_res = requests.get(url=title_url, headers=headers)
            title_soup = BeautifulSoup(title_res.text, 'html.parser')
        except:
            title_url = ''  # 若文章被刪除，網址捕空字串
            print('='*50,'沒網址','='*50)
        #抓取文章資訊
        try:
            author = title_soup.select('div[id="main-content"]')[0].select('span[class="article-meta-value"]')[0].text
            date_and_time = title_soup.select('div[id="main-content"]')[0].select('span[class="article-meta-value"]')[3].text
        except:
            author = '' #若沒作者，補上空字串
            date_and_time = ''#若沒日期時間，補上空字串
        try:
            content = title_soup.select('div[id="main-content"]')[0].text.split('※ 發信站: 批踢踢實業坊(ptt.cc)')[0]
            comment = '\n'.join(title_soup.select('div[id="main-content"]')[0].text.split('※ 發信站: 批踢踢實業坊(ptt.cc)')[1:])
        except:
            content = ''#若沒文章補上空字串
            comment = ''
        pushdown = 0
        pushup = len(title_soup.select('span[class="hl push-tag"]'))
        for i in title_soup.select('span[class="f1 hl push-tag"]'):
            if '噓' in i.text.split():
                pushdown += 1
        pushscore = pushup - pushdown
        #把值放入字典
        article_dict['title'] = title
        article_dict['author'] = author
        article_dict['date_and_time'] = date_and_time
        article_dict['pushup'] = pushup
        article_dict['pushdown'] = pushdown
        article_dict['pushscore'] = pushscore
        article_dict['content'] = content
        article_dict['comment'] = comment
        #將字典依照年份放入對應的json list
        for y, l in zip(yesr_list,json_CVS_list) :
            if date_and_time.split(' ')[-1] == y and title_url != '':
                l.append(article_dict)
                print(title_url,' ',count_n)
                count_n += 1
        # 2009以前的資料不抓
        if date_and_time.split(' ')[-1] == '2009':
            break
    # 2009以前的資料不抓
    if date_and_time.split(' ')[-1] == '2009':
        break
    url = 'https://www.ptt.cc' + soup.select('div[class="btn-group btn-group-paging"]')[0].select('a')[1]['href']
    # print('睡3秒')
    # time.sleep(3)

#寫入json
for y, l in zip(yesr_list, json_CVS_list):
    with open('%s/PttCvs_%s.json'%(resource_path,y), 'w', encoding='utf-8') as f:
        f.write(json.dumps(l, ensure_ascii=False))
t2 = time.time()
print('此程式執行了%d小時%d分鐘%d秒'%((t2-t1)/3600,(t2-t1)%3600,(t2-t1)%60))