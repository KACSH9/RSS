import re
import requests
from html import unescape
import time as time_module
from datetime import datetime, timedelta
from feedgen.feed import FeedGenerator

# AI翻译
all_news = []
DASHSCOPE_API_KEY = "sk-0700f1fb01214614af26a93ba633f395"  # API密钥
def get_news_summary(news, is_title=False):
    if DASHSCOPE_API_KEY == "YOUR_API_KEY_HERE":
        return "请配置API密钥"
    headers = {
        'Authorization': f'Bearer {DASHSCOPE_API_KEY}',
        'Content-Type': 'application/json',
    }
    prompt = f"请为以下{'外交新闻标题' if is_title else '外交新闻内容'}翻译成中文：{news}"
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

url = "https://www.wto.org/library/news/current_news_e.js"  # 替换成实际包含 news_item 的 js 文件
headers = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36 Edg/138.0.0.0"
}

resp = requests.get(url, headers=headers)
resp.encoding = 'utf-8'
js_text = resp.text

pattern = r'news_item\[(\d+)\]\s*=\s*{(.*?)};'
matches = re.findall(pattern, js_text, re.DOTALL)

for id_, content in matches:
    # 提取字段
    date_match = re.search(r'ni_date:"(.*?)"', content)
    head_match = re.search(r'ni_head:"(.*?)"', content)
    intro_match = re.search(r'ni_intro:"(.*?)"', content)
    link_match = re.search(r'nl_url:"(.*?)"', content)

    date = date_match.group(1).split('_')[0].replace('.', '-') if date_match else ""
    title = unescape(head_match.group(1)) if head_match else ""
    intro = unescape(intro_match.group(1)) if intro_match else ""
    link = "https://www.wto.org" + link_match.group(1) if link_match else ""

    all_news.append((date, title, intro, link))
'''
# 筛选当日新闻
today = datetime.now().strftime('%Y-%m-%d')
today_news = []

for date, title, intro, link in all_news:
    if date == today:
        today_news.append((date, title, intro, link))
'''

# 获取今天日期
today = datetime.now()
# 获取14天前的日期
fourteen_days_ago = today - timedelta(days=14)

# 筛选最近14天内新闻
recent_news = []
for date, title, intro, link in all_news:
    try:
        news_date = datetime.strptime(date, "%Y-%m-%d")
        if fourteen_days_ago <= news_date <= today:
            recent_news.append((date, title, intro, link))
    except:
        continue  # 跳过格式不对的日期

for date, title, intro, link in recent_news:
    translation_title = get_news_summary(title, is_title=True)
    translation_intro = get_news_summary(intro, is_title=False)
    print(f"时间：{date}")
    print(f"题目：{translation_title}")
    print(f"摘要：{translation_intro}")
    print(f"链接：{link}")
    print()
    time_module.sleep(0.5)


# 创建 Feed
fg = FeedGenerator()
fg.title("世界贸易组织 RSS")
fg.link(href="https://www.wto.org", rel="alternate")
fg.description("由自定义爬虫抓取的世界贸易组织最新新闻摘要")
fg.language('zh-cn')

# 添加每条新闻
for date, title, intro, link in recent_news:
    fe = fg.add_entry()
    fe.title(title)  # 如果需要可加标签前缀
    fe.link(href=link)
    fe.description(get_news_summary(intro))
    fe.pubDate(date + "T08:00:00+08:00")  # ISO时间格式


# 保存成 XML 文件
fg.rss_file('World Trade Organization.xml', encoding='utf-8')

print("✅ RSS Feed 文件已生成： World Trade Organization.xml")
