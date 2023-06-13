import os
import re
import sys
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
from unidecode import unidecode
import selenium
from selenium import webdriver
import logging


def get_link_from_src(src_source:str)->str:
     sp = src_source.split('/')
     last = sp[-1]
     code = last.split('.')[0]
     return code

class Direcao:

    def __init__(self, driver: uc.Chrome):
        self.driver = driver
        self.disciplina_name:str
        #marcel
        # self.disciplina_url:str = "https://aluno.direcaoconcursos.com.br/course/63879f1818de1534665aab68/module/6387a3ad18de1534665b227e/lesson/637bd499db266a0b4afcedd5/chapter/637bd499db266a0b4afcedb6"
        #civil tcdf
        # self.disciplina_url:str ="https://aluno.direcaoconcursos.com.br/course/63879f1818de1534665aab68/module/6387a2fb35dfc66e5c0ae5c5/lesson/6366e13868a6c724df91ce40/chapter/6366e13868a6c724df91ce37"
        # self.disciplina_url:str ="https://aluno.direcaoconcursos.com.br/course/637169c709dd593cb1746bd7/module/6408d599907427002744814e/lesson/6377cdc28c0ed73e27582bcb/chapter/63778c6bf76d03031b72f141"
        self.disciplina_url:str ="https://aluno.direcaoconcursos.com.br/course/637169c709dd593cb1746bd7/module/6408d51f3c629000222cf35a/lesson/63beb60f6bddcc0d4f4cdb99/chapter/63beb1d6aeeb6e0d5b9d1174"
        self.root_path:str = ""
        self.course = ""
        self.module = ""
        self.lesson = ""
        self.aulas:list
        self.current_aula:str =""
        self.total_aulas:int = ""
        self.current_capitulo:str = ""
        self.current_capitulo_index:int 
        self.current_video_index:int
        self.want_videos:bool = True
        self.want_pdfs:bool = True

    def __len__(self):
        return self.driver.execute_script("return window.localStorage.length;")

    def get_cookies(self) -> str:
        storage = ls.LocalStorage(self.driver)
        data = storage["persist:@DirecaoConcursos"]
        data = data.replace('\\"', '"')
        data = data.replace('"{', '{')
        data = data.replace('}"', '}')
        cookies = json.loads(data)
        return cookies

    def get_token(self) -> str:
        cookies = self.get_cookies()
        return cookies['auth']['token']

    def get_headers(self) -> str:
        token = self.get_token()
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
    
    def check_if_has_pdf_or_video(self)->dict:
            
            video_div = self.driver.find_elements(By.XPATH,'//button[@class="video"]')
            pdf_div = self.driver.find_elements(By.XPATH,'//button[@class="text"]')
            has_video = len(video_div) > 0
            has_pdf = len(pdf_div) > 0
            if not has_video and not has_pdf:
                return {
                    'pdf':False,
                    'video':False,
                }
            if has_video:
                video_style = video_div[0].get_attribute('style')
                has_video = not video_style.__contains__("none")
            
            if has_pdf:
                pdf_style = pdf_div[0].get_attribute('style')
                has_pdf = not pdf_style.__contains__("none")
            
            
            return_message = {
                'pdf':has_pdf,
                'video':has_video,
            }
            
            return return_message
    
    def check_if_page_has_problems_loading(self)->bool:
        has_pdf = self.check_if_has_pdf_or_video()['pdf']
        has_video = self.check_if_has_pdf_or_video()['video']
        ok =  not has_pdf and not has_video
        return ok

    def get_download_link_pdf(self, request_link):
        link = "https://prod-api.direcaoconcursos.com.br/learning/content/lesson-pdf"

        url = self.driver.current_url
        self.course = re.search("(?<=course/)(.*?)(?=\/)", url).group()
        self.lesson = re.search("(?<=lesson/)(.*?)(?=\/)", url).group()
        self.module = re.search("(?<=module/)(.*?)(?=\/)", url).group()

        headers = self.get_headers()

        json_data = {
            # 'course': '63879f1818de1534665aab68',
            # 'module': '6387a3ad18de1534665b227e',
            # 'lesson': '637bd499db266a0b4afcecee',

            'course': self.course,
            'module': self.module,
            'lesson': self.lesson,
        }
        print("request pdf info:")
        print('link: ',link)
        print('headers:',headers)
        print('json data:')
        print(self.course)
        print(self.lesson)
        print(self.module)
        

        response = requests.post(link, headers=headers, json=json_data)
        

        return response.text

    def download_video(self, link: str, file_path: str):

        if (os.path.exists(path=file_path)):
            print(f'Arquivo {file_path} já baixado. Não vou repetir')
            return False
        print(f"baixando {file_path} .... aguarde !")

        headers = self.get_headers()

        r = requests.get(link, headers=headers)

        folder = os.path.dirname(file_path)
        
        if not (os.path.exists(folder)):
            print(folder)
            os.makedirs(folder)

        with open(file_path, 'wb') as f:

            bytes = f.write(r.content)
            if bytes > 0:
                print(f'Arquivo path baixado com sucesso !')

    def webDriverWaitByXpath(self, xpath: str, seconds=10):
        try:
            WebDriverWait(self.driver, seconds).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, xpath))
            )
        except Exception as e:
            pass

    
    
    def wait_for_page_load(self,seconds=25)->bool:

        print('entrou no wait for page load')
        time.sleep(1)
        
        elements = self.driver.find_elements(By.XPATH, '//*[text()="Loading..."]')
        if (len(elements) < 1):
            time.sleep(0.5)
            return True
        for i in range(seconds):
            print(f'loop {i}')
            time.sleep(1)
            elements = self.driver.find_elements(By.XPATH, '//*[text()="Loading..."]')
            if (len(elements) < 1): 
                time.sleep(1)
                
                success = not self.check_if_page_has_problems_loading()
                return True and success
       
        return False    
        
    def close_boxtool_once(self):
        try:
            self.webDriverWaitByXpath("//button[@class='closeButton']")
            time.sleep(0.5)
            closeButton = self.driver.find_element(
                By.XPATH, "//button[@class='closeButton']")
            closeButton.click()
            return
        except Exception:
            pass

    def close_boxtool(self):
        try:
            self.webDriverWaitByXpath("//button[@class='closeButton']")
            time.sleep(2)
            closeButton = self.driver.find_element(
                By.XPATH, "//button[@class='closeButton']")
            closeButton.click()
            return
        except Exception as ex:
            print(ex)
            print("não abriu tela. continuando")
        try:
            self.webDriverWaitByXpath("//button[@class='finishButton']")
            time.sleep(2)
            closeButton = self.driver.find_element(
                By.XPATH, "//button[@class='finishButton']")
            closeButton.click()
        except Exception as ex:
            print(ex)
            print("não abriu tela. continuando")
        

    def create_link_for_pdf_request(self) -> str:
        driver: uc.Chrome = self.driver
        url = driver.current_url
        self.course = re.search("(?<=course/)(.*?)(?=\/)", url).group()
        self.lesson = re.search("(?<=lesson/)(.*?)(?=\/)", url).group()
        self.module = re.search("(?<=module/)(.*?)(?=\/)", url).group()

    def download_pdf(self, file_path: str):

        if (os.path.exists(path=file_path)):
            print(f'Arquivo {file_path} já baixado. Não vou repetir')
            return False
        print(f"baixando {file_path} .... aguarde !")

        folder = os.path.dirname(file_path)
        
        if not (os.path.exists(folder)):
            os.makedirs(folder)


        link = self.get_download_link_pdf(file_path)
        r = requests.get(link)
        with open(file_path, 'wb') as f:

            bytes = f.write(r.content)
            if bytes > 0:
                print(f'Arquivo {file_path} baixado com sucesso !')
    
    
    def check_file_name(self, text)->str:
        text = unidecode(text)
        text = re.sub('[^A-Za-z0-9\s]+', '-', text)
        
        while (len(text)>50 or text[-1] == " " or text[-1] == "-"):
            text = text[0:-1]

        return text    

    def check_for_box_tool(self):
        boxes = self.driver.find_elements(By.XPATH,'//div[@id="headlessui-popover-panel-:r1:"]')
        while (len(boxes)>0):
            self.close_boxtool()
            boxes = self.driver.find_elements(By.XPATH,'//div[@id="headlessui-popover-panel-:r1:"]')

    def open_page_till_hamburger(self, course_url:str):
        logging.warning('entrou no hamburger')
        driver = self.driver
        direcao = self
        
        driver.get(course_url)
        # direcao.wait_for_page_load()
        logging.warning('entrou no hamburger click')
        direcao.click("//button[@class='hamburguerButton']")
        logging.warning('saiu do click do hamburger ')

        # direcao.webDriverWaitByXpath("//button[@class='closeButton']", 3)

        # direcao.close_boxtool()

        boxes = driver.find_elements(By.XPATH,'//div[@id="headlessui-popover-panel-:r1:"]')
        if (len(boxes) > 0):
            direcao.close_boxtool()
        
        
        
        # direcao.check_for_box_tool()


        direcao.disciplina_name = direcao.driver.find_element(By.XPATH, '//*[@id="root"]/div[4]/div[2]/div[1]/div[1]/div[2]/h3').text
        

        # direcao.close_boxtool()

        # get class of all classes
        direcao.webDriverWaitByXpath("//*[@id='root']/div[4]/div[2]/div[2]", 10)
        classesDiv = driver.find_element(By.XPATH, "//*[@id='root']/div[4]/div[2]/div[2]")

        # get all classes from menu (childreen)
        aulas = classesDiv.find_elements(By.XPATH, './div') 
        logging.warning('saiu do def hamburger')
        return aulas

    def click(self, xpath:str=None, element:uc.webelement.WebElement=None)->bool:
        
        def try_click(element:uc.webelement.WebElement)->bool:
            try:
                sucess = element.click()
                if sucess:
                    self.wait_for_page_load()
                    return True
            except Exception as ex:
                return False
            try:
                self.wait_for_page_load()
                success = not self.check_if_page_has_problems_loading()
                print('problem Loading:', success)
                return success
            except Exception as ex:
                return False

        if (xpath):
            element = self.driver.find_element(By.XPATH, xpath)

        success = try_click(element)
        if success: return True
        success = try_click(element)
        if success: return True

        self.close_boxtool_once()
        success = try_click(element)
        if success: return True

        self.wait_for_page_load()
        success = try_click(element)
        if success: return True

        self.close_boxtool_once()
        success = try_click(element)
        if success: return True

        return False
    
    def get_all_videos(self):
        self.wait_for_page_load()
        

        capitulo_index = 1
        
        keep_going = True
        while keep_going :

            # direcao.current_capitulo = direcao.driver.find_element(By.XPATH, "//div[@class='right']").find_element(By.XPATH, "//h4").text

            self.wait_for_page_load()

            self.current_capitulo = self.driver.find_element(By.XPATH, '//*[@id="root"]/div[5]/div[1]/div[2]/div[1]/h1').text

            if self.current_capitulo.__contains__('Comentadas'):
                print('aqui.')

            self.current_capitulo = self.check_file_name(self.current_capitulo)
            self.current_capitulo = f'{capitulo_index:02d} - {self.current_capitulo}'

            print('capitulo:')
            print(self.current_capitulo)

            self.close_boxtool_once()
            next_button = self.driver.find_element(By.XPATH, "//button[@class='last']")
            
            has_videos = self.check_if_has_pdf_or_video()['video']

            success = self.wait_for_page_load() and not self.check_if_page_has_problems_loading()

            if not success:
                self.driver.refresh()
                has_videos = self.check_if_has_pdf_or_video()['video']
                success = self.wait_for_page_load() and not self.check_if_page_has_problems_loading()
                if not success:
                    print('deu merda no page load')
                    sys.exit()
            # myElem = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'IdOfMyElement')))
            video_button_elements = self.driver.find_elements(By.XPATH, "//button[@class='video']")

            
            if has_videos:
                success = self.click(element=video_button_elements[0])

            # if (success): has_videos = True
            # try:
            #     direcao.close_boxtool_once()
            #     video_button_elements[0].click()
            #     direcao.wait_for_page_load()
            #     has_videos = True
            # except Exception as ex:
            #     print('entrou no exception')
            #     has_videos = False


            print('hasvideos: ', has_videos)
            print('capitulo:', capitulo_index)
            print('capitulo name:', self.current_capitulo)

            print('has video??', has_videos)

            if (has_videos):

                video_button = self.driver.find_element(By.XPATH, "//button[@class='video']") 

                videos_class = self.driver.find_element(By.XPATH, "//div[@class='keen-slider']")

                # get all videos array from videos_class
                videos = videos_class.find_elements(By.XPATH, './div')
                video_index = 1
                for i, video in enumerate(videos):
                    print('entrou no videos')
                    # find img src from video div
                    child = video.find_element(By.XPATH,'./div')  

                    video_name = child.text
                    print('videoname:')
                    print(video_name)
                    if len(video_name) < 1:
                        video_name = f'{video_index:02d}'
                    video_name = self.check_file_name(video_name)

                    child = child.find_element(By.XPATH,'./div')

                    img_element = child.find_element(By.XPATH, './img')

                    image_source = img_element.get_attribute('src')

                    # video code of video
                    link = get_link_from_src(image_source)

                    full_videolink_to_download = f'https://videodelivery.direcaoconcursos.com.br/{link}.mp4'

                    full_video_name = f'{capitulo_index:02d}-{video_name}.mp4'

                    video_path = os.path.join(self.root_path, self.disciplina_name,self.current_aula, full_video_name)
                    
                    self.download_video(full_videolink_to_download, video_path)

                    video_index += 1

            next_button = self.driver.find_element(By.XPATH, "//button[@class='last']")
        
            next_button_text = next_button.text
            self.click(element=next_button)
            capitulo_index += 1
            if (next_button_text.__contains__("Finalizar")):
                keep_going = False

        # if (i < len(self.aulas)):
        #     aulas = self.open_page_till_hamburger(self.disciplina_url)

        
        