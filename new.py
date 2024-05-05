import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import pandas as pd
import time
from bs4 import BeautifulSoup

# Define constants
ROW_LIMIT = 3000
SAVE_OUTPUT = True

# Define web driver options
chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--incognito')
# chrome_options.add_argument('--headless')

# Define path to Chrome driver
path = '/usr/bin/chromedriver'  # Replace with your actual path

# Webdriver initialization
driver = webdriver.Chrome(executable_path=path, options=chrome_options)

# Streamlit UI
st.title("CoinMarketCap Scraper")
st.write("This app scrapes data from CoinMarketCap.")

# Scraping data
if st.button("Scrape Data"):
    start = time.time()
    scroll_location = 0
    last_row = -1

    while int(last_row) <= ROW_LIMIT:
        scroll_location += 400
        driver.execute_script(f"window.scrollTo(0, {scroll_location});")
        time.sleep(0.1)
        soup = BeautifulSoup(driver.page_source, features='lxml')
        rows = soup.find_all(class_="cmc-table__cell cmc-table__cell--sticky cmc-table__cell--sortable cmc-table__cell--left cmc-table__cell--sort-by__rank")

        if rows and rows[-1].div.text == str(last_row):
            if int(rows[-1].div.text) >= ROW_LIMIT:
                break

            try:
                load_more_button = driver.find_element(By.CLASS_NAME, 'cmc-table-listing__loadmore')
                load_more_button.click()
                time.sleep(2.5)
            except NoSuchElementException:
                st.write("Load More button not found.")

        last_row = rows[-1].div.text
        st.write(last_row)

    dfs = pd.read_html(driver.page_source)
    driver.quit()
    st.write('Time elapsed for scrape:', time.time() - start)

    # Output
    output = dfs[2].iloc[:, :10].copy()
    if SAVE_OUTPUT:
        output.to_csv('coinmarketcap_market_data.csv', index=False)
        st.write('Saved to coinmarketcap_market_data.csv')

    try:
        import winsound
        winsound.Beep(frequency=2500, duration=1000)
    except ImportError:
        pass
