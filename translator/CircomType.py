from enum import Enum

class Opcode(Enum):
    OR = 1
    AND = 2
    EQ = 3
    NEQ = 4
    LT = 5
    GT = 6
    LE = 7
    GE = 8
    OR_BIT = 9
    AND_BIT = 10
    SHIFTL = 11
    SHIFTR = 12
    PLUS = 13
    MINUS = 14
    MUL = 15
    DIV = 16
    INTDIV = 17
    MOD = 18
    POW = 19
    XOR_BIT = 20
    NOT = 21
    COMPLEMENT = 22
    ASSIGN_VAR = 23
    ASSIGN_SIGNAL = 24
    ASSIGN_CONSTRAINT_SIGNAL = 25
    RIGHT_ASSIGN_SIGNAL = 26
    RIGHT_ASSIGN_CONSTRAINT_SIGNAL = 27
    CONSTRAINT_EQUALITY = 28
    TERNARY = 29
    INTDIVEQ = 30
    POWEQ = 31
    PLUSEQ = 32
    MINUSEQ = 33
    MULTEQ = 34
    DIVEQ = 35
    MODEQ = 36
    SHIFTLEQ = 37
    SHIFTREQ = 38
    AND_BITEQ = 39
    OR_BITEQ = 40
    XOR_BITEQ = 41
    INCREMENT = 42
    DECREMENT = 43
    ARR = 44

def dispatchExpression(node):
    if node[0] == 'expression0':
        return CircomTerminal.from_json(node)
    elif len(node) > 2:
        match node:
            case ['expression1', *_]:
                return CircomArr.from_json(node)
            case ['expression2', *_]:
                return CircomPrefix.from_json(node)
            case ['expression3', *_]:
                return CircomPow.from_json(node)
            case ['expression4', *_]:
                return CircomMulDiv.from_json(node)
            case ['expression5', *_]:
                return CircomAddSub.from_json(node)
            case ['expression6', *_]:
                return CircomShift.from_json(node)
            case ['expression7', *_]:
                return CircomAndBit.from_json(node)
            case ['expression8', *_]:
                return CircomXorBit.from_json(node)
            case ['expression9', *_]:
                return CircomOrBit.from_json(node)
            case ['expression10', *_]:
                return CircomCompare.from_json(node)
            case ['expression11', *_]:
                return CircomAnd.from_json(node)
            case ['expression12', *_]:
                return CircomOr.from_json(node)
            case ['expression13', *_]:
                return CircomTernary.from_json(node)
    else:
        return dispatchExpression(node[1])

class CircomNode:
    def __init__(self):
        pass
    
    def to_compute(self):
        return ''
    
    def to_constraint(self):
        return ''
    
    def to_c_code(self):
        return ''

class CircomTemplate:
    def __init__(self, name:str, stmt:list[CircomNode]):
        self.name = name
        self.statement = stmt
    
    def from_json(node):
        match node:
            case ['templateDefinition', 'template', name, '(', ')', block]:
                stmt = []
                for s in block[2:-1]:
                    match s:
                        case ['statement3', ['declaration', *_], ';']:
                            stmt.append(CircomDeclaration.from_json(s[1]))
                        case ['statement3', ['statement', ['statement0', ['statement1', ['statement2', ['substition', *_], ';']]]]]:
                            stmt.append(CircomSubstitution.from_json(s[1][1][1][1]))
                        case ['statement3', ['statement', ['statement0', ['statement1', constraint]]]]:
                            stmt.append(CircomConstraintEq.from_json(constraint))
                        case _:
                            raise NotImplementedError(f'Unhandled case: {s}')
                return CircomTemplate(name, stmt)
            case ['templateDefinition', 'template', name, '(', arg, ')', block]:
                stmt = []
                for s in block[2:-1]:
                    match s:
                        case ['statement3', ['declaration', *_], ';']:
                            stmt.append(CircomDeclaration.from_json(s[1]))
                        case ['statement3', ['statement', ['statement0', ['statement1', ['statement2', ['substition', *_], ';']]]]]:
                            stmt.append(CircomSubstitution.from_json(s[1][1][1][1]))
                        case ['statement3', ['statement', ['statement0', ['statement1', constraint]]]]:
                            stmt.append(CircomConstraintEq.from_json(constraint))
                        case _:
                            raise NotImplementedError(f'Unhandled case: {s}')
                return CircomTemplate(name, stmt)
            case _:
                raise NotImplementedError(f'Not a template node: {node}')

