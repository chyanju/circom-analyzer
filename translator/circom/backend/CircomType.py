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
        ret = CircomTerminal.from_json(node)
        assert len(ret) == 1, f'error in dispatch expression: {node}'
        return ret[0]
    elif len(node) > 2:
        ret = []
        match node:
            case ['expression1', *_]:
                ret = CircomListable.from_json(node)
            case ['expression2', *_]:
                ret = CircomPrefix.from_json(node)
            case ['expression3', *_]:
                ret = CircomPow.from_json(node)
            case ['expression4', *_]:
                ret = CircomMulDiv.from_json(node)
            case ['expression5', *_]:
                ret = CircomAddSub.from_json(node)
            case ['expression6', *_]:
                ret = CircomShift.from_json(node)
            case ['expression7', *_]:
                ret = CircomAndBit.from_json(node)
            case ['expression8', *_]:
                ret = CircomXorBit.from_json(node)
            case ['expression9', *_]:
                ret = CircomOrBit.from_json(node)
            case ['expression10', *_]:
                ret = CircomCompare.from_json(node)
            case ['expression11', *_]:
                ret = CircomAnd.from_json(node)
            case ['expression12', *_]:
                ret = CircomOr.from_json(node)
            case ['expression13', *_]:
                ret = CircomTernary.from_json(node)
        assert len(ret) == 1, f'error in dispatch expression: {node}'
        return ret[0]
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
    
    def from_json(node, call:list, return_input, return_output, return_signal, return_var, return_public, return_private, return_intermediate, input, output, signal, var, public, private, intermediate):
        match node:
            case ['templateDefinition', 'template', name, '(', ')', block]:
                stmt = []
                for s in block[2:-1]:
                    stmt.extend(CircomStatement3.from_json(s, return_input, return_output, return_signal, return_var, return_public, return_private, return_intermediate, input, output, signal, var, public, private, intermediate))
                return CircomTemplate(name, stmt)
            case ['templateDefinition', 'template', name, '(', arg, ')', block]:
                stmt = []
                if arg[0] == 'identifierList':
                    arglst = list(a for a in arg[1:] if a != ',')
                    if len(call) != 0 and call[0] == name:
                        for i in range(1, len(call)):
                            stmt.append(CircomDeclaration(0, arglst[i - 1], val=dispatchExpression(call[i])))
                    else:
                        for a in arg:
                            stmt.append(CircomDeclaration(0, a))
                for s in block[2:-1]:
                    stmt.extend(CircomStatement3.from_json(s, return_input, return_output, return_signal, return_var, return_public, return_private, return_intermediate, input, output, signal, var, public, private, intermediate))
                return CircomTemplate(name, stmt)
            case _:
                raise NotImplementedError(f'Not a template node: {node}')

class CircomStatement3(CircomNode):
    def from_json(node, return_input, return_output, return_signal, return_var, return_public, return_private, return_intermediate, input, output, signal, var, public, private, intermediate):
        match node:
            case ['statement3', ['declaration', *_], ';']:
                return CircomDeclaration.from_json(node[1], return_input, return_output, return_signal, return_var, return_public, return_private, return_intermediate, input, output, signal, var, public, private, intermediate)
            case ['statement3', ['statement', ['statement0', ['statement1', ['statement2', ['substition', *_], ';']]]]]:
                return CircomSubstitution.from_json(node[1][1][1][1][1], return_input, return_output, return_signal, return_var, return_public, return_private, return_intermediate, input, output, signal, var, public, private, intermediate)
            case ['statement3', ['statement', ['statement0', ['statement1', constraint]]]]:
                return CircomStatement2.from_json(constraint, return_input, return_output, return_signal, return_var, return_public, return_private, return_intermediate, input, output, signal, var, public, private, intermediate)
            case _:
                raise NotImplementedError(f'Not a statement3 node: {node}')

