import collections
import re


class Parser(object):
    Token = collections.namedtuple('Token', ['typ', 'value'])

    def tokenize(self, statement):
        token_specification = [
            ('NUMBER', r'\d+(\.\d*)?'),         # Integer or decimal number
            ('AND_NOT', r'(and\s+not)'),        # Match AND NOT
            ('OR_NOT', r'(or\s+not)'),
            ('AND', r'(and)'),
            ('OR', r'(or)'),
            ('NOT', r'(not)'),
            ('QOUTED', r'(\"[\w\s]+\")+'),       # Quoted words eg. "give hope"
            ('WORD', r'[A-Za-z\-\']+'),          # Word(s)
            ('OPERATORS', r'[+\-*/%]'),          # Arithmetic operators
            ('NEWLINE', r'\n'),                  # Line endings
            ('SKIP', r'[\s\t]+'),                # Skip over spaces and tabs
            ('MISMATCH', r'.'),                  # Any other character
        ]

        token_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
        # print(token_regex)

        for match_made in re.finditer(token_regex, statement):
            kind = match_made.lastgroup
            # print('matched: ({}) lastgroup: {}'.format(match_made.group(), match_made.lastgroup))
            value = match_made.group(kind)
            if kind in ['NEWLINE', 'SKIP', 'MISMATCH']:
                pass
            else:
                yield self.Token(kind, value)

    def create_postgres_query_string(self, statement):
        pattern_replacements = {
            'and': 'AND keywords ~*',
            'and not': 'AND keywords NOT ~*',
            'or': 'OR keywords ~*',
            'or not':   'OR keywords NOT ~*',
            'not': 'AND keywords NOT ~*'
        }

        # tokenize the statement given
        tokens = list(self.tokenize(statement))

        # replace (and|or|not|and not|or not) with the
        # correct PostgresSQL regex annotation
        def replace_conjunctions(matched):
            if matched.group(0) in pattern_replacements:
                return pattern_replacements[matched.group(0)]
            else:
                return matched.group(0)

        # wrap the each of the words in quotes
        tokens = [''.join(['\'', x, '\''])
                  for x in [re.sub(r'((and|or|not)(\snot)?)', replace_conjunctions, token.value)
                            for token in tokens]]

        # we need to loop through the tokens
        # converting the quotes into brackets (for regex)
        for index, token in enumerate(tokens):
            # find the quoted tokens
            if len(re.findall(r'\"', token)) is not 0:
                # split up the characters in the string
                characters = [x for x in token]

                # loop through them, replacing the 1st quote with '('
                # and the last one with ')'
                count = 0
                for i, ch in enumerate(characters):
                    # print(characters.index(ch, i-2 if i > 2 else i), i)
                    if ch == '"' and count is 0:
                        characters[i] = '('
                        count += 1
                    elif ch == '"' and count > 0:
                        characters[i] = ')'
                        # reset the counter, last half of quote replaced
                        count = 0

                # replace the quoted token with the transformed token
                tokens[index] = ''.join(characters)

        # string back the tokens back together
        # dont forget the 1st words is also part of the search
        query_token = '~* ' + ' '.join(list(tokens))

        # match for words sharing the same REGEX conjunctions
        # eg. 'Jesus' 'saves' 'people' 'OR keywords ~*' 'bread' '(jesus wept)'
        match_adjuscent_words = r'(\'\(?[\w\s]+\)?\')(\s+(\'\(?[\w\s]+\)?\'))+'
        adjuscent_words = re.finditer(match_adjuscent_words, query_token)

        def adjuscent_words_replacement(match_made):
            # remove all single quotes and break up the string by spaces
            adjuscent_words = match_made.group(0).replace('\'', '')
            string_break_down = [x for x in adjuscent_words]

            inside_brackets = False
            for index, letter in enumerate(string_break_down):
                # wrap the words in a bracket
                if index is 0:
                    string_break_down.insert(index, '\'(')
                    string_break_down.append(')\'')

                # are getting into brackets
                if letter is '(':
                    inside_brackets = True
                    continue
                elif letter is ')':
                    inside_brackets = False
                    continue

                # check if we are inside brackets
                # do not replace the spaces of the content wrapped
                # inside the brackets
                if inside_brackets is False and letter is ' ':
                    string_break_down[index] = '|'

            return ''.join(string_break_down)

        def unqoute_posgres_keywords(match_made):
            keyword = match_made.group(0)
            # print('keyword matched: %s' % keyword)
            return keyword.replace('\'', '')

        if len(list(adjuscent_words)) > 0:
            query_token = re.sub(match_adjuscent_words, adjuscent_words_replacement, query_token)
            # return query_token

        postgres_keywords_pattern = r'(\'(AND|OR|NOT)[\w\s\~\*]+\')+'
        # print(re.findall(postgres_keywords_pattern, query_token, re.I))
        psql_query_string = re.sub(postgres_keywords_pattern, unqoute_posgres_keywords, query_token)
        return psql_query_string


# Run some tests
p = Parser()
print(p.create_postgres_query_string('Jesus saves people or bread "jesus wept"'))
print(p.create_postgres_query_string('"he wept" or earth and heaven or hell or not "lost hope"'))
print(p.create_postgres_query_string('"sick love" ('' or "")'))
print(p.create_postgres_query_string('love and hate'))
print(p.create_postgres_query_string('love and hate or faith'))
print(p.create_postgres_query_string('love and hate and not faith'))
print(p.create_postgres_query_string('love not hope'))
print(p.create_postgres_query_string('"aids patient" or hiv'))
print(p.create_postgres_query_string('"aids patient" and hiv'))
print(p.create_postgres_query_string('"aids patient" not hiv'))
print(p.create_postgres_query_string('bread fish water and wine'))
