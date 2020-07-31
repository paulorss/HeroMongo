# -*- coding: utf-8 -*-
import unidecode
import time
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.logic import LogicAdapter
from chatterbot.response_selection import get_first_response
from chatterbot.comparisons import levenshtein_distance
from chatterbot.response_selection import *  # get_first_response
from chatterbot.comparisons import *  # levenshtein_distance
from chatterbot import *
import csv
import nltk
import nltk.data
import json
import sys
import os
from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import re
import nltk
from newspaper import Article, Source
from newspaper import news_pool
from googlesearch import search
import wikipedia
from time import sleep
#from logging import *
#import logging
import urllib3
import sys
#from chatterbot.adapters import Adapter
#from chatterbot.storage import StorageAdapter
#from chatterbot.search import IndexedTextSearch
#from chatterbot.conversation import Statement

# logging.basicConfig(filename="Log_Test_File.txt", level=logging.INFO, filemode='a')
#logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

searchbot = ChatBot(
    "Chatterbot", read_only=True,
    input_adapter="chatterbot.input.VariableInputTypeAdapter",
    output_adapter="chatterbot.output.OutputAdapter",
    preprocessors=['chatterbot.preprocessors.clean_whitespace', 'chatterbot.preprocessors.convert_to_ascii'],
    storage_adapter="chatterbot.storage.MongoDatabaseAdapter",
    #database='heroku_8vh2l039',
    #database_uri="mongodb://heroku_8vh2l039:P15l4r4b2rt4@ds113736.mlab.com:13736/heroku_8vh2l039?retryWrites=false&w=majority"
    #database_uri="mongodb+srv://P15l4r4b2rt4:P15l4r4b2rt4@botheroku.j2haj.gcp.mongodb.net/botheroku?retryWrites=false&w=majority",
    # storage_adapter='chatterbot.storage.SQLStorageAdapter',
    # database_uri='sqlite:///database.db',
    statement_comparison_function=levenshtein_distance,
    response_selection_method=get_first_response,
    logic_adapters=[
        {
            'import_path': 'chatterbot.logic.BestMatch',
            "statement_comparision_function": "chatterbot.comparisions.levenshtein_distance",
            "response_selection_method": "chatterbot.response_selection.get_first_response",
            # 'default_response': 'Desculpe, não compreendi a pergunta.',
            # 'maximum_similarity_threshold': 0.60
        },
    ]
)

trainer = ListTrainer(searchbot)

conv = open('chat.txt', encoding="utf-8").readlines()
# convj = open('export.json', encoding='utf-8').readlines()


trainer.train(conv)


