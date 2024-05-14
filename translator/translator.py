import sys
from Listener import Listener
from common import *
from CircomType import CircomTemplate
from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
sys.path.append('..')
from CircomLexer import CircomLexer
from CircomParser import CircomParser

def write(template:CircomTemplate, file_name:str):
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

    for s in template.statement:
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
    template = None

    for i in json_tree:
        match i:
            case ['definition', definition]:
                template = CircomTemplate.from_json(definition)
    
    # for s in template.statement:
    #     print(s)
    
    write(template, file_name)

if __name__ == '__main__':
    main()
