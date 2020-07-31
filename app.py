# -*- coding: utf-8 -*-
import unidecode
#import time
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.logic import LogicAdapter
from chatterbot.response_selection import get_first_response
from chatterbot.comparisons import levenshtein_distance
from chatterbot.response_selection import *  # get_first_response
from chatterbot.comparisons import *  # levenshtein_distance
from chatterbot import *
import csv
#import nltk
#import nltk.data
#import json
import sys
import os
from flask import Flask, render_template, request
#from bs4 import BeautifulSoup
#import requests
#import re
#import nltk
#from newspaper import Article, Source
#from newspaper import news_pool
#from googlesearch import search
#import wikipedia
#from time import sleep
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
            return str('Repita a pergunta')

if __name__ == '__main__':
    app.run()
