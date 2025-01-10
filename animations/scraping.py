from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import time



def main():
    start_time = time.time()
    driver = webdriver.Chrome()
    driver.get("https://www.imdb.com/search/title/?title_type=feature&genres=animation&countries=US&languages=en")
    driver.implicitly_wait(10)
    count =  int(driver.find_element(by=By.CSS_SELECTOR, value=".sc-13add9d7-3.fwjHEn").text.split()[2].replace(",", ""))
    
    movies = []
    iteration = 0
    wait = WebDriverWait(driver, 10)
    short_wait = WebDriverWait(driver, 5)

    while len(movies) != count:
        if iteration > (count / 50) + 1:
            raise RuntimeError("too many iterations")

        displayed_movies = wait.

        pass


    print("--- %s seconds ---" % (time.time() - start_time))
    


if __name__ == "__main__":
    main()