class CircomDeclaration(CircomNode):
    def __init__(self, type:int, name:str, arr:bool=False, size:str='', val:CircomNode=None):
        self.type = type # 0 = input, 1 = output, 2 = var, 3 = intermediate signals
        self.name = name
        self.arr = arr
        self.size = size
        self.val = val
    
    def from_json(node, return_input, return_output, return_signal, return_var, return_public, return_private, return_intermediate, input, output, signal, var, public, private, intermediate):
        match node:
            case ['declaration', ['signalHearder', 'signal', ['signalType', type]], ['signalSymbol', ['simpleSymbol', name]]]:
                if type == 'input':
                    if return_input:
                        input.append(name)
                    if return_signal:
                        signal.append(name)
                    if return_private:
                        private.append(name)
                    return [CircomDeclaration(0, name)]
                else:
                    if return_output:
                        output.append(name)
                    if return_signal:
                        signal.append(name)
                    if return_public:
                        public.append(name)
                    return [CircomDeclaration(1, name)]
            case ['declaration', ['signalHearder', 'signal'], ['signalSymbol', ['simpleSymbol', name]]]:
                if return_signal:
                    signal.append(name)
                if return_intermediate:
                    intermediate.append(name)
                return [CircomDeclaration(3, name)]
            case ['declaration', 'var', ['simpleSymbol', name]]:
                if return_var:
                    var.append(name)
                return [CircomDeclaration(2, name)]
            case ['declaration', 'var', ['simpleSymbol', name], ['tupleInitialization', opcode, ['expression', ['parseExpression1', expr]]]]:
                if opcode == '=':
                    rhs = dispatchExpression(expr)
                    if return_var:
                        var.append(name)
                    return [CircomDeclaration(2, name, val=rhs)]
                else:
                    raise NotImplementedError(f'Unhandled assignment: {node}')
            case ['declaration', ['signalHearder', 'signal', ['signalType', type]], ['signalSymbol', arrdef]]:
                match arrdef:
                    case ['simpleSymbol', name, ['arrayAcc', '[', ['expression', ['parseExpression1', expr]], ']']]:
                        size = dispatchExpression(expr)
                        if type == 'input':
                            if return_input:
                                input.append(name)
                            if return_signal:
                                signal.append(name)
                            if return_private:
                                private.append(name)
                            return [CircomDeclaration(0, name, True, size.to_c_code())]
                        else:
                            if return_output:
                                output.append(name)
                            if return_signal:
                                signal.append(name)
                            if return_public:
                                public.append(name)
                            return [CircomDeclaration(1, name, True, size.to_c_code())]
                    case _:
                        raise NotImplementedError(f'Not an array declaration node: {node}')
            case ['declaration', ['signalHearder', 'signal'], ['signalSymbol', arrdef]]:
                match arrdef:
                    case ['simpleSymbol', name, ['arrayAcc', '[', ['expression', ['parseExpression1', expr]], ']']]:
                        size = dispatchExpression(expr)
                        if return_signal:
                            signal.append(name)
                        if return_intermediate:
                            intermediate.append(name)
                        return [CircomDeclaration(3, name, True, size.to_c_code())]
                    case _:
                        raise NotImplementedError(f'Not an array declaration node: {node}')
            case _:
                raise NotImplementedError(f'Not a declaration node: {node}')
    def to_compute(self):
        if self.arr and self.type == 0:
            return f'''int {self.name}[{self.size}];
    klee_make_symbolic(&{self.name}, sizeof(int*), "{self.name}");
    for (int i=0; i<{self.size}; i++)
        klee_assume({self.name}[i] >= 0);

    '''
        elif self.arr and self.type == 1:
            return f'''int {self.name}[{self.size}];
    klee_make_symbolic(&{self.name}, sizeof(int*), "{self.name}");

    '''
        elif self.arr and self.type == 3:
            return f'''int {self.name}[{self.size}];
    klee_make_symbolic(&{self.name}, sizeof(int*), "{self.name}");

    '''
        elif not self.arr and self.type == 0 and self.val is None:
            return f'''int {self.name};
    klee_make_symbolic(&{self.name}, sizeof(int), "{self.name}");
    klee_assume({self.name} >= 0);

    '''
        elif not self.arr and self.type == 0 and self.val is not None:
            return f'''int {self.name};
    klee_make_symbolic(&{self.name}, sizeof(int), "{self.name}");
    klee_assume({self.name} == {self.val.to_c_code()});

    '''
        elif not self.arr and self.type == 1:
            return f'''int {self.name};
    klee_make_symbolic(&{self.name}, sizeof(int), "{self.name}");

    '''
        elif not self.arr and self.type == 3:
            return f'''int {self.name};
    klee_make_symbolic(&{self.name}, sizeof(int), "{self.name}");

    '''
        elif self.type == 2 and self.val is None:
            return f'''int {self.name};

    '''
        elif self.type == 2 and self.val is not None:
            return f'''int {self.name} = {self.val.to_c_code()};

    '''

    def to_constraint(self):
        return self.to_compute()
    
    def to_c_code(self):
        if self.type != 2 or self.val is None:
            return ''
        return f'int {self.name} = {self.val.to_c_code()}'

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

    def from_json(node, return_input, return_output, return_signal, return_var, return_public, return_private, return_intermediate, input, output, signal, var, public, private, intermediate):
        match node:
            case ['substition', ['expression', ['parseExpression1', lhs]], ['assignOp', opcode], ['expression', ['parseExpression1', rhs]]]:
                op = None
                match opcode:
                    case '<==':
                        op = Opcode.ASSIGN_CONSTRAINT_SIGNAL
                    case '<--':
                        op = Opcode.ASSIGN_SIGNAL
                    case '=':
                        op = Opcode.ASSIGN_VAR
                    case _:
                        raise NotImplementedError(f'Unimplemented assign opcode in substitution node: {node}')
                op1 = dispatchExpression(lhs)
                op2 = dispatchExpression(rhs)
                return [CircomSubstitution(opcode=op, op1=op1, op2=op2)]
            case ['substition', ['expression', ['parseExpression1', lhs]], opcode]:
                op = None
                match opcode:
                    case '++':
                        op = Opcode.INCREMENT
                    case '--':
                        op = Opcode.DECREMENT
                    case _:
                        raise NotImplementedError(f'Unimplemented opcode in substitution node: {node}')
                op1 = dispatchExpression(lhs)
                return [CircomSubstitution(opcode=op, op1=op1, op2=None)]
            case ['substition', ['variable', name], opcode]:
                op = None
                match opcode:
                    case '++':
                        op = Opcode.INCREMENT
                    case '--':
                        op = Opcode.DECREMENT
                    case _:
                        raise NotImplementedError(f'Unimplemented opcode in substitution node: {node}')
                return [CircomSubstitution(opcode=op, op1=CircomVar(name), op2=None)]
            case ['substition', ['expression', ['parseExpression1', lhs]], '==>', ['expression', ['parseExpression1', rhs]]]:
                op1 = dispatchExpression(lhs)
                op2 = dispatchExpression(rhs)
                return [CircomSubstitution(opcode=Opcode.RIGHT_ASSIGN_CONSTRAINT_SIGNAL, op1=op1, op2=op2)]
            case _:
                raise NotImplementedError(f'Not a substitution node: {node}')

    def to_compute(self):
        line = ''
        if self.opcode == Opcode.ASSIGN_CONSTRAINT_SIGNAL \
        or self.opcode == Opcode.ASSIGN_SIGNAL \
        or self.opcode == Opcode.RIGHT_ASSIGN_CONSTRAINT_SIGNAL:
            if isinstance(self.op2, CircomTernary):
                return self.op2.to_c_code(self.op1)
            elif isinstance(self.op2, CircomMulDiv) and self.op2.opcode == Opcode.DIV:
                line = f'''klee_assume({self.op2.op2.to_c_code()} != 0);
    '''
            line += f'''klee_assume({self.op1.to_c_code()} == {self.op2.to_c_code()});

    '''
        elif self.opcode == Opcode.ASSIGN_VAR:
            line = f'''{self.op1.to_c_code()} = {self.op2.to_c_code()};

    '''
        return line
    
    def to_constraint(self):
        line = ''
        if self.opcode == Opcode.ASSIGN_CONSTRAINT_SIGNAL \
        or self.opcode == Opcode.RIGHT_ASSIGN_CONSTRAINT_SIGNAL:
            if isinstance(self.op2, CircomTernary):
                return self.op2.to_c_code(self.op1)
            elif isinstance(self.op2, CircomMulDiv) and self.op2.opcode == Opcode.DIV:
                line = f'''klee_assume({self.op2.op2.to_c_code()} != 0);
    '''
            line += f'''klee_assume({self.op1.to_c_code()} == {self.op2.to_c_code()});

    '''
        elif self.opcode == Opcode.ASSIGN_VAR:
            line = f'''{self.op1.to_c_code()} = {self.op2.to_c_code()};

    '''
        return line
    
    def to_c_code(self):
        if self.opcode == Opcode.INCREMENT:
            return f'{self.op1.to_c_code()}++'
        elif self.opcode == Opcode.DECREMENT:
            return f'{self.op1.to_c_code()}--'

