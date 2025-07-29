import requests
import re
from lxml import etree
from urllib.parse import urljoin
import time as time_module
from datetime import datetime
from feedgen.feed import FeedGenerator

# AI总结摘要
all_news = []
DASHSCOPE_API_KEY = "sk-0700f1fb01214614af26a93ba633f395"  # API密钥
def get_news_summary(news):
    if DASHSCOPE_API_KEY == "YOUR_API_KEY_HERE":
        return "请配置API密钥"
    headers = {
        'Authorization': f'Bearer {DASHSCOPE_API_KEY}',
        'Content-Type': 'application/json',
    }
    prompt = f"请为以下外交新闻内容生成一个150字左右的摘要，包括背景信息、主要人物、地点、事件和意义：{news}"
    data = {
        "model": "qwen-turbo",
        "input": {"messages": [{"role": "user", "content": prompt}]},
        "parameters": {"max_tokens": 200, "temperature": 0.3}
    }
    try:
        response = requests.post("https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                                 headers=headers, json=data, timeout=30)
        # 移除了所有调试信息输出
        if response.status_code == 200:
            result = response.json()
            if 'output' in result and 'text' in result['output']:
                return result['output']['text'].strip()
        return "摘要生成失败"
    except:
        return "摘要生成失败"

def fetch_news_1(section_title, url, xpath_rule):
    #print(f"\n{section_title}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36 Edg/138.0.0.0"
    }

    resp = requests.get(url, headers=headers)
    resp.encoding = 'utf-8'
    html = etree.HTML(resp.text)
    items = html.xpath(xpath_rule)

    for item in items:
        # 标题
        title = item.xpath('.//div[@class="name"]/span/@title')
        title = title[0].strip() if title else ''
        # 时间
        date = item.xpath('.//span[@class="time"]/text()')
        date = date[0].strip() if date else ''
        # 链接
        link = item.xpath('.//a/@href')
        full_link = urljoin(url, link[0].strip()) if link else ''
        # 新闻详情
        detail_resp = requests.get(full_link, headers=headers)
        detail_resp.encoding = 'utf-8'
        detail_html = etree.HTML(detail_resp.text)
        detail_items = detail_html.xpath('//div[@class="text" and @id="ch_p"]')
        for detail_item in detail_items:
            #news_list = detail_item.xpath('.//p[@style="text-indent:2em;"]/text()')
            news_list = detail_item.xpath('.//p//text()')
            news = ''.join([n.strip() for n in news_list if n.strip()])

        all_news.append((date, title, full_link, news, section_title))



fetch_news_1("海事要闻", "https://www.msa.gov.cn/page/channelArticles.do?type=xxgk&channelids=A1C5D4CC-DB15-493C-B2FC-A14C490D6331&alone=false&currentPage=1", '//li')
fetch_news_1("通知公告", "https://www.msa.gov.cn/page/channelArticles.do?type=xxgk&channelids=0308A180-57AB-4E0E-9236-20FBED32B5EF&alone=true&currentPage=1", '//li')
fetch_news_1("船舶检验", "https://www.msa.gov.cn/page/channelArticles.do?type=xxgk&channelids=CAF16466-2A5C-4AAB-82EB-61B4D45937E7&alone=true&currentPage=1", '//li')
fetch_news_1("法定主动公开内容", "https://www.msa.gov.cn/page/openInfo/articleList.do?channelId=33&pageSize=20&pageNo=1&isParent=1&type=xxgk", '//li')

# 筛选当日新闻
today = datetime.now().strftime('%Y-%m-%d')
today_news = []
for time, title, url, news, section in all_news:
    if time == today:
        today_news.append((time, title, url, news, section))

# 根据标题去重（相同标题的认为是同一条新闻）
seen_titles = set()
unique_news = []

for time, title, url, news, section in today_news:
    # 彻底清理标题：去除所有空白字符，统一比较
    clean_title = re.sub(r'\s+', '', title) if title else ''
    if clean_title and clean_title not in seen_titles:
        seen_titles.add(clean_title)
        unique_news.append((time, title.strip(), url, news, section))  # 保存原始标题（只去前后空格）

# 输出
for time, title, url, news, section in unique_news:
    summary = get_news_summary(news)
    print(f"时间：{time}")
    print(f"题目：{title}")
    print(f"摘要：{summary}")
    print(f"链接：{url}")
    print()  # 空行分隔
    time_module.sleep(0.5)  # 避免API限制


# 创建 Feed
fg = FeedGenerator()
fg.title("中国海事局 RSS")
fg.link(href="https://www.msa.gov.cn/", rel="alternate")
fg.description("由自定义爬虫抓取的中国海事局最新新闻摘要")
fg.language('zh-cn')

# 添加每条新闻
for time, title, url, news, section in unique_news:
    fe = fg.add_entry()
    fe.title(f"[{section}] {title}")
    fe.link(href=url)
    fe.description(get_news_summary(news))  # 也可直接填 news
    fe.pubDate(time + "T08:00:00+08:00")  # ISO 格式时间

# 保存成 XML 文件
fg.rss_file('China Maritime Safety Administration.xml', encoding='utf-8')

print("✅ RSS Feed 文件已生成：China Maritime Safety Administration.xml")
