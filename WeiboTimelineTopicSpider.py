# uncompyle6 version 3.9.0
# Python bytecode version base 3.6 (3379)
# Decompiled from: Python 3.6.6 (v3.6.6:4cf1f54eb7, Jun 27 2018, 03:37:03) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: ./NewSuperWeiboTimelineTopicSpider.py
# Compiled at: 2023-12-12 23:02:54
# Size of source mod 2**32: 20092 bytes
import csv, os, traceback
from datetime import datetime, timedelta
from time import sleep
import requests
from lxml import etree
import json

def formatLimitTime(limit_time):
    if limit_time[-2] == '-':
        limit_time = limit_time[:-2] + ' 0' + limit_time[-1]
    else:
        if limit_time[-3] == '-':
            limit_time = limit_time[:-3] + ' ' + limit_time[-2]
    return limit_time


def unformatLimitTime(limit_time):
    if limit_time[-2] == '0':
        limit_time = limit_time[:-3] + '-' + limit_time[-1]
    else:
        limit_time = limit_time[:-3] + '-' + limit_time[-2:]
    return limit_time


def parseTime(publish_time):
    if '刚刚' in publish_time:
        publish_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    else:
        if '分钟' in publish_time:
            minute = publish_time[:publish_time.find('分钟')]
            minute = timedelta(minutes=(int(minute)))
            publish_time = (datetime.now() - minute).strftime('%Y-%m-%d %H:%M')
        else:
            if '今天' in publish_time:
                today = datetime.now().strftime('%Y-%m-%d')
                time = publish_time[2:]
                publish_time = today + ' ' + time
            else:
                if '月' in publish_time:
                    if '年' in publish_time:
                        if '日' in publish_time:
                            publish_time = publish_time.replace('年', '-')
                            publish_time = publish_time.replace('月', '-')
                            publish_time = publish_time.replace('日', '')
                        else:
                            if publish_time.index('月') == 1:
                                publish_time = '0' + publish_time
                            if publish_time.index('日') == 4:
                                publish_time = publish_time[:3] + '0' + publish_time[3:]
                            year = datetime.now().strftime('%Y')
                            month = publish_time[0:2]
                            day = publish_time[3:5]
                            time = publish_time[7:12]
                            publish_time = year + '-' + month + '-' + day + ' ' + time
                else:
                    publish_time = publish_time[:16]
    return publish_time