class CircomConstraintEq(CircomInstruction):
    def __init__(self, op1:CircomNode, op2:CircomNode):
        super().__init__(opcode=Opcode.CONSTRAINT_EQUALITY, op1=op1, op2=op2)
    
    def to_constraint(self):
        return f'''klee_assume({self.op1.to_c_code()} == {self.op2.to_c_code()});

    '''

class CircomFor(CircomNode):
    def __init__(self, c1:CircomNode, c2:CircomNode, c3:CircomNode, stmt:list[CircomNode]):
        self.c1 = c1
        self.c2 = c2
        self.c3 = c3
        self.statement = stmt
    
    def to_compute(self):
        line = f'for ({self.c1.to_c_code()}; {self.c2.to_c_code()}; {self.c3.to_c_code()})'
        line += ''' {
    '''
        for stmt in self.statement:
            line += stmt.to_compute()
        line += '''}

    '''
        return line
    
    def to_constraint(self):
        line = f'for ({self.c1.to_c_code()}; {self.c2.to_c_code()}; {self.c3.to_c_code()})'
        line += ''' {
    '''
        for stmt in self.statement:
            line += stmt.to_constraint()
        line += '''}

    '''
        return line

class CircomStatement2(CircomInstruction):
    def __init__(self, opcode:Opcode, op1:CircomNode, op2:CircomNode):
        super().__init__(opcode=opcode, op1=op1, op2=op2)
    
    def from_json(node, return_input, return_output, return_signal, return_var, return_public, return_private, return_intermediate, input, output, signal, var, public, private, intermediate):
        if node[2] == '===':
            op1 = dispatchExpression(node[1][1][1])
            op2 = dispatchExpression(node[3][1][1])
            return [CircomConstraintEq(op1=op1, op2=op2)]
        elif node[1] == 'for':
            c1 = None
            if node[3][0] == 'substition':
                c1 = CircomSubstitution.from_json(node[3], return_input, return_output, return_signal, return_var, return_public, return_private, return_intermediate, input, output, signal, var, public, private, intermediate)
            elif node[3][0] == 'declaration':
                c1 = CircomDeclaration.from_json(node[3], return_input, return_output, return_signal, return_var, return_public, return_private, return_intermediate, input, output, signal, var, public, private, intermediate)
            else:
                raise NotImplementedError(f'Unhandled for condition: {node}')
            c2 = dispatchExpression(node[5][1][1])
            c3 = CircomSubstitution.from_json(node[7], return_input, return_output, return_signal, return_var, return_public, return_private, return_intermediate, input, output, signal, var, public, private, intermediate)
            assert len(c1) == 1, f'error in for condition: {node}'
            assert len(c3) == 1, f'error in for condition: {node}'
            stmt = []
            for s in node[9][1][2:-1]:
                stmt.extend(CircomStatement3.from_json(s, return_input, return_output, return_signal, return_var, return_public, return_private, return_intermediate, input, output, signal, var, public, private, intermediate))
            return [CircomFor(c1[0], c2, c3[0], stmt)]
        else:
            raise NotImplementedError(f'Not a statement 2 node: {node}')

