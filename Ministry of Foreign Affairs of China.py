# 导入库
from lxml import etree
import requests
import re
from urllib.parse import urljoin
import time as time_module
from datetime import datetime, timedelta
from feedgen.feed import FeedGenerator

# AI总结摘要
all_news = []
DASHSCOPE_API_KEY = "sk-0700f1fb01214614af26a93ba633f395"  # API密钥
def get_news_summary(news):
    if DASHSCOPE_API_KEY == "YOUR_API_KEY_HERE":
        return "请配置API密钥"
    headers = {
        'Authorization': f'Bearer {DASHSCOPE_API_KEY}',
        'Content-Type': 'application/json',
    }
    prompt = f"请为以下外交新闻内容生成一个150字左右的摘要，包括背景信息、主要人物、地点、事件和意义：{news}"
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

# 题目中包含时间的内容
def extract_simple_section(section_title, url, xpath_expr):
    resp = requests.get(url)
    resp.encoding = 'utf-8'
    html = etree.HTML(resp.text)
    links = html.xpath(xpath_expr)
    date_pattern = re.compile(r'（(\d{4}-\d{2}-\d{2})）')
    #板块
    #print(f"\n{section_title}")
    #爬取内容
    for a in links:
        #标题
        text = a.xpath('string(.)').strip()
        title = date_pattern.sub('', text).strip()
        #链接
        href = a.xpath('./@href')[0]
        full_url = urljoin(url, href)
        #新闻详情
        detail_resp = requests.get(full_url)
        detail_resp.encoding = 'utf-8'
        detail_html2 = etree.HTML(detail_resp.text)
        news_list = detail_html2.xpath('//div[@id="News_Body_Txt_A"]//p//text()')
        news = ''.join(news_list).strip()
        #时间
        date_match = date_pattern.search(text)
        date = date_match.group(1) if date_match else ''
        #输出格式
        all_news.append((date, title, full_url, news, section_title))

# 题目中不包含时间，需到详情页提取
def extract_detail_time_section(section_title, url, xpath_expr):
    resp = requests.get(url)
    resp.encoding = 'utf-8'
    html = etree.HTML(resp.text)
    links = html.xpath(xpath_expr)
    #板块
    #print(f"\n{section_title}")
    #爬取内容
    for a in links:
        #标题
        title = a.xpath('string(.)').strip()
        #链接
        href = a.xpath('./@href')[0]
        full_url = urljoin(url, href)
        #时间
        detail_resp = requests.get(full_url)
        detail_resp.encoding = 'utf-8'
        detail_html = etree.HTML(detail_resp.text)
        date = detail_html.xpath('string(//meta[@name="PubDate"]/@content)').strip()
        #新闻详情
        news_list = detail_html.xpath('//div[@id="News_Body_Txt_A"]//p//text()')
        news = ''.join(news_list).strip()
        # 输出格式
        all_news.append((date, title, full_url, news, section_title))

# 特殊板块：讲话全文 / 声明公报
def extract_rightbox_list(section_title, url, xpath_expr):
    resp = requests.get(url)
    resp.encoding = 'utf-8'
    html = etree.HTML(resp.text)
    items = html.xpath(xpath_expr)
    #板块
    #print(f"\n{section_title}")
    #爬取内容
    for i in items:
        #题目
        title = i.xpath('string(.//a)').strip()
        #链接
        href = i.xpath('.//a/@href')
        full_url = urljoin(url, href[0]) if href else ''
        #时间
        detail_resp = requests.get(full_url)
        detail_resp.encoding = 'utf-8'
        detail_html = etree.HTML(detail_resp.text)
        date = detail_html.xpath('string(//meta[@name="PubDate"]/@content)').strip()
        # 新闻详情
        news_list = detail_html.xpath('//div[@id="News_Body_Txt_A"]//p//text()')
        news = ''.join(news_list).strip()
        # 输出格式
        all_news.append((date, title, full_url, news, section_title))


# ---------------------- 调用函数 ----------------------

