from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

def scrape_with_js(url):
    # Cấu hình Chrome
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # Khởi tạo driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        print(f"Đang truy cập: {url}")
        driver.get(url)
        
        # Đợi trang load
        time.sleep(5)
        
        # Lấy HTML
        html = driver.page_source
        
        # Kiểm tra xem có bị chặn không
        if "Enable JavaScript and cookies to continue" in html:
            print("⚠️ Vẫn bị chặn! Thử tăng thời gian chờ hoặc kiểm tra cookies")
            return None
        
        # Parse với BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        return soup
        
    finally:
        driver.quit()

if __name__ == "__main__":
  # Sử dụng
  for i in range(1, 10):
      url = 'https://luatvietnam.vn/van-ban-luat-viet-nam.html?pSize=50&page=' + str(i)
      soup = scrape_with_js(url)

      if soup:
        # Lấy dữ liệu bạn cần
        doc_titles = soup.find_all(class_='doc-title')
            
        # Lấy tất cả thẻ <a> bên trong
        all_links = []
        for doc_title in doc_titles:
            link = doc_title.find('a')
            if link:
                all_links.append(link)
        
        # In kết quả
        print(f"Tìm thấy {len(all_links)} link(s):\n")
        for i, link in enumerate(all_links, 1):
            href = link.get('href', 'N/A')
            with open('link.txt', 'a', encoding='utf-8') as f:
              f.write(href + '\n')
      time.sleep(10)
      