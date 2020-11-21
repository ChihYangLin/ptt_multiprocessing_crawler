# 載入套件
import os
import requests
from bs4 import BeautifulSoup
import time
import json
from multiprocessing import Pool, Manager
from functools import partial


# 讀json檔案into list
def read_file_into_list(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        json_load_list = json.load(file)
    return json_load_list

def make_directory(resource_path):
    if not os.path.exists(resource_path):
        os.mkdir(resource_path)

def scrape_data_into_dict(html):
    article_dict = dict()
    # 刮取資料
    try:
        title = html.select('div[class="article-metaline"]')[1].select('span[class="article-meta-value"]')[0].text
    except:
        title = ''
        print('沒有標題')
    try:
        author = html.select('div[id="main-content"]')[0].select('span[class="article-meta-value"]')[0].text
        date_and_time = html.select('div[id="main-content"]')[0].select('span[class="article-meta-value"]')[3].text
    except:
        author = ''  # 若沒作者，補上空字串
        date_and_time = ''  # 若沒日期時間，補上空字串

    # 2009以前的資料不抓
    if date_and_time.split(' ')[-1] == '2009' or date_and_time.split(' ')[-1] == '2008' or date_and_time.split(' ')[
        -1] == '2007' or date_and_time.split(' ')[-1] == '2006' or date_and_time.split(' ')[-1] == '2005' or \
            date_and_time.split(' ')[-1] == '2004':
        pass
    try:
        content = html.select('div[id="main-content"]')[0].text.split('※ 發信站: 批踢踢實業坊(ptt.cc)')[0]
        comment = '\n'.join(html.select('div[id="main-content"]')[0].text.split('※ 發信站: 批踢踢實業坊(ptt.cc)')[1:])
    except:
        content = ''  # 若沒文章補上空字串
        comment = ''
    pushdown = 0
    pushup = len(html.select('span[class="hl push-tag"]'))
    for i in html.select('span[class="f1 hl push-tag"]'):
        if '噓' in i.text.split():
            pushdown += 1
    pushscore = pushup - pushdown

    # 把值放入字典
    article_dict['title'] = title
    article_dict['author'] = author
    article_dict['date_and_time'] = date_and_time
    article_dict['pushup'] = pushup
    article_dict['pushdown'] = pushdown
    article_dict['pushscore'] = pushscore
    article_dict['content'] = content
    article_dict['comment'] = comment
    return article_dict

def get_article_context(url, article_list):
    # 獲取html
    User_Agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    headers = {'User-Agent': User_Agent}
    res = requests.get(url=url, headers=headers)
    html = BeautifulSoup(res.text, 'html.parser')

    # 刮取資料進dict
    article_dict = scrape_data_into_dict(html)
    print(article_dict['title'])

    #文章字典新增進list
    article_list.append(article_dict)

def main():
    t_start = time.time()
    # 變數設定
    resource_path = './PttCvs'
    article_url_file = 'PttCvs/Ptt_url.json'
    process_number = 12
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
    json_CVS_list = [json_CVS_2020, json_CVS_2019, json_CVS_2018, json_CVS_2017, json_CVS_2016, json_CVS_2015,
                     json_CVS_2014, json_CVS_2013, json_CVS_2012, json_CVS_2011, json_CVS_2010]
    year_list = ['2020', '2019', '2018', '2017', '2016', '2015', '2014', '2013', '2012', '2011', '2010']

    # 建立PttCvs資料夾
    make_directory(resource_path)

    # 讀取文章URL
    article_url_list = read_file_into_list(article_url_file)

    # 設定manager list物件
    manager = Manager()
    l = manager.list()

    # 設定n個程序池化進行
    p = Pool(process_number)

    # 把get_article_context中 article_list參數固定為l
    get_article_context2 = partial(get_article_context, article_list=l)

    # 池裡的程序開始工作
    p.map(get_article_context2, article_url_list)
    p.close()
    p.join()

    # 變成list物件
    l = list(l)

    # 按年分放進list
    for i in l:
        if i['date_and_time'].split(' ')[-1] == '2020':
            json_CVS_2020.append(i)
        if i['date_and_time'].split(' ')[-1] == '2019':
            json_CVS_2019.append(i)
        if i['date_and_time'].split(' ')[-1] == '2018':
            json_CVS_2018.append(i)
        if i['date_and_time'].split(' ')[-1] == '2017':
            json_CVS_2017.append(i)
        if i['date_and_time'].split(' ')[-1] == '2016':
            json_CVS_2016.append(i)
        if i['date_and_time'].split(' ')[-1] == '2015':
            json_CVS_2015.append(i)
        if i['date_and_time'].split(' ')[-1] == '2014':
            json_CVS_2014.append(i)
        if i['date_and_time'].split(' ')[-1] == '2013':
            json_CVS_2013.append(i)
        if i['date_and_time'].split(' ')[-1] == '2012':
            json_CVS_2012.append(i)
        if i['date_and_time'].split(' ')[-1] == '2011':
            json_CVS_2011.append(i)
        if i['date_and_time'].split(' ')[-1] == '2010':
            json_CVS_2010.append(i)

    # 按年份寫入json
    for y, l in zip(year_list, json_CVS_list):
        with open('%s/PttCvs_%s.json' % (resource_path, y), 'w', encoding='utf-8') as f:
            f.write(json.dumps(l, ensure_ascii=False))
    print('花費', (time.time() - t_start) / 60, '分鐘')


if __name__ == '__main__':
    main()