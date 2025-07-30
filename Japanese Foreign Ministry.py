import requests
from lxml import etree
from datetime import datetime, timedelta
import re
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

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.mofa.go.jp/index.html",
    "Connection": "keep-alive",
    "Accept-Encoding": "gzip, deflate, br",
    "Cookie": "oFs68KIaLjNm_KkD6ZyKImmmB9durAka2sbPGJRldrs-1752996164-1.0.1.1-mUfo8n4si89ekDI1yWfA8pBJSBF8XUNvyAkLP9aouB2aoqJFu017mRTA1TgkwEp33JJ8OKgHrwCb3wapCFnVasmfTwCT1DKFgK5vhGHJwNg",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
}

base_url = "https://www.mofa.go.jp"
max_items = 10

# 爬取新闻稿
url = "https://www.mofa.go.jp/whats/index.html"
resp = requests.get(url, headers=headers)
resp.encoding = 'utf_8'
result = resp.text

html = etree.HTML(result)
dt_list = html.xpath('//div[@id="news"]/dl[@class="title-list"]/dt[@class="list-title"]')
dd_list = html.xpath('//div[@id="news"]/dl[@class="title-list"]/dd')

count = 0
for dt, dd in zip(dt_list, dd_list):
    if count >= max_items:
        break

    # 时间
    raw_date = dt.text.strip()
    date = datetime.strptime(raw_date + f", {datetime.now().year}", "%B %d, %Y").strftime("%Y-%m-%d")

    # 标题和链接
    titles = dd.xpath('.//a/text()')
    hrefs = dd.xpath('.//a/@href')

    for title, href in zip(titles, hrefs):
        if count >= max_items:
            break

        full_url = base_url + href if not href.startswith("http") else href

        try:
            # 访问每篇文章的详情页
            detail_resp = requests.get(full_url, headers=headers)
            detail_resp.encoding = 'utf-8'
            detail_html = etree.HTML(detail_resp.text)

            # 提取正文
            content_list = detail_html.xpath('//div[@class="any-area"]//text()')
            content = '\n'.join([c.strip() for c in content_list if c.strip()])

            all_news.append((date, title, content, full_url))

            count += 1

        except Exception as e:
            print(f"处理文章时出错: {e}")
            continue

# 爬取记者会
url = "https://www.mofa.go.jp/press/kaiken/index.html"
resp = requests.get(url, headers=headers)
resp.encoding = 'utf_8'
result = resp.text

html = etree.HTML(result)
items = html.xpath('//div[@id="contents-body"]//dl[@class="title-list"]')

count = 0
for item in items:
    if count >= max_items:
        break

    try:
        # 题目
        dt = item.xpath('./dt')[0]
        title = dt.xpath('./a[1]/text()')[0].strip()
        # 时间
        match = re.search(r'\(([^)]+)\)', title)
        raw_time_str = match.group(1)  # e.g. "July 15, 2025, 1:04 p.m."
        date_obj = datetime.strptime(raw_time_str.split(',')[0] + ', ' + raw_time_str.split(',')[1].strip(),
                                     "%B %d, %Y")
        date_str = date_obj.strftime("%Y-%m-%d")
        # 链接
        relative_link = dt.xpath('./a[1]/@href')[0].strip()
        full_url = base_url + relative_link if not relative_link.startswith("http") else relative_link
        # 新闻详情
        detail_resp = requests.get(full_url, headers=headers)
        detail_resp.encoding = 'utf-8'
        detail_html = etree.HTML(detail_resp.text)

        # 提取所有 <div class="any-area"> 下的文字内容
        content_blocks = detail_html.xpath('//div[@class="any-area"]')
        paragraphs = []
        for block in content_blocks:
            texts = block.xpath('.//text()')
            clean_text = ' '.join(t.strip() for t in texts if t.strip())
            if clean_text:
                paragraphs.append(clean_text)
        full_content = '\n'.join(paragraphs)

        all_news.append((date, title, content, full_url))

        count += 1

    except Exception as e:
        print(f"处理记者会时出错: {e}")
        continue

'''
# 筛选当日新闻
today = datetime.now().strftime('%Y-%m-%d')   # 获取当前日期
today_news = []
for date, title, content, full_url in all_news:
    if date == today:
        today_news.append((date, title, content, full_url))

for date, title, content, full_url in today_news:
    translation_title = get_news_title(title)
    summary = get_news_summary(content)
    print(f"时间：{date}")
    print(f"题目：{translation_title}")
    print(f"摘要：{summary}")
    print(f"链接：{full_url}")
    print()  # 空行分隔
    time_module.sleep(0.5)  # 避免API限制
'''



# 获取今天日期
today = datetime.now()
# 获取14天前的日期
fourteen_days_ago = today - timedelta(days=7)

# 筛选最近14天内新闻
recent_news = []
for date, title, content, full_url in all_news:
    try:
        news_date = datetime.strptime(date, "%Y-%m-%d")
        if fourteen_days_ago <= news_date <= today:
            recent_news.append((date, title, content, full_url))
    except:
        continue  # 跳过格式不对的日期

# 翻译后的缓存
translated_news = []
for date, title, content, full_url in recent_news:
    translation_title = get_news_title(title)
    summary = get_news_summary(content)
    translated_news.append((date, translation_title, summary, full_url))

    print(f"时间：{date}")
    print(f"题目：{translation_title}")
    print(f"摘要：{summary}")
    print(f"链接：{full_url}")
    print()
    time_module.sleep(0.5)  # 避免API限制

# 构建 RSS Feed
fg = FeedGenerator()
fg.title("日本外务省 RSS")
fg.link(href="https://www.mofa.go.jp", rel="alternate")
fg.description("由自定义爬虫抓取的日本外务省最新新闻摘要")
fg.language('zh-cn')

# 添加翻译后的新闻
for date, translation_title, summary, full_url in translated_news:
    fe = fg.add_entry()
    fe.title(translation_title)
    fe.link(href=full_url)
    fe.description(summary)
    fe.pubDate(date + "T08:00:00+08:00")

fg.rss_file('Japanese Foreign Ministry.xml', encoding='utf-8')
print("✅ RSS Feed 文件已生成： Japanese Foreign Ministry.xml")
