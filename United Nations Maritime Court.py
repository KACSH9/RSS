from lxml import etree
from urllib.parse import urljoin
import requests
from datetime import datetime, timedelta
import time as time_module
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

# 网站地址
base_url = 'https://www.itlos.org'
url = base_url + '/en/main/resources/calendar-of-events/'

# 获取网页内容
resp = requests.get(url)
resp.encoding = 'utf-8'
html = etree.HTML(resp.text)

# 遍历每条新闻
articles = html.xpath('//div[contains(@class, "article") and @itemscope]')

for article in articles:
    # 1. 日期
    date = article.xpath('.//time/@datetime')[0].strip()

    # 2. 标题
    title = article.xpath('.//span[@itemprop="headline"]/text()')[0].strip()

    # 3. 所有链接
    link_tags = article.xpath('.//div[contains(@class, "news-text-wrap")]//a/@href')
    links = ', '.join(urljoin(base_url, href) for href in link_tags if href.strip())

    # 4. 新闻内容
    news_list = article.xpath('.//div[@itemprop="description"]//p//text()')
    news = '\n'.join([n.strip() for n in news_list if n.strip()])

    all_news.append((date, title, news, links))


'''
# 筛选当日新闻
today = datetime.now().strftime('%Y-%m-%d')   # 获取当前日期
today_news = []
for date, title, news, links in all_news:
    if date == today:
        today_news.append((date, title, news, links))


for date, title, news, links in today_news:
    translation_title = get_news_title(title)
    summary = get_news_summary(news)
    print(f"时间：{date}")
    print(f"题目：{translation_title}")
    print(f"摘要：{summary}")
    print(f"链接：{links}")
    print()  # 空行分隔
    time_module.sleep(0.5)  # 避免API限制
'''




# 获取今天日期
today = datetime.now()
# 获取14天前的日期
fourteen_days_ago = today - timedelta(days=7)

# 筛选最近14天内新闻
recent_news = []
for date, title, news, links in all_news:
    try:
        news_date = datetime.strptime(date, "%Y-%m-%d")
        if fourteen_days_ago <= news_date <= today:
            recent_news.append((date, title, news, links))
    except:
        continue  # 跳过格式不对的日期

# 翻译后的缓存
translated_news = []
for date, title, news, links in recent_news:
    translation_title = get_news_title(title)
    summary = get_news_summary(news)
    translated_news.append((date, translation_title, summary, links))

    print(f"时间：{date}")
    print(f"题目：{translation_title}")
    print(f"摘要：{summary}")
    print(f"链接：{links}")
    print()
    time_module.sleep(0.5)  # 避免API限制

# 构建 RSS Feed
fg = FeedGenerator()
fg.title("联合国海洋法庭 RSS")
fg.link(href="https://www.itlos.org", rel="alternate")
fg.description("由自定义爬虫抓取的联合国海洋法庭最新新闻摘要")
fg.language('zh-cn')

# 添加翻译后的新闻
for date, translation_title, summary, links in translated_news:
    fe = fg.add_entry()
    fe.title(translation_title)
    fe.link(href=links)
    fe.description(summary)
    fe.pubDate(date + "T08:00:00+08:00")

fg.rss_file('United Nations Maritime Court.xml', encoding='utf-8')
print("✅ RSS Feed 文件已生成： United Nations Maritime Court.xml")
