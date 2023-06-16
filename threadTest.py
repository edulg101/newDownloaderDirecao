from threading import Thread
from time import sleep
import os
import re
import sys
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import By
from selenium.webdriver.support.wait import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC  # noqa
import concurrent.futures
import threading
from threading import Thread
import time
import json
import ls
import data
import requests
from unidecode import unidecode

import logging

def threaded_function(arg):
    for i in range(arg):
        print("running")
        sleep(1)
def first_test():
    thread = Thread(target = threaded_function, args = (10, ))
    thread.start()
    for i in range(20):
        print(i)
        sleep(0.5)
    thread.join()
    print("thread finished...exiting")

def download_all_videos(links):
        print('dentro do download ALL links:')
        print(links)
        print('tamanho links', len(links))
        print('tipo da links', type(links))
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            executor.map(download_video, links)

def download_video(data:str):
        data = data.split(sep="@@@")
        link = data[0]
        file_path = data[1]

        if (os.path.exists(path=file_path)):
            print(f'Arquivo {file_path} já baixado. Não vou repetir')
            return False
        print(f"baixando {file_path} .... aguarde !")

        headers = ""

        r = requests.get(link, headers=headers)


        folder = os.path.dirname(file_path)
        
        if not (os.path.exists(file_path)):
            os.makedirs(folder)

        with open(file_path, 'wb') as f:
            bytes = f.write(r.content)
            if bytes > 0:
                print(f'Arquivo {file_path} baixado com sucesso !')

        print('saiu do download')

def second_test():
    videos_list = [('https://videodelivery.direcaoconcursos.com.br/aaffb23b-9051-434a-9f23-109c6759fcc1.mp4','D:\\Users\\Eduardo\\OneDrive\\MeusConcursos\\SEFAZ\\Direcao\\AFO\\Aula 1-Introducao a Administracao Financeira e Orc\\03-01 - Introducao a AFO - Esclarecimento Inicial - L.mp4'),( 'https://videodelivery.direcaoconcursos.com.br/9efb5a99-e976-4312-9cfd-ddbb8cf7c89c.mp4', 'D:\\Users\\Eduardo\\OneDrive\\MeusConcursos\\SEFAZ\\Direcao\\AFO\\Aula 1-Introducao a Administracao Financeira e Orc\\03-02 - O que saber para comecar a estudar AFO.mp4'), ('https://videodelivery.direcaoconcursos.com.br/576c12e0-901b-437b-a90f-461cc808739b.mp4', 'D:\\Users\\Eduardo\\OneDrive\\MeusConcursos\\SEFAZ\\Direcao\\AFO\\Aula 1-Introducao a Administracao Financeira e Orc\\03-03 - Indroducao.mp4')]

    new_list = list()
    for v in videos_list:
         new_list.append(f'{v[0]}@@@{v[1]}')

    thread = Thread(target = download_all_videos, args = (new_list,))
    thread.start()
    thread.join()
    print('entrou no sleep')
    sleep(3600)

if __name__ == "__main__":
    second_test()