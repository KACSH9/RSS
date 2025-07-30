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
        f"请将下面的日语新闻标题翻译成中文，只输出中文翻译结果：{news}"
    )
    data = {
        "model": "qwen-turbo",
        "input": {"messages": [{"role": "user", "content": prompt}]},
        "parameters": {"max_tokens": 200, "temperature": 0.3}
    }
    try:
        response = requests.post("https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                                 headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            if 'output' in result and 'text' in result['output']:
                return result['output']['text'].strip()
        return "翻译生成失败"
    except Exception as e:
        return "翻译生成失败"


# 改进的AI总结摘要+翻译
def get_news_summary(summ):
    if DASHSCOPE_API_KEY == "YOUR_API_KEY_HERE":
        return "请配置API密钥"

    # 限制输入长度，避免超出模型限制
    if len(summ) > 2000:
        summ = summ[:2000] + "..."

    headers = {
        'Authorization': f'Bearer {DASHSCOPE_API_KEY}',
        'Content-Type': 'application/json',
    }

    # 改进prompt，更明确地要求中文输出
    prompt = (
        f"请阅读以下日语新闻内容，然后用中文生成一个150字左右的摘要。"
        f"摘要应包括：事件背景、涉及人物、发生地点、具体事件和重要意义。"
        f"请务必使用中文回答，不要使用日语。\n\n"
        f"日语新闻内容：{summ}\n\n"
        f"中文摘要："
    )

    data = {
        "model": "qwen-turbo",
        "input": {"messages": [
            {"role": "system", "content": "你是一个专业的中日翻译和新闻摘要专家。请始终使用中文回答，不要使用日语。"},
            {"role": "user", "content": prompt}
        ]},
        "parameters": {"max_tokens": 300, "temperature": 0.1}  # 降低temperature获得更稳定输出
    }

    try:
        response = requests.post("https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                                 headers=headers, json=data, timeout=30)

        if response.status_code == 200:
            result = response.json()
            if 'output' in result and 'text' in result['output']:
                summary_text = result['output']['text'].strip()

                # 检查返回的摘要是否包含日语字符
                japanese_chars = re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', summary_text)
                if len(japanese_chars) / len(summary_text) > 0.3:  # 如果日语字符超过30%
                    # 二次翻译
                    return translate_to_chinese(summary_text)

                return summary_text
        return "摘要生成失败"
    except Exception as e:
        return "摘要生成失败"


# 额外的翻译函数，用于二次翻译
def translate_to_chinese(text):
    headers = {
        'Authorization': f'Bearer {DASHSCOPE_API_KEY}',
        'Content-Type': 'application/json',
    }

    prompt = f"请将以下文本翻译成中文：{text}"

    data = {
        "model": "qwen-turbo",
        "input": {"messages": [
            {"role": "system", "content": "你是一个专业的翻译专家，请将输入的文本翻译成标准的中文。"},
            {"role": "user", "content": prompt}
        ]},
        "parameters": {"max_tokens": 300, "temperature": 0.1}
    }

    try:
        response = requests.post("https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
                                 headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            if 'output' in result and 'text' in result['output']:
                return result['output']['text'].strip()
    except Exception as e:
        pass

    return "翻译失败"


# 海上安全信息抓取函数（保持原有逻辑）
def extract_other_emergency_info(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Referer": "https://www6.kaiho.mlit.go.jp/index.html",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip, deflate, br",
        "Cookie": "oFs68KIaLjNm_KkD6ZyKImmmB9durAka2sbPGJRldrs-1752996164-1.0.1.1-mUfo8n4si89ekDI1yWfA8pBJSBF8XUNvyAkLP9aouB2aoqJFu017mRTA1TgkwEp33JJ8OKgHrwCb3wapCFnVasmfTwCT1DKFgK5vhGHJwNg",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
    }

    base_url = "https://www6.kaiho.mlit.go.jp"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        html = etree.HTML(resp.text)

        items = html.xpath('//a[img[@alt="その他の緊急情報"]]')
        for img in items:
            img_id = img.xpath('./img/@id')
            if not img_id:
                continue
            popup_id = img_id[0].replace("popup", "popup-content")
            li_items = html.xpath(f'//div[@id="{popup_id}"]//li/a')
            for a in li_items:
                href = a.xpath('./@href')[0]
                title = a.xpath('string(.)').strip()
                date_match = re.search(r'(\d{8})', href)
                if date_match:
                    raw_date = date_match.group(1)
                    date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
                else:
                    date = "未知"

                full_link = href if href.startswith("http") else base_url + href

                try:
                    detail_resp = requests.get(full_link, headers=headers, timeout=10)
                    detail_resp.encoding = 'utf-8'
                    detail_html = etree.HTML(detail_resp.text)

                    def extract_td(th_text):
                        xpath_expr = f'//th[text()="{th_text}"]/following-sibling::td[1]'
                        td = detail_html.xpath(xpath_expr)
                        return td[0].xpath('string(.)').strip() if td else ""

                    published_at = extract_td("発表日時")
                    department = extract_td("発表部署")
                    sea_area = extract_td("対象海域") or "無"
                    period = extract_td("対象期間") or "無"
                    remarks = extract_td("備考") or "無"

                    content_td = detail_html.xpath('//th[text()="内容"]/following-sibling::td[1]')
                    if content_td:
                        content = ''.join(content_td[0].xpath('.//p//text()')).strip()
                    else:
                        content = ""

                    content = (
                        f"発表日時：{published_at} "
                        f"発表部署：{department} "
                        f"対象海域：{sea_area} "
                        f"対象期間：{period} "
                        f"備考：{remarks} "
                        f"内容：{content}"
                    )

                except Exception as e:
                    content = f"详情页获取失败: {e}"

                all_news.append((date, title, content, full_link))
    except Exception as e:
        pass


# 新闻抓取函数（保持原有逻辑）
def extract_kouhou_news(url):
    base_url = "https://www.kaiho.mlit.go.jp"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        html = etree.HTML(resp.content)

        items = html.xpath('//li[div[@class="titleBasic"]]')
        for item in items[:20]:
            raw_date = item.xpath('.//div[@class="titleBasic"]/h3/text()')[0].strip()
            try:
                year, month, day = raw_date.split('/')
                year = str(2000 + int(year))
                date = f"{year}-{month}-{day}"
            except:
                date = "未知"

            title = item.xpath('.//div[@class="titleBasic"]/h3/a/text()')[0].strip()
            href = item.xpath('.//div[@class="titleBasic"]/h3/a/@href')[0]
            full_link = base_url + href

            try:
                detail_resp = requests.get(full_link, headers=headers, timeout=10)
                detail_resp.encoding = 'utf-8'
                detail_html = etree.HTML(detail_resp.content)
                content_node = detail_html.xpath('//div[@class="text_container__inner rich-text"]')
                if content_node:
                    paragraphs = content_node[0].xpath('.//text()')
                    content = ''.join([t.strip() for t in paragraphs if t.strip()])
                else:
                    content = "未找到正文内容"
            except Exception as e:
                content = f"请求详情页失败: {e}"

            all_news.append((date, title, content, full_link))
    except Exception as e:
        pass


# 主执行逻辑
if __name__ == "__main__":
    # 抓取各个地区的紧急信息
    regions = [
        'https://www6.kaiho.mlit.go.jp/01kanku/kinkyu.html',
        'https://www6.kaiho.mlit.go.jp/02kanku/kinkyu.html',
        'https://www6.kaiho.mlit.go.jp/03kanku/kinkyu.html',
        'https://www6.kaiho.mlit.go.jp/04kanku/kinkyu.html',
        'https://www6.kaiho.mlit.go.jp/05kanku/kinkyu.html',
        'https://www6.kaiho.mlit.go.jp/06kanku/kinkyu.html',
        'https://www6.kaiho.mlit.go.jp/07kanku/kinkyu.html',
        'https://www6.kaiho.mlit.go.jp/08kanku/kinkyu.html',
        'https://www6.kaiho.mlit.go.jp/09kanku/kinkyu.html',
        'https://www6.kaiho.mlit.go.jp/10kanku/kinkyu.html',
        'https://www6.kaiho.mlit.go.jp/11kanku/kinkyu.html'
    ]

    for region_url in regions:
        extract_other_emergency_info(region_url)

    # 抓取新闻
    extract_kouhou_news('https://www.kaiho.mlit.go.jp/info/kouhou/')


    '''
    # 筛选当日新闻
    today = datetime.now().strftime('%Y-%m-%d')
    today_news = []
    for date, title, content, full_url in all_news:
        if date == today:
            today_news.append((date, title, content, full_url))

    # 去重
    seen_titles = set()
    unique_news = []
    for date, title, content, full_url in today_news:
        clean_title = re.sub(r'\s+', '', title) if title else ''
        if clean_title and clean_title not in seen_titles:
            seen_titles.add(clean_title)
            unique_news.append((date, title.strip(), content, full_url))

    # 处理每条新闻
    for date, title, content, full_url in unique_news:
        translation_title = get_news_title(title)
        summary = get_news_summary(content)

        print(f"时间：{date}")
        print(f"题目：{translation_title}")
        print(f"摘要：{summary}")
        print(f"链接：{full_url}")
        print()  # 空行分隔

        time_module.sleep(1)  # 增加延时避免API限制
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
    fg.title("日本海上保安厅 RSS")
    fg.link(href="https://www.kaiho.mlit.go.jp", rel="alternate")
    fg.description("由自定义爬虫抓取的日本海上保安厅最新新闻摘要")
    fg.language('zh-cn')

    # 添加翻译后的新闻
    for date, translation_title, summary, full_url in translated_news:
        fe = fg.add_entry()
        fe.title(translation_title)
        fe.link(href=full_url)
        fe.description(summary)
        fe.pubDate(date + "T08:00:00+08:00")

    fg.rss_file('Japan Maritime Safety Agency.xml', encoding='utf-8')
    print("✅ RSS Feed 文件已生成： Japan Maritime Safety Agency.xml")
