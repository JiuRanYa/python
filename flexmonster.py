import subprocess
import time
import webbrowser
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyperclip  # 用于复制到剪贴板

def create_flexmonster_project():
    print("🚀 开始检查 Flexmonster Vue 3 项目...")
    
    try:
        project_dir = "./flexmonster-vue-3-es6-project"
        
        # 检查项目是否已存在
        if os.path.exists(project_dir):
            print("✅ 项目已存在，直接启动...")
            os.chdir(project_dir)
        else:
            print("📦 创建新项目...")
            # 执行 flexmonster create 命令
            subprocess.run(["flexmonster", "create", "vue", "3", "es6", "-r"], check=True)
            print("✅ Flexmonster 项目创建成功！")
            
            # 进入项目目录
            os.chdir(project_dir)
            
            # 安装依赖
            print("📦 正在安装项目依赖...")
            subprocess.run(["npm", "install"], check=True)
        
        # 启动开发服务器
        print("🌐 正在启动开发服务器...")
        # 在后台启动 npm run dev
        server_process = subprocess.Popen(["npm", "run", "start"])
        
        # 等待服务器启动
        print("⏳ 等待服务器启动...")
        time.sleep(5)
        
        # 使用 Selenium 打开浏览器并点击元素
        print("🌎 正在打开浏览器并执行操作...")
        driver = webdriver.Chrome()  # 或使用其他浏览器驱动
        driver.get("http://localhost:5173")
        
        # 等待并点击元素
        wait = WebDriverWait(driver, 20)
        parent_element = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "fm-ui-element.fm-ui.fm-ui-label.fm-link"))
        )
        info_icon = parent_element.find_element(By.CLASS_NAME, "fm-ui-element.fm-info-icon")
        info_icon.click()
        
        # 等待弹出框加载并获取 License key
        time.sleep(2)  # 等待弹出框完全显示
        license_elements = driver.find_elements(By.CLASS_NAME, "fm-ui-element.fm-ui.fm-ui-label")
        license_key = None
        for element in license_elements:
            try:
                # 获取元素的HTML内容
                html_content = element.get_attribute('innerHTML')
                if "License key:" in html_content:
                    # 先按 <br> 分割
                    parts = html_content.split("<br>")
                    # 在第一部分中查找 License key
                    for part in parts:
                        if "License key:" in part:
                            license_key = part.split("License key:")[1].strip()
                            # 复制到剪贴板
                            pyperclip.copy(license_key)
                            print(f"\n🔑 License key 已复制到剪贴板: {license_key}")
                            break
                    if license_key:
                        break
            except Exception as e:
                print(f"处理元素时出错: {str(e)}")
                continue
        
        if not license_key:
            print("❌ 未找到 License key")
        
        print("\n✨ 项目已成功启动！")
        print("💡 按 Ctrl+C 停止服务器")
        
        # 保持脚本运行
        server_process.wait()
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 错误：命令执行失败：{str(e)}")
    except Exception as e:
        print(f"❌ 错误：{str(e)}")
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    create_flexmonster_project()
