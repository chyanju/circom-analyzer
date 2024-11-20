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
    FIELD = 45

def dispatchExpression(node, var_type:dict={}):
    if node[0] == 'expression0':
        ret = CircomTerminal.from_json(node, var_type)
        assert len(ret) == 1, f'error in dispatch expression: {node}'
        return ret[0]
    elif len(node) > 2:
        ret = []
        match node:
            case ['expression1', *_]:
                ret = CircomExpression1.from_json(node, var_type)
            case ['expression2', *_]:
                ret = CircomPrefix.from_json(node, var_type)
            case ['expression3', *_]:
                ret = CircomPow.from_json(node, var_type)
            case ['expression4', *_]:
                ret = CircomMulDiv.from_json(node, var_type)
            case ['expression5', *_]:
                ret = CircomAddSub.from_json(node, var_type)
            case ['expression6', *_]:
                ret = CircomShift.from_json(node, var_type)
            case ['expression7', *_]:
                ret = CircomAndBit.from_json(node, var_type)
            case ['expression8', *_]:
                ret = CircomXorBit.from_json(node, var_type)
            case ['expression9', *_]:
                ret = CircomOrBit.from_json(node, var_type)
            case ['expression10', *_]:
                ret = CircomCompare.from_json(node, var_type)
            case ['expression11', *_]:
                ret = CircomAnd.from_json(node, var_type)
            case ['expression12', *_]:
                ret = CircomOr.from_json(node, var_type)
            case ['expression13', *_]:
                ret = CircomTernary.from_json(node, var_type)
        assert len(ret) == 1, f'error in dispatch expression: {node, var_type}'
        return ret[0]
    else:
        return dispatchExpression(node[1], var_type)

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
    def __init__(self, name:str, arg:list, stmt:list[CircomNode], var_type:dict, var_array:dict={}):
        self.name = name
        self.arg = arg
        self.statement = stmt
        self.var_type = var_type
        self.var_array = var_array
    
    def from_json(node):
        match node:
            case ['templateDefinition', 'template', name, '(', ')', block]:
                stmt = []
                var_type = {}
                var_array = {}
                for s in block[2:-1]:
                    match s:
                        case ['statement3', ['declaration', *_], ';']:
                            match s[1]:
                                case ['declaration', ['signalHearder', 'signal', ['signalType', type]], ['signalSymbol', ['simpleSymbol', symbol_name]]]:
                                    if type == 'input':
                                        var_type[symbol_name] = 'input'
                                    else:
                                        var_type[symbol_name] = 'output'
                                case ['declaration', ['signalHearder', 'signal', ['signalType', type]], ['signalSymbol', arrdef]]:
                                    match arrdef:
                                        case ['simpleSymbol', symbol_name, ['arrayAcc', '[', ['expression', ['parseExpression1', expr]], ']']]:
                                            if type == 'input':
                                                var_type[symbol_name] = 'input'
                                            else:
                                                var_type[symbol_name] = 'output'
                                            match expr:
                                                case ['expression12', ['expression11', ['expression10', ['expression9', ['expression8', ['expression7', ['expression6', ['expression5', ['expression4', ['expression3', ['expression2', ['expression1', ['expression0', ['variable', v]]]]]]]]]]]]]]:
                                                    var_array[symbol_name] = v
                                                case ['expression12', ['expression11', ['expression10', ['expression9', ['expression8', ['expression7', ['expression6', ['expression5', ['expression4', ['expression3', ['expression2', ['expression1', ['expression0', num]]]]]]]]]]]]]:
                                                    var_array[symbol_name] = num
                                                case _:
                                                    raise NotImplementedError(f'Unsupported array size: {expr}')
                                        case _:
                                            raise NotImplementedError(f'Not an array declaration node: {node}')
                                case ['declaration', ['signalHearder', 'signal'], ['signalSymbol', ['simpleSymbol', symbol_name]]]:
                                    var_type[symbol_name] = 'intermediate'
                                case ['declaration', 'var', ['simpleSymbol', symbol_name]]:
                                    var_type[symbol_name] = 'var'
                                case ['declaration', 'var', ['simpleSymbol', symbol_name], ['tupleInitialization', opcode, ['expression', ['parseExpression1', expr]]]]:
                                    var_type[symbol_name] = 'var'
                                case ['declaration', 'component', ['simpleSymbol', symbol_name]]:
                                    var_type[symbol_name] = 'component'
                                case ['declaration', 'component', ['simpleSymbol', symbol_name], ['tupleInitialization', opcode, ['expression', ['parseExpression1', expr]]]]:
                                    var_type[symbol_name] = 'component'
                                    if opcode == '=':
                                        component_name = dispatchExpression(expr)
                                        if type(component_name) == CircomExpression1:
                                            identifier = component_name.name
                                            var_type[symbol_name] = identifier
                                case ['declaration', 'component', ['simpleSymbol', symbol_name, ['arrayAcc', '[', ['expression', ['parseExpression1', expr]], ']']]]:    
                                    var_type[symbol_name] = 'component'
                                case ['declaration', ['signalHearder', 'signal'], ['signalSymbol', arrdef]]:
                                    match arrdef:
                                        case ['simpleSymbol', symbol_name, ['arrayAcc', '[', ['expression', ['parseExpression1', expr]], ']']]:
                                            var_type[symbol_name] = 'intermediate'
                                        case _:
                                            raise NotImplementedError(f'Not an array declaration node: {node}')
                    stmt.extend(CircomStatement3.from_json(s, var_type=var_type))
                return CircomTemplate(name, [], stmt, var_type, var_array)
            case ['templateDefinition', 'template', name, '(', arg, ')', block]:
                stmt = []
                var_type = {}
                var_array = {}
                if arg[0] == 'identifierList':
                    arglst = list(a for a in arg[1:] if a != ',')
                for s in block[2:-1]:
                    match s:
                        case ['statement3', ['declaration', *_], ';']:
                            match s[1]:
                                case ['declaration', ['signalHearder', 'signal', ['signalType', type]], ['signalSymbol', ['simpleSymbol', symbol_name]]]:
                                    if type == 'input':
                                        var_type[symbol_name] = 'input'
                                    else:
                                        var_type[symbol_name] = 'output'
                                case ['declaration', ['signalHearder', 'signal', ['signalType', type]], ['signalSymbol', arrdef]]:
                                    match arrdef:
                                        case ['simpleSymbol', symbol_name, ['arrayAcc', '[', ['expression', ['parseExpression1', expr]], ']']]:
                                            if type == 'input':
                                                var_type[symbol_name] = 'input'
                                            else:
                                                var_type[symbol_name] = 'output'
                                            match expr:
                                                case ['expression12', ['expression11', ['expression10', ['expression9', ['expression8', ['expression7', ['expression6', ['expression5', ['expression4', ['expression3', ['expression2', ['expression1', ['expression0', ['variable', v]]]]]]]]]]]]]]:
                                                    var_array[symbol_name] = v
                                                case ['expression12', ['expression11', ['expression10', ['expression9', ['expression8', ['expression7', ['expression6', ['expression5', ['expression4', ['expression3', ['expression2', ['expression1', ['expression0', num]]]]]]]]]]]]]:
                                                    var_array[symbol_name] = num
                                                case _:
                                                    raise NotImplementedError(f'Unsupported array size: {expr}')
                                        case _:
                                            raise NotImplementedError(f'Not an array declaration node: {node}')
                                case ['declaration', ['signalHearder', 'signal'], ['signalSymbol', ['simpleSymbol', symbol_name]]]:
                                    var_type[symbol_name] = 'intermediate'
                                case ['declaration', 'var', ['simpleSymbol', symbol_name]]:
                                    var_type[symbol_name] = 'var'
                                case ['declaration', 'var', ['simpleSymbol', symbol_name], ['tupleInitialization', opcode, ['expression', ['parseExpression1', expr]]]]:
                                    var_type[symbol_name] = 'var'
                                case ['declaration', 'component', ['simpleSymbol', symbol_name]]:
                                    var_type[symbol_name] = 'component'
                                case ['declaration', 'component', ['simpleSymbol', symbol_name], ['tupleInitialization', opcode, ['expression', ['parseExpression1', expr]]]]:
                                    var_type[symbol_name] = 'component'
                                    if opcode == '=':
                                        component_name = dispatchExpression(expr)
                                        if type(component_name) == CircomExpression1:
                                            identifier = component_name.name
                                            var_type[symbol_name] = identifier
                                case ['declaration', 'component', ['simpleSymbol', symbol_name, ['arrayAcc', '[', ['expression', ['parseExpression1', expr]], ']']]]:    
                                    var_type[symbol_name] = 'component'
                                case ['declaration', ['signalHearder', 'signal'], ['signalSymbol', arrdef]]:
                                    match arrdef:
                                        case ['simpleSymbol', symbol_name, ['arrayAcc', '[', ['expression', ['parseExpression1', expr]], ']']]:
                                            var_type[symbol_name] = 'intermediate'
                                        case _:
                                            raise NotImplementedError(f'Not an array declaration node: {node}')
                    stmt.extend(CircomStatement3.from_json(s, var_type=var_type))
                return CircomTemplate(name, arglst, stmt, var_type, var_array)
            case _:
                raise NotImplementedError(f'Not a template node: {node}')
    
    def to_compute(self):
        string = f'''struct {self.name}_RESULT''' + ''' {'''
        for var in list(self.var_type):
            if self.var_type[var] == 'input' or self.var_type[var] == 'output':
                string += f'''\n    int* {var};'''
        string += '''\n};\n\n'''
        string += f'''struct {self.name}_RESULT* {self.name}('''
        if self.arg:
            l = len(self.arg)
            for i in range(0, l):
                string += f'''const int {self.arg[i]}'''
                if i != l - 1:
                    string += ''', '''
        string += ''') {\n'''
        string += f'''    struct {self.name}_RESULT* result = (struct {self.name}_RESULT*)malloc(sizeof(struct {self.name}_RESULT));

    '''
            
        return string
    
    def to_constraint(self):
        return self.to_compute()

    def to_main(self, call:list):
        string = ''
        if self.arg:
            l = len(self.arg)
            for i in range(0, l):
                string += f'''const int {self.arg[i]} = {call[i]};
    '''
        string += f'''struct {self.name}_RESULT* template = {self.name}('''
        if self.arg:
            l = len(self.arg)
            for i in range(0, l):
                string += f'''{self.arg[i]}'''
                if i != l - 1:
                    string += ''', '''
        string += ''');
    '''
        for var in list(self.var_type):
            if self.var_type[var] == 'input' or self.var_type[var] == 'output':
                if var in list(self.var_array):
                    string += f'''int {var}[{self.var_array[var]}];
    '''
                    string += f'''klee_make_symbolic(&{var}, sizeof {var}, "{var}");
    '''
                    string += f'''for (int i = 0; i < {self.var_array[var]}; i++)'''
                    string += ''' {
    '''
                    string += f'''    klee_assume(template->{var}[i] == {var}[i]);'''
                    string += '''
    }
    '''
                else:
                    string += f'''int {var};
    '''
                    string += f'''klee_make_symbolic(&{var}, sizeof({var}), "{var}");
    '''
                    string += f'''klee_assume(*(template->{var}) == {var});
    '''
        return string

