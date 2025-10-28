import os
import time
import random
import requests
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


def scrape_with_js(url):
    options = Options()
    options.add_argument('--headless=new')  # Sử dụng headless mode mới
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-gpu')  # Quan trọng cho Ubuntu
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    user_agents = [
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/121.0',
    ]

    window_sizes = ['1920,1080', '1366,768', '1440,900']
    options.add_argument(f'user-agent={random.choice(user_agents)}')
    options.add_argument(f'--window-size={random.choice(window_sizes)}')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        print(f"Đang truy cập: {url}")
        driver.get(url)
        time.sleep(5)
        
        html = driver.page_source
        
        if "Enable JavaScript and cookies to continue" in html:
            print("⚠️ Vẫn bị chặn! Thử tăng thời gian chờ hoặc kiểm tra cookies")
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        return soup
        
    finally:
        driver.quit()


def download_pdf(pdf_url, output_path):
    """Download PDF from URL and save to specified path"""
    try:
        # Create directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/pdf,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Referer': 'https://luatvietnam.vn/',
        }
        
        print(f"Downloading PDF from: {pdf_url}")
        
        session = requests.Session()
        session.headers.update(headers)
        
        time.sleep(random.uniform(1, 3))
        
        response = session.get(pdf_url, stream=True, timeout=30, allow_redirects=True)
        response.raise_for_status()
        
        content_type = response.headers.get('content-type', '').lower()
        
        if 'application/pdf' in content_type or 'octet-stream' in content_type:
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Verify file was created and has content
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"✅ Downloaded: {output_path} ({os.path.getsize(output_path)} bytes)")
                return True
            else:
                print(f"❌ File created but empty or not found")
                return False
        else:
            print(f"⚠️ Response is not a PDF (content-type: {content_type})")
            return False
        
    except Exception as e:
        print(f"❌ Error downloading {pdf_url}: {str(e)}")
        return False


def download_pdf_with_selenium(pdf_url, output_path):
    """Download PDF using Selenium for sites that require JS execution"""
    
    # Create absolute path for download directory
    download_dir = os.path.abspath(os.path.dirname(output_path))
    os.makedirs(download_dir, exist_ok=True)
    
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-software-rasterizer')
    
    # Set download preferences
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False,  # Disable safe browsing
        "plugins.always_open_pdf_externally": True,
        "plugins.plugins_disabled": ["Chrome PDF Viewer"]
    }
    options.add_experimental_option("prefs", prefs)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        print(f"Accessing PDF with Selenium: {pdf_url}")
        driver.get(pdf_url)
        
        # Wait for download to start and complete
        time.sleep(5)
        
        # Check for downloaded file (may have different name)
        original_filename = pdf_url.split('/')[-1]
        if not original_filename.endswith('.pdf'):
            original_filename += '.pdf'
        
        temp_download_path = os.path.join(download_dir, original_filename)
        
        # Wait up to 30 seconds for download
        max_wait = 30
        waited = 0
        while waited < max_wait:
            # Check for .crdownload files (Chrome downloading)
            crdownload_files = [f for f in os.listdir(download_dir) if f.endswith('.crdownload')]
            
            if os.path.exists(temp_download_path) and os.path.getsize(temp_download_path) > 0:
                # Move file to desired location if different
                if temp_download_path != output_path:
                    os.rename(temp_download_path, output_path)
                print(f"✅ Downloaded with Selenium: {output_path} ({os.path.getsize(output_path)} bytes)")
                return True
            elif not crdownload_files and waited > 5:
                # No download in progress and we've waited a bit
                break
            
            time.sleep(1)
            waited += 1
        
        # Check if any PDF was downloaded in the directory
        pdf_files = [f for f in os.listdir(download_dir) if f.endswith('.pdf')]
        if pdf_files:
            # Use the most recently modified PDF
            pdf_files.sort(key=lambda x: os.path.getmtime(os.path.join(download_dir, x)), reverse=True)
            latest_pdf = os.path.join(download_dir, pdf_files[0])
            if latest_pdf != output_path:
                os.rename(latest_pdf, output_path)
            print(f"✅ Downloaded with Selenium: {output_path}")
            return True
        
        print(f"❌ File not found after Selenium download: {output_path}")
        return False
        
    except Exception as e:
        print(f"❌ Selenium download error: {str(e)}")
        return False
    finally:
        driver.quit()


if __name__ == "__main__":
    # Ensure directories exist
    os.makedirs('file', exist_ok=True)
    
    # Read existing links
    existing_links = set()
    try:
        with open('link_used.txt', 'r', encoding='utf-8') as f:
            existing_links = set(line.strip() for line in f)
    except FileNotFoundError:
        pass
    
    links = []
    with open('link.txt', 'r', encoding='utf-8') as f:
        for line in f:
            link = line.strip()
            if link and link not in existing_links:
                links.append(link)
    
    print(f"Found {len(links)} links to process")
    
    for link in links:
        url = 'https://luatvietnam.vn' + link
        soup = scrape_with_js(url)
        
        # Mark link as used
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
                    
                    if pdf_link != 'N/A':
                        # Save link
                        with open('link_get.txt', 'a', encoding='utf-8') as f:
                            f.write(pdf_link + '\n')
                        
                        # Generate output path
                        filename = pdf_link.split('/')[-1].split('.')[0]
                        outpath = os.path.join('file', f"{filename}.pdf")
                        
                        # Try downloading
                        success = download_pdf(pdf_link, outpath)
                        
                        # If failed, try with Selenium
                        if not success:
                            print("Trying with Selenium...")
                            download_pdf_with_selenium(pdf_link, outpath)
                        
                        print('-------------------------\n')
        
        # Random delay between requests
        time.sleep(random.randint(15, 30))