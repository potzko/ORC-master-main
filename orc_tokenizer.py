import re

spec = [
    # white space
    (r'( +)'            , None),
    # new line
    (r'(\n)'            , None),
    # comments
    (r'(//[^\n]*)\n'    , None),
    (r'(/\*[^/]*/)'     , None),

    # int literal
    (r'([0-9]+)'        , 'literal_num'),
    # string literal
    (r'"([^"]*)"'       , 'literal_string'),
    # bool literal
    (r'(true|false)'    , 'literal_boolean'),

    # binary ops
    (r"(\+|-) "                  , 'op_+'),
    (r"(\*|\/|\%) "              , 'op_*'),
    (r"(<=|>=|==|!=|\|\||&&) "   , 'op_<'),
    (r"(<|>|\^) "                , 'op_<'),
    (r"(=|:=) "                     , 'op_='),

    # unary ops
    (r"(\+|-|&|\!|\*)"          , 'unary_op'),

    # delimiters
    (r"(\()"        , '('),
    (r"(\))"        , ')'),
    (r"(;)"         , ';'),
    (r"(:)"         , ':'),
    (r"({)"         , '{'),
    (r"(})"         , '}'),
    (r"(,)"         , ','),

    # key words
    (r"(if )"       , 'if'),
    (r"(else )"     , 'else'),
    (r"(while )"    , 'while'),
    (r"(return )"   , 'return'),
    (r"(let )"      , 'let'),
    (r"(fn )"       , 'fn'),


    # function call
    (r"([a-zA-Z_][a-zA-Z_0-9]*)\(", 'function_call'),

    # identifier
    (r"([a-zA-Z_][a-zA-Z_0-9]*)"  , 'identifier'),
]

class tokenizer:
    def __init__(self, st = '') -> None:
        self.reset(st)

    def reset(self, st):
        self.ind = 0
        self.st = st
        self.last = None

    def has_next_token(self):
        return self.next_token() != ('eof')

    def next_token(self, ret_group = 1):
        if self.last != None and ret_group == 1:
            return self.last
        
        st = self.st[self.ind:]
        matches = ((mat, exp, token_type) for exp, token_type in spec if (mat := re.match(exp, st)))
        for (mat, exp, token_type) in matches:
            if token_type == None:
                self.advance(len(mat[0]))
                return self.next_token()
            return (token_type, mat[ret_group])
        
        if self.ind >= len(self.st):
            return ('eof',)
        
        raise Exception(f'could not tokenize {st} {self.ind, len(self.st)}')
    
    def eat(self, token_type):
        ret = self.next_token(ret_group=1)
        if ret == None:
            a = f'unexpected file end, expected {token_type}'
            raise Exception(a)
        if ret[0] != token_type:
            a = 'unexpected token. expected {0} found {1} instead'.format(token_type, ret)
            raise Exception(a)

        token_length = len(self.next_token(ret_group=0)[1])
        self.advance(token_length)
        return ret[1]

    def advance(self, num):
        self.ind += num
        self.last = None