class CircomStatement3(CircomNode):
    def from_json(node, var_type={}):
        match node:
            case ['statement3', ['declaration', *_], ';']:
                return CircomDeclaration.from_json(node[1], var_type)
            case ['statement3', ['statement', ['statement0', ['statement1', *_]]]]:
                return CircomStatement1.from_json(node[1][1][1], var_type)
            case _:
                raise NotImplementedError(f'Not a statement3 node: {node}')

class CircomStatement1(CircomNode):
    def from_json(node, var_type={}):
        match node:
            case ['statement1', 'if', *_]:
                return CircomIf.from_json(node[1:], var_type)
            case ['statement1', ['statement2', *_]]:
                return CircomStatement2.from_json(node[1], var_type)
            case ['statement2', *_]:
                return CircomStatement2.from_json(node, var_type)
            case _:
                raise NotImplementedError(f'Not a statement1 node: {node}')

class CircomIf(CircomNode):
    def __init__(self, c1:CircomNode, c2:CircomNode, c3:CircomNode):
        self.c1 = c1
        self.c2 = c2
        self.c3 = c3
    
    def from_json(node, var_type={}):
        match node:
            case ['if', '(', expression, ')', stmt1, ['parseElseStatement1', 'else', stmt2]]:
                c1 = dispatchExpression(expression, var_type)
                c2 = CircomStatement1.from_json(stmt1, var_type)
                c3 = CircomStatement1.from_json(stmt2, var_type)
                return [CircomIf(c1, c2, c3)]
            case _:
                raise NotImplementedError(f'Not an if node: {node}')
    
    def to_compute(self):
        line = f'if {self.c1.to_c_code()}'
        line += ''' {
    '''
        if isinstance(self.c2, list):
            for stmt in self.c2:
                line += '    '
                line += stmt.to_compute()
        else:
            line += '    '
            line += self.c2.to_compute()
        line += '''} else {
    '''
        if isinstance(self.c3, list):
            for stmt in self.c3:
                line += '    '
                line += stmt.to_compute()
        else:
            line += '    '
            line += self.c3.to_compute()
        line += '''}
    '''

        return line
    
    def to_constraint(self):
        line = f'if {self.c1.to_c_code()}'
        line += ''' {
    '''
        if isinstance(self.c2, list):
            for stmt in self.c2:
                line += '    '
                line += stmt.to_constraint()
        else:
            line += '    '
            line += self.c2.to_constraint()
        line += '''} else {
    '''
        if isinstance(self.c3, list):
            for stmt in self.c3:
                line += '    '
                line += stmt.to_constraint()
        else:
            line += '    '
            line += self.c3.to_constraint()
        line += '''}
    '''

        return line

