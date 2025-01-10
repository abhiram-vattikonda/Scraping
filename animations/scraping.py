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
    last_movie_index = 0
    iteration = 0
    wait = WebDriverWait(driver, 10)
    short_wait = WebDriverWait(driver, 5)

    while len(movies) != count:
        if iteration > (count / 50) + 1:
            raise RuntimeError("too many iterations")

        displayed_movies = wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//li[contains(@class, 'ipc-metadata-list-summary-item')]")))

        for i in range(last_movie_index, len(displayed_movies)):
            el = wait.until(EC.visibility_of_element_located((By.XPATH, f"(//li[contains(@class, 'ipc-metadata-list-summary-item')])[{i}]")))
            pass

        last_movie_index = len(movies)
        if last_movie_index != count:
            try:
                showmore = wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(@class, 'ipc-see-more__button')]")))
                driver.execute_script("arguments[0].click();", showmore)
                

        iteration += 1

    print(last_movie_index)
    print("--- %s seconds ---" % (time.time() - start_time))
    


if __name__ == "__main__":
    main()