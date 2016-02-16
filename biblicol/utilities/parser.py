import collections
import re


class Parser(object):
    Token = collections.namedtuple('Token', ['typ', 'value'])

    def tokenize(self, statement):
        """
        Returns a list of [Token('typ', 'value'), Token()...]
        extracted from the statement provided
        """
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

    def create_postgres_query_string(self, statement, db_column='keywords'):
        """
        -------- SIMPLE ALTERNATIVE TO A FULLTEXT SEARCH in SQL --------
        *
        * NO FULLTEXT
        * NO BOOLEAN MODE
        * NO database modifications required
        * NO breaking - in searches or script
        *
        * @Params COVERED:
        *
        *  [x] -> love hope -- it searches for both or either
        *  [x] -> "sick love" ('' or "") -- searches for exact phrase
        *  [x] -> love and hate -- searches for stories containing both words.
        *  [x] -> love and hate or faith -- searches for stories containing "love" and "hate" and maybe "faith"
        *  [x] -> love and hate (and not|not) faith
        *  [x] -> love (and not|not) hope
        *  [x] -> "aids patient" or hiv
        *  [x] -> "aids patient" and hiv and not cancer
        *  [x] -> "aids patient" (and not|not) hiv or cancer
        *
        * "and" becomes "AND {database_column} ~* 'word'"
        * "or" becomes "OR {database_column} ~* 'word'"
        * "and not/not" becomes "AND NOT {database_column} ~* 'word'"
        *
        * STEPS to consider:
        * 1. Find the search parameter QUOTED
        * 2. Find if all occur in a text, not necessarily adjuscent (this AND that)
        * 3. Try find if either of the params are in a text (this OR that)
        *
        """
        pattern_replacements = {
            'and': 'AND {db_column} ~*',
            'and not': 'AND {db_column} NOT ~*',
            'or': 'OR {db_column} ~*',
            'or not':   'OR {db_column} NOT ~*',
            'not': 'AND {db_column} NOT ~*'
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
        query_token = 'keywords ~* ' + ' '.join(list(tokens))

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

        postgres_keywords_pattern = r'(\'(AND|OR|NOT)[\w\s\~\*\{\}]+\')+'
        # print(re.findall(postgres_keywords_pattern, query_token, re.I))
        psql_query_string = re.sub(postgres_keywords_pattern, unqoute_posgres_keywords, query_token)
        return psql_query_string.format(db_column=db_column)