# 含有明显日期
extract_simple_section('重要新闻', 'https://www.fmprc.gov.cn/zyxw/', '//ul[@class="list1"][1]/li/a | //ul[@class="list1"][2]/li/a')
extract_simple_section('外交部长活动', 'https://www.fmprc.gov.cn/wjbzhd/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('外交部新闻', 'https://www.fmprc.gov.cn/wjbxw_new/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('领导人活动', 'https://www.fmprc.gov.cn/wjdt_674879/gjldrhd_674881/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('外事日程', 'https://www.fmprc.gov.cn/wjdt_674879/wsrc_674883/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('部领导活动', 'https://www.fmprc.gov.cn/wjdt_674879/wjbxw_674885/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('业务动态', 'https://www.fmprc.gov.cn/wjdt_674879/sjxw_674887/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('吹风会', 'https://www.fmprc.gov.cn/wjdt_674879/cfhsl_674891/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('大使任免', 'https://www.fmprc.gov.cn/wjdt_674879/dsrm_674893/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('驻外报道', 'https://www.fmprc.gov.cn/wjdt_674879/zwbd_674895/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('政策解读', 'https://www.fmprc.gov.cn/wjdt_674879/zcjd/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('外事活动', 'https://www.fmprc.gov.cn/zwbd_673032/wshd_673034/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('公众活动', 'https://www.fmprc.gov.cn/zwbd_673032/gzhd_673042/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('外交之声', 'https://www.fmprc.gov.cn/zwbd_673032/wjzs/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('外交掠影', 'https://www.fmprc.gov.cn/zwbd_673032/ywfc_673029/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('文化交流', 'https://www.fmprc.gov.cn/zwbd_673032/whjl/', '//ul[@class="list1"][1]/li/a')
extract_simple_section('侨务中资机构活动', 'https://www.fmprc.gov.cn/zwbd_673032/jghd_673046/', '//ul[@class="list1"][1]/li/a')

# 需要进详情页取时间者
extract_detail_time_section('发言人表态', 'https://www.fmprc.gov.cn/fyrbt_673021/', '//ul[@class="list1 list1-1"][1]/li[not(@style)]/a | //ul[@class="list1 list1-1"][2]/li[not(@style)]/a')

# 特殊结构：rightbox 列表页
extract_rightbox_list('讲话全文', 'https://www.mfa.gov.cn/web/ziliao_674904/zyjh_674906/', '//div[@class="rightbox"]//li')
extract_rightbox_list('声明公报', 'https://www.mfa.gov.cn/web/ziliao_674904/1179_674909/', '//div[@class="rightbox"]//li')


# 获取今天和前一天日期
today = datetime.now()
yesterday = today - timedelta(days=2)

# 筛选近两日新闻
recent_news = []
for date, title, full_url, news, section in all_news:
    try:
        news_date = datetime.strptime(date, "%Y-%m-%d")
        if yesterday <= news_date <= today:
            recent_news.append((date, title, full_url, news, section))
    except:
        continue  # 跳过格式异常的数据

# 根据标题去重（相同标题的认为是同一条新闻）
seen_titles = set()
unique_news = []

for date, title, full_url, news, section in recent_news:
    clean_title = re.sub(r'\s+', '', title) if title else ''
    if clean_title and clean_title not in seen_titles:
        seen_titles.add(clean_title)
        unique_news.append((date, title.strip(), full_url, news, section))

# 输出新闻并翻译摘要
for date, title, full_url, news, section in unique_news:
    summary = get_news_summary(news)
    print(f"时间：{date}")
    print(f"题目：{title}")
    print(f"摘要：{summary}")
    print(f"链接：{full_url}")
    print()
    time_module.sleep(0.5)  # 避免触发 API 限速

# 创建 Feed
fg = FeedGenerator()
fg.title("中国外交部每日新闻 RSS")
fg.link(href="https://www.fmprc.gov.cn/", rel="alternate")
fg.description("由自定义爬虫抓取的外交部最新新闻摘要")
fg.language('zh-cn')

# 添加每条新闻
for time, title, url, news, section in unique_news:
    fe = fg.add_entry()
    fe.title(f"[{section}] {title}")
    fe.link(href=url)
    fe.description(summary)  # 也可直接填 news
    fe.pubDate(time + "T08:00:00+08:00")  # ISO 格式时间

# 保存成 XML 文件
fg.rss_file('Ministry of Foreign Affairs of China.xml', encoding='utf-8')

print("✅ RSS Feed 文件已生成：Ministry of Foreign Affairs of China.xml")




