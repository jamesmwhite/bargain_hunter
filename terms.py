import os
import json

class Terms():

    def __init__(self):
        scriptdir = os.path.dirname(os.path.realpath(__file__))
        self.search_terms = {}
        self.search_terms_path = os.path.join(scriptdir,'search_terms.txt')

    def add_term(self, term):
        self.search_terms[term] = None
        with open(self.search_terms_path, 'w') as f:
            json.dump(self.search_terms, f)
        return self.get_printable_terms()

    def remove_term(self, term):
        self.search_terms.pop(term)
        with open(self.search_terms_path, 'w') as f:
            json.dump(self.search_terms, f)
        return self.get_printable_terms()

    def read_terms(self):
        try:
            with open(self.search_terms_path, 'r') as f:
                terms = json.load(f)
                for term in terms.keys():
                    if term is not None and len(term) > 0:
                        print('reading term... {}'.format(term))
                        self.search_terms[term] = None
                    
        except Exception as e:
            print('problem reading search terms {}'.format(e))

    def get_printable_terms(self):
        ret_str = ''
        instructions = '[t term] to add [r term] to remove'
        for key in self.search_terms.keys():
            ret_str = '{} {}{}'.format(ret_str, os.linesep, key)
        if len(ret_str) == 0:
            ret_str = 'No terms added yet'
        return '{} {}{} '.format(ret_str, os.linesep, instructions)
        # self.send_message()

    def get_terms(self):
        return self.search_terms