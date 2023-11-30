import IR_compiler

class compiler:
    def __init__(self, func_signatures) -> None:
        self.func_signatures = func_signatures
        self.free_all_reg()
        self.state = {}

        self.Mov = self._construct('mov', 2)
        self.Lea = self._construct('lea', 2)
        self.Deref = lambda a, b: f'mov {a}, [{b}]\n'
        self.Write = lambda a, b: f'mov [{a}], {b}\n'

        self.Add = self._construct('add', 2)
        self.Sub = self._construct('sub', 2)
        self.Or = self._construct('or', 2)
        self.Xor = self._construct('xor', 2)
        self.And = self._construct('and', 2)

        self.Mul = self._construct('imul', 1)
        self.Div = self._construct('idiv', 1)
        self.Cmp = self._construct('cmp', 2)
        self.Jnz = self._construct('jnz', 1)

        self.Sete = self._construct('sete', 1)
        self.Setg = self._construct('setg', 1)
        self.Setge = self._construct('setge', 1)

        self.Neg = self._construct('neg', 1)
        self.Not = self._construct('not', 1)

        self.Push = self._construct('push', 1)
        self.Pop = self._construct('pop', 1)
        self.Call = self._construct('call', 1)

        self.Ret = self._construct('ret', 0)
        self.Nop = self._construct('nop', 0)


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
        self.regs = ['r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15', 'rbx', 'rcx']
        self.state = {}
    
    def input_regs(self, num):
        return ['rcx', 'rdx', 'r8', 'r9'][:num]

    def aloc_reg(self):
        return self.regs.pop()
    
    def free_reg(self, *args):
        for reg in args:
            self.regs.append(reg)

    def compile(self, code):
        ret = '.code\n'
        proc = None
        lines = code.strip().split('\n')
        for line in lines:
            tmp = line.split(' ')
            op, data = tmp[0], tmp[1:]
            match op:
                case 'proc':
                    self.free_all_reg()
                    ret += f'{data[0]} proc\n'
                    ret += self.Push('rbx')
                    proc = data[0]
                    print(self.func_signatures[proc])
                    for i, reg in enumerate(self.input_regs(self.func_signatures[proc])):
                        ret += self.Mov(self.assign(f'@F{i}'), reg)
                case 'endp':
                    ret += self.Pop('rbx')
                    ret += f'{data[0]} endp\n'
                    self.free_all_reg()
                case 'nop':
                    ret += self.Nop()
                case 'jmp':
                    ret += f'jmp {data[0]}\n'
                case 'lea':
                    a, b = self.assign(data[0]), self.assign(data[1])
                    ret += self.Lea(a, b)
                case 'read':
                    a, b = self.assign(data[0]), self.assign(data[1])
                    ret += self.Deref(a, b)
                case 'write':
                    a, b = self.assign(data[0]), self.assign(data[1])
                    ret += self.Write(a, b)
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
                    ret += self.Xor('rax', 'rax')
                    ret += self.Cmp(b, c)
                    ret += self.Setg('al')
                    ret += self.Mov(a, 'rax')                
                case 'ge':
                    a, b, c = self.assign(data[0]), self.assign(data[1]), self.assign(data[2])
                    ret += self.Xor('rax', 'rax')
                    ret += self.Cmp(b, c)
                    ret += self.Setge('al')
                    ret += self.Mov(a, 'rax')
                case 'and':
                    a, b, c = self.assign(data[0]), self.assign(data[1]), self.assign(data[2])
                    ret += self.Mov(a, b)
                    ret += self.And(a, c)
                case 'mul':
                    a, b, c = self.assign(data[0]), self.assign(data[1]), self.assign(data[2])
                    ret += self.Push('rdx')
                    ret += self.Mov('rax', b)
                    ret += self.Mul(c)
                    ret += self.Mov(a, 'rax')
                    ret += self.Pop('rdx')
                case 'div':
                    a, b, c = self.assign(data[0]), self.assign(data[1]), self.assign(data[2])
                    ret += self.Push('rdx')
                    ret += self.Xor('rdx', 'rdx')
                    ret += self.Mov('rax', b)
                    ret += self.Div(c)
                    ret += self.Mov(a, 'rax')
                    ret += self.Pop('rdx')
                case 'mod':
                    a, b, c = self.assign(data[0]), self.assign(data[1]), self.assign(data[2])
                    ret += self.Push('rdx')
                    ret += self.Xor('rdx', 'rdx')
                    ret += self.Mov('rax', b)
                    ret += self.Div(c)
                    ret += self.Mov(a, 'rdx')
                    ret += self.Pop('rdx')
                case 'ifnz':
                    a = self.assign(data[0])
                    ret += self.Cmp(a, '0')
                    ret += self.Jnz(data[1])
                case 'ret':
                    print('ret not implemented!')
                    ret += self.Mov('rax', self.assign(data[0]))
                    ret += self.Pop('rbx')
                    ret += self.Ret()
                case 'fcall':
                    ret_reg, name, inputs = data[0], data[1], data[2:] 
                    regs = [i for i in self.state.values()]
                    for i in regs:
                        ret += self.Push(i)
                    for value, target in zip([self.get(i) for i in inputs] ,self.input_regs(self.func_signatures[name])):
                        ret += self.Mov(target, value)
                    ret += self.Call(name)
                    for i in reversed(regs):
                        ret += self.Pop(i)
                    ret += self.Mov(self.assign(ret_reg), 'rax')
                    print(regs)                    
                case _:
                    if len(op) != 0:
                        match op[0]:
                            case 'L':
                                ret += f'{op}:\n'
                            case 'nop':
                                ret += 'nop\n'
                            case _:
                                raise Exception(f'{op} not supported yet')
                    else:
                        raise Exception(f'{op} not supported yet')
        ret += 'END'
        return ret
                    
