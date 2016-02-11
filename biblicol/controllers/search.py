import re
from django.shortcuts import render
from django.http import HttpResponse


def index(request, param='', pageno=1):
    # if nothing has been passed to the search, back to home page
    if param is '':
        return render(request, 'index.html', {})

    # remove underscores from smart URL
    param = re.sub(r'_{1,}', ' ', param, flags=re.IGNORECASE)

    # and double spaces
    param = re.sub(r'(\s{2,}|_)', ' ', param, flags=re.IGNORECASE)

    searchterm = param.lower().split(' ')
    for word in searchterm:
        num_of_same_words = [x for x in searchterm if x == word]

        if len(num_of_same_words) > 1:
            searchterm = [x for x in searchterm if x != word]
            searchterm.append(word)

    searchterm = ' '.join([str(x) for x in searchterm])
    param = searchterm

    return HttpResponse("The search param sent is %s" % searchterm)
