import requests
from lxml import etree
from urllib.parse import urljoin
import html
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


url = "https://www.dav.edu.vn/tin-tuc/"
resp = requests.get(url)
resp.encoding = "utf-8"
html_tree = etree.HTML(resp.text)

articles = html_tree.xpath('//article[contains(@class, "story")]')

for article in articles:
    # 日期
    raw_date = article.xpath('.//time/text()')
    if not raw_date:
        continue
    try:
        raw_date_str = raw_date[0].strip()[:10]
        date_obj = datetime.strptime(raw_date_str, "%d/%m/%Y")
        date_fmt = date_obj.strftime("%Y-%m-%d")
    except:
        continue

    # 标题与链接
    title_nodes = article.xpath('.//h3[@class="story__title"]/a')
    if not title_nodes:
        continue
    title = html.unescape(title_nodes[0].xpath('string(.)').strip())
    href = title_nodes[0].xpath('./@href')[0]
    full_url = urljoin(url, href)

    # 正文抓取
    news = ''
    try:
        resp2 = requests.get(full_url, timeout=10)
        resp2.encoding = "utf-8"
        html_tree2 = etree.HTML(resp2.content.decode('utf-8'))

        news_paras = html_tree2.xpath('//div[contains(@class, "detail__content")]//p//text()')
        news = ' '.join(html.unescape(p.strip()) for p in news_paras if p.strip())
    except Exception as e:
        news = f"[抓取失败] {e}"

    all_news.append((date_fmt, title, news, full_url))

'''
# 筛选当日新闻
today = datetime.now().strftime('%Y-%m-%d')   # 获取当前日期
today_news = []
for date_fmt, title, news, full_url in all_news:
    if date_fmt == today:
        today_news.append((date_fmt, title, news, full_url))

for date_fmt, title, news, full_url in today_news:
    translation_title = get_news_title(title)
    summary = get_news_summary(news)
    print(f"时间：{date_fmt}")
    print(f"题目：{translation_title}")
    print(f"摘要：{summary}")
    print(f"链接：{full_url}")
    print()  # 空行分隔
    time_module.sleep(0.5)  # 避免API限制
'''





# 获取今天日期
today = datetime.now()
# 获取14天前的日期
fourteen_days_ago = today - timedelta(days=10)

# 筛选最近14天内新闻
recent_news = []
for date_fmt, title, news, full_url in all_news:
    try:
        news_date = datetime.strptime(date_fmt, "%Y-%m-%d")
        if fourteen_days_ago <= news_date <= today:
            recent_news.append((date_fmt, title, news, full_url))
    except:
        continue  # 跳过格式不对的日期

# 翻译后的缓存
translated_news = []
for date_fmt, title, news, full_url in recent_news:
    translation_title = get_news_title(title)
    summary = get_news_summary(news)
    translated_news.append((date_fmt, translation_title, summary, full_url))

    print(f"时间：{date_fmt}")
    print(f"题目：{translation_title}")
    print(f"摘要：{summary}")
    print(f"链接：{full_url}")
    print()
    time_module.sleep(0.5)  # 避免API限制

# 构建 RSS Feed
fg = FeedGenerator()
fg.title("越南外交部 RSS")
fg.link(href="https://www.dav.edu.vn", rel="alternate")
fg.description("由自定义爬虫抓取的越南外交部最新新闻摘要")
fg.language('zh-cn')

# 添加翻译后的新闻
for date_fmt, translation_title, summary, full_url in translated_news:
    fe = fg.add_entry()
    fe.title(translation_title)
    fe.link(href=full_url)
    fe.description(summary)
    fe.pubDate(date_fmt + "T08:00:00+08:00")

fg.rss_file('Vietnam Diplomatic Academy.xml', encoding='utf-8')
print("✅ RSS Feed 文件已生成： Vietnam Diplomatic Academy.xml")
