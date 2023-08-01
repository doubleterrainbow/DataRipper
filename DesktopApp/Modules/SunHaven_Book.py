import json
import re

from DesktopApp.datum import Datum

class Book:
    def __init__(self):
        self.book_name = ""
        self.text = ""

def getBook(jsonPath):
    # Opening JSON file
    with open(jsonPath, "r") as data_file:
        data = json.load(data_file)

        book = Book()
        book.text = str(data['text'])
        book.text = re.sub(r'<align="center">', '', book.text)
        book.text = re.sub(r'</align>', '', book.text)
        book.text = re.sub(r'\n+', '\n', book.text)
        
        if 'bookName' in data:
            book.book_name = data['bookName']
        else:
            book.book_name = book.text.split('\n')[0]
        

        return book
