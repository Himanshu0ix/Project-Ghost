import os
import sys
import ctypes
import random
import time
import winreg as reg
import requests
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# --- CONSTANTS ---
TEST_URL = 'http://httpbin.org/ip'
REQUEST_TIMEOUT = 5 # Seconds
INTERNET_OPTION_SETTINGS_CHANGED = 39
INTERNET_OPTION_REFRESH = 37

def check_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def setup_firefox_browser():
    ff_options = Options()
    ff_options.add_argument("--headless")
    service = Service(executable_path='geckodriver.exe')
    driver = webdriver.Firefox(service=service, options=ff_options)
    return driver

def get_proxies_with_firefox(driver):
    print("[INFO] Deploying Firefox browser for ammunition run...")
    try:
        url = "https://www.sslproxies.org/"
        driver.get(url)
        wait = WebDriverWait(driver, 20)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "table.table-striped")))
        print("[INFO] Supplier page loaded. Extracting raw proxy list...")
        soup = BeautifulSoup(driver.page_source, 'lxml')
        proxies = [f"{tds[0].text.strip()}:{tds[1].text.strip()}" for row in soup.find("table", class_="table-striped").find_all("tr")[1:] if len(tds := row.find_all("td")) > 6 and "yes" in tds[6].text]
        print(f"[SUCCESS] Harvested {len(proxies)} raw proxies.")
        return proxies
    except Exception as e:
        print(f"[FATAL] A critical error occurred while harvesting proxies: {e}")
        return []

def filter_initial_proxies(proxies):
    live_proxies = []
    print(f"\n[INFO] Starting initial validation of {len(proxies)} proxies. This will take a while...")
    for i, proxy in enumerate(proxies):
        print(f"    -> Testing proxy {i+1}/{len(proxies)}: {proxy}", end='\r')
        try:
            if requests.get(TEST_URL, proxies={"http": proxy, "https": proxy}, timeout=REQUEST_TIMEOUT).status_code == 200:
                live_proxies.append(proxy)
        except:
            continue
    print(f"\n[SUCCESS] Initial validation complete. Found {len(live_proxies)} potentially live proxies.")
    return live_proxies

def check_proxy_health(proxy):
    try:
        requests.get(TEST_URL, proxies={"http": proxy, "https": proxy}, timeout=REQUEST_TIMEOUT)
        return True
    except:
        return False

def set_system_proxy(proxy_address):
    print(f"[+] Engaging new identity: {proxy_address}")
    try:
        key_path = r'Software\Microsoft\Windows\CurrentVersion\Internet Settings'
        internet_settings_key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_WRITE)
        reg.SetValueEx(internet_settings_key, 'ProxyServer', 0, reg.REG_SZ, proxy_address)
        reg.SetValueEx(internet_settings_key, 'ProxyEnable', 0, reg.REG_DWORD, 1)
        reg.CloseKey(internet_settings_key)
        internet_set_option = ctypes.windll.Wininet.InternetSetOptionW
        internet_set_option(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
        internet_set_option(0, INTERNET_OPTION_REFRESH, 0, 0)
        print("[+] Proxy engaged. System notified. You are now a ghost.")
    except Exception as e:
        print(f"[ERROR] FAILED to set system proxy: {e}")

def disable_system_proxy():
    print("\n[!] Disengaging proxy. Returning to civilian identity...")
    try:
        key_path = r'Software\Microsoft\Windows\CurrentVersion\Internet Settings'
        internet_settings_key = reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_WRITE)
        reg.SetValueEx(internet_settings_key, 'ProxyEnable', 0, reg.REG_DWORD, 0)
        reg.CloseKey(internet_settings_key)
        internet_set_option = ctypes.windll.Wininet.InternetSetOptionW
        internet_set_option(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)
        internet_set_option(0, INTERNET_OPTION_REFRESH, 0, 0)
        print("[!] Proxy disengaged. System notified. You are exposed.")
    except Exception as e:
        print(f"[ERROR] FAILED to disable system proxy: {e}")

if __name__ == "__main__":
    if not check_admin():
        print("[FATAL] This script manipulates the Windows Registry. You must run it as an Administrator.")
        sys.exit(1)

    driver = setup_firefox_browser()
    raw_proxies = get_proxies_with_firefox(driver)
    driver.quit()

    if not raw_proxies:
        sys.exit("[FATAL] No proxies were harvested.")
    
    live_proxies = filter_initial_proxies(raw_proxies)

    if not live_proxies:
        sys.exit("[FATAL] After testing, no live proxies were found. Try again later.")

    try:
        interval = int(input("Enter the time interval in seconds to change IP: "))
    except ValueError:
        sys.exit("[FATAL] That's not a number, you idiot.")

    try:
        print("\n" + "="*50)
        print("Starting Apex Predator Rotator (System Override). Press Ctrl+C to stop.")
        print("="*50 + "\n")
        while True:
            if not live_proxies:
                print("[WARN] Ran out of live proxies! Restart to harvest more.")
                break
            
            chosen_proxy = random.choice(live_proxies)
            print(f"--> Pre-engagement check on {chosen_proxy}...")
            if check_proxy_health(chosen_proxy):
                set_system_proxy(chosen_proxy)
                print(f"    -> Waiting for {interval} seconds before changing identity...")
                time.sleep(interval)
            else:
                print(f"[!] PROXY DIED: {chosen_proxy} is offline. Discarding.")
                live_proxies.remove(chosen_proxy)
                continue
            
    except KeyboardInterrupt:
        print("\n[INFO] User interruption detected. Shutting down.")
    finally:
        disable_system_proxy()