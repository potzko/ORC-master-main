import orc_parser

code = """
fn fibo x: {
    if x < 2 return x;
    return fibo(x - 1) + fibo(x - 2);
}
fn main:
    print(fibo(15));
"""

parser = orc_parser.parser(code)
program, functions = parser.program()
#print(functions)

class interpreter:
    def __init__(self, functions, node) -> None:
        self.func = {i[0][1]: [ii[1] for ii in i[1]] for i in functions}
        self.func_lookup = {i[1][1]: i[3] for i in node[1:]}
        self.inbuilt = {'print': print}

    def _get_num(self, num, type = 'u8'):
        return self.expression(('literal_num', num, type), {})

    def function(self, name, values):
        if name in self.inbuilt:
            return self.inbuilt[name](*values)
        if not name in self.func:
            raise Exception(f"function {name}, not found")
        node = self.func_lookup[name]
        signature = self.func[name]
        if len(values) != len(signature):
            raise Exception(f"function {name} got {len(values)} arguments, expected {len(signature)}")
        scope = {name: value for name, value in zip(signature, values)}
        return self.statement(node, scope)
    
    def statement(self, node, scope):
        if len(node) == 0:
            return
        primary, *secondary = node
        match primary:
            case 'let':
                name, value = secondary[0], secondary[1]
                if name in scope:
                    raise Exception("not supported")
                scope[name[1]] = self.expression(value, scope)
            case '=':
                scope[secondary[0][1]] = self.expression(secondary[1], scope)
            case 'return':
                return self.expression(secondary[0], scope)
            case 'if':
                if self.expression(secondary[0], scope) != 0:
                    return self.statement(secondary[1], scope)
                else:
                    return self.statement(secondary[2], scope)
            case 'statement_list':
                for i in secondary:
                    ret = self.statement(i, scope)
                    if ret is not None:
                        return ret
            case 'while':
                cond = self.expression(secondary[0], scope)
                while cond != 0:
                    ret = self.statement(secondary[1], scope)
                    if ret != None:
                        return ret
                    cond = self.expression(secondary[0], scope)
            case _:
                self.expression(node, scope)
    
    def expression(self, exp, scope):
        match exp[0]:
            case 'literal_num':
                return int(exp[1])
            case 'literal_string':
                return exp[1]
            case 'identifier':
                return scope[exp[1]]
            case '+':
                return self.expression(exp[1], scope) + self.expression(exp[2], scope)
            case '-':
                return self.expression(exp[1], scope) - self.expression(exp[2], scope)
            case '%':
                return self.expression(exp[1], scope) % self.expression(exp[2], scope)
            case '/':
                return self.expression(exp[1], scope) // self.expression(exp[2], scope)
            case '*':
                return self.expression(exp[1], scope) * self.expression(exp[2], scope)
            case '<':
                return 1 if self.expression(exp[1], scope) < self.expression(exp[2], scope) else 0
            case '<=':
                return 1 if self.expression(exp[1], scope) <= self.expression(exp[2], scope) else 0
            case '==':
                return 1 if self.expression(exp[1], scope) == self.expression(exp[2], scope) else 0
            case 'call':
                return self.function(exp[1], [self.expression(i, scope) for i in exp[2][1:]])
            case _:
                raise Exception(f"expression error, {exp[0]} not supported")


def construct_integer_type(byte_count):
    class ret:
        def __init__(self, value) -> None:
            print('init', value)
            if type(value) != int:
                value = value.value
            self.size = byte_count
            self.value = value % (2 ** byte_count)
        
        def __eq__(self, other) -> bool:
            return self.value == other.value
        def __add__(self, other):
            if self.size < other.size:
                return other + self
            return ret(self.value + other.value)
        def __sub__(self, other):
            if self.size < other.size:
                return other - self
            return ret(self.value - other.value)
        def __mul__(self, other):
            if self.size < other.size:
                return other * self
            return ret(self.value * other.value)
        def __floordiv__(self, other):
            if self.size < other.size:
                return other // self
            return ret(self.value // other.value)
        def __mod__(self, other):
            if self.size < other.size:
                return other % self
            return ret(self.value % other.value)
        def __str__(self) -> str:
            return f'{self.value}: u{self.size}'
    return ret
        
        
inter = interpreter(functions, program)
print(inter.function('main', []))