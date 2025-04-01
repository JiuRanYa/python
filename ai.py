import requests
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import base64
from selenium.common.exceptions import TimeoutException, WebDriverException
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import threading
from PIL import Image
import io
import os
import uuid

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--start-maximized')
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    return webdriver.Chrome(options=chrome_options)

def compress_base64_image(base64_str, max_size_kb=500):
    try:
        # 解码base64字符串
        img_data = base64.b64decode(base64_str)
        img = Image.open(io.BytesIO(img_data))
        
        # 初始质量
        quality = 95
        output = io.BytesIO()
        
        # 压缩图片直到大小小于max_size_kb
        while True:
            output.seek(0)
            output.truncate()
            img.save(output, format='JPEG', quality=quality)
            size_kb = len(output.getvalue()) / 1024
            
            if size_kb <= max_size_kb or quality <= 5:
                break
                
            quality -= 5
        
        # 转换回base64
        compressed_base64 = base64.b64encode(output.getvalue()).decode('utf-8')
        return compressed_base64
    except Exception as e:
        print(f"Error compressing image: {e}")
        return base64_str

def save_progress(tools, filename='result.json'):
    try:
        # 如果文件存在，读取现有数据
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        else:
            existing_data = []
        
        # 更新数据
        existing_data.extend(tools)
        
        # 保存更新后的数据
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"Error saving progress: {e}")

def upload_image(base64_str):
    try:
        # 解码base64字符串
        img_data = base64.b64decode(base64_str)
        
        # 创建临时文件名
        temp_filename = f"temp_{uuid.uuid4()}.jpg"
        
        # 将图片数据写入临时文件
        with open(temp_filename, 'wb') as f:
            f.write(img_data)
        
        try:
            # 准备上传文件
            files = {
                'file': ('screenshot.jpg', open(temp_filename, 'rb'), 'image/jpeg')
            }
            
            # 发送POST请求
            response = requests.post('http://localhost:3000/api/upload', files=files)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'success' and result.get('data', {}).get('url'):
                    return result['data']['url']
                print(f"Invalid response format: {result}")
                return None
            else:
                print(f"Error uploading image: {response.status_code} - {response.text}")
                return None
                
        finally:
            # 关闭文件并删除临时文件
            files['file'][1].close()
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
                
    except Exception as e:
        print(f"Error in upload_image: {e}")
        return None

def get_screenshot_data(url, driver):
    try:
        # 访问URL
        driver.get(url)
        
        # 等待页面加载
        time.sleep(5)
        
        # 设置视窗大小为1920x1080
        driver.set_window_size(1920, 1080)
        
        # 使用JavaScript设置body高度为100vh
        driver.execute_script("""
            document.body.style.height = '100vh';
            document.body.style.overflow = 'hidden';
        """)
        
        # 获取截图并压缩
        screenshot = driver.get_screenshot_as_base64()
        compressed_screenshot = compress_base64_image(screenshot)
        
        # 上传图片并获取URL
        image_url = upload_image(compressed_screenshot)
        return image_url
        
    except TimeoutException:
        print(f"Timeout while loading URL: {url}")
    except WebDriverException as e:
        print(f"Error taking screenshot of {url}: {e}")
    except Exception as e:
        print(f"Unexpected error while processing {url}: {e}")
    return None

def process_urls(urls, tool_cards, max_workers=10):
    results = {}
    driver_queue = Queue()
    processed_count = 0
    total_count = len(urls)
    
    # 创建多个WebDriver实例
    for _ in range(max_workers):
        driver_queue.put(create_driver())
    
    def process_single_url(url, card):
        driver = driver_queue.get()
        try:
            title = card.select_one('.text-xl').get_text(strip=True) if card.select_one('.text-xl') else "N/A"
            description = card.select_one('.tool-desc').get_text(strip=True) if card.select_one('.tool-desc') else "N/A"
            tags = [tag.get_text(strip=True) for tag in card.select('.t-label')]
            
            screenshot_url = get_screenshot_data(url, driver)
            
            tool_data = {
                "title": title,
                "description": description,
                "url": url,
                "tags": tags,
                "image": screenshot_url
            }
            
            # 实时保存进度
            save_progress([tool_data])
            
            return url, tool_data
        finally:
            driver_queue.put(driver)
    
    # 使用线程池处理URLs
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 将URL和对应的card一起传递给处理函数
        future_to_url = {
            executor.submit(process_single_url, url, card): url 
            for url, card in zip(urls, [card for card in tool_cards if get_actual_url(None, card) in urls])
        }
        
        for future in as_completed(future_to_url):
            url, tool_data = future.result()
            results[url] = tool_data
            processed_count += 1
            print(f"Progress: {processed_count}/{total_count} ({(processed_count/total_count*100):.2f}%) - Completed: {tool_data['title']}")
    
    # 关闭所有WebDriver实例
    while not driver_queue.empty():
        driver = driver_queue.get()
        driver.quit()
    
    return results

