import requests
from lxml import etree
from urllib.parse import urljoin
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


url = 'https://www.academy.kaiho.mlit.go.jp/index.html'
base = 'https://www.academy.kaiho.mlit.go.jp'

headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36 Edg/138.0.0.0"
}

resp = requests.get(url, headers=headers)
resp.encoding = 'utf-8'

html = etree.HTML(resp.text)
items = html.xpath('//dl[@class="info_list"]/div')

#print("---------- 新闻和话题 ----------")
for item in items:
    date = item.xpath('.//time/@datetime')
    title = item.xpath('.//a/text()')
    link = item.xpath('.//a/@href')

    # 提取实际值
    date_str = date[0].strip() if date else ''
    title_str = title[0].strip() if title else ''
    full_link = urljoin(base, link[0].strip()) if link else ''

    # 获取详情页正文内容
    resp2 = requests.get(full_link, headers=headers)
    resp2.encoding = 'utf-8'
    html2 = etree.HTML(resp2.text)
    content_area = html2.xpath('//main[@id="mainContents"]')[0]  # 提取 main 内容区域

    paragraphs = content_area.xpath('.//p//text() | .//h3//text() | .//h6//text() | .//li//text() | .//div//text()')

    content_text = ''.join([t.strip() for t in paragraphs if t.strip()])

    all_news.append((date_str, title_str, content_text, full_link))

'''
# 筛选当日新闻
today = datetime.now().strftime('%Y-%m-%d')   # 获取当前日期
today_news = []
for date_str, title_str, content_text, full_link in all_news:
    if date_str == today:
        today_news.append((date_str, title_str, content_text, full_link))

for date_str, title_str, content_text, full_link in today_news:
    translation_title = get_news_title(title_str)
    summary = get_news_summary(content_text)
    print(f"时间：{date_str}")
    print(f"题目：{translation_title}")
    print(f"摘要：{summary}")
    print(f"链接：{full_link}")
    print()  # 空行分隔
    time_module.sleep(0.5)  # 避免API限制
'''



# 获取今天日期
today = datetime.now()
# 获取14天前的日期
fourteen_days_ago = today - timedelta(days=7)

# 筛选最近14天内新闻
recent_news = []
for date_str, title_str, content_text, full_link in all_news:
    try:
        news_date = datetime.strptime(date_str, "%Y-%m-%d")
        if fourteen_days_ago <= news_date <= today:
            recent_news.append((date_str, title_str, content_text, full_link))
    except:
        continue  # 跳过格式不对的日期

# 翻译后的缓存
translated_news = []
for date_str, title_str, content_text, full_link in recent_news:
    translation_title = get_news_title(title_str)
    summary = get_news_summary(content_text)
    translated_news.append((date_str, translation_title, summary, full_link))

    print(f"时间：{date_str}")
    print(f"题目：{translation_title}")
    print(f"摘要：{summary}")
    print(f"链接：{full_link}")
    print()
    time_module.sleep(0.5)  # 避免API限制

# 构建 RSS Feed
fg = FeedGenerator()
fg.title("日本海上保安大学校 RSS")
fg.link(href="https://www.academy.kaiho.mlit.go.jp", rel="alternate")
fg.description("由自定义爬虫抓取的日本海上保安大学校最新新闻摘要")
fg.language('zh-cn')

# 添加翻译后的新闻
for date_str, translation_title, summary, full_link in translated_news:
    fe = fg.add_entry()
    fe.title(translation_title)
    fe.link(href=full_link)
    fe.description(summary)
    fe.pubDate(date_str + "T08:00:00+08:00")

fg.rss_file('Japan Maritime Security University.xml', encoding='utf-8')
print("✅ RSS Feed 文件已生成： Japan Maritime Security University.xml")
