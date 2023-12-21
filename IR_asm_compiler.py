import IR_compiler

class compiler:
    def __init__(self) -> None:
        self.func_signatures = {}
        self.free_all_reg()
        self.state = {}
        self.local_vals_over = 0

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

    def get_signatures(self, header):
        for i in header.split('\n'):
            name, count =  i.split(' ')[0:2]
            count = int(count)
            self.func_signatures[name] = count

    def _construct(self, st, val_count):
        def ret(*args):
            if len(args) != val_count:
                raise Exception(f'expected {val_count} variables, found {len(args)} instead')
            return f'{st} {", ".join([i for i in args])}\n'
        return ret

    def get(self, var):
        return self.state.get(var, False)
    
    def reversed_get(self, addres):
        for var, addr in self.state.items():
            if addr == addres:
                return var
        return False

    def assign(self, var):
        if var[0] != '@':
            return var
        if not self.get(var):
            if len(self.regs) > 0:
                self.state[var] = self.aloc_reg()
            else:
                self.state[var] = self.aloc_mem()
        return self.get(var)
    
    def assign_mem(self, var):
        if not self.get(var):
            self.state[var] = self.aloc_mem()
        return self.get(var)

    def assign_reg(self, var):
        a = self.assign(var)
        if self.is_reg_name(a):
            return (a, '')

        return ('r15', self.Mov(a, 'r15'))

    def is_reg_name(self, name):
        return not '[' in name

    def is_reg_var(self, var):
        return self.get(var) and self.is_reg_name(self.get(var))

    def free_all_reg(self):
        self.regs = self.get_valid_regs()
        self.state = {}
        self.local_vals_over = 0

    def input_regs(self, num):
        ret = ['rcx', 'rdx', 'r8', 'r9'][:num]
        for i in range(num - 4):
            ret.append(f'QWORD PTR [rbp + {48 + i * 8}]')
        return ret
    
    def get_valid_regs(self):
        #return ['r14', 'r9', 'r8', 'rbx', 'rcx']
        return ['r10', 'r11', 'r12', 'r13', 'r14', 'r9', 'r8', 'rbx', 'rcx'] 

    def aloc_reg(self):
        return self.regs.pop()
    
    def aloc_mem(self):
        self.local_vals_over += 1
        return f'QWORD PTR [rbp - {8 * self.local_vals_over}]'
    
    def free_reg(self, *args):
        for reg in args:
            self.regs.append(reg)

    def compile(self, code):
        ret = '.code\n'
        proc = None
        lines = code.strip().split('\n')
        for ind, line in enumerate(lines):
            tmp = line.split(' ')
            op, data = tmp[0], tmp[1:]
            match op:
                case 'proc':
                    self.free_all_reg()
                    ret += f'{data[0]} proc\n'
                    ret += self.Push('rbp')
                    ret += self.Mov('rbp', 'rsp')
                    proc = data[0]
                    input_var_count = self.func_signatures[proc]
                    input_vars = [f'@F{i}' for i in range(input_var_count)]
                    self.state = {var_name: var for var_name, var in zip(input_vars, self.input_regs(input_var_count))}
                    for i in range(min(4, input_var_count)):
                        self.aloc_reg()
                    for i in self.get_valid_regs():
                        ret += self.Mov(self.assign_mem(f'tmp_{i}'), i)
                    if input_var_count >= 2:
                        ret += self.Mov('rbx', 'rdx')
                        self.state['@F1'] = 'rbx'

                case 'endp':
                    ret += f'{data[0]} endp\n'
                    self.free_all_reg()
                case 'nop':
                    ret += self.Nop()
                case 'jmp':
                    ret += f'jmp {data[0]}\n'
                case 'lea':
                    a, fin = self.assign_reg(data[0])
                    b = self.assign(data[1])
                    ret += self.Lea(a, b)
                    ret += fin
                case 'read':
                    a, fin = self.assign_reg(data[0])
                    b = self.assign(data[1])
                    ret += self.Mov('rax', b)
                    ret += self.Deref(a, 'rax')
                    ret += fin
                case 'write':
                    a, fin = self.assign_reg(data[0])
                    b = self.assign(data[1])
                    ret += self.Mov('rax', b)
                    ret += self.Write(a, 'rax')
                    ret += fin
                case 'mov':
                    a, fin = self.assign_reg(data[0])
                    b = self.assign(data[1])
                    ret += self.Mov(a, b)
                    ret += fin
                case 'neg':
                    a, fin = self.assign_reg(data[0])
                    b = self.assign(data[1])
                    ret += self.Mov(a, b)
                    ret += self.Neg(a)
                    ret += fin
                case 'boolean_not':
                    a, fin = self.assign_reg(data[0])
                    b = self.assign(data[1])
                    ret += self.Mov(a, b)
                    ret += self.Xor(a, '1')
                    ret += fin
                case 'add':
                    a, fin = self.assign_reg(data[0])
                    b, c = self.assign(data[1]), self.assign(data[2])
                    ret += self.Mov(a, b)
                    ret += self.Add(a, c)
                    ret += fin
                case 'sub':
                    a, fin = self.assign_reg(data[0])
                    b, c = self.assign(data[1]), self.assign(data[2])
                    ret += self.Mov(a, b)
                    ret += self.Sub(a, c)
                    ret += fin                    
                case 'or':
                    a, fin = self.assign_reg(data[0])
                    b, c = self.assign(data[1]), self.assign(data[2])
                    ret += self.Mov(a, b)
                    ret += self.Or(a, c)
                    ret += fin
                case 'xor':
                    a, fin = self.assign_reg(data[0])
                    b, c = self.assign(data[1]), self.assign(data[2])
                    ret += self.Mov(a, b)
                    ret += self.Xor(a, c)
                    ret += fin
                case 'eq':
                    a, b, c = self.assign(data[0]), self.assign(data[1]), self.assign(data[2])
                    ret += self.Xor('rax', 'rax')
                    ret += self.Mov('r15', b)
                    ret += self.Cmp('r15', c)
                    ret += self.Sete('al')
                    ret += self.Mov(a, 'rax')
                case 'g':
                    a, b, c = self.assign(data[0]), self.assign(data[1]), self.assign(data[2])
                    ret += self.Xor('rax', 'rax')
                    ret += self.Mov('r15', b)
                    ret += self.Cmp('r15', c)
                    ret += self.Setg('al')
                    ret += self.Mov(a, 'rax')             
                case 'ge':
                    a, b, c = self.assign(data[0]), self.assign(data[1]), self.assign(data[2])
                    ret += self.Xor('rax', 'rax')
                    ret += self.Mov('r15', b)
                    ret += self.Cmp('r15', c)
                    ret += self.Setge('al')
                    ret += self.Mov(a, 'rax')
                case 'and':
                    a, fin = self.assign_reg(data[0])
                    b, c = self.assign(data[1]), self.assign(data[2])
                    ret += self.Mov(a, b)
                    ret += self.And(a, c)
                    ret += fin
                case 'mul':
                    a, b, c = self.assign(data[0]), self.assign(data[1]), self.assign(data[2])
                    ret += self.Mov('r15', 'rdx')
                    ret += self.Mov('rax', b)
                    ret += self.Mul(c)
                    ret += self.Mov(a, 'rax')
                    ret += self.Mov('rdx', 'r15')
                case 'div':
                    a, b, c = self.assign(data[0]), self.assign(data[1]), self.assign(data[2])
                    ret += self.Mov('r15', 'rdx')
                    ret += self.Xor('rdx', 'rdx')
                    ret += self.Mov('rax', b)
                    ret += self.Div(c)
                    ret += self.Mov(a, 'rax')
                    ret += self.Mov('rdx', 'r15')
                case 'mod':
                    a, b, c = self.assign(data[0]), self.assign(data[1]), self.assign(data[2])
                    ret += self.Mov('r15', 'rdx')
                    ret += self.Xor('rdx', 'rdx')
                    ret += self.Mov('rax', b)
                    ret += self.Div(c)
                    ret += self.Mov(a, 'rdx')
                    ret += self.Mov('rdx', 'r15')
                case 'ifnz':
                    a = self.assign(data[0])
                    ret += self.Cmp(a, '0')
                    ret += self.Jnz(data[1])
                case 'ret':
                    ret += self.Mov('rax', self.assign(data[0]))
                    for i in self.get_valid_regs():
                        ret += self.Mov(i, self.get(f'tmp_{i}'))
                    ret += self.Mov('rsp', 'rbp')
                    ret += self.Pop('rbp')
                    ret += self.Ret()
                case 'fcall':
                    ret_reg, name, inputs = data[0], data[1], data[2:] 
                    for i in self.input_regs(4):
                       ret += self.Mov(self.assign_mem(f'rec_tmp_{i}'), i)
                    stack_space_required = 8 * (self.local_vals_over + max(self.func_signatures[name] - 4, 0)) + 32
                    ret += self.Sub('rsp', str(stack_space_required))
                    for value, target in zip([self.get(i) for i in inputs], self.input_regs(self.func_signatures[name])):
                        if self.is_reg_name(value) or self.is_reg_name(target):
                            ret += self.Mov(target.replace('rbp', 'rsp'), value)
                        else:
                            ret += self.Mov('r15', value)
                            ret += self.Mov(target.replace('rbp', 'rsp'), 'r15')
                    ret += self.Add('rsp', '16')
                    ret += self.Call(name)
                    for i in self.input_regs(4):
                        ret += self.Mov(i, self.get(f'rec_tmp_{i}'))
                    ret += self.Mov(self.assign(ret_reg), 'rax')
                    ret += self.Add('rsp', str(stack_space_required - 16))


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
    a = IR_compiler.compile(code).split('\n\n')
    header, ir_code = a[0], a[1]
    #print(ir_code)
    #print(funcs)
    comp = compiler()
    comp.get_signatures(header)
    return comp.compile(ir_code)