class CircomDeclaration(CircomNode):
    def __init__(self, type:bool, name:str, arr:bool=False, size:str=''):
        self.type = type # True = input, False = output
        self.name = name
        self.arr = arr
        self.size = size
    
    def from_json(node):
        match node:
            case ['declaration', ['signalHearder', 'signal', ['signalType', type]], ['signalSymbol', ['simpleSymbol', name]]]:
                if type == 'input':
                    return CircomDeclaration(True, name)
                else:
                    return CircomDeclaration(False, name)
            case ['declaration', ['signalHearder', 'signal', ['signalType', type]], ['signalSymbol', arrdef]]:
                match arrdef:
                    case ['simpleSymbol', name, ['arrayAcc', '[', ['expression', ['parseExpression1', expr]], ']']]:
                        size = dispatchExpression(expr)
                        assert size.terminal, f'array error: {size.label} in {node}'
                        # assert size.terminal and size.label.isdigit(), f'array error: {size.label} in {node}'
                        if type == 'input':
                            return CircomDeclaration(True, name, True, size.label)
                        else:
                            return CircomDeclaration(False, name, True, size.label)
                    case _:
                        raise NotImplementedError(f'Not an array declaration node: {node}')
            case _:
                raise NotImplementedError(f'Not a declaration node: {node}')

    def to_compute(self):
        if not self.arr:
            if self.type:
                return f'''int {self.name};
    klee_make_symbolic(&{self.name}, sizeof(int), "{self.name}");
    klee_assume({self.name} >= 0);

    '''
            else:
                return f'''int {self.name};
    klee_make_symbolic(&{self.name}, sizeof(int), "{self.name}");

    '''
        else:
            if self.type:
                return f'''int {self.name}[{self.size}];
    klee_make_symbolic(&{self.name}, sizeof(int*), "{self.name}");
    for (int i=0; i<{self.size}; i++)
        klee_assume({self.name}[i] >= 0);

    '''
            else:
                return f'''int {self.name}[{self.size}];
    klee_make_symbolic(&{self.name}, sizeof(int*), "{self.name}");

    '''

    def to_constraint(self):
        return self.to_compute()

class CircomVar(CircomNode):
    def __init__(self, label:str):
        self.terminal = True
        self.label = label
    
    def to_c_code(self):
        return self.label

class CircomInstruction(CircomNode):
    def __init__(self, opcode:Opcode, op1:CircomNode=None, op2:CircomNode=None, op3:CircomNode=None):
        self.terminal = False
        self.op1 = op1
        self.op2 = op2
        self.op3 = op3
        self.opcode = opcode

class CircomSubstitution(CircomInstruction):
    def __init__(self, opcode:Opcode, op1:CircomNode, op2:CircomNode):
        super().__init__(opcode=opcode, op1=op1, op2=op2)

    def from_json(node):
        match node[1]:
            case ['substition', ['expression', ['parseExpression1', lhs]], opcode, ['expression', ['parseExpression1', rhs]]]:
                op = None
                match opcode[1]:
                    case '<==':
                        op = Opcode.ASSIGN_CONSTRAINT_SIGNAL
                    case '<--':
                        op = Opcode.ASSIGN_SIGNAL
                op1 = dispatchExpression(lhs)
                op2 = dispatchExpression(rhs)
                return CircomSubstitution(opcode=op, op1=op1, op2=op2)
            case _:
                raise NotImplementedError(f'Not a substitution node: {node}')
    
    def to_compute(self):
        line = ''
        if self.opcode == Opcode.ASSIGN_CONSTRAINT_SIGNAL or self.opcode == Opcode.ASSIGN_SIGNAL:
            if isinstance(self.op2, CircomTernary):
                return self.op2.to_c_code(self.op1)
            elif isinstance(self.op2, CircomMulDiv) and self.op2.opcode == Opcode.DIV:
                line = f'''klee_assume({self.op2.op2.to_c_code()} != 0);
    '''
            line += f'''klee_assume({self.op1.to_c_code()} == {self.op2.to_c_code()});

    '''
        return line
    
    def to_constraint(self):
        line = ''
        if self.opcode == Opcode.ASSIGN_CONSTRAINT_SIGNAL:
            if isinstance(self.op2, CircomTernary):
                return self.op2.to_c_code(self.op1)
            elif isinstance(self.op2, CircomMulDiv) and self.op2.opcode == Opcode.DIV:
                line = f'''klee_assume({self.op2.op2.to_c_code()} != 0);
    '''
            line += f'''klee_assume({self.op1.to_c_code()} == {self.op2.to_c_code()});

    '''
        return line

