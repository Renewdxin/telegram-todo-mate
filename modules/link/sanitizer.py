from bs4 import BeautifulSoup

def sanitize_telegram_html(html_str: str) -> str:
    """
    清理输入的HTML字符串，只保留Telegram支持的HTML标签。
    允许的标签有：b, strong, i, em, u, ins, s, strike, del, code, pre, a
    """
    allowed_tags = {'b', 'strong', 'i', 'em', 'u', 'ins', 's', 'strike', 'del', 'code', 'pre', 'a'}
    soup = BeautifulSoup(html_str, "html.parser")
    # 如果文档中存在<body>则优先处理<body>内的内容
    content = soup.body if soup.body else soup

    for tag in content.find_all(True):
        if tag.name.lower() not in allowed_tags:
            tag.unwrap()  # 移除不支持的标签，但保留内部文本
        else:
            if tag.name.lower() == 'a':
                href = tag.get('href')
                # 如果没有 href 则直接去除标签
                if href:
                    tag.attrs = {'href': href}
                else:
                    tag.unwrap()
            else:
                tag.attrs = {}
    # 拼接所有子节点的字符串，避免产生额外的<html>、<body>包装
    return ''.join(str(child) for child in content.children) 