class NewSuperWeiboTimelineTopicSpider(object):
    headers = {
     'Connection': "'keep-alive'", 
     'sec-ch-ua-mobile': "'?0'", 
     'Upgrade-Insecure-Requests': "'1'", 
     'User-Agent': "'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'", 
     'Accept': "'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'", 
     'Sec-Fetch-Site': "'same-origin'", 
     'Sec-Fetch-Mode': "'navigate'", 
     'Sec-Fetch-User': "'?1'", 
     'Sec-Fetch-Dest': "'document'", 
     'Referer': "'https://s.weibo.com/weibo?q=%E7%9F%AD%E5%89%A7'", 
     'Accept-Language': "'zh-CN,zh;q=0.9,en-CN;q=0.8,en;q=0.7,es-MX;q=0.6,es;q=0.5'", 
     'Cookie': "'SINAGLOBAL=9725772483514.139.1613553315797; UOR=,,login.sina.com.cn; ALF=1659101552; SSOLoginState=1627565555; _s_tentry=weibo.com; Apache=2637325324112.2607.1627565587195; ULV=1627565587202:10:5:2:2637325324112.2607.1627565587195:1627305811035; wb_view_log_7343943709=1440*9002; SCF=Ak5UIygEew_0NkA_WvuL8CBEDoRWNdgAQNITQ0vB_Z5_JIbZb9n-ZA02uRx-EiC9ZnrF3l3seJyF9HgoTxHXD6Q.; SUB=_2A25MAHANDeRhGeFN71EY9C3LyzWIHXVvdObFrDV8PUJbmtAKLU32kW9NQDeegWi--yhLzxG_pOTq6ZrlSaJRzIOw; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9Wh.o0WH0iR_VjZs.QN5p_NR5JpX5K-hUgL.FoM0She4SheNeh.2dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMNe0B01KB0S054; webim_unReadCount=%7B%22time%22%3A1627656664107%2C%22dm_pub_total%22%3A1%2C%22chat_group_client%22%3A0%2C%22chat_group_notice%22%3A0%2C%22allcountNum%22%3A1%2C%22msgbox%22%3A0%7D'"}
    params = {
     'q': "'华为P50'", 
     'typeall': "'1'", 
     'suball': "'1'", 
     'timescope': "'custom:2021-05-01-9:2021-06-01-16'", 
     'Refer': "'g'", 
     'page': "'1'"}
    realtime_params = {
     'q': "'苏炳添晋级百米半决赛'", 
     'rd': "'realtime'", 
     'tw': "'realtime'", 
     'Refer': "'hot_realtime'", 
     'page': "'3'"}
    hot_params = {
     'q': "'苏炳添晋级百米半决赛'", 
     'suball': "'1'", 
     'xsort': "'hot'", 
     'tw': "'hotweibo'", 
     'Refer': "'weibo_hot'", 
     'page': "'2'"}
    max_page = 50
    timeout = 10
    topic_folder = 'topic'

    def __init__(self, keyword, start_time, end_time, cookies=None, only_origin=False):
        self.keyword = keyword
        self.start_time = start_time
        self.end_time = end_time
        self.got_weibos = []
        self.got_weibo_ids = []
        self.got_weibos_num = 0
        self.written_weibos_num = 0
        if cookies:
            self.headers['Cookie'] = cookies
        if only_origin:
            self.params['scope'] = 'ori'
        if not os.path.exists(self.topic_folder):
            os.mkdir(self.topic_folder)
        self.result_file = self.topic_folder + '/' + self.keyword + '.csv'

    def getLocation(self, html):
        candidate = html.xpath('.//p[@class="txt"]/a[child::*[contains(text(), "2")]]')
        if len(candidate) > 0:
            location_url = candidate[0].xpath('./@href')[0]
            location_name = candidate[0].xpath('string(.)').strip().replace('2', '')
            return (location_url, location_name)

    def parseWeibo(self, html):
        weibos = html.xpath('//div[@class="card-wrap" and @mid]')
        if len(weibos) == 0:
            print(html)
            yield
        print(len(weibos))
        for weibo in weibos:
            mid = weibo.xpath('./@mid')[0]
            user_info = weibo.xpath('.//div[@class="info"]/div/a[@class="name"]')[0]
            user_name, user_link = user_info.xpath('./text()')[0], 'https:' + user_info.xpath('./@href')[0]
            try:
                content = weibo.xpath('.//div[@class="content"]/p[@class="txt" and @node-type="feed_list_content_full"]')[0].xpath('string(.)').strip()
            except:
                content = weibo.xpath('.//div[@class="content"]/p[@class="txt" and @node-type="feed_list_content"]')[0].xpath('string(.)').strip()

            images = weibo.xpath('.//div[@node-type="feed_list_media_prev"]/div/ul/li')
            image_urls = []
            for image in images:
                if image.xpath('./video/@src'):
                    pass
                else:
                    image_url = image.xpath('./img/@src')[0]
                    if not image_url.startswith('http'):
                        image_url = 'https:' + image_url
                    image_urls.append(image_url)

            p_from = weibo.xpath('.//div[@class="content"]/div[@class="from"]/a')[0]
            try:
                source = weibo.xpath('.//div[@class="content"]/div[@class="from"]/a[@rel="nofollow"]/text()')[0]
            except:
                source = ''

            weibo_link = 'https:' + p_from.xpath('./@href')[0]
            weibo_link = weibo_link[:weibo_link.rindex('?')]
            publish_time = p_from.xpath('./text()')[0].strip()
            publish_time = parseTime(publish_time)
            bottoms = weibo.xpath('.//div[@class="card-act"]/ul/li')
            location = self.getLocation(weibo)
            if location:
                if not location[0].strip() == 'javascript:void(0);':
                    location_url, location_name = location[0], location[1]
                else:
                    location_url, location_name = ('', '')
                print(location_url, location_name)
                if weibo.xpath('.//span[@title="微博个人认证"]'):
                    if weibo.xpath('.//svg[@id="woo_svg_vyellow"]'):
                        verify_typ = '黄V认证'
                    else:
                        if weibo.xpath('.//svg[@id="woo_svg_vgold"]'):
                            verify_typ = '红V认证'
                        else:
                            if weibo.xpath('.//svg[@id="woo_svg_vorange"]'):
                                verify_typ = '橙V认证'
                            else:
                                raise Exception(f"{weibo_link} {user_name}")
                else:
                    if weibo.xpath('.//span[@title="微博官方认证"]'):
                        verify_typ = '蓝V认证'
                    else:
                        verify_typ = '没有认证'
                    forward_num, comment_num, like_num = (0, 0, 0)
                    start_index = len(bottoms) - 4
                    for index, bottom in enumerate(bottoms):
                        if index == start_index + 1:
                            try:
                                forward_num = bottom.xpath('./a/text()')[1].strip()
                            except:
                                forward_num = bottom.xpath('./a/text()')[0].strip()

                            forward_num = forward_num.replace('转发', '').strip()
                            if len(forward_num) == 0:
                                forward_num = 0
                            else:
                                if index == start_index + 2:
                                    comment_num = bottom.xpath('./a/text()')[0].strip()
                                    comment_num = comment_num.replace('评论', '').strip()
                                    if len(comment_num) == 0:
                                        comment_num = 0
                                elif index == start_index + 3:
                                    try:
                                        like_num = bottom.xpath('./a/button/span[last()]/text()')[0].strip()
                                        like_num = like_num.replace('赞', '').strip()
                                        if len(like_num) == 0:
                                            like_num = 0
                                    except:
                                        try:
                                            like_num = bottom.xpath('.//em/text()')[0].strip()
                                        except:
                                            like_num = 0

                    aweibo = {'mid':mid, 
                     'publish_time':publish_time, 
                     'user_name':user_name, 
                     'user_link':user_link, 
                     'content':content, 
                     'source':source, 
                     'location_url':location_url, 
                     'location_name':location_name, 
                     'image_urls':' '.join(image_urls), 
                     'weibo_link':weibo_link, 
                     'forward_num':forward_num, 
                     'comment_num':comment_num, 
                     'like_num':like_num, 
                     'verify_typ':verify_typ}
                    print(publish_time, mid, user_name, user_link, content.encode('GBK', 'ignore').decode('GBK'), image_urls, weibo_link, forward_num, comment_num, like_num, verify_typ)
                    yield aweibo

    def write_csv(self):
        """将爬取的信息写入csv文件"""
        try:
            result_headers = [
             "'mid'", 
             "'publish_time'", 
             "'user_name'", 
             "'user_link'", 
             "'content'", 
             "'source'", 
             "'location_url'", 
             "'location_name'", 
             "'image_urls'", 
             "'weibo_link'", 
             "'forward_num'", 
             "'comment_num'", 
             "'like_num'", 
             "'verify_typ'"]
            result_data = [w.values() for w in self.got_weibos][self.written_weibos_num:]
            with open((self.result_file), 'a', encoding='utf-8-sig', newline='') as (f):
                writer = csv.writer(f)
                if self.written_weibos_num == 0:
                    writer.writerows([result_headers])
                writer.writerows(result_data)
            print('%d条微博写入csv文件完毕:' % self.got_weibos_num)
            self.written_weibos_num = self.got_weibos_num
        except Exception as e:
            print('Error: ', e)
            traceback.print_exc()

    def crawl(self):
        global config_json
        global consist_error_times
        while True:
            print(' ... 公众号 @ 月小水长 ... \n\n')
            self.params['q'] = self.keyword
            self.params['timescope'] = f"custom:{self.start_time}:{self.end_time}"
            current_page = 1
            this_turn_weibo_count = 0
            while current_page <= self.max_page:
                self.params['page'] = str(current_page)
                try:
                    response = requests.get('https://s.weibo.com/weibo', headers=(self.headers), params=(self.params), timeout=(self.timeout))
                    print(response.url)
                except:
                    print(traceback.format_exc())
                    print('network error')
                    config_json['end_time'] = self.end_time
                    saveConfig()
                    break

                print(f"\n page : {current_page} {response.url}\n")
                if response.status_code == 200:
                    res_html = etree.HTML(response.text)
                    res_html or print(response.text)
                    print('\t\t\t cur resp ==  null \t\t\t')
                    print(response.encoding)
                    sleep(5)
                    continue
                    if res_html.xpath('//div[contains(@class,"card-no-result")]/p/text()'):
                        print(f"\n\n\n  抱歉，未找到“{self.keyword}”相关结果。 \n\n\n")
                        sleep(10)
                        break
                    for weibo in self.parseWeibo(res_html):
                        if weibo is None:
                            current_page = self.max_page
                            print('\n________ DATA IS NONE__________\n')
                            break
                        if self.keyword in weibo.get('content', 'weibo') or True:
                            self.got_weibos.append(weibo)
                            self.got_weibo_ids.append(weibo['mid'])
                            self.got_weibos_num += 1
                            this_turn_weibo_count += 1

                if current_page % 3 == 0:
                    if self.got_weibos_num > self.written_weibos_num:
                        self.write_csv()
                sleep(3)
                current_page += 1

            if self.got_weibos_num > self.written_weibos_num:
                self.write_csv()
            try:
                earliest_time = unformatLimitTime(self.got_weibos[-1]['publish_time'][:-3])
                if this_turn_weibo_count == 0:
                    raise Exception('data none exception')
                consist_error_times = 0
            except:
                consist_error_times += 1
                print(traceback.format_exc())
                earliest_time = dateToStr(strToDate(self.end_time) + timedelta(hours=(consist_error_times * -2)))

            if earliest_time > self.start_time:
                self.end_time = earliest_time
                print(f"\n------------{self.start_time}---------------{self.end_time}--------------\n")
            else:
                break


