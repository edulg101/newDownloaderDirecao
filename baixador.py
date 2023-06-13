import os
import re
import undetected_chromedriver as uc
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC  # noqa
import time
import json
import ls
import requests
import pprint

def get_link_from_src(src_source:str)->str:
     sp = src_source.split('/')
     last = sp[-1]
     code = last.split('.')[0]
     return code

def pause():
     time.sleep(3600)

def get_cookies(driver:uc.Chrome)->str:
    storage = ls.LocalStorage(driver)
    data = storage["persist:@DirecaoConcursos"]
    data = data.replace('\\"', '"')
    data = data.replace('"{', '{')
    data = data.replace('}"', '}')
    cookies = json.loads(data)
    return cookies

def get_token(driver:uc.Chrome)->str:
    cookies = get_cookies(driver)
    return cookies['auth']['token']

def get_headers(driver:uc.Chrome)->str:
    token = get_token(driver)
    headers = {
        'authority': 'prod-api.direcaoconcursos.com.br',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'authorization': f'Bearer {token}',
        'content-type': 'application/json',
        'origin': 'https://aluno.direcaoconcursos.com.br',
        'referer': 'https://aluno.direcaoconcursos.com.br/',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    }
    return headers
     

def get_download_link_pdf(driver:uc.Chrome, request_link):
    
    headers = get_headers(driver)

    json_data = {
        'course': '63879f1818de1534665aab68',
        'module': '6387a3ad18de1534665b227e',
        'lesson': '637bd499db266a0b4afcecee',
    }

    response = requests.post(request_link, headers=headers, json=json_data)

    return response.text

def download_video(driver: uc.Chrome, link:str, file_path:str):
    
    headers = get_headers(driver)

    r = requests.get(link, headers=headers)

    with open(file_path, 'wb') as f:

            bytes = f.write(r.content)
            if bytes > 0:
                print(f'Arquivo path baixado com sucesso !')
     

def webDriverWaitByXpath(driver:uc.Chrome, xpath:str):
    try:
        WebDriverWait(driver, 4).until(
            EC.presence_of_all_elements_located(
                (By.XPATH, xpath))
        )
    except Exception as e:
            print("nao aceitou waitClass")
            print(e)

def close_boxtool(driver:uc.Chrome):
    try:
        webDriverWaitByXpath(driver, "//button[@class='closeButton']")
        time.sleep(1) 
        closeButton = driver.find_element(By.XPATH, "//button[@class='closeButton']") 
        closeButton.click()
    except Exception as ex:
        print(ex)
        print("não abriu tela. continuando")

def start():
   
    options = Options()
    options.add_experimental_option("safebrowsing", {"enabled": False})
    options.add_experimental_option(
        "excludeSwitches", ["disable-popup-blocking"])
    options.add_argument("--disable-popup-blocking")
    driver = uc.Chrome(chrome_options=options)
    driver.get("https://aluno.direcaoconcursos.com.br/")
    email = "jaxdevander@gmail.com"
    password = "At3P@ss@r"
    time.sleep(5)
    email_form = driver.find_element(By.XPATH, "//input[@placeholder='E-mail']")
    email_form.send_keys(email)
    pass_form = driver.find_element(By.XPATH, "//input[@placeholder='Senha']")
    pass_form.send_keys(password)
    driver.find_element(By.XPATH, "//button[contains(., 'Aceitar e sair')]").click()
    time.sleep(1)
    button = driver.find_element(By.XPATH, "//button[@type='submit']")
    button.submit()
    time.sleep(5)
    # TEST
    token = get_cookies(driver)
    # return token
    link = get_download_link_pdf(driver, "https://prod-api.direcaoconcursos.com.br/learning/content/lesson-pdf")
    print(link)
    

    course_temp= "https://aluno.direcaoconcursos.com.br/course/63879f1818de1534665aab68/module/6387a3ad18de1534665b227e/lesson/637bd499db266a0b4afcedd5/chapter/637bd499db266a0b4afcedb6"
    
    
    driver.get(course_temp)

    #ENDTEST

    r = requests.get(link)

    with open("path.pdf", 'wb') as f:

            bytes = f.write(r.content)
            if bytes > 0:
                print(f'Arquivo path baixado com sucesso !')


    close_boxtool(driver)

    download_video(driver, "https://videodelivery.direcaoconcursos.com.br/fb9e9639-189d-4b76-af7a-219ddf56e5b9.mp4", "path.mp4")
    

    hamburguerButton = driver.find_element(By.XPATH, "//button[@class='hamburguerButton']")  
    hamburguerButton.click()

    return driver

    close_boxtool(driver)

    # get class of all classes
    classesDiv = driver.find_element(By.XPATH, "//*[@id='root']/div[4]/div[2]/div[2]")

    # get all classes from menu (childreen)
    aulas = classesDiv.find_elements(By.XPATH, './div') 

    next_class = aulas[0].find_element(By.XPATH, "following-sibling::*[1]")

    next_button = driver.find_element(By.XPATH, "//button[@class='last']")  

    video_button = driver.find_element(By.XPATH, "//button[@class='video']") 

    videos_class = driver.find_element(By.XPATH, "//div[@class='keen-slider']")

    # get all videos array from videos_class
    videos = videos_class.find_elements(By.XPATH, './div')

    for video in videos:
        # find img src from video div
        child = video.find_element(By.XPATH,'./div')  

        video_name = child.text

        child = child.find_element(By.XPATH,'./div')

        img_element = child.find_element(By.XPATH, './img')

        image_source = img_element.get_attribute('src')

        # video code of video
        link = get_link_from_src(image_source)

        full_videolink_to_download = f'https://videodelivery.direcaoconcursos.com.br/{link}.mp4'

        print(video_name, full_videolink_to_download)

    # get




    






    # videos_class = driver.find_element(By.XPATH, "//*[@id='root']/div[6]/div[2]/div[1]/div/div[3]/div[2]")



    aulas = classesDiv.find_elements(By.XPATH, "//div[@class='sc-knKHOI']")
    # fazer loop aqui #IMPORTANT!

    aula_name = aulas[0].text
    aula_name = aula_name.replace("\n", " - ")
    aulas[0].click()

    # fazer loop aqui #IMPORTANT!

    capitulos = aulas[0].find_elements(By.XPATH, "//div[@class='sc-knKHOI cVnrss']")
    aulas = classesDiv.find_elements(By.XPATH, "//div[contains(., 'Aula')]")



    return driver



if __name__ == "__main__":

    start()
    print("Done")
    time.sleep(500)