class CircomTernary(CircomInstruction): # expression13
    def __init__(self, op1, op2, op3):
        super().__init__(opcode=Opcode.TERNARY, op1=op1, op2=op2, op3=op3)

    def from_json(node):
        match node:
            case ['expression13', cond, '?', true, ':', false]:
                op1 = dispatchExpression(cond)
                op2 = dispatchExpression(true)
                op3 = dispatchExpression(false)
                return [CircomTernary(op1, op2, op3)]
            case _:
                raise NotImplementedError(f'Not a ternary node: {node}')

    def to_c_code(self, lhs:CircomNode):
        return f'''if {self.op1.to_c_code()} klee_assume({lhs.to_c_code()} == {self.op2.to_c_code()});
    else klee_assume({lhs.to_c_code()} == {self.op3.to_c_code()});
    
    '''

class CircomOr(CircomInstruction): #expression12
    def __init__(self, opcode:Opcode, op1:CircomNode, op2:CircomNode):
        super().__init__(opcode=opcode, op1=op1, op2=op2)

    def from_json(node):
        match node:
            case ['expression12', lhs, '||', rhs]:
                op1 = dispatchExpression(lhs)
                op2 = dispatchExpression(rhs)
                return [CircomOr(opcode=Opcode.OR, op1=op1, op2=op2)]
            case _:
                raise NotImplementedError(f'Not an or node: {node}')

