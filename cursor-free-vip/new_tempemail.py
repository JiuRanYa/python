from DrissionPage import ChromiumPage, ChromiumOptions
import time
import os
import sys
from colorama import Fore, Style, init

# 初始化 colorama
init()

class NewTempEmail:
    def __init__(self, translator=None):
        self.translator = translator
        self.page = None
        self.setup_browser()
        
    def get_extension_block(self):
        """获取插件路径"""
        root_dir = os.getcwd()
        extension_path = os.path.join(root_dir, "PBlock")
        
        if hasattr(sys, "_MEIPASS"):
            extension_path = os.path.join(sys._MEIPASS, "PBlock")

        if not os.path.exists(extension_path):
            raise FileNotFoundError(f"插件不存在: {extension_path}")

        return extension_path
        
    def setup_browser(self):
        """设置浏览器"""
        try:
            if self.translator:
                print(f"{Fore.CYAN}ℹ️ {self.translator.get('email.starting_browser')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}ℹ️ 正在启动浏览器...{Style.RESET_ALL}")
            
            # 创建浏览器选项
            co = ChromiumOptions()
            co.set_argument("--headless=new")
            
            co.auto_port()  # 自动设置端口
            
            # 加载 uBlock 插件
            try:
                extension_path = self.get_extension_block()
                co.set_argument("--allow-extensions-in-incognito")
                co.add_extension(extension_path)
            except Exception as e:
                if self.translator:
                    print(f"{Fore.YELLOW}⚠️ {self.translator.get('email.extension_load_error')}: {str(e)}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}⚠️ 加载插件失败: {str(e)}{Style.RESET_ALL}")
            
            self.page = ChromiumPage(co)
            return True
        except Exception as e:
            if self.translator:
                print(f"{Fore.RED}❌ {self.translator.get('email.browser_start_error')}: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ 启动浏览器失败: {str(e)}{Style.RESET_ALL}")
            return False
            
    def create_email(self):
        """创建临时邮箱"""
        try:
            if self.translator:
                print(f"{Fore.CYAN}ℹ️ {self.translator.get('email.visiting_site')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}ℹ️ 正在访问 smailpro.com...{Style.RESET_ALL}")
            
            # 访问网站
            self.page.get("https://smailpro.com/")
            time.sleep(2)
            
            # 点击创建邮箱按钮
            create_button = self.page.ele('xpath://button[@title="Create temporary email"]')
            if create_button:
                create_button.click()
                time.sleep(1)
                
                # 点击弹窗中的 Create 按钮
                modal_create_button = self.page.ele('xpath://button[contains(text(), "Create")]')
                if modal_create_button:
                    modal_create_button.click()
                    time.sleep(2)
                    
                    # 获取邮箱地址 - 修改选择器
                    email_div = self.page.ele('xpath://div[@class="text-base sm:text-lg md:text-xl text-gray-700"]')
                    if email_div:
                        email = email_div.text.strip()
                        if '@' in email:  # 验证是否是有效的邮箱地址
                            if self.translator:
                                print(f"{Fore.GREEN}✅ {self.translator.get('email.create_success')}: {email}{Style.RESET_ALL}")
                            else:
                                print(f"{Fore.GREEN}✅ 创建邮箱成功: {email}{Style.RESET_ALL}")
                            return email
            if self.translator:
                print(f"{Fore.RED}❌ {self.translator.get('email.create_failed')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ 创建邮箱失败{Style.RESET_ALL}")
            return None
            
        except Exception as e:
            if self.translator:
                print(f"{Fore.RED}❌ {self.translator.get('email.create_error')}: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ 创建邮箱出错: {str(e)}{Style.RESET_ALL}")
            return None
            
    def close(self):
        """关闭浏览器"""
        if self.page:
            self.page.quit()

    def refresh_inbox(self):
        """刷新邮箱"""
        try:
            if self.translator:
                print(f"{Fore.CYAN}🔄 {self.translator.get('email.refreshing')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.CYAN}🔄 正在刷新邮箱...{Style.RESET_ALL}")
            
            # 点击刷新按钮
            refresh_button = self.page.ele('xpath://button[@id="refresh"]')
            if refresh_button:
                refresh_button.click()
                time.sleep(2)  # 等待刷新完成
                if self.translator:
                    print(f"{Fore.GREEN}✅ {self.translator.get('email.refresh_success')}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}✅ 邮箱刷新成功{Style.RESET_ALL}")
                return True
            
            if self.translator:
                print(f"{Fore.RED}❌ {self.translator.get('email.refresh_button_not_found')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ 未找到刷新按钮{Style.RESET_ALL}")
            return False
            
        except Exception as e:
            if self.translator:
                print(f"{Fore.RED}❌ {self.translator.get('email.refresh_error')}: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ 刷新邮箱出错: {str(e)}{Style.RESET_ALL}")
            return False

    def check_for_cursor_email(self):
        """检查是否有 Cursor 的验证邮件"""
        try:
            # 查找验证邮件 - 使用更精确的选择器
            email_div = self.page.ele('xpath://div[contains(@class, "p-2") and contains(@class, "cursor-pointer") and contains(@class, "bg-white") and contains(@class, "shadow") and .//b[text()="no-reply@cursor.sh"] and .//span[text()="Verify your email address"]]')
            if email_div:
                if self.translator:
                    print(f"{Fore.GREEN}✅ {self.translator.get('email.verification_found')}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}✅ 找到验证邮件{Style.RESET_ALL}")
                # 使用 JavaScript 点击元素
                self.page.run_js('arguments[0].click()', email_div)
                time.sleep(2)  # 等待邮件内容加载
                return True
            if self.translator:
                print(f"{Fore.YELLOW}⚠️ {self.translator.get('email.verification_not_found')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️ 未找到验证邮件{Style.RESET_ALL}")
            return False
            
        except Exception as e:
            if self.translator:
                print(f"{Fore.RED}❌ {self.translator.get('email.verification_error')}: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ 检查验证邮件出错: {str(e)}{Style.RESET_ALL}")
            return False

    def get_verification_code(self):
        """获取验证码"""
        try:
            # 查找验证码元素
            code_element = self.page.ele('xpath://td//div[contains(@style, "font-size:28px") and contains(@style, "letter-spacing:2px")]')
            if code_element:
                code = code_element.text.strip()
                if code.isdigit() and len(code) == 6:
                    if self.translator:
                        print(f"{Fore.GREEN}✅ {self.translator.get('email.verification_code_found')}: {code}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.GREEN}✅ 获取验证码成功: {code}{Style.RESET_ALL}")
                    return code
            if self.translator:
                print(f"{Fore.YELLOW}⚠️ {self.translator.get('email.verification_code_not_found')}{Style.RESET_ALL}")
            else:
                print(f"{Fore.YELLOW}⚠️ 未找到有效的验证码{Style.RESET_ALL}")
            return None
            
        except Exception as e:
            if self.translator:
                print(f"{Fore.RED}❌ {self.translator.get('email.verification_code_error')}: {str(e)}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ 获取验证码出错: {str(e)}{Style.RESET_ALL}")
            return None

def main(translator=None):
    temp_email = NewTempEmail(translator)
    
    try:
        email = temp_email.create_email()
        if email:
            if translator:
                print(f"\n{Fore.CYAN}📧 {translator.get('email.address')}: {email}{Style.RESET_ALL}")
            else:
                print(f"\n{Fore.CYAN}📧 临时邮箱地址: {email}{Style.RESET_ALL}")
            
            # 测试刷新功能
            while True:
                if translator:
                    choice = input(f"\n{translator.get('email.refresh_prompt')}: ").lower()
                else:
                    choice = input("\n按 R 刷新邮箱，按 Q 退出: ").lower()
                if choice == 'r':
                    temp_email.refresh_inbox()
                elif choice == 'q':
                    break
                    
    finally:
        temp_email.close()

if __name__ == "__main__":
    main() 