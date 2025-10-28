from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import random
import os
import requests
def scrape_with_js(url):
    # Cấu hình Chrome với randomization
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # Random user agents
    user_agents = [
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
    ]

    # Random window size
    window_sizes = ['1920,1080', '1366,768', '1440,900', '1536,864', '1280,720']

    options.add_argument(f'user-agent={random.choice(user_agents)}')
    options.add_argument(f'--window-size={random.choice(window_sizes)}')

    # Random viewport
    viewports = ['1920,1080', '1366,768', '1440,900', '1536,864']
    options.add_argument(f'--viewport-size={random.choice(viewports)}')
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
def download_pdf(pdf_url, output_path):
    """Download PDF from URL and save to specified path"""
    try:
        # Create directory if it doesn't exist - Windows compatible
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Enhanced headers with more realistic browser behavior
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://luatvietnam.vn/',
            'Origin': 'https://luatvietnam.vn',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"'
        }
        
        print(f"Downloading PDF from: {pdf_url}")
        
        # Create a session to maintain cookies
        session = requests.Session()
        session.headers.update(headers)
        
        # Add delay to mimic human behavior
        time.sleep(random.uniform(1, 3))
        
        # First, try to get the page (for .aspx files)
        response = session.get(pdf_url, stream=True, timeout=30, allow_redirects=True)
        response.raise_for_status()
                
        # Check if the response is actually a PDF
        content_type = response.headers.get('content-type', '').lower()
        
        if 'application/pdf' in content_type:
            # It's a PDF, download it
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"✅ Downloaded: {output_path}")
            return True
        else:
            # It might be an HTML page with a PDF viewer
            print(f"⚠️ Response is not a PDF (content-type: {content_type})")
            # Save the response to check what we got
            debug_path = output_path.replace('.pdf', '_debug.html')
            with open(debug_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"📄 Saved response to {debug_path} for debugging")
            return False
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request error downloading {pdf_url}: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Error downloading {pdf_url}: {str(e)}")
        return False
def download_pdf_with_selenium(pdf_url, output_path):
    """Download PDF using Selenium for sites that require JS execution"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Set download preferences
    prefs = {
        "download.default_directory": os.path.abspath(os.path.dirname(output_path)),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.always_open_pdf_externally": True
    }
    options.add_experimental_option("prefs", prefs)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        print(f"Accessing PDF with Selenium: {pdf_url}")
        driver.get(pdf_url)
        time.sleep(10)  # Wait for download to complete
        
        # Check if file was downloaded
        if os.path.exists(output_path):
            print(f"✅ Downloaded with Selenium: {output_path}")
            return True
        else:
            print(f"❌ File not found after Selenium download: {output_path}")
            return False
            
    except Exception as e:
        print(f"❌ Selenium download error: {str(e)}")
        return False
    finally:
        driver.quit()


if __name__ == "__main__":
  # Read existing links from link_get.txt to avoid duplicates
  existing_links = set()
  try:
      with open('link_used.txt', 'r', encoding='utf-8') as f:
          existing_links = set(line.strip() for line in f)
  except FileNotFoundError:
      pass  # File doesn't exist yet, continue with empty set
  links = []
  with open('link.txt', 'r', encoding='utf-8') as f:
    for line in f:
      link = line.strip()
      if link not in existing_links:
          links.append(link)
  # Sử dụng
  for link in links:
      url = 'https://luatvietnam.vn' + link
      soup = scrape_with_js(url)
      with open('link_used.txt', 'a', encoding='utf-8') as f:
              f.write(link + '\n')
      if soup:
        embedContent2 = soup.find_all(class_='embedContent2')
        print(f"Tìm thấy {len(embedContent2)} PDF link(s) trong {url}:\n")
        for item in embedContent2: 
          iframe = item.find('iframe')
          if iframe:
            pdf_link = iframe.get('src', 'N/A')
            print(f"PDF Link: {pdf_link}\n")
            with open('link_get.txt', 'a', encoding='utf-8') as f:
              f.write(pdf_link + '\n')
            outpath = 'file/' + (pdf_link.split('/')[-1]).split('.')[0] + '.pdf'
            # Download the PDF file
            if pdf_link != 'N/A':
              success = download_pdf(pdf_link, outpath)        
              # If failed, try with Selenium
              if not success:
                  print("Trying with Selenium...")
                  download_pdf_with_selenium(pdf_link, outpath)
            print('-------------------------\n')

      time.sleep(random.randint(15, 30))
      