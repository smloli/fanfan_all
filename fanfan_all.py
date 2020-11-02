import os
import re
import time
import requests
from lxml import etree
from fake_useragent import UserAgent


class Novel:
    session = requests.session()

    def __init__(self):
        self.ua = UserAgent()
        self.headers = {'UserAgent': self.ua.random}
        self.root = 'https://bbs.fanfann.com/'
        # 判断Novel文件夹是否存在，不存在就创建
        self.path = '/home/novel/'
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def get_html(self, url):
        try:

            html = self.session.get(url, headers=self.headers)
            html.encoding = 'gbk'
            return html.text
        except Exception as error:
            with open('/home/error.log', 'a', encoding='utf-8') as f:
                f.write(f'{error}\n')
            return

    def get_xpath(self):
        url = 'https://bbs.fanfann.com/thread.php?fid=117&type=49&page=1'
        html = self.get_html(url)
        page_max = int(re.findall(r'">...(\d+)</a><a class="pages_next"', html)[0])
        for page in range(page_max):
            try:
                time.sleep(10)
                page += 1
                url = 'https://bbs.fanfann.com/thread.php?fid=117&type=49&page=' + str(page)
                html = self.get_html(url)
                html = html.replace('<font color=#008000>', '')
                html = html.replace('</font>', '')
                html = etree.HTML(html)
                temp_url_list = html.xpath("//a[@name='readlink']/@href")
                temp_name_list = html.xpath("//a[@name='readlink']/text()")
                if page == 1:
                    temp_url_list = temp_url_list[9:]
                info_list = []
                i_index = 0
                name_reg = r'》(.*?)作'
                for i in temp_name_list:
                    replace_content = re.findall(name_reg, i)[0]
                    i = i.replace(replace_content, '')
                    i = re.sub(r'[/|:|【完结】]', '', i)
                    # 下载路径
                    path = f'{self.path}{i}.txt'
                    # 判断文件是否存在
                    if  not os.path.exists(path):
                        info_list.append((temp_url_list[i_index], i))
                    i_index += 1
                if len(info_list) == 0:
                    continue
    
            except Exception as error:
                    with open('/home/error.log', 'a', encoding='utf-8') as f:
                        f.write(f'error:{error}\n')
                    continue
            for info in info_list:
                try:
                    html = etree.HTML(self.get_html(self.root + info[0]))
                    # 帖子id
                    url_cid = html.xpath("//a[@style='color:green;']/@href")
                    # 访问在线阅读
                    html = etree.HTML(self.get_html(self.root + url_cid[0]))
                    # 文案
                    wenan = html.xpath("//p[@class='intro']/text()")
                    wenan = wenan[0].lstrip() + '\n'
                    # 章节地址
                    url = html.xpath("//ul[@class='cf']//li//a/@href")
                    if len(url) == 1:
                        html = self.get_chapter(info[0])
                        html = etree.HTML(html)
                        url = html.xpath("//ul[@class='cf']//li//a/@href")
                    # 章节名
                    title = html.xpath("//ul[@class='cf']//li//a/text()")
                    # 标题计次
                    i = 0
                    # 去除文章简介
                    #url = url[1:]
                    #title = title[1:]
                    path = f'{self.path}{info[1]}.txt'
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(wenan)
                        for a in url:
                            # 正文
                            html = etree.HTML(self.get_html(self.root + a))
                            result = html.xpath('//div[@class="read-content j_readContent"]//text()')
                            # 转换成字符串
                            temp = ''.join(result)
                            # 替换特殊段落字符
                            temp = re.sub(r'[\s{4,}|\u3000]', '\n', temp)
                            temp = re.sub(r'\n{3,}', '\n', temp)
                            f.write(f'\n{title[i]}\n')
                            f.write(temp)
                            i += 1
                    time.sleep(5)
                except Exception as error:
                        with open('/home/error.log', 'a', encoding='utf-8') as f:
                            f.write(f'name:{info[1]}\turl:{info[0]}\terror:{error}\n')
                        continue
        requests.get('https://sc.ftqq.com/SCU61029Td3b93962fb54bd3d256ceb2ad0a0573d5d7f320397530.send?text=主人小说已经全部爬取完毕啦~')

    def get_chapter(self, ydn):
        ydn_id = ydn[3:-1]
        url = f'https://bbs.fanfann.com/{ydn}'
        cookie = f'906a6_ol_offset=81868; 906a6_readlog=%2C292373%2C1192874%2C1197600%2C1171105%2C287047%2C335767%2C293101%2C289368%2C288699%2C332234%2C; 906a6_lastpos=other; 906a6_cloudClientUid=50515752; pathid_1042483=1; qdrs=0%7C3%7C0%7C0%7C3; qdgd=1; pw_nofocus=1; 906a6_lastvisit=3659%09{time.time():.0f}%09%2Freadatt%2Freadatttest.php%3Faid{ydn_id}%26actionshow; pathid_{ydn_id}=1'
        headers = {
            'referer': url,
            'user-agent': self.ua.random,
            'cookie': cookie
        }
        result = requests.get(url + '?pathid_1', headers=headers)
        result.encoding = 'gb2312'
        return result.text

if __name__ == '__main__':
    novel = Novel()
    novel.get_xpath()
