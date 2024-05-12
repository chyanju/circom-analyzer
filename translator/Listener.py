import sys
sys.path.append('..')
from CircomParser import CircomParser
from CircomParserListener import CircomParserListener

class Listener(CircomParserListener):

    def __init__(self, file_name:str):
        self.queue = []
        self.inst_op = []
        self.compute = open(file_name + '_compute.c', 'w')
        self.constraint = open(file_name + '_constraint.c', 'w')

    def enterTemplateDefinition(self, ctx:CircomParser.TemplateDefinitionContext):
        print('Template:', ctx.IDENTIFIER())
        # pass
    
    def enterDeclaration(self, ctx:CircomParser.DeclarationContext):
        typ = ctx.signalHearder().signalType()
        vars = ctx.signalSymbol()
        ids = map(lambda v: v.simpleSymbol().IDENTIFIER(), vars)
        if typ.INPUT() is not None:
            print('Input signal:')
            for i in ids:
                line = f'''int {i};
    klee_make_symbolic(&{i}, sizeof(int), "{i}");
    klee_assume({i} >= 0);

    '''
                self.compute.write(line)
                self.constraint.write(line)
        else:
            print('Output signal:')
            for i in ids:
                line = f'''int {i};
    klee_make_symbolic(&{i}, sizeof(int), "{i}");

    '''
                self.compute.write(line)
                self.constraint.write(line)
        
        for v in vars:
            print(v.simpleSymbol().IDENTIFIER())
    
    def enterVariable(self, ctx:CircomParser.VariableContext):
        self.queue.append(ctx.IDENTIFIER())
    
    def enterAssignOp(self, ctx:CircomParser.AssignOpContext):
        self.inst_op.append(ctx)
    
    def enterMulDivOp(self, ctx:CircomParser.MulDivOpContext):
        if len(self.queue) > 0:
            lhs = self.queue.pop(0)
            self.inst_op.append(lhs)
        if ctx.MUL() is not None:
            self.inst_op.append(ctx.MUL())
        elif ctx.DIV() is not None:
            self.inst_op.append(ctx.DIV())
        elif ctx.INTDIV() is not None:
            self.inst_op.append(ctx.INTDIV())
        elif ctx.MOD() is not None:
            self.inst_op.append(ctx.MOD())
    
    def enterAddSubOp(self, ctx:CircomParser.MulDivOpContext):
        if len(self.queue) > 0:
            lhs = self.queue.pop(0)
            self.inst_op.append(lhs)
        if ctx.PLUS() is not None:
            self.inst_op.append(ctx.PLUS())
        elif ctx.MINUS() is not None:
            self.inst_op.append(ctx.MINUS())
    
    def exitExpression(self, ctx:CircomParser.ExpressionContext):
        if len(self.queue) > 0:
            var = self.queue.pop(0)
            self.inst_op.append(var)
    
    def enterSubstition(self, ctx:CircomParser.SubstitionContext):
        print('Substitution:')
        # pass
    
    def exitSubstition(self, ctx:CircomParser.SubstitionContext):
        idx = self.inst_op.index(next(op for op in self.inst_op if isinstance(op, CircomParser.AssignOpContext)))
        lhs = self.inst_op[0:idx]
        rhs = self.inst_op[idx + 1:]
        lhs_str = str(lhs[0]) if len(lhs) == 1 else '(' + ' '.join(str(i) for i in lhs) + ')'
        rhs_str = str(rhs[0]) if len(rhs) == 1 else '(' + ' '.join(str(i) for i in rhs) + ')'
        line = f'''klee_assume({lhs_str} == {rhs_str});

    '''
        if self.inst_op[idx].ASSIGN_CONSTRAINT_SIGNAL() is not None:
            self.compute.write(line)
            self.constraint.write(line)

        print(*self.inst_op)
        self.inst_op.clear()
    
    def enterMainComponent(self, ctx:CircomParser.MainComponentContext):
        print('Main:')
        # pass
    
    def enterExpression1(self, ctx:CircomParser.Expression1Context):
        if ctx.IDENTIFIER() is not None:
            print('Call function:', ctx.IDENTIFIER())
        # pass
    
    def enterExpression0(self, ctx:CircomParser.Expression0Context):
        if ctx.LPAREN() is not None:
            self.inst_op.append(ctx.LPAREN())

    def exitExpression0(self, ctx:CircomParser.Expression0Context):
        if ctx.RPAREN() is not None:
            self.inst_op.append(ctx.RPAREN())

    def enterProgram(self, ctx:CircomParser.ProgramContext):
        header = '''// AUTO GENERATED
#include <stdio.h>
#include <stdbool.h>
#include <klee/klee.h>
unsigned long long constant = 2188824287183927;


int main(int argc, char** argv) {

    '''
        self.compute.write(header)
        self.constraint.write(header)
    
    def exitProgram(self, ctx:CircomParser.ProgramContext):
        line = '''return 0;
}
'''
        self.compute.write(line)
        self.constraint.write(line)
        self.compute.close()
        self.constraint.close()
