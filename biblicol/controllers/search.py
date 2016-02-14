import re
from django.shortcuts import render
from django.http import HttpResponse
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..helpers.utility import Helper
from ..models.bible import Bible


class Search(object):

    # By default we expect books that dont start with no.s
    book_starts_with_no = False
    page = 1

    @staticmethod
    def index(request, param='', pageno=1):
        # if nothing has been passed to the search, back to home page
        if param == '':
            return render(request, 'index.html', {})

        if request.GET.get('page') is not None:
            Search.page = request.GET.get('page')

        # remove underscores from smart URL
        param = re.sub(r'_{1,}', ' ', param, flags=re.IGNORECASE)

        # and double spaces
        param = re.sub(r'(\s{2,}|_)', ' ', param, flags=re.IGNORECASE)
        search_term = param.lower().split(' ')

        for word in search_term:
            num_of_same_words = [x for x in search_term if x == word]

            if len(num_of_same_words) > 1:
                search_term = [x for x in search_term if x != word]
                search_term.append(word)

        search_term = ' '.join([str(x) for x in search_term])
        param = search_term

        search_info = Search.get_search_info(param)
        search_info['read_book'] = False

        # 1[st] john something..something
        Search.book_starts_with_no = search_info['starts_with_no']

        if search_info['is_book_search'] is True and not search_info['is_multiple_verses']:
            response = Search.get_single_verse(param)

        elif search_info['is_multiple_verses'] is True:
            response = Search.get_multiple_verses(param)

        elif search_info['search_in_book'] is True:
            response = Search.search_in_book(param)

        elif search_info['is_chapter_search'] is True:
            response = Search.get_chapter(param)

        else:
            # get words that have more than 3 characters
            more_than_3_character = [x for x in param.split(' ') if len(x) >= 3]
            old_param = param  # keep in cache to remember what the

            if len(more_than_3_character) > 0:
                pass
            else:
                param = "abcdefghijklmnopqrstuvwxyz"

            if re.match(r'^([\w.\-\d]+){1}$', param) is True:
                book = Helper.get_the_book_requested(param)
                book_is_valid = Helper.is_book_in_bible(book)

                if book_is_valid is object:
                    search_info['read_book'] = book_is_valid.bookname
                    param = book_is_valid.bookname

            search_info['simple_search'] = True
            response = Search.my_simple_duckduckgo_search(param)

            if len(response) is 0:
                search_info['really_simple_search'] = True
                response = Search.really_simple_search(param)

            param = old_param

        return HttpResponse("The search param sent is %s" % search_term)

    @staticmethod
    def get_search_info(search_param):
        search_info = {
            'is_book_search': False,
            'is_chapter_search': False,
            'is_multiple_verses': False,
            'search_in_book': False,
            'is_regex_search': False,
            'starts_with_no': False
        }

        chapter_search_pattern = r'([\d]\w{1,2}?)?(\s)?([\w.-]){2,20}(\s)([\d]){1,4}$'
        search_in_specific_book_pattern = r'([\d]\w{1,2}?)?(\s|\-|\_)?([\w.-]){2,20}(\:)(\s)?([\w\d.\-\s]{3,})+'
        book_search_pattern = r'([\d]\w{1,2}?)?(\s)?([\w.-]){2,20}(\s)([\d]){1,4}(\:)([\d]){1,4}'
        starts_with_no = r'^(([\d](\w{1,})?)|((\w{1,})?[\d]))(\s|\-|\_)?([\w\d.\-\s]+)?'

        # For natural language searches
        # eg. hope or love, hope not love, hope and love
        if re.match(r'(and|and not|not|or)+', search_param) is not None:
            search_info['is_regex_search'] = True

        # A possibiity that the search might be just a chapter mentioned
        elif re.match(chapter_search_pattern, search_param) is not None:
            search_info['is_chapter_search'] = True

        # If the search search_param matches a bible verse search
        if re.match(book_search_pattern, search_param) is not None:
            search_info['is_book_search'] = True
            stn_pattern = r'^(([\d](\w{1,})?)|((\w{1,})?[\d]))(\s|\-|\_)([\w\d\.\-\s]+)'
            is_multiple_verses_pattern = r'([\d])?(\s)?([a-zA-Z]){2,20}(\s)([\d]){1,4}(\:)([\d]){1,4}(\-)([\d]){1,4}'

            # For books that start with no.s
            # eg. chronicles, john, peter -- 1john,
            # 1 john, 1-john, 1st john...4th john
            if re.match(stn_pattern, search_param) is not None:
                search_info['starts_with_no'] = True

            # if it matches a search_param for multiple verses - genesis 1:1-30
            if re.match(is_multiple_verses_pattern, search_param) is not None:
                search_info['is_multiple_verses'] = True

            return search_info

        # Search in book param - genesis:love hope
        elif re.match(search_in_specific_book_pattern, search_param) is not None:
            search_info['search_in_book'] = True
            return search_info

        # For books that start with no.s
        # eg. chronicles, john, peter - - 1john,
        # 1 john, 1-john, 1st john...4th john
        elif re.match(starts_with_no, search_param) is not None:
            search_info['starts_with_no'] = True

        return search_info

    @staticmethod
    def get_single_verse(search_param):
        book_requested = Helper.get_the_book_requested(
            search_param,
            Search.book_starts_with_no
        )
        exists = Helper.is_book_in_Bible(book_requested['book'])

        if exists is not False:
            return Search.show(
                book_requested['book'],
                book_requested['chapter'],
                book_requested['verses'],
                False
            )
        else:
            return None

    @staticmethod
    def get_multiple_verses(search_param):
        book_requested = Helper.get_the_book_requested(
            search_param,
            Search.book_starts_with_no
        )
        exists = Helper.is_book_in_Bible(book_requested['book'])

        if exists is not False:
            v = book_requested['verses'].split('-')

            if v[0] > v[1]:
                print("1st verse larger than last verse.")
                return

            # include the last one
            verses_range = list(range(int(v[0]), int(v[1])) + 1)
            verses = Bible.objects.filter(
                bookname=book_requested['book'],
                chapter=book_requested['chapter'],
                verse__in=verses_range
            )

            # Join up all the verses into a sentence
            sentense = Helper.buildSentense(verses, book_requested)
            return sentense
        else:
            return None

    @staticmethod
    def get_chapter():
        pass

    @staticmethod
    def search_in_book():
        pass

    @staticmethod
    def my_simple_duckduckgo_search():
        pass

    @staticmethod
    def really_simple_search():
        pass

    @staticmethod
    def no_boolean_search():
        pass
