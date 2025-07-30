import requests
from lxml import etree
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

def extract_mofa_news(section_name, url, limit=10):
    #print(f'----------{section_name}----------')
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36 Edg/138.0.0.0"
    }

    resp = requests.get(url, headers=headers)
    resp.encoding = 'utf-8'
    html = etree.HTML(resp.text)

    blocks = html.xpath('//div[@class="block-category-container"]')

    def extract_date(raw):
        try:
            # 原始格式如："12:47 | 07/07/2025"
            date_part = raw.split('|')[-1].strip()
            dt = datetime.strptime(date_part, '%d/%m/%Y')
            return dt.strftime('%Y-%m-%d')
        except:
            return '未知日期'

    for block in blocks[:limit]:
        title = block.xpath('.//h3[@class="news-title"]/a/text()')
        title = title[0].strip() if title else '无标题'

        link = block.xpath('.//h3[@class="news-title"]/a/@href')
        link = link[0].strip() if link else ''
        link = link.replace('http://', 'https://')

        resp2 = requests.get(link, headers=headers)
        resp2.encoding = 'utf-8'
        html2 = etree.HTML(resp2.text)
        news_list = html2.xpath('//div[@class="article-content"]/p//text()')
        news_list = [text.strip() for text in news_list if text.strip()]
        news = '\n'.join(news_list)

        date_raw = block.xpath('string(.//div[@class="news-time"])').strip()
        date = extract_date(date_raw)

        all_news.append((date, title, news, link))

extract_mofa_news('高级外部活动', 'https://mofa.gov.vn/hoat-dong-doi-ngoai-cap-cao')
extract_mofa_news('副首相和部长的活动', 'https://mofa.gov.vn/hoat-dong-pho-thu-tuong-bo-truong')
extract_mofa_news('该部领导的活动', 'https://mofa.gov.vn/hoat-dong-lanh-dao-bo')
extract_mofa_news('发言人', 'https://mofa.gov.vn/nguoi-phat-ngon')
extract_mofa_news('新闻发布会', 'https://mofa.gov.vn/hop-bao')

'''
# 筛选当日新闻
today = datetime.now().strftime('%Y-%m-%d')   # 获取当前日期
today_news = []
for date, title, news, link in all_news:
    if date == today:
        today_news.append((date, title, news, link))


for date, title, news, link in today_news:
    translation_title = get_news_title(title)
    summary = get_news_summary(news)
    print(f"时间：{date}")
    print(f"题目：{translation_title}")
    print(f"摘要：{summary}")
    print(f"链接：{link}")
    print()  # 空行分隔
    time_module.sleep(0.5)  
'''




# 获取今天日期
today = datetime.now()
# 获取14天前的日期
fourteen_days_ago = today - timedelta(days=10)

# 筛选最近14天内新闻
recent_news = []
for date, title, news, link in all_news:
    try:
        news_date = datetime.strptime(date, "%Y-%m-%d")
        if fourteen_days_ago <= news_date <= today:
            recent_news.append((date, title, news, link))
    except:
        continue  # 跳过格式不对的日期

# 翻译后的缓存
translated_news = []
for date, title, news, link in recent_news:
    translation_title = get_news_title(title)
    summary = get_news_summary(news)
    translated_news.append((date, translation_title, summary, link))

    print(f"时间：{date}")
    print(f"题目：{translation_title}")
    print(f"摘要：{summary}")
    print(f"链接：{link}")
    print()
    time_module.sleep(0.5)  # 避免API限制

# 构建 RSS Feed
fg = FeedGenerator()
fg.title("越南外交部 RSS")
fg.link(href="https://mofa.gov.vn", rel="alternate")
fg.description("由自定义爬虫抓取的越南外交部最新新闻摘要")
fg.language('zh-cn')

# 添加翻译后的新闻
for date, translation_title, summary, link in translated_news:
    fe = fg.add_entry()
    fe.title(translation_title)
    fe.link(href=link)
    fe.description(summary)
    fe.pubDate(date + "T08:00:00+08:00")

fg.rss_file('Ministry of Foreign Affairs of Vietnam.xml', encoding='utf-8')
print("✅ RSS Feed 文件已生成： Ministry of Foreign Affairs of Vietnam.xml")
