import os
import glob
import json
from django.http import HttpResponse
from ..models.bible import Bible
from ..models.bookstats import BookStats
from ..utilities.helper import Helper


class Loader(object):

    @staticmethod
    def load_books_into_db(request):
        the_json_books = glob.glob(os.path.join('biblicol/data/books/', '*.json'))
        # print(the_json_books)

        for json_file in the_json_books:
            chapter_title = ''

            # { book_details, chapters[chapter[verse{}, verse{}...]] }
            file_data = open(json_file, mode='r', encoding='utf-8')
            data = json.loads(file_data.read())
            file_data.close()

            # print({"name": json_file, "content": data.get('book'), "len": len(data['chapters'])})
            book = data.get('book')
            print('Bookname: ' + book['name'])

            # Loop thru the chapters
            for chapters in data.get('chapters'):

                for verse in chapters:
                    v = Bible()
                    v.bookname = verse['bookname'].lower()
                    v.chapter = verse['chapter'].lower()
                    v.verse = verse['verse'].lower()
                    v.text = Helper.extract_common_words(verse['text'])
                    v.quoted = ' '.join([x.lower() for x in [verse['bookname'], verse['chapter'], verse['verse']]])
                    v.abbrev = book['abbrev']

                    # turn all the row values into keywords,
                    # chuck [keywords, quoted, title, timestamp] - not ordered as listed though
                    # finally clean it and join into string
                    v.keywords = ' '.join([v.bookname, v.chapter, v.verse, v.text, v.abbrev])

                    # use assigned  title to verses that dont have title
                    if "title" in verse:
                        chapter_title = verse['title']

                    v.title = chapter_title

                    verses_found = Bible.objects.filter(
                        bookname=book['name'],
                        chapter=verse['chapter'],
                        verse=verse['verse']
                    ).values('text')

                    if len(verses_found) is 0:
                        v.save()

        Loader.load_chapter_stats_into_db()
        return HttpResponse("Loading up the data into DB")

    @staticmethod
    def load_chapter_stats_into_db(request=None):
        with open('biblicol/data/books-chapter-info.json', mode='r', encoding='utf-8') as file_data:
            data = json.loads(file_data.read())
            books = data.get('books')

            for book in books:
                b = BookStats()
                b.abbrev = book['abbrev']
                b.value = book['chapters']
                b.name = "chapters"
                b.description = book['name'].lower()
                b.save()

        Loader.load_verse_stats_into_db()
        return HttpResponse("Loading up chapter stats into DB")

    @staticmethod
    def load_verse_stats_into_db(request=None):
        path = 'biblicol/data/books-info/'
        for book_info_file in glob.glob(os.path.join(path, '*.json')):

            with open(book_info_file, mode='r', encoding='utf-8') as json_data:
                data = json.loads(json_data.read())
                book = data.get('chapters')
                book_abbreviation = data.get('book').get('abbrev').upper()

                for chapter in book:
                    b = BookStats()
                    b.abbrev = book_abbreviation
                    b.value = chapter['versecount']
                    b.name = "verse_count"
                    b.description = "{abbrev} {chapter}".format(
                        abbrev=book_abbreviation,
                        chapter=chapter['chapter']
                    )
                    b.save()
