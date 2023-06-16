import os
import undetected_chromedriver as uc
from selenium.webdriver.remote.webdriver import By
from selenium import webdriver
import selenium.webdriver.support.expected_conditions as EC  # noqa
from data import get_data
import time
import Direcao
import sys

# def get_link_from_src(src_source:str)->str:
#      sp = src_source.split('/')
#      last = sp[-1]
#      code = last.split('.')[0]
#      return code

def pause():
     time.sleep(3600)

def start():
    
    direcao = Direcao.Direcao()
    driver = direcao.driver

    driver.get("https://aluno.direcaoconcursos.com.br/")
    
    data = get_data()
    email = data['user'] 
    password = data['pass']
    time.sleep(2)
    email_form = driver.find_element(By.XPATH, "//input[@placeholder='E-mail']")
    email_form.send_keys(email)
    pass_form = driver.find_element(By.XPATH, "//input[@placeholder='Senha']")
    pass_form.send_keys(password)

    button = driver.find_element(By.XPATH, "//button[@type='submit']")
    button.submit()
    time.sleep(5)
    direcao.wait_for_page_load()

    current_url = driver.current_url
    if (current_url== "https://aluno.direcaoconcursos.com.br/"):
       time.sleep(10)
       if (current_url== "https://aluno.direcaoconcursos.com.br/"):
        print('não fez login. tente novamente')
        sys.exit() 

    direcao.click("//button[contains(.,'Aceitar e sair')]")
    direcao.aulas = direcao.open_page_till_hamburger(course_url=direcao.disciplina_url)
    direcao.total_aulas = len(direcao.aulas) 

    for i in range(direcao.start_aula_index - 1, len(direcao.aulas), 1):
       
        sucess = direcao.click(element=direcao.aulas[i])
        while not sucess:
            driver.refresh()
            direcao.wait_for_page_load()
            sucess = direcao.click(element=direcao.aulas[i])
            print('trancou no while not success')

        next_class = direcao.aulas[i].find_element(By.XPATH, "following-sibling::*[1]")
        next_class_text = next_class.text
        if not (next_class_text.__contains__('Capítulo')):
            direcao.click(element=direcao.aulas[i])
            
        aula_name = direcao.aulas[i].text
        aula_name = aula_name.replace("\n", "-",-1)
        aula_name = direcao.check_file_name(text=aula_name)
        
        direcao.current_aula = aula_name
        
        success = direcao.click(element=next_class)

        if not success:
            print('deu merda recarregando página')
            direcao.driver.refresh()
            direcao.wait_for_page_load()

        if direcao.want_pdfs:
            direcao.webDriverWaitByXpath("//button[@class='text']", 2)
            has_pdf = direcao.check_if_has_pdf_or_video()['pdf']
            print('haspdf ?? ->', has_pdf)
            if has_pdf:
                ebook_button_elements = driver.find_elements(By.XPATH, "//button[@class='text']")
                direcao.click(element=ebook_button_elements[0])
                aula_fullpath = os.path.join(direcao.root_path, direcao.disciplina_name,f'{aula_name}.pdf')
                direcao.download_pdf(aula_fullpath)


        if direcao.want_videos:
            direcao.get_all_videos()
        

        if (i < len(direcao.aulas)-1):
            direcao.aulas = direcao.open_page_till_hamburger(direcao.disciplina_url)

    return driver



if __name__ == "__main__":

    start()
    print("Done")
    time.sleep(500)
