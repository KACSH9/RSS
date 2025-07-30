import requests
from lxml import etree
import re
import time as time_module
from datetime import datetime, timedelta
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

url = 'https://www.isa.org.jm/news/'
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}
resp = requests.get(url, headers=headers)
result = resp.text

html = etree.HTML(result)

articles = html.xpath('//article[contains(@id,"post")]')

for article in articles:
    #时间
    date_1 = article.xpath('.//span[@class="post_date"]/text()')[0]
    date_2 = datetime.strptime(date_1, "%d %B %Y")
    date_3 = date_2.strftime("%Y-%m-%d")
    #标题
    title = article.xpath('.//h4[@class="entry-titles default-max-width"]/a/text()')[0]
    #链接
    link = article.xpath('.//h4[@class="entry-titles default-max-width"]/a/@href')[0]
    #详细内容
    resp2 = requests.get(link)
    result2 = resp2.text
    obj = re.search(r'<div class="entry-content">(.*?)</div>', result2, re.S)
    raw_html = obj.group(1)  #<p>...<p>  ...
    paragraphs = re.findall(r'<p>(.*?)</p>', raw_html, re.S)   #提取...
    text = ' '.join([re.sub(r'<.*?>', '', p).strip() for p in paragraphs if p.strip()])

    all_news.append((date_3, title, text, link))



'''
# 筛选当日新闻
today = datetime.now().strftime('%Y-%m-%d')   # 获取当前日期
today_news = []
for date_3, title, text, link in all_news:
    if date_3 == today:
        today_news.append((date_3, title, text, link))

for date_3, title, text, link in today_news:
    translation_title = get_news_title(title)
    summary = get_news_summary(text)
    print(f"时间：{date_3}")
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
for date_3, title, text, link in all_news:
    try:
        news_date = datetime.strptime(date_3, "%Y-%m-%d")
        if fourteen_days_ago <= news_date <= today:
            recent_news.append((date_3, title, text, link))
    except:
        continue  # 跳过格式不对的日期

# 翻译后的缓存
translated_news = []
for date_3, title, text, link in recent_news:
    translation_title = get_news_title(title)
    summary = get_news_summary(text)
    translated_news.append((date_3, translation_title, summary, link))

    print(f"时间：{date_3}")
    print(f"题目：{translation_title}")
    print(f"摘要：{summary}")
    print(f"链接：{link}")
    print()
    time_module.sleep(0.5)  # 避免API限制

# 构建 RSS Feed
fg = FeedGenerator()
fg.title("国际海底管理局 RSS")
fg.link(href="https://www.isa.org.jm", rel="alternate")
fg.description("由自定义爬虫抓取的国际海底管理局最新新闻摘要")
fg.language('zh-cn')

# 添加翻译后的新闻
for date_3, translation_title, summary, link in translated_news:
    fe = fg.add_entry()
    fe.title(translation_title)
    fe.link(href=link)
    fe.description(summary)
    fe.pubDate(date_3 + "T08:00:00+08:00")

fg.rss_file('International Seabed Authority.xml', encoding='utf-8')
print("✅ RSS Feed 文件已生成： International Seabed Authority.xml")
