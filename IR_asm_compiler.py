import IR_compiler

class compiler:
    def __init__(self, func_signatures) -> None:
        self.func_signatures = func_signatures
        self.free_all_reg()
        self.state = {}

        self.Mov = self._construct('mov', 2)
        self.Add = self._construct('add', 2)
        self.Sub = self._construct('sub', 2)
        self.Or = self._construct('or', 2)
        self.Xor = self._construct('xor', 2)
        self.And = self._construct('and', 2)

        self.Mul = self._construct('mul', 1)
        self.Div = self._construct('div', 1)
        self.Cmp = self._construct('cmp', 2)
        self.Jnz = self._construct('jnz', 1)

        self.Sete = self._construct('sete', 1)
        self.Setg = self._construct('setg', 1)
        self.Setge = self._construct('setge', 1)

        self.Neg = self._construct('neg', 1)
        self.Not = self._construct('not', 1)

        self.Ret = self._construct('ret', 0)


    def _construct(self, st, val_count):
        def ret(*args):
            if len(args) != val_count:
                raise Exception(f'expected {val_count} variables, found {len(args)} instead')
            return f'{st} {", ".join([i for i in args])}\n'
        return ret

    def get(self, var):
        return self.state.get(var, False)

    def assign(self, var):
        if var[0] != '@':
            return var
        if not self.get(var):
            self.state[var] = self.aloc_reg()
        return self.get(var)

    def free_all_reg(self):
        self.regs = ['r8', 'r9', 'r10', 'r11', 'rcx']

    def aloc_reg(self):
        return self.regs.pop()
    
    def free_reg(self, reg):
        self.regs.append(reg)

    def compile(self, code):
        ret = '.code\n'
        proc = None
        lines = code.strip().split('\n')
        for line in lines:
            tmp = line.split(' ')
            op, data = tmp[0], tmp[1:]
            print(line, self.state)
            match op:
                case 'proc':
                    ret += f'{data[0]} proc\n'
                    proc = data[0]
                    self.free_all_reg()
                case 'endp':
                    ret += f'{data[0]} endp\n'
                    self.free_all_reg()
                case 'jmp':
                    ret += f'jmp {data[0]}\n'
                case 'mov':
                    a, b = self.assign(data[0]), self.assign(data[1])
                    ret += self.Mov(a, b)
                case 'neg':
                    a, b = self.assign(data[0]), self.assign(data[1])
                    ret += self.Mov(a, b)
                    ret += self.Neg(a)
                case 'boolean_not':
                    a, b = self.assign(data[0]), self.assign(data[1])
                    ret += self.Mov(a, b)
                    ret += self.Xor(a, '1')
                case 'add':
                    a, b, c = self.assign(data[0]), self.assign(data[1]), self.assign(data[2])
                    ret += self.Mov(a, b)
                    ret += self.Add(a, c)
                case 'sub':
                    a, b, c = self.assign(data[0]), self.assign(data[1]), self.assign(data[2])
                    ret += self.Mov(a, b)
                    ret += self.Sub(a, c)                    
                case 'or':
                    a, b, c = self.assign(data[0]), self.assign(data[1]), self.assign(data[2])
                    ret += self.Mov(a, b)
                    ret += self.Or(a, c)
                case 'xor':
                    a, b, c = self.assign(data[0]), self.assign(data[1]), self.assign(data[2])
                    ret += self.Mov(a, b)
                    ret += self.Xor(a, c)
                case 'eq':
                    a, b, c = self.assign(data[0]), self.assign(data[1]), self.assign(data[2])
                    self.Xor('rax', 'rax')
                    ret += self.Cmp(b, c)
                    ret += self.Sete('al')
                    ret += self.Mov(a, 'rax')
                case 'g':
                    a, b, c = self.assign(data[0]), self.assign(data[1]), self.assign(data[2])
                    self.Xor('rax', 'rax')
                    ret += self.Cmp(b, c)
                    ret += self.Setg('al')
                    ret += self.Mov(a, 'rax')                
                case 'ge':
                    a, b, c = self.assign(data[0]), self.assign(data[1]), self.assign(data[2])
                    self.Xor('rax', 'rax')
                    ret += self.Cmp(b, c)
                    ret += self.Setge('al')
                    ret += self.Mov(a, 'rax')
                case 'and':
                    a, b, c = self.assign(data[0]), self.assign(data[1]), self.assign(data[2])
                    ret += self.Mov(a, b)
                    ret += self.And(a, c)
                case 'mul':
                    a, b, c = self.assign(data[0]), self.assign(data[1]), self.assign(data[2])
                    ret += self.Mov('rax', b)
                    ret += self.Mul(c)
                    ret += self.Mov(a, 'rax')
                case 'div':
                    a, b, c = self.assign(data[0]), self.assign(data[1]), self.assign(data[2])
                    ret += self.Mov('rax', b)
                    ret += self.Div(c)
                    ret += self.Mov(a, 'rax')
                case 'mod':
                    a, b, c = self.assign(data[0]), self.assign(data[1]), self.assign(data[2])
                    ret += self.Mov('rax', b)
                    ret += self.Div(c)
                    ret += self.Mov(a, 'rdx')
                case 'ifnz':
                    a = self.assign(data[0])
                    ret += self.Cmp(a, '0')
                    ret += self.Jnz(data[1])
                case 'ret':
                    print('ret not implemented!')
                    ret += self.Mov('rax', self.get(data[0]))
                    ret += self.Ret()
                case _:
                    if len(op) != 0:
                        match op[0]:
                            case 'L':
                                ret += f'{op}:\n'
                            case 'nop':
                                ret += 'nop\n'
                    else:
                        raise Exception(f'{op} not supported yet')
        ret += 'END'
        return ret
                    
def compile(code):
    ir_code, funcs = IR_compiler.compile(code)
    print(IR_compiler.format_code(ir_code[0]))
    print(ir_code)
    #print(funcs)
    comp = compiler(funcs)
    return comp.compile(ir_code)


code = """
fn fibo: {
    return 5;
}
fn main: {
    
}
"""

print('\n\n\n', compile(code))