class CircomAnd(CircomInstruction): #expression11
    def __init__(self, opcode:Opcode, op1:CircomNode, op2:CircomNode):
        super().__init__(opcode=opcode, op1=op1, op2=op2)

    def from_json(node):
        match node:
            case ['expression11', lhs, '&&', rhs]:
                op1 = dispatchExpression(lhs)
                op2 = dispatchExpression(rhs)
                return [CircomAnd(opcode=Opcode.AND, op1=op1, op2=op2)]
            case _:
                raise NotImplementedError(f'Not an and node: {node}')

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
                return [CircomCompare(opcode=op, op1=op1, op2=op2)]
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
    def __init__(self, opcode:Opcode, op1:CircomNode, op2:CircomNode):
        super().__init__(opcode=opcode, op1=op1, op2=op2)

    def from_json(node):
        match node:
            case ['expression9', lhs, '|', rhs]:
                op1 = dispatchExpression(lhs)
                op2 = dispatchExpression(rhs)
                return [CircomOrBit(opcode=Opcode.OR_BIT, op1=op1, op2=op2)]
            case _:
                raise NotImplementedError(f'Not an or bit node: {node}')
            

class CircomXorBit(CircomInstruction): #expression8
    def __init__(self, opcode:Opcode, op1:CircomNode, op2:CircomNode):
        super().__init__(opcode=opcode, op1=op1, op2=op2)

    def from_json(node):
        match node:
            case ['expression8', lhs, '^', rhs]:
                op1 = dispatchExpression(lhs)
                op2 = dispatchExpression(rhs)
                return [CircomXorBit(opcode=Opcode.XOR_BIT, op1=op1, op2=op2)]
            case _:
                raise NotImplementedError(f'Not an xor bit node: {node}')