code = """
fn ind a, b: return a + 8 * b;
fn cmp_lt arr, a, b: {
    let a_val = *ind(arr, a);
    let b_val = *ind(arr, b);
    return a_val < b_val;
}
fn cmp_le arr, a, b: {
    let a_val = *ind(arr, a);
    let b_val = *ind(arr, b);
    return a_val <= b_val;
}
fn read arr, index: {
    return *ind(arr, index);
}
fn write arr, index, value: {
    let mem_slot = ind(arr, index);
    mem_slot := value;
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
fn partition arr, len: {
    let pivot = read(arr, len - 1);
    let i = 0;
    let small_ind = 0;
    while i < len - 1 {
        if cmp_lt(arr, i, len - 1) {
            swap(arr, i, small_ind);
            small_ind = small_ind + 1;
        }
        i = i + 1;
    }
    swap(arr, len - 1, small_ind);
    return small_ind;
}
fn quick_sort arr, len: {
    if len < 2 {
        return 0;
    }
    let split = partition(arr, len);
    quick_sort(arr, split);
    quick_sort(ind(arr, split + 1), len - split - 1);
    return 0;
}
"""

if __name__ == "__main__":
    tmp = compile(code)
    #print('\n\n\n')
    #print(tmp)
    import pyperclip
    pyperclip.copy(tmp)
