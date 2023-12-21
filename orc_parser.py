import orc_tokenizer as tokenizer

class parser:
    def __init__(self, code = '') -> None:
        self.tok = tokenizer.tokenizer(st = code)
    
    @property
    def lookahead(self):
        return self.tok.next_token()
    
    def eat(self, token_type):
        return self.tok.eat(token_type)
    
    def parse(self, code):
        self.tok = tokenizer.tokenizer(code)
        return self.program()

    def program(self):
        ret = self.function_decleration_block()
        fn_names = [(i[1], i[2]) for i in ret[1:]]
        return [ret, fn_names]
    
    def function_decleration_block(self):
        ret = ['fn_block']
        while self.lookahead[0] != 'eof':
            ret.append(self.function_decleration())
        return ret

    def function_decleration(self):
        self.eat('fn')
        name = self.identifier()
        if self.lookahead[0] == ':':
            self.eat(':')
            return ['fn', name, [], self.statement()]
        delimiter  = ':'
        if self.lookahead[0] == '(':
            self.eat('(')
            delimiter = ')'
        variables = [self.identifier()]
        while self.lookahead[0] != delimiter:
            self.eat(',')
            variables.append(self.identifier())
        if delimiter == ')':
            self.eat(')')
        self.eat(':')

        return ['fn', name, variables, self.statement()]

    def statement(self):
        match self.lookahead[0]:
            case ';'     : return self.empty_statement()
            case '{'     : return self.block_statement()
            case 'if'    : return self.if_statement()
            case 'while' : return self.while_statement()
            case 'let'   : return self.let_statement()
            case 'return': return self.return_statement()
            case _       : return self.expression_statement()

    def return_statement(self):
        self.eat('return')
        exp = self.expression()
        self.eat(';')
        return ['return', exp]

    def let_statement(self):
        self.eat('let')
        id = self.identifier()
        match self.lookahead[0]:
            case ';':
                self.eat(';')
                return ['let', id, ('literal_num', '0')]
            case 'op_=':
                self.eat('op_=')
                return ['let', id, self.expression_statement()]


    def block_statement(self):
        self.eat('{')
        ret = self.statement_list(delimiter='}')
        self.eat('}')
        return ret

    def statement_list(self, delimiter = 'eof'):
        ret = ['statement_list']
        while self.lookahead[0] != delimiter:
            ret.append(self.statement())
        return ret

    def if_statement(self):
        ret = self.conditional_statement('if')
        if self.lookahead[0] == 'else':
            self.eat('else')
            return [*ret, self.statement()]
        return [*ret, ()]

    def while_statement(self):
        return self.conditional_statement('while')
    
    def conditional_statement(self, token_type):
        self.eat(token_type)
        condition = self.expression()
        block = self.statement()
        return [token_type, condition, block]

    def empty_statement(self):
        self.eat(';')
        return tuple()

    def expression_statement(self):
        ret = self.expression()
        self.eat(';')
        return ret
    
    def unary_expression(self):
        if self.lookahead[0] == 'unary_op':
            return ['unary_op', self.eat('unary_op'), self.unary_expression()]
        return self.single_expression()

    def expression(self):
        return self.asignment_expression()
    
    def single_expression(self):
        match self.lookahead[0]:
            case 'literal_string'   : return self.literal()
            case 'literal_num'      : return self.literal()
            case 'literal_boolean'  : return self.literal()
            case 'unary_op'         : return self.unary_expression()
            case '('                : return self.paran_expression()
            case 'identifier'       : return self.identifier()
            case 'function_call'    : return self.function_call()

    def function_call(self):
        ret = ['call', self.eat('function_call'), self.comma_expression()]
        self.eat(')')
        return ret

    def identifier(self):
        ret = self.lookahead
        self.eat('identifier')
        return ret

    def comma_expression(self):
        ret = ['comma_expression', self.expression()]
        while self.lookahead[0] == ',':
            self.eat(',')
            ret.append(self.expression())
        return ret

    def asignment_expression(self):
        return self.binary_expression(self.boolean_expression, 'op_=')

    def boolean_expression(self):
        return self.binary_expression(self.addative_expression,'op_<')

    def addative_expression(self):
        return self.binary_expression(self.multiplicative_expression, 'op_+')
    
    def multiplicative_expression(self):
        return self.binary_expression(self.single_expression, 'op_*')

    def paran_expression(self):
        self.eat('(')
        ret = self.expression()
        self.eat(')')
        return ret

    def binary_expression(self, op_type, op_token):
        left = op_type()
        while self.lookahead[0] == op_token:
            operator = self.eat(op_token)
            right = op_type()
            left = [operator, left, right]
        return left

    def literal(self):
        if not self.lookahead[0].startswith('literal'):
            raise Exception(f"expected literal found {self.lookahead[0]}")
        match self.lookahead[0]:
            case 'literal_boolean':
                return ['literal_num', 1 if self.eat('literal_boolean') == 'true' else 0]
            case 'literal_string':
                return self.eat('literal_string')
            case 'literal_num':
                num = self.eat('literal_num')
                return ['literal_num', num]
            case _:
                raise Exception(f"expected literal found {self.lookahead[0]}")


            
        
code = """
1 + 2 + 4 * 4 - (5 * (2 - 1))
"""

def pprint(ast):
    import json
    print(json.dumps(ast, indent=4))
if __name__ == '__main__':
    p = parser(code)
    pprint(p.expression())

