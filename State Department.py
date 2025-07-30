import requests
from lxml import etree
from urllib.parse import urljoin
from datetime import datetime, timedelta
import time as time_module
import re
from feedgen.feed import FeedGenerator


# AI题目翻译
all_news = []
DASHSCOPE_API_KEY = "sk-0700f1fb01214614af26a93ba633f395"  # API密钥
def get_news_title(news):
    if DASHSCOPE_API_KEY == "YOUR_API_KEY_HERE":
        return "请配置API密钥"
    headers = {
        'Authorization': f'Bearer {DASHSCOPE_API_KEY}',
        'Content-Type': 'application/json',
    }
    prompt = (
        f"请将下面题目翻译成中文：{news}"
    )
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
        return "翻译生成失败"
    except:
        return "翻译生成失败"

# AI总结摘要+翻译
DASHSCOPE_API_KEY = "sk-0700f1fb01214614af26a93ba633f395"  # API密钥
def get_news_summary(summ):
    if DASHSCOPE_API_KEY == "YOUR_API_KEY_HERE":
        return "请配置API密钥"
    headers = {
        'Authorization': f'Bearer {DASHSCOPE_API_KEY}',
        'Content-Type': 'application/json',
    }
    prompt = (
        f"请为以下外交新闻内容生成一个150字左右的摘要，包括背景信息、主要人物、地点、事件和意义，然后将该摘要翻译成中文，只给我中文版即可：{summ}"
    )
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


url = 'https://www.state.gov/'
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}
resp = requests.get(url, headers=headers)
resp.encoding = 'utf-8'

html = etree.HTML(resp.text)
items = html.xpath('//li[@class="news-bar__post"]')

#print("---------- 头条新闻 ----------")
for item in items:
    # 抓取字段
    raw_date = item.xpath('string(.//div[@class="news-bar__post-date"])').strip()
    title = item.xpath('string(.//p[@class="news-bar__post-title"]/a)').strip()
    link = item.xpath('string(.//p[@class="news-bar__post-title"]/a/@href)').strip()

    # 日期格式转换
    try:
        date_obj = datetime.strptime(raw_date, "%B %d, %Y")
        formatted_date = date_obj.strftime("%Y-%m-%d")
    except Exception:
        formatted_date = raw_date  # fallback，保留原始

    resp2 = requests.get(link, headers=headers)
    resp2.encoding = 'utf-8'
    html2 = etree.HTML(resp2.text)
    items2 = html2.xpath('//div[@class="classic-block-wrapper"]')
    for item2 in items2:
        content_list = item2.xpath('.//p/text()')
        content = ''.join([t.strip() for t in content_list if t.strip()])


        all_news.append((formatted_date, title, content, link))


#print("---------- 其他新闻 ----------")
items = html.xpath('//ul[@class="other-news__list"]/li')

for item in items:
    # 日期
    raw_date_list = item.xpath('.//div[@class="eyebrow other-news__eyebrow"]/text()')
    raw_date = raw_date_list[0].strip() if raw_date_list else ""

    # 标题
    title_list = item.xpath('.//h3[@class="header--four"]/a/text()')
    title = title_list[0].strip() if title_list else ""

    # 链接
    link_list = item.xpath('.//h3[@class="header--four"]/a/@href')
    link = link_list[0].strip() if link_list else ""

    # 日期格式转换
    try:
        formatted_date = datetime.strptime(raw_date, "%B %d, %Y").strftime("%Y-%m-%d")
    except:
        formatted_date = raw_date

    resp3 = requests.get(link, headers=headers)
    resp3.encoding = 'utf-8'
    html3 = etree.HTML(resp3.text)
    items3 = html3.xpath('//div[@class="classic-block-wrapper"]')
    for item3 in items3:
        content_list = item3.xpath('.//p/text()')
        content = ''.join([t.strip() for t in content_list if t.strip()])

        all_news.append((formatted_date, title, content, link))


#print("---------- 发言人简报 ----------")
briefing_url = 'https://www.state.gov/department-press-briefings'
resp4 = requests.get(briefing_url, headers=headers)
resp4.encoding = 'utf-8'

html4 = etree.HTML(resp4.text)
items = html4.xpath('//li[@class="collection-result"]')

for item in items:
    # 标题
    title_list = item.xpath('.//a[@class="collection-result__link"]/text()')
    title = title_list[0].strip() if title_list else ""

    # 链接
    link_list = item.xpath('.//a[@class="collection-result__link"]/@href')
    link = link_list[0].strip() if link_list else ""

    # 日期（一般在第二个 span）
    date_list = item.xpath('.//div[@class="collection-result-meta"]/span[2]/text()')
    raw_date = date_list[0].strip() if date_list else ""

    # 日期格式转换
    try:
        formatted_date = datetime.strptime(raw_date, "%B %d, %Y").strftime("%Y-%m-%d")
    except:
        formatted_date = raw_date

    resp5 = requests.get(link, headers=headers)
    resp5.encoding = 'utf-8'
    html5 = etree.HTML(resp5.text)
    items5 = html5.xpath('//div[@class="classic-block-wrapper"]')
    for item5 in items5:
        content_list = item5.xpath('.//p/text()')
        content = ''.join([t.strip() for t in content_list if t.strip()])

        all_news.append((formatted_date, title, content, link))



