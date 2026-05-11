"""
通用网页爬虫 - 简单版
可爬取：豆瓣、天气、新闻等公开网站
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import random


def crawl_douban_movies(keyword="科幻", max_pages=3):
    """爬取豆瓣电影"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    movies = []
    for page in range(0, max_pages):
        url = f"https://search.douban.com/movie/subject_search?search_text={keyword}&start={page*15}"
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            items = soup.find_all('div', class_='item-root')
            
            for item in items:
                movie = {}
                
                title = item.find('span', class_='title-text')
                if title:
                    movie['标题'] = title.get_text(strip=True)
                
                rating = item.find('span', class_='rating_nums')
                if rating:
                    movie['评分'] = rating.get_text(strip=True)
                
                abstract = item.find('span', class_='abstract')
                if abstract:
                    movie['简介'] = abstract.get_text(strip=True)
                
                if movie.get('标题'):
                    movies.append(movie)
                    print(f"  - {movie['标题']} ({movie.get('评分', 'N/A')})")
            
            time.sleep(random.uniform(2, 4))
        except Exception as e:
            print(f"出错: {e}")
    
    return movies


def crawl_weather(city="北京"):
    """爬取天气信息"""
    url = f"https://www.tianqi.com/{city}/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        weather_data = {}
        
        temp = soup.find('span', class_='temp')
        if temp:
            weather_data['温度'] = temp.get_text(strip=True)
        
        desc = soup.find('dd', class_='weather')
        if desc:
            weather_data['天气'] = desc.get_text(strip=True)
        
        return weather_data
    except Exception as e:
        print(f"出错: {e}")
        return {}


def save_to_csv(data, filename):
    """保存到CSV文件"""
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"\n已保存到: {filename}")


if __name__ == "__main__":
    print("=" * 50)
    print("简易网页爬虫")
    print("=" * 50)
    
    # 示例1：爬取豆瓣电影
    print("\n【示例1】爬取豆瓣电影")
    movies = crawl_douban_movies("人工智能", max_pages=2)
    if movies:
        save_to_csv(movies, "movies.csv")
        print(f"共获取 {len(movies)} 部电影")
    
    # 示例2：获取天气
    print("\n【示例2】获取北京天气")
    weather = crawl_weather("北京")
    if weather:
        print(f"北京天气: {weather}")