class CircomDeclaration(CircomNode):
    def __init__(self, type:int, name:str, arr:bool=False, size:str='', val:CircomNode=None):
        self.type = type # 0 = input, 1 = output, 2 = var, 3 = intermediate signals, 4 = component
        self.name = name
        self.arr = arr
        self.size = size
        self.val = val
    
    def from_json(node, var_type={}):
        match node:
            case ['declaration', ['signalHearder', 'signal', ['signalType', type]], ['signalSymbol', ['simpleSymbol', name]]]:
                var_type[name] = type
                if type == 'input':
                    return [CircomDeclaration(0, name)]
                else:
                    return [CircomDeclaration(1, name)]
            case ['declaration', ['signalHearder', 'signal'], ['signalSymbol', ['simpleSymbol', name]]]:
                var_type[name] = 'intermediate'
                return [CircomDeclaration(3, name)]
            case ['declaration', 'var', ['simpleSymbol', name]]:
                var_type[name] = 'var'
                return [CircomDeclaration(2, name)]
            case ['declaration', 'var', ['simpleSymbol', name], ['tupleInitialization', opcode, ['expression', ['parseExpression1', expr]]]]:
                if opcode == '=':
                    var_type[name] = 'var'
                    rhs = dispatchExpression(expr)
                    return [CircomDeclaration(2, name, val=rhs.to_c_code())]
                else:
                    raise NotImplementedError(f'Unhandled assignment: {node}')
            case ['declaration', 'component', ['simpleSymbol', name]]:
                var_type[name] = 'component'
                return [CircomDeclaration(4, name)]
            case ['declaration', 'component', ['simpleSymbol', name], ['tupleInitialization', opcode, ['expression', ['parseExpression1', expr]]]]:
                if opcode == '=':
                    var_type[name] = 'component'
                    rhs = dispatchExpression(expr)
                    return [CircomDeclaration(4, name, val=rhs.to_c_code())]
                else:
                    raise NotImplementedError(f'Unhandled assignment: {node}')
            case ['declaration', 'component', ['simpleSymbol', name, ['arrayAcc', '[', ['expression', ['parseExpression1', expr]], ']']]]:    
                var_type[name] = 'component'
                size = dispatchExpression(expr)
                return [CircomDeclaration(4, name, True, size.to_c_code())]
            case ['declaration', ['signalHearder', 'signal', ['signalType', type]], ['signalSymbol', arrdef]]:
                match arrdef:
                    case ['simpleSymbol', name, ['arrayAcc', '[', ['expression', ['parseExpression1', expr]], ']']]:
                        var_type[name] = type
                        size = dispatchExpression(expr)
                        if type == 'input':
                            return [CircomDeclaration(0, name, True, size.to_c_code())]
                        else:
                            return [CircomDeclaration(1, name, True, size.to_c_code())]
                    case _:
                        raise NotImplementedError(f'Not an array declaration node: {node}')
            case ['declaration', ['signalHearder', 'signal'], ['signalSymbol', arrdef]]:
                match arrdef:
                    case ['simpleSymbol', name, ['arrayAcc', '[', ['expression', ['parseExpression1', expr]], ']']]:
                        var_type[name] = 'intermediate'
                        size = dispatchExpression(expr)
                        return [CircomDeclaration(3, name, True, size.to_c_code())]
                    case _:
                        raise NotImplementedError(f'Not an array declaration node: {node}')
            case _:
                raise NotImplementedError(f'Not a declaration node: {node}')
    def to_compute(self):
        if self.arr and self.type == 0:
            return f'''result->{self.name} = (int*)malloc(sizeof(int) * {self.size});
    klee_make_symbolic(result->{self.name}, sizeof(int) * {self.size}, "{self.name}");
    for (int i=0; i<{self.size}; i++)
        klee_assume(result->{self.name}[i] >= 0);

    '''
        elif self.arr and self.type == 1:
            return f'''result->{self.name} = (int*)malloc(sizeof(int) * {self.size});
    klee_make_symbolic(result->{self.name}, sizeof(int) * {self.size}, "{self.name}");

    '''
        elif self.arr and self.type == 3:
            return f'''int {self.name}[{self.size}];
    klee_make_symbolic(&{self.name}, sizeof(int*), "{self.name}");

    '''
        elif not self.arr and self.type == 0 and self.val is None:
            return f'''result->{self.name} = (int*)malloc(sizeof(int));
    klee_make_symbolic(result->{self.name}, sizeof(int), "{self.name}");
    klee_assume(*(result->{self.name}) >= 0);

    '''
        elif not self.arr and self.type == 0 and self.val is not None:
            return f'''result->{self.name} = (int*)malloc(sizeof(int));
    klee_make_symbolic(result->{self.name}, sizeof(int), "{self.name}");
    klee_assume(*(result->{self.name}) == {self.val});

    '''
        elif not self.arr and self.type == 1:
            return f'''result->{self.name} = (int*)malloc(sizeof(int));
    klee_make_symbolic(result->{self.name}, sizeof(int), "{self.name}");

    '''
        elif not self.arr and self.type == 3:
            return f'''int {self.name};
    klee_make_symbolic(&{self.name}, sizeof(int), "{self.name}");

    '''
        elif self.type == 2 and self.val is None:
            return f'''int {self.name};

    '''
        elif self.type == 2 and self.val is not None:
            return f'''int {self.name} = {self.val};

    '''
        elif self.type == 4 and self.arr:
            return f'''void* {self.name}[{self.size}];

    '''
        elif self.type == 4 and not self.arr and self.val is None:
            return f'''void* {self.name};

    '''
        elif self.type == 4 and not self.arr and self.val is not None:
            return f'''void* {self.name};
    {self.name} = {self.val};
    '''

    def to_constraint(self):
        return self.to_compute()
    
    def to_c_code(self):
        if self.type != 2 or self.val is None:
            return ''
        return f'int {self.name} = {self.val}'

