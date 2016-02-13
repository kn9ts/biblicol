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
