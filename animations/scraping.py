from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup as bs
import time, requests, re

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"

def getMovies(driver, count):
    movies = {}
    last_movie_index = 0
    iteration = 0
    wait = WebDriverWait(driver, 10)

    while len(movies) != count:
        if iteration > (count / 50) + 1:
            raise RuntimeError("too many iterations")

        displayed_movies = wait.until(EC.visibility_of_all_elements_located((By.XPATH, "//li[contains(@class, 'ipc-metadata-list-summary-item')]")))

        for i in range(last_movie_index, len(displayed_movies)):
            el = wait.until(EC.visibility_of_element_located((By.XPATH, f"(//li[contains(@class, 'ipc-metadata-list-summary-item')])[{i+1}]")))
        
            name = el.find_element(By.XPATH, './/h3').text.split(". ")[1]
            link = el.find_element(By.XPATH, ".//a").get_attribute("href")
            movies.update({link : name})
            print("Collected:", name,len(movies))

        last_movie_index = len(movies)
        if last_movie_index != count:
            try:
                showmore = wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(@class, 'ipc-see-more__button')]")))
                driver.execute_script("arguments[0].click();", showmore)
                wait.until(EC.invisibility_of_element_located((By.XPATH, f"//button[contains(@class, 'ipc-see-more__button') and @disabled]")))
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            except TimeoutError:
                pass

        iteration += 1

    print(last_movie_index)

    with open("animation.txt", "w") as file:
        for link in movies:
            file.write(f"{movies[link]} : {link}\n")



def awards(driver : webdriver.Chrome, movies :dict):
    """wait = WebDriverWait(driver, 10)
    animation_companies = {}
    for link in movies:
        driver.get(link)
        driver.implicitly_wait(10)
        try:
            awards_info = wait.until(EC.visibility_of_element_located((By.XPATH, f"//li[contains(@data-testid, 'award_information')]")))
            awards_summary = awards_info.find_element(By.XPATH, f".//span").text
            awards_lable = awards_info.find_element(By.XPATH, f".//a[contains(@aria-label, 'See more awards and nominations')]").text
            print(awards_lable, awards_summary)
            if ("win" in awards_summary):
                print(awards_lable, awards_summary, "*************")
        except TimeoutError:
            pass"""
    
    headers = {"user-agent": USER_AGENT}
    for link in movies:
        url_content = requests.get(link, headers=headers)
        soup = bs(url_content.content, "html.parser")
        try:
            awards_lable = soup.find('a', attrs={'aria-label':'See more awards and nominations'}).text
        except AttributeError:
            pass

        if "Won" in awards_lable:
            print(movies[link])



def main():
    start_time = time.time()
    driver = webdriver.Chrome()
    driver.get("https://www.imdb.com/search/title/?title_type=feature&genres=animation&countries=US&languages=en")
    driver.implicitly_wait(10)
    count =  int(driver.find_element(by=By.CSS_SELECTOR, value=".sc-285b550-3.cgeYTn").text.split()[2].replace(",", ""))
    

    movies = {}
    try:
        with open("animation.txt",'r') as file:
            for line in file:
                movies.update({line.split(" : ")[1] : line.split(" : ")[0]})

        if len(movies) != count:
            getMovies(driver, count)
            print("Tried again")

    except FileNotFoundError:
        getMovies(driver, count)

    driver.quit()
    awards(driver, movies)
    print("--- %s seconds ---" % (time.time() - start_time))

    


if __name__ == "__main__":
    main()