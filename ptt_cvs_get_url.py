#載入套件
import requests
from bs4 import BeautifulSoup
import os
import re
import time
import json
from multiprocessing import Pool, Manager
from functools import partial

def make_directory(resource_path):
    if not os.path.exists(resource_path):
        os.mkdir(resource_path)

def page_max_index():
    User_Agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    headers = {'User-Agent': User_Agent}
    url = 'https://www.ptt.cc/bbs/CVS/index.html'
    res = requests.get(url=url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    index = soup.select('div[class="btn-group btn-group-paging"]')[0].select('a')[1]['href']
    max_index = int((re.findall('[0-9]+',index)[0])) + 1
    return max_index

def page_url_list(max_index):
    page_url_list = []
    for index in range(1,max_index+1):
        page_url = 'https://www.ptt.cc/bbs/CVS/index{}.html'.format(index)
        page_url_list.append(page_url)
    return page_url_list

def get_article_url(page_url,article_url_list):
    # 網址設定
    User_Agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36'
    headers = {'User-Agent': User_Agent}

    # request進每個分頁
    res = requests.get(url=page_url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')

    # get分頁裡每篇文章的網址, 放進article_url_list
    title_list = soup.select('div[class="title"]')
    for i in title_list:
        try:
            title_url = 'https://www.ptt.cc' + i.select('a')[0]['href']
            article_url_list.append(title_url)
        except:
            pass
    print(page_url)

def main():
    #變數設定
    resource_path = './PttCvs'
    file_name = 'PttCvs/Ptt_url.json'
    process_number = 12

    t1 = time.time()

    #建立資料夾
    make_directory(resource_path)
    #得到分頁max_index
    max_index = page_max_index()

    #得到每個分頁url的list
    page_uel_list = page_url_list(max_index)
    print(page_uel_list)

    #空的manager.list
    manager = Manager()
    l = manager.list()

    #n個程序進行
    p = Pool(process_number)

    #把get_article_url中 article_url_list參數固定為l
    get_article_url2 = partial(get_article_url,article_url_list=l)

    #池裡的程序開始工作
    p.map(get_article_url2,page_uel_list)
    p.close()
    p.join()

    # mqnager 物件變成 list 物件
    l = list(l)
    print('共 ', len(l),' 個文章網址')
    #寫入json
    with open(file_name, 'w', encoding='utf-8') as f:
        f.write(json.dumps(l, ensure_ascii=False))

    spend_time = time.time() - t1
    print('共花費', spend_time/60,'分鐘')

if __name__ == '__main__':
    main()