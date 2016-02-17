import re
from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
# from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from ..utilities.helper import Helper
from ..utilities.parser import Parser
from ..models.bible import Bible


class Search(object):

    # By default we expect books that dont start with no.s
    book_starts_with_no = False
    page = 1

    @staticmethod
    def index(request, param='', pageno=1):
        # if nothing has been passed to the search,
        # redirect back to home page
        if param == '':
            return render(request, 'index.html', {})

        # keep in old param in cache
        old_param = param

        # if a specific page to the results was requested get it
        if request.GET.get('page') is not None:
            Search.page = request.GET.get('page')

        # remove underscores from smart URL
        # they should be spaces
        param = re.sub(r'_{1,}', ' ', param, flags=re.IGNORECASE)

        # and replace double or more spaces with single spaces
        # then lower case and split it
        param = re.sub(r'(\s{2,}|_)', ' ', param, flags=re.IGNORECASE)
        search_term = param.lower().split(' ')

        # remove the extra words that have been repeated
        # that exist more than once in the search
        for word in search_term:
            num_of_same_words = [x for x in search_term if x == word]

            if len(num_of_same_words) > 1:
                search_term = [x for x in search_term if x != word]
                search_term.append(word)

        # join the cleansed search param back
        # we are now ready to do a search
        search_term = ' '.join([str(x) for x in search_term])
        param = search_term

        # but 1st, let's collect information about the current search
        search_info = Search.collect_current_search_info(param)
        search_info['read_book'] = False

        # does the search query start with a number
        # Pattern: <no>(st,nd,rd,th) <book_name> <something>...<many more>
        Search.book_starts_with_no = search_info['starts_with_no']

        # now get what we we think the user/client requested
        if search_info['is_book_search'] is True \
                and not search_info['is_multiple_verses']:
            response = Search.get_single_verse(param)

        elif search_info['is_multiple_verses'] is True:
            response = Search.get_multiple_verses(param)

        elif search_info['search_in_book'] is True:
            response = Search.search_in_specific_book(param)

        elif search_info['is_chapter_search'] is True:
            response = Search.get_chapter(param)

        else:
            # get words that have more than 3 characters
            more_than_3_character = [x for x in param.split(' ') if len(x) >= 3]

            # if no word from the search param is more than 3 characters
            # substitute search param with all letters of alphabets
            if len(more_than_3_character) is 0:
                param = "abcdefghijklmnopqrstuvwxyz"

            # if a single word was provided
            # check if it matches a book in the bible
            if re.match(r'^([\w.\-\d]+){1}$', param) is not None:
                book = Helper.get_the_book_requested(param)
                book_exists = Helper.is_book_in_Bible(book)

                if book_exists:
                    param = search_info['read_book'] = book['bookname']

            # just do a simple search
            search_info['is_simple_search'] = True
            response = Search.my_simple_duckduckgo_search(param)

            # things have become complicated, let's do a complex search
            if len(response) is 0:
                search_info['is_complex_search'] = True
                response = Search.complex_search(param)

            # restore old search param
            param = old_param

        return HttpResponse(serializers.serialize('json', response),
                            content_type="application/json")

    @staticmethod
    def collect_current_search_info(search_param):
        search_info = {
            'is_book_search': False,
            'is_chapter_search': False,
            'is_multiple_verses': False,
            'is_complex_search': False,
            'search_in_book': False,
            'starts_with_no': False
        }

        chapter_search_pattern = r'([\d]\w{1,2}?)?(\s)?([\w.-]){2,20}(\s)([\d]){1,4}$'
        search_in_specific_book_pattern = r'([\d]\w{1,2}?)?(\s|\-|\_)?([\w.-]){2,20}(\:)(\s)?([\w\d.\-\s]{3,})+'
        book_search_pattern = r'([\d]\w{1,2}?)?(\s)?([\w.-]){2,20}(\s)([\d]){1,4}(\:)([\d]){1,4}'
        starts_with_no = r'^(([\d](\w{1,})?)|((\w{1,})?[\d]))(\s|\-|\_)?([\w\d.\-\s]+)?'

        # check for natural language searches
        # eg. hope or love, hope not love, hope and love
        if re.match(r'(and|and not|not|or)+', search_param) is not None:
            search_info['is_complex_search'] = True

        # A possibiity that the search might be just a chapter mentioned
        elif re.match(chapter_search_pattern, search_param) is not None:
            search_info['is_chapter_search'] = True

        # If the search_param matches a bible verse common annotation/structure
        if re.match(book_search_pattern, search_param) is not None:
            # a book should have been specified
            # so it is a search in the specified book
            search_info['is_book_search'] = True

            # check if it starts with a no. or
            # and if it is a multiple verse search
            start_with_no_pattern = r'^(([\d](\w{1,})?)|((\w{1,})?[\d]))(\s|\-|\_)([\w\d\.\-\s]+)'
            multiple_verses_pattern = r'([\d])?(\s)?([a-zA-Z]){2,20}(\s)([\d]){1,4}(\:)([\d]){1,4}(\-)([\d]){1,4}'

            # check for books that start with no.s
            # eg. chronicles, john, peter
            # 1john, 1 john, 1-john, 1st john...4th john
            if re.match(start_with_no_pattern, search_param) is not None:
                search_info['starts_with_no'] = True

            # if search_param is a match for multiple verses - genesis 1:1-30
            if re.match(multiple_verses_pattern, search_param) is not None:
                search_info['is_multiple_verses'] = True

            return search_info

        # check for specification of book to search in
        # eg. genesis:love hope or hate
        elif re.match(search_in_specific_book_pattern, search_param) is not None:
            search_info['search_in_book'] = True
            return search_info

        # check for books that start with no.s
        # eg. chronicles, john, peter
        # 1john, 1 john, 1-john, 1st john...4th john
        elif re.match(starts_with_no, search_param) is not None:
            search_info['starts_with_no'] = True

        return search_info

    @staticmethod
    def get_single_verse(search_param):
        book_requested = Helper.get_the_book_requested(
            search_param,
            Search.book_starts_with_no
        )
        book_exists = Helper.is_book_in_Bible(book_requested['book'])

        if book_exists:
            return Bible.objects.filter(
                bookname=book_requested['book'],
                chapter=book_requested['chapter'],
                verse__contains=book_requested['verses']
            )
        else:
            return None

    @staticmethod
    def get_multiple_verses(search_param):
        book_requested = Helper.get_the_book_requested(
            search_param,
            Search.book_starts_with_no
        )
        book_exists = Helper.is_book_in_Bible(book_requested['book'])

        if book_exists:
            # get the verse range
            vr = book_requested['verses'].split('-')

            if vr[0] > vr[1]:
                print("1st verse larger than last verse.")
                return

            # include the last one (+1 of last verse range)
            verses_range = list(range(int(vr[0]), int(vr[1]) + 1))
            verses = Bible.objects.filter(
                bookname=book_requested['book'],
                chapter=book_requested['chapter'],
                verse__in=verses_range
            )

            # Join up all the verses into a sentence
            # sentense = Helper.build_sentense(verses, book_requested)
            # return sentense
            return verses
        else:
            return None

    @staticmethod
    def get_chapter(search_param):
        """
        Gets the chapter of a specified bookname
        eg. John 3
        """
        book_requested = Helper.get_the_book_requested(
            search_param,
            Search.book_starts_with_no
        )
        book_exists = Helper.is_book_in_Bible(book_requested['book'])

        if book_exists:
            verses_of_the_chapter = Bible.objects.filter(
                bookname=book_requested['book'],
                chapter=book_requested['chapter']
            )

            # sentense = Helper.build_sentence(verses_of_the_chapter, book_requested)
            # return sentense
            return verses_of_the_chapter

    @staticmethod
    def search_in_specific_book(search_param):
        # expect search_param => "genesis:hope or love"
        param = [x.strip() for x in search_param.split(':')]
        book_to_search_in = param[0]
        book_requested = Helper.get_the_book_requested(
            book_to_search_in,
            Search.book_starts_with_no
        )
        book_exists = Helper.is_book_in_Bible(book_requested['book'])

        # use the valid bookname if it exists
        if book_exists:
            search_string = ' '.join([x for x in param
                                      if x is not book_to_search_in])

            # first run a simple(a bit complex) search
            results = Search.my_simple_duckduckgo_search(search_string, 0, 30, book_requested['book'])
            if len(results) is not 0:
                return results

            # if there were no results, do try Googling! :)
            else:
                # basically replaces spaces and colon with ' and '
                # eg. "genesis:hope or love"
                # becomes "genesis and hope and love"
                search_param = re.sub(r'(\:|\s{1,})', ' and ', search_param)
                results = Search.complex_search(search_param, book_requested['book'])
        else:
            return []

    @staticmethod
    def my_simple_duckduckgo_search(search_param, start=0, limit=30, book=None, simple_search=False):
        keywords = r''
        search_param = re.sub(r'(\.|\/|\s{2,}|\~|\-|\#|\@|\!|\&|\*|\"|\?|\\|\,|\_)', '', search_param)

        if simple_search is True:
            stop_words = Helper.extract_common_words()
            keywords = '|'.join([word for word in search_param.split(' ')
                                 if word not in stop_words])
        else:
            top_20_words = Helper.extract_common_words(search_param)
            # top_20_words => [{'the': 3}, {'their': 1}, {'text': 1}...]
            keywords = '|'.join([word[0] for word in
                                 [list(word_dict.keys()) for word_dict in top_20_words]])

        # keywords => (the|theirs|text|...)
        search = r'({search_regex})'.format(search_regex=keywords)
        results = Bible.objects.filter(bookname=book, keywords__regex=search)
        return results[start:(start+limit)]

    @staticmethod
    def complex_search(search_param, book=None):
        return Search.no_boolean_search(search_param, book)

    @staticmethod
    def no_boolean_search(search_param, book=None, start=0, limit=30):
        p = Parser()
        postgres_where_string = p.create_postgres_query_string(search_param)
        results = Bible.objects.extra(where=[postgres_where_string])
        return results[start:(start+limit)]
