import requests
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import csv

def get_actual_url(soup, card):
    try:
        # 在当前卡片中查找带有 rel="dofollow" 的链接
        dofollow_link = card.find('a', attrs={'rel': 'dofollow'})
        if dofollow_link and 'href' in dofollow_link.attrs:
            return dofollow_link['href'].split('?')[0]  # 移除 utm 参数
    except Exception as e:
        print(f"Error getting actual URL: {e}")
    return None

def save_to_csv(tools):
    # 准备CSV文件
    with open('result.csv', 'w', encoding='utf-8', newline='') as f:
        # 定义CSV表头
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)  # 对所有字段使用引号
        writer.writerow(['title', 'description', 'url', 'tags'])
        
        # 写入数据
        for item in tools:
            # 将tags列表转换为字符串，使用分号分隔
            tags_str = ';'.join(item['tags'])
            writer.writerow([
                item['title'],
                item['description'],
                item['url'],
                tags_str
            ])

def scrape_toolify_ai():
    # 设置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    try:
        # 使用Selenium打开页面
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.toolify.ai/")
        
        # 模拟滚动到底部
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            # 滚动到底部
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # 等待加载
            time.sleep(2)
            
            # 计算新的滚动高度并与上一个滚动高度进行比较
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # 获取页面源代码
        page_source = driver.page_source
        
        # 使用BeautifulSoup解析页面
        soup = BeautifulSoup(page_source, 'html.parser')
        tools = []
        tool_cards = soup.select('.tool-item')
        
        for card in tool_cards:
            title = card.select_one('.text-xl').get_text(strip=True) if card.select_one('.text-xl') else "N/A"
            description = card.select_one('.tool-desc').get_text(strip=True) if card.select_one('.tool-desc') else "N/A"
            tags = [tag.get_text(strip=True) for tag in card.select('.t-label')]
            # 在当前卡片中查找dofollow链接
            url = get_actual_url(soup, card)
            
            # 只有当有URL时才添加到列表中
            if url:
                tools.append({
                    "title": title,
                    "description": description,
                    "url": url,
                    "tags": tags
                })
        
        driver.quit()
        return tools
        
    except Exception as e:
        print(f"Error scraping Toolify.ai: {e}")
        if 'driver' in locals():
            driver.quit()
        return []

if __name__ == "__main__":
    latest_tools = scrape_toolify_ai()
    # 将结果写入JSON文件
    with open('result.json', 'w', encoding='utf-8') as f:
        json.dump(latest_tools, f, ensure_ascii=False, indent=2)
    print(f"已成功将{len(latest_tools)}个工具的信息保存到 result.json")
    
    # 自动转换为CSV
    save_to_csv(latest_tools)
    print(f"已成功将{len(latest_tools)}条数据转换为CSV格式")