class CircomVar(CircomNode):
    def __init__(self, label:str, var_type:dict={}):
        self.terminal = True
        self.label = label
        self.var_type = var_type
    
    def to_c_code(self):
        if self.var_type:
            if self.label in list(self.var_type):
                if self.var_type[self.label] == 'input' or self.var_type[self.label] == 'output':
                    return f'''*(result->{self.label})'''
        return self.label

class CircomInstruction(CircomNode):
    def __init__(self, opcode:Opcode, op1:CircomNode=None, op2:CircomNode=None, op3:CircomNode=None, op4:CircomNode=None):
        self.terminal = False
        self.op1 = op1
        self.op2 = op2
        self.op3 = op3
        self.op4 = op4
        self.opcode = opcode

class CircomSubstitution(CircomInstruction):
    def __init__(self, opcode:Opcode, op1:CircomNode, op2:CircomNode):
        super().__init__(opcode=opcode, op1=op1, op2=op2)

    def from_json(node, var_type):
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
                op1 = dispatchExpression(lhs, var_type)
                op2 = dispatchExpression(rhs, var_type)
                if opcode == '=':
                    t = type(op1)
                    if t == CircomVar:
                        var = op1.label
                        if var_type[var] == 'component':
                            if type(op2) == CircomExpression1:
                                identifier = op2.name
                                var_type[var] = identifier
                    if t == CircomListable:
                        var = op1.op1.label
                        if var_type[var] == 'component':
                            if type(op2) == CircomExpression1:
                                identifier = op2.name
                                var_type[var] = identifier
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
                op1 = dispatchExpression(lhs, var_type)
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
                return [CircomSubstitution(opcode=op, op1=CircomVar(name, var_type=var_type), op2=None)]
            case ['substition', ['expression', ['parseExpression1', lhs]], '==>', ['expression', ['parseExpression1', rhs]]]:
                op1 = dispatchExpression(lhs, var_type)
                op2 = dispatchExpression(rhs, var_type)
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
        elif self.opcode == Opcode.ASSIGN_VAR:
            return f'{self.op1.to_c_code()} = {self.op2.to_c_code()}'

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
    
    def from_json(node, var_type={}):
        match node:
            case ['statement2', ['substition', *_], ';']:
                return CircomSubstitution.from_json(node[1], var_type)
            case ['statement2', ['block', *_]]:
                stmt = []
                for s in node[1][2:-1]:
                    stmt.extend(CircomStatement3.from_json(s, var_type))
                return CircomBlock.from_json(stmt)
            case ['statement2', _, '===', _, ';']:
                op1 = dispatchExpression(node[1][1][1], var_type)
                op2 = dispatchExpression(node[3][1][1], var_type)
                return [CircomConstraintEq(op1=op1, op2=op2)]
            case ['statement2', 'for', *_]:
                c1 = None
                if node[3][0] == 'substition':
                    c1 = CircomSubstitution.from_json(node[3], var_type)
                elif node[3][0] == 'declaration':
                    c1 = CircomDeclaration.from_json(node[3], var_type)
                else:
                    raise NotImplementedError(f'Unhandled for condition: {node}')
                c2 = dispatchExpression(node[5][1][1], var_type)
                c3 = CircomSubstitution.from_json(node[7], var_type)
                assert len(c1) == 1, f'error in for condition: {node}'
                assert len(c3) == 1, f'error in for condition: {node}'
                stmt = []
                if node[9][1][0] == 'block':
                    for s in node[9][1][2:-1]:
                        stmt.extend(CircomStatement3.from_json(s, var_type))
                else:
                    stmt.extend(CircomStatement2.from_json(node[9], var_type))
                return [CircomFor(c1[0], c2, c3[0], stmt)]
            case _:
                raise NotImplementedError(f'Not a statement2 node: {node}')

