import os
import json
import time
import sys, traceback
from threading import Thread, Event
import telepot
from handlers.boards import check_for_bargains
from terms import Terms

class BargainFinder():

    def __init__(self):
        self.setup_paths()
        self.telegram_token = None
        self.current_msg_id = self.check_for_message_id()
        print('message id = {}'.format(self.current_msg_id))
        self.running = True
        self.bot = None
        self.terms = Terms()
        self.search_terms = {}
        self.terms.read_terms()
        self.stop = None
        self.bargain_spider_thread = None
        self.read_telegram_token()
        if self.telegram_token is None:
            print('no token set, paste token string into telegram_token.txt')
            self.running = False
            return
        self.setup_telgram()

    def setup_paths(self):
        scriptdir = os.path.dirname(os.path.realpath(__file__))
        self.telegram_token_path = os.path.join(scriptdir,'telegram_token.txt')
        self.msg_id_path = os.path.join(scriptdir,'msg_id.txt')
        self.help_path = os.path.join(scriptdir,'help.txt')

    def read_telegram_token(self):
        try:
            with open(self.telegram_token_path) as f:
                self.telegram_token = f.readline().strip()
        except Exception as e:
            traceback.print_exc()

    def persist_message_id(self, msg_id):
        try:
            if msg_id is None or self.current_msg_id == msg_id:
                return
            self.current_msg_id = msg_id
            print('writing message id {}'.format(msg_id))
            with open(self.msg_id_path,'w') as f:
                f.write(str(msg_id))
        except Exception as e:
            traceback.print_exc()
        
    def check_for_message_id(self):
        try:
            with open(self.msg_id_path,'r') as f:
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
            traceback.print_exc()

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
                new_terms = self.terms.add_term(message)
                self.kill_bargain_thread()
                self.send_message(new_terms)
            elif message.startswith('r '):
                message = message[2:]
                new_terms = self.terms.remove_term(message)
                self.kill_bargain_thread()
                self.send_message(new_terms)
            elif message =='p':
                all_terms = self.terms.get_printable_terms()
                self.send_message(all_terms)
            elif message =='h' or message == 'help':
                self.print_help()
        except Exception as e:
            traceback.print_exc()

    def print_help(self):
        with open(self.help_path) as f:
            self.send_message(f.read())    

    def setup_telgram(self):
        try:
            self.bot = telepot.Bot(self.telegram_token)
            self.bot.message_loop(self.handle_message)
        except Exception as e:
            traceback.print_exc()

    def kill_bargain_thread(self):
        try:
            if self.bargain_spider_thread is not None:
                if self.bargain_spider_thread.isAlive():
                    self.stop.set()
                    while self.bargain_spider_thread.isAlive():
                        time.sleep(2)
                    self.bargain_spider_thread = None
        except Exception as e:
            traceback.print_exc()

    def run_app(self):
        try:
            bargain_spider_thread = None
            while self.running:
                if self.bargain_spider_thread is None and self.current_msg_id is not None:
                    self.stop = Event()
                    self.bargain_spider_thread = Thread(target=check_for_bargains, args=(self.stop, self.bot, self.current_msg_id, self.terms.get_terms().keys()))
                    self.bargain_spider_thread.start()
                time.sleep(1)
            self.send_message('Exiting as requested')
            print('Exiting app as requested')
        except Exception as e:
            print('problem with app, exiting')
            traceback.print_exc()
        finally:
            self.kill_bargain_thread()

bf = BargainFinder()
bf.run_app()