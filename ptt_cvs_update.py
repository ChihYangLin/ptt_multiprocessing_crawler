#載入套件
import requests
from bs4 import BeautifulSoup
import re
import time
import json
from multiprocessing import Pool, Manager
from functools import partial

def read_file_into_list(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        json_load_list = json.load(file)
    return json_load_list

def l1_union_l2(l1,l2):
    l = list(set(l1).union(set(l2)))
    return l

def l2_minus_l1(l1,l2):
    l = list(set(l2)-set(l1))
    return l

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
    #只抓最新六頁
    for index in range(max_index-6,max_index+1):
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
    orginal_url_file = 'PttCvs/Ptt_url.json'
    process_number = 12
    t1 = time.time()

    #得到分頁max_index
    max_index = page_max_index()

    #得到每個分頁url的list
    page_uel_list = page_url_list(max_index)
    print('page_url_list : ',page_uel_list)

    #多程序工作
    manager = Manager()
    l_url = manager.list()
    p = Pool(process_number)
    get_article_url2 = partial(get_article_url,article_url_list=l_url)
    p.map(get_article_url2,page_uel_list)
    p.close()
    p.join()
    l_url = list(l_url)

    #載入原有檔案
    ptt_url_list = read_file_into_list(orginal_url_file)
    print('original_list 共:',len(ptt_url_list),'個網址')
    #更新list,做聯集
    updated_list = l1_union_l2(ptt_url_list, l_url)
    print('updated_list : 共',len(updated_list),'個網址')
    #更新的 list 寫回 json
    with open(orginal_url_file, 'w', encoding='utf-8') as f:
        f.write(json.dumps(updated_list, ensure_ascii=False))

    # 讀取2020文章json檔
    json_CVS_2020_list = read_file_into_list('PttCvs/PttCvs_2020.json')
    # 與原list做差集
    new_url_list = l2_minus_l1(ptt_url_list, l_url)
    print('numbers of new url :', len(new_url_list), '個新網址')
    print(new_url_list)
    #若差集不等於0, 則新增文章字典進去2020 list
    if len(new_url_list) > 0:
        l_article = manager.list()
        p2 = Pool(process_number)
        get_article_context2 = partial(get_article_context, article_list=l_article)
        p2.map(get_article_context2, new_url_list)
        p2.close()
        p2.join()
        l_article = list(l_article)
        for i in l_article:
            json_CVS_2020_list.append(i)

    #寫回ptt_cvs_2020.json
    with open('PttCvs/PttCvs_2020.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(json_CVS_2020_list, ensure_ascii=False))

    spend_time = time.time() - t1
    print('共花費', spend_time, '秒')

if __name__ == '__main__':
    main()