import requests
from lxml import etree
from urllib.parse import urljoin
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

def convert_date(date_str):
    """
    将 '09 July 2025' 转为 '2025-07-09'
    """
    try:
        dt = datetime.strptime(date_str.strip(), '%d %B %Y')
        return dt.strftime('%Y-%m-%d')
    except:
        return date_str.strip()

url = 'https://forumsec.org/publications'
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36 Edg/138.0.0.0"
}

resp = requests.get(url, headers=headers)
html = etree.HTML(resp.text)

cards = html.xpath('//div[contains(@class, "card publication")]')[:10]  # 前10条

for card in cards:
    # 提取日期
    date = card.xpath('.//div[@class="card__date"]/text()')
    date_str = convert_date(date[0]) if date else '未知日期'

    # 提取标题
    title = card.xpath('.//a[contains(@class, "card__title")]/text()')
    title_str = title[0].strip() if title else '无标题'

    # 提取链接
    href = card.xpath('.//a[contains(@class, "card__title")]/@href')
    link_str = urljoin(url, href[0]) if href else ''

    # 提取内容
    resp2 = requests.get(link_str, headers=headers)
    html2 = etree.HTML(resp2.text)
    news_div = html2.xpath('//div[@class="margin-v-2 body-copy"]')
    if news_div:
        # 提取所有文本，去除空白行
        news_text_list = news_div[0].xpath('.//text()')
        news_text = '\n'.join([t.strip() for t in news_text_list if t.strip()])
    else:
        news_text = '[正文抓取失败]'

    all_news.append((date_str, title_str, news_text, link_str))

'''
# 筛选当日新闻
today = datetime.now().strftime('%Y-%m-%d')   # 获取当前日期
today_news = []
for date_str, title_str, news_text, link_str in all_news:
    if date_str == today:
        today_news.append((date_str, title_str, news_text, link_str))


for date_str, title_str, news_text, link_str in today_news:
    translation_title = get_news_title(title_str)
    summary = get_news_summary(news_text)
    print(f"时间：{date_str}")
    print(f"题目：{translation_title}")
    print(f"摘要：{summary}")
    print(f"链接：{link_str}")
    print()  # 空行分隔
    time_module.sleep(0.5)  # 避免API限制
'''


# 获取今天日期
today = datetime.now()
# 获取14天前的日期
fourteen_days_ago = today - timedelta(days=14)

# 筛选最近14天内新闻
recent_news = []
for date_str, title_str, news_text, link_str in all_news:
    try:
        news_date = datetime.strptime(date_str, "%Y-%m-%d")
        if fourteen_days_ago <= news_date <= today:
            recent_news.append((date_str, title_str, news_text, link_str))
    except:
        continue  # 跳过格式不对的日期

# 翻译后的缓存
translated_news = []
for date_str, title_str, news_text, link_str in recent_news:
    translation_title = get_news_title(title_str)
    summary = get_news_summary(news_text)
    translated_news.append((date_str, translation_title, summary, link_str))

    print(f"时间：{date_str}")
    print(f"题目：{translation_title}")
    print(f"摘要：{summary}")
    print(f"链接：{link_str}")
    print()
    time_module.sleep(0.5)  # 避免API限制

# 构建 RSS Feed
fg = FeedGenerator()
fg.title("太平洋岛国论坛 RSS")
fg.link(href="https://forumsec.org", rel="alternate")
fg.description("由自定义爬虫抓取的太平洋岛国论坛最新新闻摘要")
fg.language('zh-cn')

# 添加翻译后的新闻
for date_str, translation_title, summary, link_str in translated_news:
    fe = fg.add_entry()
    fe.title(translation_title)
    fe.link(href=link_str)
    fe.description(summary)
    fe.pubDate(date_str + "T08:00:00+08:00")

fg.rss_file('Pacific Islands Forum.xml', encoding='utf-8')
print("✅ RSS Feed 文件已生成： Pacific Islands Forum.xml")