consist_error_times = 0

def strToDate(str_time):
    times_arr = str_time.split('-')
    year = int(times_arr[0])
    month = int(times_arr[1])
    day = int(times_arr[2])
    hour = int(times_arr[3])
    return datetime(year=year, month=month, day=day, hour=hour)


def dateToStr(dt_time):
    year = str(dt_time.year)
    month = str(dt_time.month).zfill(2)
    day = str(dt_time.day).zfill(2)
    hour = str(dt_time.hour)
    return f"{year}-{month}-{day}-{hour}"


def loadConfig():
    if not os.path.exists(config_path):
        raise Exception(f"没有配置文件 {config_path}")
    with open(config_path, 'r', encoding='utf-8-sig') as (f):
        config_json = json.loads(f.read())
    keys = config_json.keys()
    print(keys)
    if 'cookie' in keys:
        if 'keyword' in keys:
            if 'start_time' in keys:
                if 'end_time' in keys:
                    if 'only_origin' in keys:
                        return config_json
    raise Exception(f"配置文件 {config_path} 缺少 cookie/keyword/start_time/end_time/only_origin 字段")


def saveConfig():
    with open(config_path, 'w', encoding='utf-8-sig') as (f):
        f.write(json.dumps(config_json, indent=2, ensure_ascii=False))