class CircomBlock(CircomNode):
    def __init__(self, stmt:list[CircomNode]):
        self.statement = stmt
    
    def from_json(stmt:list[CircomNode]):
        return [CircomBlock(stmt)]
    
    def to_compute(self):
        line = ''
        for stmt in self.statement:
            line += stmt.to_compute()
        return line
    
    def to_constraint(self):
        line = ''
        for stmt in self.statement:
            line += stmt.to_constraint()
        return line

class CircomTernary(CircomInstruction): # expression13
    def __init__(self, op1, op2, op3):
        super().__init__(opcode=Opcode.TERNARY, op1=op1, op2=op2, op3=op3)

    def from_json(node, var_type={}):
        match node:
            case ['expression13', cond, '?', true, ':', false]:
                op1 = dispatchExpression(cond, var_type)
                op2 = dispatchExpression(true, var_type)
                op3 = dispatchExpression(false, var_type)
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

    def from_json(node, var_type={}):
        match node:
            case ['expression12', *lhs, '||', rhs]:
                if len(lhs) == 1:
                    op1 = dispatchExpression(lhs[0], var_type)
                else:
                    op1 = dispatchExpression(['expression12', *lhs], var_type)
                op2 = dispatchExpression(rhs, var_type)
                return [CircomOr(opcode=Opcode.OR, op1=op1, op2=op2)]
            case _:
                raise NotImplementedError(f'Not an or node: {node}')

    def to_c_code(self):
        return '(' + self.op1.to_c_code() + ' || ' + self.op2.to_c_code() + ')'

