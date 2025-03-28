from colorama import Fore, Style, init
from dotenv import load_dotenv
import os

# 獲取當前腳本所在目錄
current_dir = os.path.dirname(os.path.abspath(__file__))
# 構建.env文件的完整路徑
env_path = os.path.join(current_dir, '.env')

# 加載環境變量，指定.env文件路徑
load_dotenv(env_path)
# 獲取版本號，如果未找到則使用默認值
version = os.getenv('VERSION', '1.0.0')

# 初始化 colorama
init()

CURSOR_LOGO = f"""
{Fore.CYAN}
   ██████╗██╗   ██╗██████╗ ███████╗ ██████╗ ██████╗      ██████╗ ██████╗  ██████╗   
  ██╔════╝██║   ██║██╔══██╗██╔════╝██╔═══██╗██╔══██╗     ██╔══██╗██╔══██╗██╔═══██╗  
  ██║     ██║   ██║██████╔╝███████╗██║   ██║██████╔╝     ██████╔╝██████╔╝██║   ██║  
  ██║     ██║   ██║██╔══██╗╚════██║██║   ██║██╔══██╗     ██╔═══╝ ██╔══██╗██║   ██║  
  ╚██████╗╚██████╔╝██║  ██║███████║╚██████╔╝██║  ██║     ██║     ██║  ██║╚██████╔╝  
   ╚═════╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝     ╚═╝     ╚═╝  ╚═╝ ╚═════╝  
{Fore.YELLOW}
                Pro Version Activator v{version}
{Fore.GREEN}
                Author: Pin Studios | yeongpin
{Fore.RED}
        Press 5 to change language | 按下 5 键切换语言
{Style.RESET_ALL}
    """

def print_logo():
    print(CURSOR_LOGO)

if __name__ == "__main__":
    print_logo()