import collections
import re


class Parser(object):
    Token = collections.namedtuple('Token', ['typ', 'value'])

    def tokenize(self, statement):
        # keywords = {'AND', 'OR', 'AND NOT', 'OR NOT', 'NOT'}
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

        for mo in re.finditer(token_regex, statement):
            kind = mo.lastgroup
            # print('matched: ({}) lastgroup: {}'.format(mo.group(), mo.lastgroup))
            value = mo.group(kind)
            if kind in ['NEWLINE', 'SKIP', 'MISMATCH']:
                pass
            else:
                yield self.Token(kind, value)

    def return_postgres_regex_query(self, statement):
        tokens = list(self.tokenize(statement))
        build_regex_query = ''

        pattern_replacements = {
            'and': 'AND keywords ~*',
            'and not': 'AND keywords NOT ~*',
            'or': 'OR keywords ~*',
            'or not':   'OR keywords NOT ~*',
            'not': 'AND keywords NOT ~*'
        }

        # replace (and|or|not|and not|or not) with the
        # correct PostgresSQL regex annotation
        def replace_regex(matched):
            if matched.group(0) in pattern_replacements:
                return pattern_replacements[matched.group(0)]
            else:
                return matched.group(0)

        tokens = [re.sub(r'((and|or|not)(\snot)?)', replace_regex, token.value)
                  for token in tokens]

        for token in tokens:
            matches = list(re.finditer('\"', token))
            if len(matches) == 2:
                for x in matches:
                    token = ''.join([letter for letter in str(x.group())])

        return tokens


statement = '''
    Eugene says "This is a tokenizer"
    It shoud be able to match jack and jill or hannah and not mary
    or quoted words such as "a new hope"
    This seems a "dream come true" or not at all
    matching "quoted words" should be a breeze and not a "nightmare"
    niether should it be hard to match you and me or someone
    not bad at all eh!
'''

p = Parser()
# print(' '.join(list(p.return_postgres_regex_query(
#     "\"aids patient\" and hiv"))).replace('"', "("))

for token in p.tokenize(statement):
    print(token)
