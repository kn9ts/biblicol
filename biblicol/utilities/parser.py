import collections
import re


class Parser(object):
    Token = collections.namedtuple('Token', ['typ', 'value'])

    def tokenize(self, statements):
        # keywords = {'AND', 'OR', 'AND NOT', 'OR NOT', 'NOT'}
        token_specification = [
            ('NUMBER', r'\d+(\.\d*)?'),         # Integer or decimal number
            ('AND_NOT', r'(and\s+not)'),        # Match AND NOT
            ('OR_NOT', r'(or\s+not)'),
            ('AND', r'(and)'),
            ('OR', r'(or)'),
            ('NOT', r'(not)'),
            ('QOUTED', r'(\"[\w\s]+\")+'),  # Quoted words eg. "give hope"
            ('WORD', r'[A-Za-z\-\']+'),          # Word(s)
            ('OPERATORS', r'[+\-*/%]'),          # Arithmetic operators
            ('NEWLINE', r'\n'),                  # Line endings
            ('SKIP', r'[\s\t]+'),                # Skip over spaces and tabs
            ('MISMATCH', r'.'),                  # Any other character
        ]

        token_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
        # print(token_regex)

        for mo in re.finditer(token_regex, statements):
            kind = mo.lastgroup
            # print('matched: ({}) lastgroup: {}'.format(mo.group(), mo.lastgroup))
            value = mo.group(kind)
            if kind in ['NEWLINE', 'SKIP', 'MISMATCH']:
                pass
            else:
                yield self.Token(kind, value)

statements = '''
    "Benedictial man" Eugene is trying to match jack and jill or hannah and not mary
    but he has kinda "lost hope"
    This is a "dream come true" or not at all
    matching "great hope" should be a breeze and not a "nightmare"
    niether should it be "disturbing" or not facinating
    not bad at all
        total := total + price * quantity;
        tax := price * 0.05;
    ENDIF;
'''

p = Parser()
for token in p.tokenize(statements):
    print(token)
