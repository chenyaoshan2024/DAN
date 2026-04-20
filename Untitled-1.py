#!/usr/bin/env python3
# 简单爬虫 (需要安装: requests beautifulsoup4)
# 用法: python crawler.py https://example.com --max 100 --delay 1.0

import argparse
import os
import time
import hashlib
import requests
from bs4 import BeautifulSoup
from collections import deque
from urllib.parse import urljoin, urlparse
import urllib.robotparser

HEADERS = {"User-Agent": "SimpleCrawler/1.0 (+https://example.com)"}

def get_robots_parser(root_url):
    parsed = urlparse(root_url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
    except Exception:
        # 如果读取失败，返回允许所有的假parser
        rp = None
    return rp

def is_allowed(rp, url):
    if rp is None:
        return True
    return rp.can_fetch(HEADERS["User-Agent"], url)

def safe_filename(url):
    h = hashlib.sha1(url.encode("utf-8")).hexdigest()
    parsed = urlparse(url)
    name = parsed.path.rstrip("/").split("/")[-1] or "index"
    name = "".join(c for c in name if c.isalnum() or c in ("-", "_"))
    return f"{name}_{h}.html"

def extract_links(base_url, html):
    soup = BeautifulSoup(html, "html.parser")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # 规范化为绝对URL
        full = urljoin(base_url, href)
        parsed = urlparse(full)
        if parsed.scheme in ("http", "https"):
            # 去掉片段
            full = full.split("#")[0]
            links.add(full)
    return links

def crawl(start_url, max_pages=50, delay=1.0, output_dir="pages"):
    os.makedirs(output_dir, exist_ok=True)
    parsed_start = urlparse(start_url)
    root = f"{parsed_start.scheme}://{parsed_start.netloc}"
    rp = get_robots_parser(root)

    q = deque([start_url])
    visited = set()
    count = 0

    while q and count < max_pages:
        url = q.popleft()
        if url in visited:
            continue
        if not is_allowed(rp, url):
            # 跳过 robots.txt 不允许的 URL
            continue
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            time.sleep(delay)
        except Exception:
            continue
        if resp.status_code != 200 or "text/html" not in resp.headers.get("Content-Type", ""):
            visited.add(url)
            continue

        # 保存页面
        fname = safe_filename(url)
        path = os.path.join(output_dir, fname)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(resp.text)
        except Exception:
            pass

        visited.add(url)
        count += 1

        # 只跟随同一站点的链接
        links = extract_links(url, resp.text)
        for link in links:
            if urlparse(link).netloc == parsed_start.netloc and link not in visited:
                q.append(link)

    return visited

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="简单爬虫")
    parser.add_argument("start_url", help="起始 URL")
    parser.add_argument("--max", type=int, default=50, help="最多抓取页面数")
    parser.add_argument("--delay", type=float, default=1.0, help="请求间隔秒数")
    parser.add_argument("--out", default="pages", help="保存目录")
    args = parser.parse_args()

    visited = crawl(args.start_url, max_pages=args.max, delay=args.delay, output_dir=args.out)
    print(f"Crawled {len(visited)} pages. Saved to {args.out}")