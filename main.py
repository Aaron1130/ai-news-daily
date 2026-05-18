import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

# ===== 配置区 =====
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")    # 发件邮箱
SENDER_PWD = os.environ.get("SENDER_PWD")        # 邮箱授权码
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL") # 收件邮箱

# AI新闻RSS源（可自行替换）
RSS_FEEDS = [
    "https://36kr.com/feed",
    "https://www.jiqizhixin.com/rss",
]

def fetch_ai_news():
    """从RSS源抓取AI新闻标题和链接"""
    news_list = []
    for feed_url in RSS_FEEDS:
        try:
            resp = requests.get(feed_url, timeout=10)
            # 简单解析XML格式的RSS
            import xml.etree.ElementTree as ET
            root = ET.fromstring(resp.content)
            for item in root.findall('.//item')[:5]:  # 每个源取5条
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else ''
                news_list.append(f"  - {title}\n    {link}")
        except Exception as e:
            news_list.append(f"  - [抓取失败] {feed_url}: {e}")
    return news_list

def send_email(news_list):
    """发送邮件"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    # 构造邮件内容
    html_content = f"""
    <h2>AI 日报 - {today}</h2>
    <h3>今日 AI 新闻汇总</h3>
    <ul>
    {''.join(f'<li>{n}</li>' for n in news_list)}
    </ul>
    <p style="color:gray;font-size:12px;">本邮件由 GitHub Actions 自动发送</p>
    """
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"AI 日报 {today}"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg.attach(MIMEText(html_content, "html", "utf-8"))
    
    # SMTP发送（以QQ邮箱为例）
    server = smtplib.SMTP_SSL("smtp.qq.com", 465)
    server.login(SENDER_EMAIL, SENDER_PWD)
    server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
    server.quit()
    print("邮件发送成功!")

if __name__ == "__main__":
    news = fetch_ai_news()
    send_email(news)
