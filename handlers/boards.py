from bs4 import BeautifulSoup
import requests
import sys, traceback
import time

def check_for_bargains(stop, bot, msg_id, terms):
    try:
        check_count = 0
        print(terms)
        found_terms = {}
        while not stop.isSet():
            if check_count == 0:
                print('checking for bargains...')
                r = requests.get('https://touch.boards.ie/forum/346')
                soup = BeautifulSoup(r.content, 'html.parser')
                links = soup.find_all('a')
                for l in links:
                    hit_text = None
                    # print(l)
                    if 'href' not in str(l):
                        continue

                    link = l.get('href').strip()

                    if link is not None and '/thread/post/' in link:
                        for term in terms:
                            if term in l.text.lower():
                                hit_text = '"{}" triggered hit for: '.format(term)
                                link = '{}{}'.format('https:', link)
                    elif link is not None and '/b/thread/' in link:
                        for term in terms:
                            if term in l.text.lower():    
                                hit_text = '"{}" triggered hit for: '.format(term)
                                link = '{}{}'.format('https://boards.ie', link)
                    elif link is not None and 'showthread.php' in link:
                        for term in terms:
                            if term in l.text.lower():    
                                hit_text = '"{}" triggered hit for: '.format(term)
                                link = '{}{}'.format('https://boards.ie/vbulletin/', link)
                    if hit_text is not None:
                        if hit_text not in found_terms:
                            found_terms[hit_text] = None
                            message_text = '{} {} aa {}'.format(hit_text, l.text.strip(), link)
                            bot.sendMessage(msg_id, message_text)
                print('completed check')
            check_count = check_count + 1
            if check_count == 60:
                check_count = 0
            time.sleep(5)
    except Exception as e:
        traceback.print_exc()