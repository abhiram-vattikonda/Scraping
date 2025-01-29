import requests, time, os
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import google.generativeai as genai
from dotenv import load_dotenv

def configure():
    load_dotenv()

def main():
    start_time = time.time()
    configure()

    URL = input("Enter your youtube URL: ")
    driver = webdriver.Chrome()
    driver.get(URL)
    wait = WebDriverWait(driver, 10)
    dsi = wait.until(EC.element_to_be_clickable((By.ID, 'expand')))
    driver.execute_script("arguments[0].click();", dsi)
    page = wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(@aria-label, 'Show transcript')]")))
    driver.execute_script("arguments[0].click();", page)
    s = wait.until(EC.presence_of_element_located((By.XPATH, f"//yt-formatted-string[contains(@class, 'segment-text style-scope ytd-transcript-segment-renderer')]")))
    html = driver.page_source
    driver.close()

    soup = bs(html, "html.parser")
    data = soup.find_all('yt-formatted-string', attrs= {'class' : 'segment-text style-scope ytd-transcript-segment-renderer'})
    
    para = ""
    for x in data:
        para += " " + x.text

    #print(para)
    print()

    genai.configure(api_key=os.getenv('api_key'))
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("Here is the transcription of a youtube video, I need you to give me detailed summary of this paragraph:\n" + para)

    with open("youtube-summary.md", 'w') as file:
        file.writelines(response.text)
    print(response.text)
    print("--- %s seconds ---" % (time.time() - start_time))


if __name__ == "__main__":
    main()