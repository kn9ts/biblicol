import re
import operator


class Helper(object):
    default_book = "matthew"

    books = {
        "total_books": 66,
        "old_testament": [
            "genesis", "exodus", "leviticus", "numbers", "deuteronomy",
            "joshua", "judges", "ruth", "samuel", "2 samuel",
            "1 kings", "kings", "chronicles", "2 chronicles",
            "ezra", "nehemiah", "esther", "job", "psalms", "proverbs",
            "ecclesiastes", "song of solomon", "isaiah", "jeremiah",
            "lamentations", "ezekiel", "daniel", "hosea", "joel",
            "amos", "obadiah", "jonah", "micah", "nahum", "habakkuk",
            "zephaniah", "haggai", "zechariah", "malachi"
        ],
        'new_testament': [
            "matthew", "mark", "luke", "john", "acts", "romans",
            "corinthians", "2 corinthians", "galatians", "ephesians",
            "philippians", "colossians", "thessalonians", "2 thessalonians",
            "timothy", "2 timothy", "titus", "philemon", "hebrew",
            "james", "1 peter", "peter", "john", "2 john", "3 john",
            "jude", "revelation"
        ]
    }

    @staticmethod
    def is_book_in_Bible(bookname):
        return bookname in Helper.books['old_testament'] \
            or bookname in Helper.books['new_testament']

    @staticmethod
    def get_the_book_requested(search_param, starts_with_no=False):
        break_down = {}
        splitted_param = search_param.split(' ')

        # usual books eg. exodus 1:1-15, john 3:16-18
        # splitted_param ==> ['John', '3:16-18'] Indexes(0,1)
        if starts_with_no is False:
            if ':' in search_param:
                chapter_and_verses = splitted_param[1].split(':')
                break_down['book'] = splitted_param[0]
                break_down['chapter'] = chapter_and_verses[0]
                break_down['verses'] = chapter_and_verses[1]
            else:
                break_down['book'] = splitted_param[0]

                if len(splitted_param) > 1:
                    break_down['chapter'] = splitted_param[1]

        # splitted_param ==> ['2(nd)', 'John', '3:16-18'] Indexes(0,1,2)
        else:
            book_number = ''
            # for books that starts or
            # ends with no - 1[st, nd, rd, th] john 1:1-3
            match_made = re.match(r'^\d(\w{1,})?', search_param)
            if match_made is not None:
                # remove the [st, nd, rd...]
                book_number = re.sub(r'[A-Za-z]{1,}', '', match_made.group())

            # get the book & numeric part, check for 1ti 1:1, 1pe 1:12
            size_of_splits = len(splitted_param)

            if size_of_splits >= 2:
                # get the verse request part
                verse_part = splitted_param[2] if size_of_splits is 3 else splitted_param[1]
                chapter_and_verses = verse_part.split(':')

                if size_of_splits is 3:
                    book = book_number + ' ' + splitted_param[1]
                else:
                    book = book_number + ' ' + re.sub(r'\d{1,}', '', splitted_param[0])

                # Clean abbreviated book params eg. 1 kg, 1 co
                break_down['book'] = book
                break_down['chapter'] = chapter_and_verses[0]
                if len(chapter_and_verses) is 2:
                    break_down['verses'] = chapter_and_verses[1]

            elif size_of_splits is 1:
                break_down['book'] = book_number + ' ' + re.sub(r'\d{1,}', '', splitted_param[0])

        return break_down

    @staticmethod
    def extract_common_words(text=None):
        """
        Counts the occurence of each word in the text provided
        returning the top 20 words ordered in decending order of
        their number of occurences
        """
        stop_words = []

        if text is not None:
            # strip out these symbols for spaces or nothing
            text = re.sub(r'(\.|\/|\s{1,}|\~|\-|\#|\@|\!|\&|\*|\"|\?|\\\\|\,|\_)+', ' ', text)
            text = re.sub(r'([0-9]+\/[0-9]+:?|\')+', '', text)
            text = re.sub(r'[^a-zA-Z0-9 -]', '', text.strip()).lower()

            # get words that
            # are not empty strings
            # are more than 3 characters long
            # are not stop words
            appropriate_search_words = [x for x in text.split()
                                        if len(x) > 2 and x is not '' and
                                        x not in stop_words]

            word_count = {}
            # count how many times a word appears in the sentense
            for word in appropriate_search_words:
                # if more than one time, count up (x+1)
                word_count[word] = word_count[word] + 1 \
                    if word in word_count else 1

            # sort by the words that appear most
            sorted_word_count = sorted(
                word_count.items(),
                key=operator.itemgetter(1),
                reverse=True
            )

            # return only the top most 20 [{word: count}...] objects
            sorted_word_count = [{x[0]:x[1]} for x in sorted_word_count[:20]]
            return sorted_word_count
        else:
            return stop_words