class CircomAndBit(CircomInstruction): #expression7
    def __init__(self, opcode:Opcode, op1:CircomNode, op2:CircomNode):
        super().__init__(opcode=opcode, op1=op1, op2=op2)
    
    def from_json(node):
        match node:
            case ['expression7', lhs, '&', rhs]:
                op1 = dispatchExpression(lhs)
                op2 = dispatchExpression(rhs)
                return [CircomAndBit(opcode=Opcode.AND_BIT, op1=op1, op2=op2)]
            case _:
                raise NotImplementedError(f'Not an and bit node: {node}')

class CircomShift(CircomInstruction): #expression6
    def __init__(self, opcode:Opcode, op1:CircomNode, op2:CircomNode):
        super().__init__(opcode=opcode, op1=op1, op2=op2)

    def from_json(node):
        match node:
            case ['expression6', lhs, ['shiftOp', opcode], rhs]:
                op = None
                match opcode:
                    case '<<':
                        op = Opcode.SHIFTL
                    case '>>':
                        op = Opcode.SHIFTR
                op1 = dispatchExpression(lhs)
                op2 = dispatchExpression(rhs)
                return [CircomShift(opcode=op, op1=op1, op2=op2)]
            case _:
                raise NotImplementedError(f'Not a shift node: {node}')

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
                return [CircomAddSub(opcode=op, op1=op1, op2=op2)]
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
                return [CircomMulDiv(opcode=op, op1=op1, op2=op2)]
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
    def __init__(self, opcode:Opcode, op1:CircomNode, op2:CircomNode):
        super().__init__(opcode=opcode, op1=op1, op2=op2)

    def from_json(node):
        match node:
            case ['expression3', lhs, '**', rhs]:
                op1 = dispatchExpression(lhs)
                op2 = dispatchExpression(rhs)
                return [CircomPow(opcode=Opcode.POW, op1=op1, op2=op2)]
            case _:
                raise NotImplementedError(f'Not a pow node: {node}')

class CircomPrefix(CircomInstruction): #expression2
    def __init__(self, opcode:Opcode, op1:CircomNode):
        super().__init__(opcode=opcode, op1=op1)
        
    def from_json(node):
        match node:
            case ['expression2', ['expressionPrefixOp', opcode], rhs]:
                op = None
                match opcode:
                    case '-':
                        op = Opcode.MINUS
                    case '!':
                        op = Opcode.NOT
                    case '~':
                        op = Opcode.COMPLEMENT
                op1 = dispatchExpression(rhs)
                return [CircomPrefix(opcode=op, op1=op1)]
            case _:
                raise NotImplementedError(f'Not a prefix node: {node}')

    def to_c_code(self):
        op_str = ''
        if self.opcode == Opcode.MINUS:
            op_str = '-'
        elif self.opcode == Opcode.NOT:
            op_str = '!'
        elif self.opcode == Opcode.COMPLEMENT:
            op_str = '~'
        return '(' + op_str + self.op1.to_c_code() + ')'

class CircomListable(CircomInstruction): #expression1
    def __init__(self, op1:str, op2:str):
        super().__init__(opcode=Opcode.ARR, op1=CircomVar(op1), op2=CircomVar(op2))

    def from_json(node):
        print('In Listable')

    def to_c_code(self):
        return f'{self.op1.label}[{self.op2.label}]'

class CircomTerminal(CircomVar): #expression0
    def from_json(node):
        match node:
            case ['expression0', ['variable', label]]:
                return [CircomVar(label)]
            case ['expression0', ['variable', label, ['varAccess', ['arrayAcc', '[', ['expression', ['parseExpression1', expr]], ']']]]]:
                idx = dispatchExpression(expr)
                return [CircomListable(label, idx.to_c_code())]
            case ['expression0', i]:
                assert isinstance(i, str), f'expression0 error: {i} in {node}'
                if i.isdigit():
                    return [CircomVar(i)]
            case ['expression0', '(', ['expression', ['parseExpression1', expr]], ')']:
                return [dispatchExpression(expr)]
            case _:
                raise NotImplementedError(f'Not a terminal node: {node}')