config_path = 'topic_config.json'
config_json = None

def main():
    global config_json
    config_json = loadConfig()
    if config_json:
        cookies, keyword, start_time, end_time = (
         config_json['cookie'], config_json['keyword'],
         config_json['start_time'],
         config_json['end_time'])
        only_origin = config_json['only_origin']
    else:
        cookies = 'SINAGLOBAL=9725772483514.139.1613553315797; UOR=,,login.sina.com.cn; SSOLoginState=1629942645; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5MCOuIe9TuswxEEPRIFh7X5JpX5KMhUgL.FoqRSK.pe0e7eK.2dJLoIXnLxKML1hML1K-LxK-LBoML1--LxKML1h.LBKMLxK.LBKzL1hqLxKnLBK2LBK2LxK-LBoML1--LxK-L1hnLB.2LxK-L12qLBozt; ALF=1661786575; SCF=Ak5UIygEew_0NkA_WvuL8CBEDoRWNdgAQNITQ0vB_Z5_yduCWa1fsbSg_sDv_mxaDNlkb_V_0B8LM28k-D0Xf2U.; SUB=_2A25ML9YADeRhGeBG7lsQ8y3MyjWIHXVvXUDIrDV8PUNbmtAKLXfnkW9NRhjQcIMmJICi7jgvqjBtKQCBsKFU2y00; _s_tentry=-; Apache=6606979092043.827.1630251389837; ULV=1630251389909:22:9:1:6606979092043.827.1630251389837:1629899087834; WBStorage=2ceabba76d81138d|undefined'
        keyword = '华为手机'
        start_time = '2012-01-01-1'
        end_time = '2021-08-19-16'
        only_origin = False
    spider = NewSuperWeiboTimelineTopicSpider(cookies=cookies, keyword=keyword, start_time=start_time, end_time=end_time,
      only_origin=only_origin)
    spider.crawl()


if __name__ == '__main__':
    main()