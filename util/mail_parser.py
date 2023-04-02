import collections
import email
import html
import re


def parse(raw_email):
    """Parse raw email content and extract sender, recipient, subject, content, and URLs if present."""
    raw_email = re.sub(r"<style.*?>.*?</style>", "", raw_email, flags=re.DOTALL)

    msg = email.message_from_string(raw_email)
    sender = msg["From"]
    recipient = msg["To"]
    subject = msg["Subject"]
    text_content = None
    html_content = None
    urls = []

    for part in msg.walk():
        content_type = part.get_content_type()
        charset = part.get_content_charset() or "utf-8"
        if content_type == "text/plain":
            text_content = part.get_payload(decode=True).decode(charset)
        elif content_type == "text/html":
            html_content = part.get_payload(decode=True).decode(charset)

        if html_content:
            urls += re.findall(r"<a.*?href=\"(.*?)\".*?>", html_content)
            urls = [url for url in urls if not url.endswith((".jpg", ".png", ".webp"))]
            urls = list(collections.OrderedDict.fromkeys(urls))

    if html_content:
        text_content = html.unescape(html_content)
        text_content = re.sub(r"<[^>]+>", "", text_content).strip()
        text_content = re.sub(r"\n+", "", text_content)

    return sender, recipient, subject, text_content, urls
