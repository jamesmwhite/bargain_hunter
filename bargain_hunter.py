import os
import json
import time
from threading import Thread, Event
import requests
from bs4 import BeautifulSoup
import telepot


class BargainFinder():

    def __init__(self):
        self.telegram_token = None
        self.current_msg_id = self.check_for_message_id()
        print('message id = {}'.format(self.current_msg_id))
        self.running = True
        self.bot = None
        
        self.search_terms = {}
        self.read_terms()
        self.stop = None
        self.bargain_spider_thread = None
        self.read_telegram_token()
        if self.telegram_token is None:
            print('no token set, paste token string into telegram_token.txt')
            self.running = False
            return
        self.setup_telgram()

    def read_telegram_token(self):
        try:
            with open('telegram_token.txt') as f:
                self.telegram_token = f.read()
                
        except Exception as e:
            print(e)
        


    def persist_message_id(self, msg_id):
        try:
            if msg_id is None or self.current_msg_id == msg_id:
                return
            self.current_msg_id = msg_id
            print('writing message id {}'.format(msg_id))
            with open('msg_id.txt','w') as f:
                f.write(str(msg_id))

        except Exception as e:
            print(e)
        

    def check_for_message_id(self):
        try:
            with open('msg_id.txt','r') as f:
                msg_id = f.read()
                if msg_id is None or msg_id.strip() == '':
                    return None
                return msg_id
        except:
            return None

    def send_message(self, message):
        if len(message) > 4000:
                message = message[-4000:]
        try:
            self.bot.sendMessage(self.current_msg_id, message)
        except Exception as e:
            print(e)

    def handle_message(self, msg):
        try:
            print(msg)
            self.persist_message_id(msg['from']['id'])
            message = msg['text']
            message = message.lower()
            if message == 'ping':
                self.send_message("pong")
            elif message == 'exit':
                self.running = False
            elif message.startswith('t '):
                message = message[2:]
                self.add_term(message)
            elif message.startswith('r '):
                message = message[2:]
                self.remove_term(message)
            elif message =='p':
                self.print_terms()
            elif message =='h' or message == 'help':
                self.print_help()
        except Exception as e:
            print(e)

    def print_help(self):
        with open('help.txt') as f:
            self.send_message(f.read())

    def read_terms(self):
        try:
            with open('search_terms.txt', 'r') as f:
                terms = json.load(f)
                for term in terms.keys():
                    if term is not None and len(term) > 0:
                        print('reading term... {}'.format(term))
                        self.search_terms[term] = None
                    
        except Exception as e:
            print('problem reading search terms {}'.format(e))

    def add_term(self, term):
        self.search_terms[term] = None
        with open('search_terms.txt', 'w') as f:
            json.dump(self.search_terms, f)
        self.kill_bargain_thread()
        self.print_terms()

    def remove_term(self, term):
        self.search_terms.pop(term)
        with open('search_terms.txt', 'w') as f:
            json.dump(self.search_terms, f)
        self.kill_bargain_thread()
        self.print_terms()
    
    def print_terms(self):
        ret_str = ''
        instructions = '[t term] to add [r term] to remove'
        for key in self.search_terms.keys():
            ret_str = '{} {}{}'.format(ret_str, os.linesep, key)
        if len(ret_str) == 0:
            ret_str = 'No terms added yet'
        self.send_message('{} {}{} '.format(ret_str, os.linesep, instructions))

    def setup_telgram(self):
        try:
            self.bot = telepot.Bot(self.telegram_token)
            self.bot.message_loop(self.handle_message)
        except Exception as e:
            print(e)

    def kill_bargain_thread(self):
        try:
            if self.bargain_spider_thread is not None:
                if self.bargain_spider_thread.isAlive():
                    self.stop.set()
                    while self.bargain_spider_thread.isAlive():
                        time.sleep(2)
                    self.bargain_spider_thread = None
        except Exception as e:
            print(e)

    def run_app(self):
        try:
            bargain_spider_thread = None
            while self.running:
                if self.bargain_spider_thread is None and self.current_msg_id is not None:
                    self.stop = Event()
                    self.bargain_spider_thread = Thread(target=check_for_bargains, args=(self.stop, self.bot, self.current_msg_id, self.search_terms.keys()))
                    self.bargain_spider_thread.start()
                time.sleep(1)
            self.send_message('Exiting as requested')
            print('Exiting app as requested')
        except Exception as e:
            print('problem with app, exiting')
            print(e)
        finally:
            self.kill_bargain_thread()

def check_for_bargains(stop, bot, msg_id, terms):
    try:
        check_count = 0
        print(terms)
        while not stop.isSet():
            if check_count == 0:
                print('checking for bargains...')
                r = requests.get('https://www.boards.ie/vbulletin/forumdisplay.php?f=346')
                soup = BeautifulSoup(r.text, 'html.parser')

                links = soup.find_all('a')
                for l in links:
                    id_text = l.get('id')
                    # bargains = []
                    if id_text is not None and 'thread_title' in id_text:
                        for term in terms:
                            if term in l.text.lower():    
                                hit_text = '"{}" triggered hit for: '.format(term)
                                link = 'https://www.boards.ie/vbulletin/{}'.format(l.get('href'))
                                message_text = '{} {} [inline URL]({})'.format(hit_text, l.text, link)
                                print('{}'.format(message_text))
                                bot.sendMessage(msg_id, message_text)
                print('completed check')
            check_count = check_count + 1
            if check_count == 12:
                check_count = 0
            time.sleep(5)
    except Exception as e:
        print(e)
        

bf = BargainFinder()
bf.run_app()