from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import time



def main():
    start_time = time.time()
    driver = webdriver.Chrome()
    driver.get("https://www.imdb.com/search/title/?title_type=feature&genres=animation&countries=US&languages=en")
    driver.implicitly_wait(10)
    count =  int(driver.find_element(by=By.CSS_SELECTOR, value=".sc-13add9d7-3.fwjHEn").text.split()[2].replace(",", ""))
    driver.implicitly_wait(10)
    buttons = driver.find_element(by=By.CLASS_NAME, value="ipc-see-more__text")
    click=driver.execute_script("arguments[0].click();",buttons)
   # while buttons.tag_name != "button":
    #    buttons = buttons.find_element(By.XPATH, "..")
    #buttons.click()

    print("--- %s seconds ---" % (time.time() - start_time))
    


if __name__ == "__main__":
    main()