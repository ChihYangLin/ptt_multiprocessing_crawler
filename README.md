# PTT-超商版-多程序爬蟲

## 實作步驟

* 1.按 f12 觀察所需的資料位於html的哪個標籤裡面
* 2.使用BeautifulSoup刮取標籤裡面的資料
  * 抓取出每一篇文章的url (ptt_cvs_get_url.py)
  * 再訪問每篇文章的url，刮取資料 (ptt_cvs_get_data.py)
* 3.將步驟1, 2寫成多程序去執行
* 4.按照年份(2010~2020)存成json檔
* 5.寫一份更新檔，不用每次都重新抓取資料(ptt_cvs_update.py)

Ptt_CVS_ETL.py是沒有多程序的爬蟲，耗時約6小時，多程序只要約25分鐘