def compile(code):
    ir_code, funcs = IR_compiler.compile(code)
    print(IR_compiler.format_code(ir_code))
    #print(funcs)
    comp = compiler(funcs)
    return comp.compile(ir_code)


code = """
fn fibo x: {
    if x < 2 return x;
    return fibo(x - 2) + fibo(x - 1);
}
fn is_prime num: {
    if num < 2 return false;
    let a = 2;
    while a < num / 2 {
        if num % a == 0 return false;
        a = a + 1;
    }
    return true;
}
fn power a, b: {
    if b == 0 return 1;
    let pow_tmp = power(a, b / 2);
    let remainder_tmp = 1;
    if b % 2 == 1 remainder_tmp = a;
    return pow_tmp * pow_tmp * remainder_tmp;
}
fn read_a arr, len: {
    while len > 0 {
        len = len - 1;
        let tmp = ind(arr, len);
        tmp := len;
    }
    return 0;
}
fn ind a, b: return a + 8 * b;
fn slow_sort arr, len: {
    if len < 2 return 0;
    slow_sort(ind(arr, 1), len - 1);
    if compare(arr, 1, 0) {
        swap(arr, 0, 1);
        slow_sort(ind(arr, 1), len - 1);
    }
    return 0;
}
fn swap arr, a, b: {
    let tmp_a = *ind(arr, a);
    let tmp_ind = ind(arr, a);
    tmp_ind := *ind(arr, b);
    tmp_ind = ind(arr, b);
    tmp_ind := tmp_a;
    return 0;
}
fn compare arr, a, b: {
    let a_val = *ind(arr, a);
    let b_val = *ind(arr, b);
    return a_val < b_val;
}
fn partition arr, len: {
    let val = *ind(arr, len - 1);
    let i = 0;
    let ii = 0;
    while i < len - 1 {
        let tmp = *ind(arr, i);
        if compare(arr, val, tmp) {
            swap(arr, i, ii);
            ii = ii + 1;
        }
        i = i + 1;
    }
    swap(arr, ii, len - 1);
    return 0;
}
"""



if __name__ == "__main__":
    tmp = compile(code)
    print('\n\n\n')
    print(tmp)
    import pyperclip
    pyperclip.copy(tmp)
