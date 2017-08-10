'''
javlibraryp爬虫
功能：
输入URL_INDEX(你所想爬取的页面，ex.艺人所演出影片、最高评价、最期待)、
    PATH (你想把图片存放的目录)，
即可爬取图片，并以车牌号、评分来命名。


#目的功能1： 下载图片，以分数，番号命名  get √
#目的功能2： 存入mongodb

问题：
1. urlretrieve下载图片返回403， 现在的opener的原理是什么？
2. 如何使用代理？ 或者shadowsocks？ （现在是用的是全局代理）get √
3. 如何加快速度？ （太慢了，解析网页获取目录，进入车辆，获取图片，然后下一车辆。。。。。。）
4. 出现确认满足十八岁的页面问题，mac出现 windows没有
'''
import re
from urllib.request import urlretrieve
from urllib import request

import requests
from pyquery import PyQuery as pq

# 所爬取的艺人目录
URL_INDEX = 'http://www.javlibrary.com/cn/vl_mostwanted.php'
# 输出目录
#PATH = 'D:\LZZZZB\P\javlibrary\最想要\\'
PATH = '/Users/zhibinliu/scrapypra/javlib/new'

# 实现翻页，每一页调用parse_item_url(html)。所以要实现一个方法来获取html
def crawl_start(url):
    proxies = {
        'http': 'socks5://127.0.0.1:1080',
        'https': 'socks5://127.0.0.1:1080'
    }

    response = requests.get(url, proxies=proxies)
    print(response.status_code)
    html = response.text
    print(html)
    # 开始爬取图片
    parse_item_url(html)
    # 判断是否存在下一页
    pattern_nextpage = re.compile('page\snext"\shref="(.*?)">', re.S)
    url_part_re = re.findall(pattern_nextpage, html)
    # 如果没有下一页
    if len(url_part_re) == 0:
        print("没有下一页了，Done.")
        return 0
    # 如果有下一页
    elif len(url_part_re) == 1:
        print("\n")
        print(">>>爬取继续.....................")
        print("\n")
        url_part = url_part_re[0]
        url_next = 'http://www.javlibrary.com' + url_part
        print("爬取", url_next)
        return crawl_start(url_next)



# 获取源代码，所有信息均在源代码，没有ajax加载
def get_source(url):
    response = requests.get(url)
    return response.text


# 找出目录的各个item的url，生成请求
def parse_index(html):
    base_url_item = 'http://www.javlibrary.com/cn/'
    doc = pq(html)
    #print(type(doc))
    items = doc('.videothumblist .videos .video').items()

    for item in items:
        #print(type(item))
        query = item('a').attr('href')[2:]
        #print(query)
        item_url = base_url_item + query
        yield requests.get(item_url).text


def parse_item_url(html):
    for html in parse_index(html):
        #print(html)
        print('----------------------------------------------------------------------')
        # 图片地址
        pattern = re.compile('image_src"\shref="(.*?)">',re.S)
        image_url_re = re.findall(pattern, html)
        image_url = image_url_re[0]
        print("图片地址:", image_url, end='   ')

        # 车牌号码
        doc = pq(html)
        #print(type(doc))
        tds = doc('#video_id  > table > tr > td.text ').items()
        for td in tds:
            plat_no = td.text()
            print("车牌号码: ", plat_no, end='   ')

        # 评分
        pattern2 = re.compile('rating\s=\s"(\d+)";', re.S)
        image_rating_re = re.findall(pattern2, html)
        image_rating = image_rating_re[0]
        print("车辆评分: ", image_rating)

        download_pic(image_url, plat_no, image_rating)
        #return image_url, plat_no, image_rating


def download_pic(image_url, plat_no, image_rating):
    path = PATH + plat_no + '_' + image_rating + '.jpg'
    #print(path)

    opener = request.build_opener()
    opener.addheaders = [('User-Agent',
                          'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
    request.install_opener(opener)
    request.urlretrieve(image_url, path)
    print("Downloading to: ", path)


def main():
    crawl_start(URL_INDEX)
    # html = get_source(url_index)
    #
    # parse_item_url(html)


if __name__ == '__main__':
    main()