#trainer.export_for_training('./export.json')


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/get")
# function for the bot response
def get_bot_response():
    while True:
        userText = request.args.get('msg')
        msg = str(userText).lower()
        entrada = msg
        #f = csv.writer(open('inputs.csv', 'a', encoding='utf-8'))
        #f.writerow([msg])
        response = searchbot.get_response(userText)
        if float(response.confidence) >= 0.5:
            return str(searchbot.get_response(userText))
        elif 0.2 <= float(response.confidence) < 0.5:
            return str('Desculpe, não compreendi! Tente novamente, por favor!')
        elif msg == str('não'):
            return str('Nesse caso, você pode refazer a pergunta com outros termos!')
        elif msg == str("sim"):
            return str("Ótimo! Agradecemos o seu contato")
        elif 0.0 <= float(response.confidence) < 0.2:
            pass
        entrada = str(entrada).lower()
        stop2 = nltk.corpus.stopwords.words('portuguese')
        stop2.append('faço')
        stop2.append('um')
        stop2.append('gostaria')
        stop2.append('fazer')
        stop2.append('saber')
        stop2.append('posso')
        stop2.append('como')
        splitter = re.compile('\\W+')

        lista_palavras = []
        lista = [p for p in splitter.split(entrada) if p != '']
        for p in lista:
            if p not in stop2:
                if len(p) > 1:
                    lista_palavras.append(p)
        ar = len(lista_palavras)
        ax = str(lista_palavras[0:ar])
        e = str(ax).replace(',', ' ').strip('[]')
        e.strip("'")
        p1 = 'http://receita.economia.gov.br/onde-encontro/'
        p2 = 'http://receita.economia.gov.br/@@busca?advanced_search=False&sort_on=&SearchableText='
        p3 = '&portal_type%3Alist=Document&created.query%3Arecord%3Alist%3Adate=1970-01-02&created.range%3Arecord=min'

        print(e)
        html = str(p1)
        html2 = (p2 + entrada + p3)

        req = requests.get(p1)
        if req.status_code == 200:
            print('Requisição bem sucedida!')
            print('\n')
            contenta = req.content
        elif req != 200:
            return str('Refaça a pergunta, por favor!')
            pass

        # headers = {'User-Agent': 'Mozilla/5.0'}
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0'}
        # page = requests.get(p1)
        # soup = BeautifulSoup(page.text, 'html.parser')

        try:
            page = requests.get(p1, html2, headers=headers, verify=False, stream=False, timeout=7)
            page2 = requests.get(html2, headers=headers, verify=False, stream=False, timeout=7)
            soup = BeautifulSoup(page.content, 'html.parser')
            soup2 = BeautifulSoup(page2.content, 'html.parser')
            cla = soup.find(class_='cover-richtext-tile tile-content')
            cla2 = soup2.find(class_='searchResults')
            links1 = cla.find_all('a')
            links2 = cla2.find_all('a')
            links = links1 + links2
        except:
            pass

        listr = []
        try:
            for link in range(len(links)):
                texto = str(link.get_text()).lower().replace('ã', 'a').replace('-', ' ').replace('ç', 'c').split()
                # time.sleep(1)
                # print(len(texto))
                url = str(link.get('href'))
                # time.sleep(1)
                # print(len(url))
                urls = str(link.get('href')).lower().replace('/', ' ').replace('-', ' ').replace('.', ' ').split()
                # time.sleep(1)
                # print(len(urls))
                if entrada in texto:
                    listr.append(url)
                for i in range(0, ar):
                    if lista_palavras[i] in texto:
                        listr.append(url)
                    elif lista_palavras[i] in urls:
                        listr.append(url)
            print(listr)

        except:
            pass

        listag = []
        rec = 'site:receita.economia.gov.br intext:' + msg + " -filetype:pdf -.pdf"
        for urla in search(rec, tld='com.br', lang='pt-br', stop=4, pause=10, user_agent='Mozilla/5.0'):
            time.sleep(1)
            listag.append(urla)

        listaunida = listr + listag
        print(listag)
        conja = set(listaunida)
        conj = list(conja)
        j = len(conj)
        print(conj)

        reports2 = []
        news_pool.set(reports2, threads_per_source=2)
        news_pool.join()
        try:
            for r in range(len(conj)):
                    ia = (conj[r])
                    article = Article(ia, language="pt", memoize_articles=False)
                    article.download()
                    article.parse()
                    #textu = article.text
                    article.nlp()
                    #suma = article.summary
                    #df = article.title
                    #ur = article.url
                    reports2.append(str(article.title) + ' ' + str(article.summary).replace('\n', ' ') + ' ' + str(article.url))
                    #reports2.append(str(article.summary).replace('\n', ' '))
        except:
            break

            #for r in range(len(conj)):
             #   ia = (conj[r])
              #  article = Article(ia, language="pt")
         #       article.download()
          #      article.parse()
         #       article.text
         #       article.nlp()
         #       #article.keywords
         #       #article.title
         #       #article.url
         #       #article.images
         #       article.summary
         #       reports2.append(str(article.title) + ' ' + str(article.summary) + ' ' + str(article.url))
                #reports2.append(str(article.summary))  # .replace('\n', ' ')
    #            #reports2.append(str(article.url))
   #             #reports2.append(str(article.keywords))
  #              #print(article.images)
 #       except:
#            continue

        print(reports2)
        resposta_finalc = set(reports2)
        print(resposta_finalc)

        if resposta_finalc == set():
            wikipedia.set_lang("pt")
            a = msg
            result = wikipedia.search(a, results=1)
            page = wikipedia.summary(result, sentences=6)
            content = page
            return str(content)
        else:
            try:
                resposta_final = (
                    str(resposta_finalc).replace('\n', ' ').replace('[', ' ').replace(']', ' ').replace(',',
                                                                                                        ' ').replace(
                        "'", ' ').replace('{', ' ').replace("}", ' '))
                f = csv.writer(open('chat.txt', 'a', encoding='utf-8'))
                f.writerow([msg + '\n' + resposta_final])
                return str(resposta_final + ' ' + '\nEncontrou a resposta que precisava? SIM ou NÃO?')
            except:
                return str('Desculpe! Não encontrei uma resposta para sua pergunta. Poderia repetir com outros termos?')


if __name__ == '__main__':
    app.run()