def get_actual_url(soup, card):
    try:
        # 在当前卡片中查找带有 rel="dofollow" 的链接
        dofollow_link = card.find('a', attrs={'rel': 'dofollow'})
        if dofollow_link and 'href' in dofollow_link.attrs:
            return dofollow_link['href'].split('?')[0]  # 移除 utm 参数
    except Exception as e:
        print(f"Error getting actual URL: {e}")
    return None

def get_image_data(card):
    try:
        # 查找图片标签
        img_tag = card.find('img')
        if img_tag and 'src' in img_tag.attrs:
            img_url = img_tag['src']
            # 如果是相对路径，添加域名
            if img_url.startswith('/'):
                img_url = 'https://www.toolify.ai' + img_url
            
            # 下载图片
            response = requests.get(img_url)
            if response.status_code == 200:
                # 将图片转换为base64字符串
                img_base64 = base64.b64encode(response.content).decode('utf-8')
                return img_base64
    except Exception as e:
        print(f"Error getting image data: {e}")
    return None

def save_to_csv(tools):
    # 准备CSV文件
    with open('result.csv', 'w', encoding='utf-8', newline='') as f:
        # 定义CSV表头
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)  # 对所有字段使用引号
        writer.writerow(['title', 'description', 'url', 'tags', 'image'])
        
        # 写入数据
        for item in tools:
            # 将tags列表转换为JSON字符串，保持数组格式
            tags_str = json.dumps(item['tags'], ensure_ascii=False)
            writer.writerow([
                item['title'],
                item['description'],
                item['url'],
                tags_str,  # 使用JSON格式保存数组
                item['image']
            ])

def get_api_products():
    try:
        # 请求API获取所有产品
        response = requests.get('http://localhost:3001/api/products?pageSize=all')
        if response.status_code != 200:
            print(f"请求API失败: {response.status_code}")
            return None
            
        data = response.json()
        if data.get('status') != 'success' or 'data' not in data:
            print("API返回格式错误")
            return None
            
        return data['data']['items']
        
    except Exception as e:
        print(f"获取API产品数据时出错: {e}")
        return None

def scrape_toolify_ai():
    try:
        # 清除之前的结果文件
        if os.path.exists('result.json'):
            os.remove('result.json')
            

                # 首先获取API中的产品
        api_products = get_api_products()
        if api_products is None:
            print("获取API产品失败，退出程序")
            return []
            
        # 获取已存在的URL集合
        existing_urls = {item['url'] for item in api_products}
        print(f"API中已有 {len(existing_urls)} 个产品")

        # 使用Selenium打开页面
        driver = create_driver()
        driver.get("https://www.toolify.ai/")
        
        # 等待页面基本元素加载
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'tool-item')))
        
        # 模拟滚动到底部
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                time.sleep(3)
                break
            last_height = new_height

        # 获取页面源代码
        page_source = driver.page_source
        driver.quit()
        
        # 使用BeautifulSoup解析页面
        soup = BeautifulSoup(page_source, 'html.parser')
        tool_cards = soup.select('.tool-item')
        
        # 收集所有URL
        urls_to_process = []
        for card in tool_cards:
            url = get_actual_url(soup, card)
            if url not in existing_urls and url:
                print(f"发现新工具: {url}")
                urls_to_process.append(url)
        
        # 并发处理URLs
        print(f"Starting concurrent processing of {len(urls_to_process)} URLs...")
        results = process_urls(urls_to_process, tool_cards)
        
        return list(results.values())
        
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