class CircomConstraintEq(CircomInstruction):
    def __init__(self, op1:CircomNode, op2:CircomNode):
        super().__init__(opcode=Opcode.CONSTRAINT_EQUALITY, op1=op1, op2=op2)
    
    def from_json(node):
        if node[2] != '===':
            raise NotImplementedError(f'Not a constraint equality node: {node}')
        
        op1 = dispatchExpression(node[1][1][1])
        op2 = dispatchExpression(node[3][1][1])
        return CircomConstraintEq(op1=op1, op2=op2)
    
    def to_constraint(self):
        return f'''klee_assume({self.op1.to_c_code()} == {self.op2.to_c_code()});

    '''

class CircomTernary(CircomInstruction): # expression13
    def __init__(self, op1, op2, op3):
        super().__init__(opcode=Opcode.TERNARY, op1=op1, op2=op2, op3=op3)

    def from_json(node):
        match node:
            case ['expression13', cond, '?', true, ':', false]:
                op1 = dispatchExpression(cond)
                op2 = dispatchExpression(true)
                op3 = dispatchExpression(false)
                return CircomTernary(op1, op2, op3)
            case _:
                raise NotImplementedError(f'Not a ternary node: {node}')

    def to_c_code(self, lhs:CircomNode):
        return f'''if {self.op1.to_c_code()} klee_assume({lhs.to_c_code()} == {self.op2.to_c_code()});
    else klee_assume({lhs.to_c_code()} == {self.op3.to_c_code()});
    
    '''

class CircomOr(CircomInstruction): #expression12
    def from_json(node):
        print('In Or')

class CircomAnd(CircomInstruction): #expression11
    def from_json(node):
        print('In And')

class CircomCompare(CircomInstruction): #expression10
    def __init__(self, opcode:Opcode, op1:CircomNode, op2:CircomNode):
        super().__init__(opcode=opcode, op1=op1, op2=op2)

    def from_json(node):
        match node:
            case ['expression10', lhs, opcode, rhs]:
                op = None
                match opcode[1]:
                    case '==':
                        op = Opcode.EQ
                    case '!=':
                        op = Opcode.NEQ
                    case '<':
                        op = Opcode.LT
                    case '>':
                        op = Opcode.GT
                    case '<=':
                        op = Opcode.LE
                    case '>=':
                        op = Opcode.GE
                op1 = dispatchExpression(lhs)
                op2 = dispatchExpression(rhs)
                return CircomCompare(opcode=op, op1=op1, op2=op2)
            case _:
                raise NotImplementedError(f'Not a compare node: {node}')
    
    def to_c_code(self):
        op_str = ''
        if self.opcode == Opcode.EQ:
            op_str = '=='
        elif self.opcode == Opcode.NEQ:
            op_str = '!='
        elif self.opcode == Opcode.LT:
            op_str = '<'
        elif self.opcode == Opcode.GT:
            op_str = '>'
        elif self.opcode == Opcode.LE:
            op_str = '<='
        elif self.opcode == Opcode.GE:
            op_str = '>='
        return '(' + self.op1.to_c_code() + ' ' + op_str + ' ' + self.op2.to_c_code() + ')'

class CircomOrBit(CircomInstruction): #expression9
    def from_json(node):
        print('In Or Bit')