#print("---------- 中国专页新闻 ----------")
china_url = 'https://www.state.gov/countries-areas/china/'
resp_china = requests.get(china_url, headers=headers)
resp_china.encoding = 'utf-8'
china_html = etree.HTML(resp_china.text)

# 定位到新闻块
china_items = china_html.xpath('//div[contains(@class, "state-content-feed__article")]')

# 去重集合
seen = set()

for item in china_items:
    # 日期
    raw_date_list = item.xpath('.//span[contains(@class, "state-content-feed__article-eyebrow")]/text()')
    raw_date = raw_date_list[0].strip() if raw_date_list else ""

    # 标题
    title_list = item.xpath('.//p[@class="state-content-feed__article-headline"]/a/text()')
    title = title_list[0].strip() if title_list else ""

    # 链接
    link_list = item.xpath('.//p[@class="state-content-feed__article-headline"]/a/@href')
    link = link_list[0].strip() if link_list else ""

    # 去重逻辑
    key = (raw_date, title, link)
    if key in seen:
        continue
    seen.add(key)

    # 日期格式化
    try:
        formatted_date = datetime.strptime(raw_date, "%B %d, %Y").strftime("%Y-%m-%d")
    except:
        formatted_date = raw_date

    resp6 = requests.get(link, headers=headers)
    resp6.encoding = 'utf-8'
    html6 = etree.HTML(resp6.text)
    items6 = html6.xpath('//div[@class="classic-block-wrapper"]')
    for item6 in items6:
        content_list = item6.xpath('.//p/text()')
        content = ''.join([t.strip() for t in content_list if t.strip()])

        all_news.append((formatted_date, title, content, link))
'''
# 筛选当日新闻
today = datetime.now().strftime('%Y-%m-%d')   # 获取当前日期
today_news = []
for formatted_date, title, content, link in all_news:
    if formatted_date == today:
        today_news.append((formatted_date, title, content, link))

seen_titles = set()
unique_news = []
for formatted_date, title, content, link in today_news:
    # 彻底清理标题：去除所有空白字符，统一比较
    clean_title = re.sub(r'\s+', '', title) if title else ''
    if clean_title and clean_title not in seen_titles:
        seen_titles.add(clean_title)
        unique_news.append((formatted_date, title.strip(), content, link))  # 保存原始标题（只去前后空格）

for formatted_date, title, content, link in unique_news:
    translation_title = get_news_title(title)
    summary = get_news_summary(content)
    print(f"时间：{formatted_date}")
    print(f"题目：{translation_title}")
    print(f"摘要：{summary}")
    print(f"链接：{link}")
    print()  # 空行分隔
    time_module.sleep(0.5)  # 避免API限制
'''


# 获取今天日期
today = datetime.now()
# 获取14天前的日期
fourteen_days_ago = today - timedelta(days=30)

# 筛选最近14天内新闻
recent_news = []
for formatted_date, title, content, link in all_news:
    try:
        news_date = datetime.strptime(formatted_date, "%Y-%m-%d")
        if fourteen_days_ago <= news_date <= today:
            recent_news.append((formatted_date, title, content, link))
    except:
        continue  # 跳过格式不对的日期

seen_titles = set()
unique_news = []

for formatted_date, title, content, link in recent_news:
    clean_title = re.sub(r'\s+', '', title) if title else ''
    if clean_title and clean_title not in seen_titles:
        seen_titles.add(clean_title)
        unique_news.append((formatted_date, title.strip(), link, content))

# 翻译后的缓存
translated_news = []
for formatted_date, title, link, content in unique_news:
    translation_title = get_news_title(title)
    summary = get_news_summary(content)
    translated_news.append((formatted_date, translation_title, summary, link))

    print(f"时间：{formatted_date}")
    print(f"题目：{translation_title}")
    print(f"摘要：{summary}")
    print(f"链接：{link}")
    print()
    time_module.sleep(0.5)  # 避免API限制

# 构建 RSS Feed
fg = FeedGenerator()
fg.title("美国国务院 RSS")
fg.link(href="https://www.state.gov/", rel="alternate")
fg.description("由自定义爬虫抓取的美国国务院最新新闻摘要")
fg.language('zh-cn')

# 添加翻译后的新闻
for formatted_date, translation_title, summary, link in translated_news:
    fe = fg.add_entry()
    fe.title(translation_title)
    fe.link(href=link)
    fe.description(summary)
    fe.pubDate(formatted_date + "T08:00:00+08:00")

fg.rss_file('State Department.xml', encoding='utf-8')
print("✅ RSS Feed 文件已生成： State Department.xml")