class CircomAnd(CircomInstruction): #expression11
    def __init__(self, opcode:Opcode, op1:CircomNode, op2:CircomNode):
        super().__init__(opcode=opcode, op1=op1, op2=op2)

    def from_json(node, var_type={}):
        match node:
            case ['expression11', *lhs, '&&', rhs]:
                if len(lhs) == 1:
                    op1 = dispatchExpression(lhs[0], var_type)
                else:
                    op1 = dispatchExpression(['expression11', *lhs], var_type)
                op2 = dispatchExpression(rhs, var_type)
                return [CircomAnd(opcode=Opcode.AND, op1=op1, op2=op2)]
            case _:
                raise NotImplementedError(f'Not an and node: {node}')

    def to_c_code(self):
        return '(' + self.op1.to_c_code() + ' && ' + self.op2.to_c_code() + ')'

class CircomCompare(CircomInstruction): #expression10
    def __init__(self, opcode:Opcode, op1:CircomNode, op2:CircomNode):
        super().__init__(opcode=opcode, op1=op1, op2=op2)

    def from_json(node, var_type={}):
        match node:
            case ['expression10', *lhs, ['cmpOpCodes', opcode], rhs]:
                op = None
                match opcode:
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
                if len(lhs) == 1:
                    op1 = dispatchExpression(lhs[0], var_type)
                else:
                    op1 = dispatchExpression(['expression10', *lhs], var_type)
                op2 = dispatchExpression(rhs, var_type)
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

    def from_json(node, var_type={}):
        match node:
            case ['expression9', *lhs, '|', rhs]:
                if len(lhs) == 1:
                    op1 = dispatchExpression(lhs[0], var_type)
                else:
                    op1 = dispatchExpression(['expression9', *lhs], var_type)
                op2 = dispatchExpression(rhs, var_type)
                return [CircomOrBit(opcode=Opcode.OR_BIT, op1=op1, op2=op2)]
            case _:
                raise NotImplementedError(f'Not an or bit node: {node}')

    def to_c_code(self):
        return '(' + self.op1.to_c_code() + ' | ' + self.op2.to_c_code() + ')'
            

class CircomXorBit(CircomInstruction): #expression8
    def __init__(self, opcode:Opcode, op1:CircomNode, op2:CircomNode):
        super().__init__(opcode=opcode, op1=op1, op2=op2)

    def from_json(node, var_type={}):
        match node:
            case ['expression8', *lhs, '^', rhs]:
                if len(lhs) == 1:
                    op1 = dispatchExpression(lhs[0], var_type)
                else:
                    op1 = dispatchExpression(['expression8', *lhs], var_type)
                op2 = dispatchExpression(rhs, var_type)
                return [CircomXorBit(opcode=Opcode.XOR_BIT, op1=op1, op2=op2)]
            case _:
                raise NotImplementedError(f'Not an xor bit node: {node}')

    def to_c_code(self):
        return '(' + self.op1.to_c_code() + ' ^ ' + self.op2.to_c_code() + ')'

class CircomAndBit(CircomInstruction): #expression7
    def __init__(self, opcode:Opcode, op1:CircomNode, op2:CircomNode):
        super().__init__(opcode=opcode, op1=op1, op2=op2)
    
    def from_json(node, var_type={}):
        match node:
            case ['expression7', *lhs, '&', rhs]:
                if len(lhs) == 1:
                    op1 = dispatchExpression(lhs[0], var_type)
                else:
                    op1 = dispatchExpression(['expression7', *lhs], var_type)
                op2 = dispatchExpression(rhs, var_type)
                return [CircomAndBit(opcode=Opcode.AND_BIT, op1=op1, op2=op2)]
            case _:
                raise NotImplementedError(f'Not an and bit node: {node}')

    def to_c_code(self):
        return '(' + self.op1.to_c_code() + ' & ' + self.op2.to_c_code() + ')'

