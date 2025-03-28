import requests
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

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
        driver.quit()
        
        # 使用BeautifulSoup解析页面
        soup = BeautifulSoup(page_source, 'html.parser')
        tools = []
        tool_cards = soup.select('.tool-item')
        
        for card in tool_cards:
            title = card.select_one('.text-xl').get_text(strip=True) if card.select_one('.text-xl') else "N/A"
            description = card.select_one('.tool-desc').get_text(strip=True) if card.select_one('.tool-desc') else "N/A"
            url = card.select_one('a.go-tool-detail-name')['href'] if card.select_one('a.go-tool-detail-name') else "N/A"
            tags = [tag.get_text(strip=True) for tag in card.select('.t-label')]
            
            tools.append({
                "title": title,
                "description": description,
                "url": url,
                "tags": tags
            })
        
        return tools
        
    except Exception as e:
        print(f"Error scraping Toolify.ai: {e}")
        return []

if __name__ == "__main__":
    latest_tools = scrape_toolify_ai()
    # 将结果写入JSON文件
    with open('result.json', 'w', encoding='utf-8') as f:
        json.dump(latest_tools, f, ensure_ascii=False, indent=2)
    print(f"已成功将{len(latest_tools)}个工具的信息保存到 result.json")
