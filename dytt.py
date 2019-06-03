import requests
from fake_useragent import UserAgent
from lxml import etree
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(filename)s] [line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    # filename='myapp.log', #文件位置
    filemode='w'
)

logger = logging.getLogger(__name__)

ua = UserAgent()
USER_AGENT = ua.random
BASE_DOMAIN = 'http://www.ygdy8.net'
HEADERS = {

    'User-Agent': USER_AGENT
}


def get_detail_urls(url):
    response = requests.get(url, headers=HEADERS)
    # text = response.text.encode('utf-8').decode('utf-8')  # 先解析整个网页编码再解码
    text = response.text
    html = etree.HTML(text)
    detail_urls = html.xpath('//a[@class="ulink"]/@href')
    detail_urls = map(lambda url: BASE_DOMAIN + url, detail_urls)
    # logger.info(detail_urls)
    return detail_urls


def parse_detail_page(url):
    movie = {}
    response = requests.get(url, headers=HEADERS)
    text = response.content.decode('gbk')  # 自己对text 内容进行解码
    html = etree.HTML(text)
    title = html.xpath('//h1/font[@color="#07519a"]/text()')[0]
    # logger.info(title)
    movie['title'] = title
    # 具体内容获取，先拿到大的内容区域
    zoom_ele = html.xpath('//div[@id="Zoom"]')[0]
    imgs = zoom_ele.xpath('.//img/@src')
    if len(imgs) > 1:
        cover = imgs[0]
        screenshot = imgs[1]
        movie['cover'] = cover
        movie['screenshot'] = screenshot
    else:
        cover = imgs[0]
        movie['cover'] = cover
        movie['screenshot'] = ''
    contents = zoom_ele.xpath('.//text()')

    # 返回zoom 下面的子孙节点的所有文字内容
    # 并且每一行作为列表中的一项
    def paser_content(content, rule):
        return content.replace(rule, '').strip()

    for index, content in enumerate(contents):
        if content.startswith('◎译　　名'):
            another_names = paser_content(content, '◎译　　名')
            movie['another_names'] = another_names
            # logger.info(another_names)
        elif content.startswith('◎年　　代'):
            year = paser_content(content, '◎年　　代')
            movie['year'] = year
        elif content.startswith('◎产　　地'):
            region = paser_content(content, '◎产　　地')
            movie['region'] = region
        elif content.startswith('◎类　　别'):
            type = paser_content(content, '◎类　　别')
            movie['type'] = type
        elif content.startswith('◎语　　言'):
            lang = paser_content(content, '◎语　　言')
            movie['lang'] = lang
        elif content.startswith('◎IMDb评分'):
            content = paser_content(content, '◎IMDb评分')
            movie['imdb_rating'] = content
        elif content.startswith('◎豆瓣评分'):
            content = paser_content(content, '◎豆瓣评分')
            movie['douban_rating'] = content
        elif content.startswith('◎主　　演'):
            content = paser_content(content, '◎主　　演')  # 根据列表中的下标获取更多的演员信息
            actors = [content]
            for index in range(index + 1, len(contents)):
                if contents[index].startswith(('◎标　　签', '◎简　　介')):
                    break
                else:
                    actors.append(contents[index].strip())
            movie['actors'] = [actor for actor in actors if len(actor) > 0]
        elif content.startswith('◎简　　介'):
            # profile = paser_content(content, '◎简　　介')
            profiles = []
            for index in range(index + 1, len(contents)):
                if contents[index].startswith('【下载地址】'):
                    break
                else:
                    profile = contents[index].strip()
                    profiles.append(profile)
            movie['profile'] = [profile for profile in profiles if len(profile) > 0]
    download_link = html.xpath('//td[@bgcolor="#fdfddf"]/a/text()')[0]
    movie['download_link'] = download_link.strip()
    # logger.info(movie)
    return movie


def spider():
    base_url = 'http://www.ygdy8.net/html/gndy/dyzz/list_23_{}.html'
    movies = []
    for i in range(1, 7):  # 定义爬虫第几页的数据
        url = base_url.format(i)
        # logger.info(url)
        detail_urls = get_detail_urls(url)
        for detail_url in detail_urls:  # 爬虫每一页的数据里电影的详情页面
            # logger.info(detail_url)
            movie = parse_detail_page(detail_url)
            movies.append(movie)
            # break
        # break


if __name__ == '__main__':
    spider()
