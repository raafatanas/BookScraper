def intialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options)
    return driver

# Gets category urls from given homepage url
def get_travel_and_nonfiction_category_urls(driver, url):
    driver.get(url)
    time.sleep(SLEEP_TIME)
    
    category_elements_xpath = "//a[contains(text(), 'Travel') or contains(text(), 'Nonfiction')]"
    category_elements = driver.find_elements(By.XPATH, category_elements_xpath)
    category_urls = [element.get_attribute("href") for element in category_elements]
    
    return category_urls

# Gets book urls from given category detail page url
def get_book_urls(driver, url):
    MAX_PAGINATION = 3
    
    book_urls = []
    book_elements_xpath = "//div[@class='image_container']/a"
    
    for i in range(1, MAX_PAGINATION):
        updated_url = url if i == 1 else url.replace("index", f"page-{i}")
        driver.get(updated_url)
        time.sleep(SLEEP_TIME)
        book_elements = driver.find_elements(By.XPATH, book_elements_xpath)
        
        # Controller of pagination
        if not book_elements:
            break
        temp_urls = [element.get_attribute("href") for element in book_elements]
        book_urls.extend(temp_urls)
        
    return book_urls
    
# Gets book data from given book detail page url    
def get_book_detail(driver, url):
    driver.get(url)
    time.sleep(SLEEP_TIME)
    
    content_div = driver.find_elements(By.XPATH, "//div[@class='content']")
    
    inner_html = content_div[0].get_attribute("innerHTML")
    
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(inner_html, "html.parser")

    name_elem = soup.find("h1")
    book_name = name_elem.text
    print(book_name)

    price_elem = soup.find("p", attrs={"class":"price_color"})
    book_price = price_elem.text
    print(book_price)
    import re #regex
    regex = re.compile('^star-rating ')
    star_elem = soup.find("p", attrs={"class":regex})
    book_star_count = star_elem["class"][-1]
    print(book_star_count)
    desc_elem = soup.find("div", attrs={"id":"product_description"}).find_next_sibling()
    book_desc = desc_elem.text
    print(book_desc)

    product_info = {}
    table_rows = soup.find("table").find_all("tr")
    for row in table_rows:
        key = row.find("th").text
        value = row.find("td").text
        product_info[key] = value 
        
    return {'book_name': book_name, 'book_price': book_price, 'book_star_count': book_star_count, 'book_desc': book_desc, **product_info}

import time
from selenium import webdriver
from selenium.webdriver.common.by import By

SLEEP_TIME = 0.25

def main():
    BASE_URL = "https://books.toscrape.com/"
    driver = intialize_driver()
    category_urls = get_travel_and_nonfiction_category_urls(driver, BASE_URL)
    
    data = []
    for cat_url in category_urls:
        book_urls = get_book_urls(driver, cat_url)
        for book_url in book_urls:
            book_data = get_book_detail(driver, book_url)
            book_data["cat_url"] = cat_url
            data.append(book_data)
    
    len(data)
    
    import pandas as pd
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', 40)
    pd.set_option('display.width', 2000)
    df = pd.DataFrame(data)
    df.to_excel("books_data.xlsx", index=False)
    return df

df = main()
print(df.head())
print(df.shape)