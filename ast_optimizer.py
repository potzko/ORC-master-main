import orc_interpreter
import orc_parser
class ast_optimiser:
    def __init__(self, code) -> None:
        parser = orc_parser.parser(code)
        program, functions = parser.program()
        self.interpreter = orc_interpreter.interpreter(functions, program)

    def cull(self, tree):
        return ['literal_num', self.interpreter.expression(tree, {})]

    def cull_constant_exp_rec(self, tree):
        if not tree:
            return False
        primary, rest = tree[0], tree[1:]
        print(primary, rest)
        match primary:
            case 'fn_block' | 'statement_list' | 'if' | 'while' | 'return':
                for ind, val in enumerate(rest):
                    if self.cull_constant_exp_rec(val):
                        tree[ind + 1] = self.cull(val)
                return False
            
            case 'fn':
                if self.cull_constant_exp_rec(rest[2]):
                    tree[3] = self.cull(tree[3])
                    return True
                return False

            case 'let':
                self.cull_constant_exp_rec(rest[1])
                return False

            case '+' | '-' | '*' | '/' | '%' | '<' | '<=' | ">" | ">=" | "==" | "!=":
                left_opt = self.cull_constant_exp_rec(rest[0])
                right_ops = self.cull_constant_exp_rec(rest[1])
                if left_opt:
                    tree[1] = self.cull(tree[1])
                if right_ops:
                    tree[2] = self.cull(tree[2])
                return left_opt and right_ops
            
            case 'call':
                self.cull_constant_exp_rec(rest[1])
                return False
            
            case 'comma_expression':
                flag = True
                for ind, val in enumerate(rest):
                    print(val)
                    if self.cull_constant_exp_rec(val):
                        tree[ind + 1] = self.cull(tree[ind + 1])
                    else:
                        flag = False
                return flag 

                return flag
            case 'literal_num':
                return True
            case 'literal_bool':
                return True
            case 'identifier':
                return False
            case _:
                return False
                
def optimise(code):
    parser = orc_parser.parser(code)
    program, functions = parser.program()
    opt = ast_optimiser(code)
    opt.cull_constant_exp_rec(program)
    return program
                    
code = """
fn fibo x: {
    if x < 2 return x;
    return fibo(x - 1) + fibo(x - 2);
}
fn power a, b: {
    if b == 0 return 1;
    let pow_tmp = power(a, b / 2);
    let remainder_tmp = 1;
    if b % 2 == 1 remainder_tmp = a;
    return pow_tmp * pow_tmp * remainder_tmp;
}
fn tetrate a,b: {
    if b == 0 return 1;
    let ret = a;
    while b > 1 {
        ret = power(ret, a);
        b = b - 1;
    }
    return ret;
}
fn main:
    return tetrate(2, 4) - 1;
"""
optimise(code)