class CircomShift(CircomInstruction): #expression6
    def __init__(self, opcode:Opcode, op1:CircomNode, op2:CircomNode):
        super().__init__(opcode=opcode, op1=op1, op2=op2)

    def from_json(node, var_type={}):
        match node:
            case ['expression6', *lhs, ['shiftOp', opcode], rhs]:
                op = None
                match opcode:
                    case '<<':
                        op = Opcode.SHIFTL
                    case '>>':
                        op = Opcode.SHIFTR
                if len(lhs) == 1:
                    op1 = dispatchExpression(lhs[0], var_type)
                else:
                    op1 = dispatchExpression(['expression6', *lhs], var_type)
                op2 = dispatchExpression(rhs, var_type)
                return [CircomShift(opcode=op, op1=op1, op2=op2)]
            case _:
                raise NotImplementedError(f'Not a shift node: {node}')

    def to_c_code(self):
        op_str = ''
        if self.opcode == Opcode.SHIFTL:
            op_str = '<<'
        elif self.opcode == Opcode.SHIFTR:
            op_str = '>>'
        return '(' + self.op1.to_c_code() + ' ' + op_str + ' ' + self.op2.to_c_code() + ')'

class CircomAddSub(CircomInstruction): #expression5
    def __init__(self, opcode:Opcode, op1:CircomNode, op2:CircomNode):
        super().__init__(opcode=opcode, op1=op1, op2=op2)
    
    def from_json(node, var_type={}):
        match node:
            case ['expression5', *lhs, ['addSubOp', opcode], rhs]:
                op = None
                match opcode:
                    case '+':
                        op = Opcode.PLUS
                    case '-':
                        op = Opcode.MINUS
                if len(lhs) == 1:
                    op1 = dispatchExpression(lhs[0], var_type)
                else:
                    op1 = dispatchExpression(['expression5', *lhs], var_type)
                op2 = dispatchExpression(rhs, var_type)
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

    def from_json(node, var_type={}):
        match node:
            case ['expression4', *lhs, ['mulDivOp', opcode], rhs]:
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
                if len(lhs) == 1:
                    op1 = dispatchExpression(lhs[0], var_type)
                else:
                    op1 = dispatchExpression(['expression4', *lhs], var_type)
                op2 = dispatchExpression(rhs, var_type)
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
            op_str = '/'
        elif self.opcode == Opcode.MOD:
            op_str = '%'
        return '(' + self.op1.to_c_code() + ' ' + op_str + ' ' + self.op2.to_c_code() + ')'

class CircomPow(CircomInstruction): #expression3
    def __init__(self, opcode:Opcode, op1:CircomNode, op2:CircomNode):
        super().__init__(opcode=opcode, op1=op1, op2=op2)

    def from_json(node, var_type={}):
        match node:
            case ['expression3', *lhs, '**', rhs]:
                if len(lhs) == 1:
                    op1 = dispatchExpression(lhs[0], var_type)
                else:
                    op1 = dispatchExpression(['expression3', *lhs], var_type)
                op2 = dispatchExpression(rhs, var_type)
                return [CircomPow(opcode=Opcode.POW, op1=op1, op2=op2)]
            case _:
                raise NotImplementedError(f'Not a pow node: {node}')

    def to_c_code(self):
        return f'pow({self.op1.to_c_code()}, {self.op2.to_c_code()})'

class CircomPrefix(CircomInstruction): #expression2
    def __init__(self, opcode:Opcode, op1:CircomNode):
        super().__init__(opcode=opcode, op1=op1)
        
    def from_json(node, var_type={}):
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
                op1 = dispatchExpression(rhs, var_type)
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
        return '(' + ' ' + op_str + ' ' + self.op1.to_c_code() + ')'

class CircomListable(CircomInstruction):
    def __init__(self, op1:str, op2:str, var_type:dict={}):
        self.var_type = var_type
        super().__init__(opcode=Opcode.ARR, op1=CircomVar(op1,var_type), op2=CircomVar(op2,var_type))

    def from_json(node, var_type={}):
        print('In Listable')

    def to_c_code(self):
        if not self.op1.label in list(self.var_type):
            return f'{self.op1.label}[{self.op2.label}]'
        elif self.var_type[self.op1.label] == 'input' or self.var_type[self.op1.label] == 'output':
            return f'result->{self.op1.label}[{self.op2.label}]'
        else:
            return f'{self.op1.label}[{self.op2.label}]'

class CircomListableField(CircomInstruction):
    def __init__(self, op1:str, op2:str, op3:str, var_type:dict={}):
        self.var_type = var_type
        super().__init__(opcode=Opcode.FIELD, op1=CircomVar(op1,var_type), op2=CircomVar(op2,var_type), op3=CircomVar(op3,var_type))

    def from_json(node, var_type={}):
        print('In ListableField')

    def to_c_code(self):
        assert self.var_type[self.op1.label], f'component not found error: {self.op1.label}'
        return f'*(((struct {self.var_type[self.op1.label]}_RESULT*){self.op1.label}[{self.op2.label}])->{self.op3.label})'

