# -*- coding: utf-8 -*-
"""
Created on Thu Oct  2 12:35:48 2025

@author: titou
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
from bs4 import BeautifulSoup
import os

# ---------------- USER SETTINGS ----------------
LOGIN_URL = "https://live.netsens.it/login.php"
USERNAME = "provvidenza.durso@unict.it"
PASSWORD = "Stazionimeteo2023@"
DATA_DIR = "data_meteo_station"
os.makedirs(DATA_DIR, exist_ok=True)
HEADLESS = False
OUTPUT_HTML = "measures_page.html"
EXPORT_COOKIES = "cookies.json"
# ------------------------------------------------

def make_driver(headless=False):
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("start-maximized")
    if headless:
        options.add_argument("--headless=new")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def robust_set_input(driver, element, value):
    try:
        element.click()
    except Exception:
        pass
    element.clear()
    element.send_keys(value)
    events = ["focus", "keydown", "keypress", "input", "keyup", "change", "blur"]
    for ev in events:
        try:
            driver.execute_script(
                "arguments[0].dispatchEvent(new Event(arguments[1], {bubbles:true}));",
                element, ev
            )
        except Exception:
            pass

def read_current_table(html):
    soup = BeautifulSoup(html, "html.parser")
    table_bloc = soup.find("div", id="obs_div")
    rows = table_bloc.find_all("tr")
    data_list = []
    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) == 5:
            data_list.append([col.get_text(strip=True) for col in cols])
    df = pd.DataFrame(data_list, columns=['Data', 'Postazione', 'Unità', 'Sensore', 'Misura'])
    df['Misura'] = pd.to_numeric(df['Misura'], errors='coerce')
    df['Data'] = pd.to_datetime(df['Data'], format="%d-%m-%Y %H:%M:%S", errors='coerce')
    return df

def scrape_all_pages(driver):
    full_df = pd.DataFrame()
    last_span = driver.find_element(By.XPATH, "//span[contains(@onclick,'set_measures_page')][last()]")
    last_page = int(last_span.text.strip())
    print("[*] Last page detected:", last_page)

    for p in range(1, last_page + 1):
        driver.execute_script(f"set_measures_page('{p}');")
        # Wait for table to have at least 1 row
        WebDriverWait(driver, 10).until(
            lambda d: len(d.find_element(By.ID, "obs_div").find_elements(By.TAG_NAME, "tr")) > 1
        )
        html = driver.page_source
        df_page = read_current_table(html)
        full_df = pd.concat([full_df, df_page], ignore_index=True)
        print(f"[+] Page {p} scraped, total rows:", len(full_df))

    return full_df

def wait_for_table_update(driver):
    WebDriverWait(driver, 10).until(
        lambda d: len(d.find_element(By.ID, "obs_div").find_elements(By.TAG_NAME, "tr")) > 1
    )

def main():
    driver = make_driver(headless=HEADLESS)
    wait = WebDriverWait(driver, 15)

    try:
        print("[*] Opening login page...")
        driver.get(LOGIN_URL)

        username_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
        print("[*] Username input found (id='username').")
        password_input = driver.find_element(By.ID, "password")

        print("[*] Filling username...")
        robust_set_input(driver, username_input, USERNAME)
        print("[*] Filling password...")
        robust_set_input(driver, password_input, PASSWORD)

        # Login button
        login_clicked = False
        try:
            btn = driver.find_element(By.ID, "mybtn")
            btn.click()
            login_clicked = True
        except Exception:
            candidates = [
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "//input[@type='submit']"),
                (By.XPATH, "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'login') or contains(., 'Accedi') or contains(., 'Sign in')]"),
                (By.CSS_SELECTOR, "button"),
            ]
            for by, sel in candidates:
                try:
                    el = driver.find_element(by, sel)
                    driver.execute_script("arguments[0].scrollIntoView(true);", el)
                    el.click()
                    login_clicked = True
                    print(f"[*] Clicked fallback button ({by}, {sel}).")
                    break
                except Exception:
                    continue

        if not login_clicked:
            form = username_input.find_element(By.XPATH, "./ancestor::form")
            driver.execute_script("arguments[0].submit();", form)
            login_clicked = True

        start_url = driver.current_url
        try:
            wait.until(EC.url_changes(start_url))
            print("[+] URL changed after login. Current URL:", driver.current_url)
        except TimeoutException:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.logout, nav, #div_page_1a")))
            print("[+] Found dashboard element - probably logged in. Current URL:", driver.current_url)

        # Click on "Misure" link
        misure_clicked = False
        for a in driver.find_elements(By.TAG_NAME, "a"):
            txt = (a.text or "").strip().lower()
            href = a.get_attribute("href") or ""
            if "misur" in txt or "misure" in href or "measures" in href or "measures" in txt:
                try:
                    a.click()
                    misure_clicked = True
                    break
                except Exception:
                    continue

        # Wait for initial table
        wait_for_table_update(driver)

        # Advanced options checkbox
        adv_checkbox = driver.find_element(By.ID, "data_advanced_options_checkbox")
        if not adv_checkbox.is_selected():
            adv_checkbox.click()
        wait_for_table_update(driver)
        print("[*] 'Opzioni avanzate' checkbox checked")
        
        # Récupération de tous les jours
        day_select_elem = driver.find_element(By.ID, "days_select")
        day_select = Select(day_select_elem)
        all_days = [opt.get_attribute("value") for opt in day_select.options]
        print("[*] Days found:", all_days)
        
        for day in all_days:
            print(f"[*] Processing day: {day}")
            
            # Rechercher le select à chaque jour pour éviter StaleElementReference
            day_select_elem = wait.until(EC.presence_of_element_located((By.ID, "days_select")))
            day_select = Select(day_select_elem)
            day_select.select_by_value(day)
            wait_for_table_update(driver)
            
            # First station
            gateway_select = Select(driver.find_element(By.ID, "gateway_select"))
            gateway_select.select_by_index(0)
            wait_for_table_update(driver)
            print("[*] First station selected")
    
            # Node select
            node_select = Select(driver.find_element(By.ID, "node_multiple_select"))
            node_select.deselect_all()
            node_select.select_by_visible_text("Sensore Integrato (64)")
            wait_for_table_update(driver)
            print("[*] 'Sensore Integrato (64)' selected")
    
            update_btn = driver.find_element(By.ID, "update_button")
            update_btn.click()
            wait_for_table_update(driver)
            print("[*] Clicked 'Aggiorna' button")
    
            df_measures_1 = scrape_all_pages(driver)
            print("[+] Total rows scraped Station 1:", len(df_measures_1))
    
            # Second station
            gateway_select = Select(driver.find_element(By.ID, "gateway_select"))
            gateway_select.select_by_index(1)
            wait_for_table_update(driver)
            print("[*] Second station selected")
    
            node_select = Select(driver.find_element(By.ID, "node_multiple_select"))
            node_select.deselect_all()
            node_select.select_by_visible_text("Sensore Integrato (64)")
            wait_for_table_update(driver)
            print("[*] 'Sensore Integrato (64)' selected")
    
            update_btn = driver.find_element(By.ID, "update_button")
            update_btn.click()
            wait_for_table_update(driver)
            print("[*] Clicked 'Aggiorna' button")
    
            df_measures_2 = scrape_all_pages(driver)
            print("[+] Total rows scraped Station 2:", len(df_measures_2))
    
            df_day = pd.concat([df_measures_1, df_measures_2], ignore_index=True)
            
            csv_path = os.path.join(DATA_DIR, f"data_raw/{day}.csv")
            df_day.to_csv(csv_path, index=False, sep=",", encoding="utf-8-sig")
            print(f"[+] Saved day {day} to {csv_path}")

    finally:
        if not HEADLESS:
            print("[*] Leaving browser open for manual inspection (close it when done).")
        else:
            driver.quit()
            print("[*] Driver closed (headless mode).")

    return 


if __name__ == "__main__":
    main()
    #df.to_csv("mesures_netsens.csv", index=False, sep=",", encoding="utf-8-sig")