class CircomXorBit(CircomInstruction): #expression8
    def from_json(node):
        print('In Xor Bit')

class CircomAndBit(CircomInstruction): #expression7
    def from_json(node):
        print('In And Bit')

class CircomShift(CircomInstruction): #expression6
    def from_json(node):
        print('In Shift')

class CircomAddSub(CircomInstruction): #expression5
    def __init__(self, opcode:Opcode, op1:CircomNode, op2:CircomNode):
        super().__init__(opcode=opcode, op1=op1, op2=op2)
    
    def from_json(node):
        match node:
            case ['expression5', lhs, ['addSubOp', opcode], rhs]:
                op = None
                match opcode:
                    case '+':
                        op = Opcode.PLUS
                    case '-':
                        op = Opcode.MINUS
                op1 = dispatchExpression(lhs)
                op2 = dispatchExpression(rhs)
                return CircomAddSub(opcode=op, op1=op1, op2=op2)
            case _:
                raise NotImplementedError(f'Not a add sub node: {node}')
    
    def to_c_code(self):
        op_str = ''
        if self.opcode == Opcode.PLUS:
            op_str = '+'
        elif self.opcode == Opcode.MINUS:
            op_str = '-'
        return '(' + self.op1.to_c_code() + ' ' + op_str + ' ' + self.op2.to_c_code() + ')'

class CircomMulDiv(CircomInstruction): #expression4
    def __init__(self, opcode:Opcode, op1:CircomNode, op2:CircomNode):
        super().__init__(opcode=opcode, op1=op1, op2=op2)

    def from_json(node):
        match node:
            case ['expression4', lhs, ['mulDivOp', opcode], rhs]:
                op = None
                match opcode:
                    case '*':
                        op = Opcode.MUL
                    case '/':
                        op = Opcode.DIV
                    case '\\':
                        op = Opcode.INTDIV
                    case '%':
                        op = Opcode.MOD
                op1 = dispatchExpression(lhs)
                op2 = dispatchExpression(rhs)
                return CircomMulDiv(opcode=op, op1=op1, op2=op2)
            case _:
                raise NotImplementedError(f'Not a mul div node: {node}')
    
    def to_c_code(self):
        op_str = ''
        if self.opcode == Opcode.MUL:
            op_str = '*'
        elif self.opcode == Opcode.DIV:
            op_str = '/'
        elif self.opcode == Opcode.INTDIV:
            op_str = '\\'
        elif self.opcode == Opcode.MOD:
            op_str = '%'
        return '(' + self.op1.to_c_code() + ' ' + op_str + ' ' + self.op2.to_c_code() + ')'

class CircomPow(CircomInstruction): #expression3
    def from_json(node):
        print('In Pow')

class CircomPrefix(CircomInstruction): #expression2
    def from_json(node):
        print('In Prefix')

class CircomArr(CircomInstruction): #expression1
    def __init__(self, op1:str, op2:str):
        super().__init__(opcode=Opcode.ARR, op1=CircomVar(op1), op2=CircomVar(op2))

    def from_json(node):
        print('In Arr')

    def to_c_code(self):
        return f'{self.op1.label}[{self.op2.label}]'

class CircomTerminal(CircomVar): #expression0
    def from_json(node):
        match node:
            case ['expression0', ['variable', label]]:
                return CircomVar(label)
            case ['expression0', ['variable', label, ['varAccess', ['arrayAcc', '[', ['expression', ['parseExpression1', expr]], ']']]]]:
                idx = dispatchExpression(expr)
                # assert idx.terminal and idx.label.isdigit(), f'array error: {idx.label} in {node}'
                assert idx.terminal, f'array error: {idx.label} in {node}'
                return CircomArr(label, idx.label)
            case ['expression0', i]:
                assert isinstance(i, str), f'expression0 error: {i} in {node}'
                if i.isdigit():
                    return CircomVar(i)
            case ['expression0', '(', ['expression', ['parseExpression1', expr]], ')']:
                return dispatchExpression(expr)
            case _:
                raise NotImplementedError(f'Not a terminal node: {node}')