class CircomListableFieldListable(CircomInstruction):
    def __init__(self, op1:str, op2:str, op3:str, op4:str, var_type:dict={}):
        self.var_type = var_type
        super().__init__(opcode=Opcode.ARR, op1=CircomVar(op1,var_type), op2=CircomVar(op2,var_type), op3=CircomVar(op3,var_type), op4=CircomVar(op4,var_type))

    def from_json(node, var_type={}):
        print('In ListableFieldListable')

    def to_c_code(self):
        assert self.var_type[self.op1.label], f'component not found error: {self.op1.label}'
        return f'((struct {self.var_type[self.op1.label]}_RESULT*){self.op1.label}[{self.op2.label}])->{self.op3.label}[{self.op4.label}]'


class CircomField(CircomInstruction):
    def __init__(self, op1:str, op2:str, var_type:dict={}):
        self.var_type = var_type
        super().__init__(opcode=Opcode.FIELD, op1=CircomVar(op1,var_type), op2=CircomVar(op2,var_type))

    def from_json(node, var_type={}):
        print('In Field')

    def to_c_code(self):
        assert self.var_type[self.op1.label], f'component not found error: {self.op1.label}'
        return f'*(((struct {self.var_type[self.op1.label]}_RESULT*){self.op1.label})->{self.op2.label})'

class CircomFieldListable(CircomInstruction):
    def __init__(self, op1:str, op2:str, op3:str, var_type:dict={}):
        self.var_type = var_type
        super().__init__(opcode=Opcode.ARR, op1=CircomVar(op1,var_type), op2=CircomVar(op2,var_type), op3=CircomVar(op3,var_type))

    def from_json(node, var_type={}):
        print('In FieldListable')

    def to_c_code(self):
        assert self.var_type[self.op1.label], f'component not found error: {self.op1.label}'
        return f'((struct {self.var_type[self.op1.label]}_RESULT*){self.op1.label})->{self.op2.label}[{self.op3.label}]'


class CircomExpression1(): #expression1
    def __init__(self, name:str, para:CircomNode=None):
        self.name = name
        self.para = para

    def from_json(node, var_type={}):
        match node:
            case ['expression1', name, '(', ')']:
                return [CircomExpression1(name=name)]
            case ['expression1', name, '(', expr,  ')']:
                para = dispatchExpression(expr, var_type=var_type)
                return [CircomExpression1(name=name, para=para)]
            case _:
                raise NotImplementedError(f'Not a expression1 node: {node}')
    
    def to_c_code(self):
        if self.para:
            return f'{self.name}({self.para.to_c_code()})'
        else:
            return f'{self.name}()'


class CircomTerminal(CircomVar): #expression0
    def from_json(node, var_type={}):
        match node:
            case ['expression0', ['variable', label]]:
                return [CircomVar(label, var_type=var_type)]
            case ['expression0', ['variable', label, ['varAccess', ['arrayAcc', '[', ['expression', ['parseExpression1', expr]], ']']]]]:
                idx = dispatchExpression(expr, var_type)
                return [CircomListable(label, idx.to_c_code(), var_type=var_type)]
            case ['expression0', ['variable', label, ['varAccess', ['arrayAcc', '[', ['expression', ['parseExpression1', expr]], ']']], ['varAccess', ['componentAcc', '.', name]]]]:
                idx = dispatchExpression(expr, var_type)
                return [CircomListableField(label, idx.to_c_code(), name, var_type=var_type)]
            case ['expression0', ['variable', label, ['varAccess', ['arrayAcc', '[', ['expression', ['parseExpression1', expr]], ']']], ['varAccess', ['componentAcc', '.', name]], ['varAccess', ['arrayAcc', '[', ['expression', ['parseExpression1', expr2]], ']']]]]:
                idx = dispatchExpression(expr, var_type)
                idx2 = dispatchExpression(expr2, var_type)
                return [CircomListableFieldListable(label, idx.to_c_code(), name, idx2.to_c_code(), var_type=var_type)]
            case ['expression0', ['variable', label, ['varAccess', ['componentAcc', '.', name]]]]:
                return [CircomField(label, name, var_type=var_type)]
            case ['expression0', ['variable', label, ['varAccess', ['componentAcc', '.', name]], ['varAccess', ['arrayAcc', '[', ['expression', ['parseExpression1', expr]], ']']]]]:
                idx = dispatchExpression(expr, var_type)
                return [CircomFieldListable(label, name, idx.to_c_code(), var_type=var_type)]
            case ['expression0', ['variable', label, ['varAccess', ['arrayAcc', '[', ['expression', ['parseExpression1', expr]], ']']]]]:
                idx = dispatchExpression(expr, var_type)
                return [CircomListable(label, idx.to_c_code(), var_type=var_type)]
            case ['expression0', i]:
                assert isinstance(i, str), f'expression0 error: {i} in {node}'
                if i.isdigit():
                    return [CircomVar(i)]
            case ['expression0', '(', ['expression', ['parseExpression1', expr]], ')']:
                return [dispatchExpression(expr, var_type)]
            case _:
                raise NotImplementedError(f'Not a terminal node: {node}')