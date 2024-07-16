import sys
from common import *
from CircomType import CircomTemplate, CircomNode
from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
sys.path.append('..')
sys.path.append('../parser/')
from CircomLexer import CircomLexer
from CircomParser import CircomParser

def write(stmt:list[CircomNode], file_name:str):
    compute = open(file_name + '_compute.c', 'w')
    constraint = open(file_name + '_constraint.c', 'w')

    header = '''// AUTO GENERATED
#include <stdio.h>
#include <stdbool.h>
#include <klee/klee.h>
unsigned long long constant = 2188824287183927;


int main(int argc, char** argv) {

    '''
    compute.write(header)
    constraint.write(header)

    for s in stmt:
        # print(f'writing: {s}')
        compute.write(s.to_compute())
        constraint.write(s.to_constraint())
    
    end = '''return 0;
}
'''
    compute.write(end)
    constraint.write(end)
    compute.close()
    constraint.close()

def main():
    if (len(sys.argv) != 2):
        print('Enter file name!')
        return

    file_name = sys.argv[1]
    input_stream = FileStream(file_name)
    
    json_tree = tree2json(input_stream)
    template_def = None
    call = []

    # print(json_tree)

    for i in json_tree:
        match i:
            case ['definition', definition]:
                template_def = definition
            case ['mainComponent', 'component', 'main', '=', ['expression', ['parseExpression1', body]], ';']:
                match body:
                    case ['expression12', ['expression11', ['expression10', ['expression9', ['expression8', ['expression7', ['expression6', ['expression5', ['expression4', ['expression3', ['expression2', ['expression1', template, '(', ['listableExpression', ['expression', ['parseExpression1', expr]]], ')']]]]]]]]]]]]:
                        call.append(template)
                        call.append(expr)

    template = CircomTemplate.from_json(template_def, call)
    
    # for s in template.statement:
    #     print(s)

    write(template.statement, file_name)

if __name__ == '__main__':
    main()
