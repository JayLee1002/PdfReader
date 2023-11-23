from bs4 import BeautifulSoup
import urllib.request
import re
import time
import traceback
import pandas as pd
import warnings

warnings.filterwarnings("ignore")

headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/90.0.4430.93 Safari/537.36'
}


def get_paper_page(url):
    req = urllib.request.Request(url=url, headers=headers)
    res = urllib.request.urlopen(req, timeout=100)
    html = res.read().decode('utf-8')
    soup = BeautifulSoup(html)
    data = [[
        div.select('.gs_rt > a')[0].text,
        div.select('.gs_fl > a')[2].string,
        re.search("- .*?\</div>",
                  str(div.select('.gs_a')[0])).group()[1:-6].replace(
                      "\xa0", ""),
        div.select('.gs_rt > a')[0]["href"]
    ] for div in soup.select('.gs_ri')]
    data = [[
        x[0],
        int(x[1][6:]) if x[1] is not None and x[1].startswith("被引用次数") else 0,
        x[2], x[3]
    ] for x in data]
    return data


def save_paper_list(data, file_name):
    data = pd.DataFrame(
        data, columns=['paper title', 'reference', 'publish info', 'url'])
    writer = pd.ExcelWriter(file_name)
    data.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.save()
    writer.close()
    
    
def make_url(url_base: str,
             keyword: str,
             start_year: int = None,
             end_year: int = None,
             start: int = 0):
    url = url_base + '&q=' + keyword
    if start_year is not None:
        url += "&as_ylo=" + str(start_year)
    if end_year is not None:
        url += "&as_yhi=" + str(end_year)
    return url


def get_paper_list_by_keywork(keyword,
                              start_year=None,
                              end_year=None,
                              max_capacity=100,
                              debug_mode=False,
                              retry_times=4):
    keyword = re.sub(" +", "+", keyword.strip())
    url_out = ('https://', '/scholar?hl=zh-CN&as_sdt=0%2C5')
    mid = ['scholar.google.com', 'xs.cljtscd.com', 'so1.cljtscd.com', 'scholar.lanfanshu.cn']
    url_init = url_out[0] + mid[0] + url_out[1]
    i = 0
    url_base = make_url(url_init, keyword, start_year, end_year)

    retry_times = max(retry_times, len(mid))
    start = 0
    data = []
    while start < max_capacity:
        url = url_base + "&start=" + str(start)
        start += 10
        print(url)
        for t in range(retry_times):
            try:
                data.extend(get_paper_page(url))
                break
            except Exception as e:
                if t < retry_times - 1:
                    print("error, retrying ... ")
                    i += 1
                    if i > len(mid) - 1:
                        raise Exception("network error")
                    print("switch url_base to ", end="")
                    url_init = url_out[0] + mid[i] + url_out[1]
                    url_base = make_url(url_init, keyword, start_year,
                                        end_year)
                    print(url_base)
                    url = url_base + "&start=" + str(start)
                else:
                    print(e)
                    print("error, fail to get ", url)
                if debug_mode:
                    traceback.print_exc()
                time.sleep(5)
        time.sleep(5)
    # data: [论文标题, 引用数, 发表时间及机构缩写, 论文链接]
    return data


if __name__ == "__main__":
    out = get_paper_list_by_keywork(" bert ",
                              start_year=2020,
                              max_capacity=20,
                              debug_mode=False,)
    print(out)
    print("end")
