#!/usr/bin/env python
# NOTE: this is project script and shall not be called directly

import argparse
import sys
import json
import os

from .backend.common import *
from .backend.CircomType import CircomTemplate, CircomNode
from antlr4 import FileStream

def process_includes(json_tree, base_path, processed_files=None):
    if processed_files is None:
        processed_files = set()
        
    processed_tree = []
    for node in json_tree:
        if isinstance(node, list) and node[0] == 'include':
            include_path = node[2].strip('"')
            full_path = os.path.normpath(os.path.join(base_path, include_path))
            
            if full_path in processed_files:
                continue
                
            processed_files.add(full_path)
            
            include_stream = FileStream(full_path, encoding='utf-8')
            include_tree = tree2json(include_stream)
            
            include_tree = process_includes(include_tree, os.path.dirname(full_path), processed_files)
            
            for include_node in include_tree:
                if isinstance(include_node, list) and include_node[0] == 'definition':
                    processed_tree.append(include_node)
        
        elif isinstance(node, list):
            processed_tree.append(node)
    return processed_tree

def write(templates:list[CircomTemplate], main, file_name:str, call:list):
    compute = open(file_name + '_compute.c', 'w')
    constraint = open(file_name + '_constraint.c', 'w')

    header = '''// AUTO GENERATED
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <klee/klee.h>
unsigned long long constant = 2188824287183927;

'''
    compute.write(header)
    constraint.write(header)

    return_part = '''return result;
}

'''

    for t in templates:
        # print(f'writing: {s}')
        compute.write(t.to_compute())
        constraint.write(t.to_constraint())
        for s in t.statement:
            compute.write(s.to_compute())
            constraint.write(s.to_constraint())
        compute.write(return_part)
        constraint.write(return_part)
    if main:
        main_header = '''int main(int argc, char** argv) {

    '''
        compute.write(main_header)
        constraint.write(main_header)

        for t in templates:
            if main == t.name:
                compute.write(t.to_main(call))
                constraint.write(t.to_main(call))
                break

        end = '''return 0;
}
'''
        compute.write(end)
        constraint.write(end)
    compute.close()
    constraint.close()

def translate(file_name, return_input, return_output, return_signal, return_var, return_public, return_private, return_intermediate, return_c_files):
    input_stream = FileStream(file_name, encoding='utf-8')
    json_tree = tree2json(input_stream)
    
    base_path = os.path.dirname(file_name)
    json_tree = process_includes(json_tree, base_path)
    
    input = []
    output = []
    signal = []
    var = []
    public = []
    private = []
    intermediate = []
    
    template_lst = []
    call = []

    # print(json_tree)
    main_component = None

    # find main component
    # for i in json_tree:
    #     match i:
    #         case ['mainComponent', 'component', 'main', '=', ['expression', ['parseExpression1', body]], ';']:
    #             match body:
    #                 case ['expression12', ['expression11', ['expression10', ['expression9', ['expression8', ['expression7', ['expression6', ['expression5', ['expression4', ['expression3', ['expression2', ['expression1', template, '(', ['listableExpression', ['expression', ['parseExpression1', expr]]], ')']]]]]]]]]]:
    #                     main_component = template
    #         case ['mainComponent', 'component', 'main', ['publicList', '{', 'public', '[', arg, ']', '}'], '=', ['expression', ['parseExpression1', body]], ';']:
    #             match body:
    #                 case ['expression12', ['expression11', ['expression10', ['expression9', ['expression8', ['expression7', ['expression6', ['expression5', ['expression4', ['expression3', ['expression2', ['expression1', template, '(', ['listableExpression', ['expression', ['parseExpression1', expr]]], ')']]]]]]]]]]]]:
    #                     main_component = template
    
    # if main_component is None:
    #     raise NotImplementedError(f'No main component found in {file_name}')

    for i in json_tree:
        match i:
            case ['definition', definition]:
                template_lst.append(CircomTemplate.from_json(definition))
            case ['mainComponent', 'component', 'main', '=', ['expression', ['parseExpression1', body]], ';']:
                match body:
                    case ['expression12', ['expression11', ['expression10', ['expression9', ['expression8', ['expression7', ['expression6', ['expression5', ['expression4', ['expression3', ['expression2', ['expression1', template, '(', ')']]]]]]]]]]]]:
                        main_component = template
                    case ['expression12', ['expression11', ['expression10', ['expression9', ['expression8', ['expression7', ['expression6', ['expression5', ['expression4', ['expression3', ['expression2', ['expression1', template, '(', ['listableExpression', ['expression', ['parseExpression1', expr]]], ')']]]]]]]]]]]]:
                        main_component = template
                        match expr:
                            case ['expression12', ['expression11', ['expression10', ['expression9', ['expression8', ['expression7', ['expression6', ['expression5', ['expression4', ['expression3', ['expression2', ['expression1', ['expression0', num]]]]]]]]]]]]]:
                                call.append(num)
                            case _:
                                raise NotImplementedError(f'Unsupported argument for main function: {expr}')
            case ['mainComponent', 'component', 'main', ['publicList', '{', 'public', '[', arg, ']', '}'], '=', ['expression', ['parseExpression1', body]], ';']:
                if arg[0] == 'identifierList':
                    arglst = list(a for a in arg[1:] if a != ',')
                match body:
                    case ['expression12', ['expression11', ['expression10', ['expression9', ['expression8', ['expression7', ['expression6', ['expression5', ['expression4', ['expression3', ['expression2', ['expression1', template, '(', ')']]]]]]]]]]]]:
                        main_component = template
                    case ['expression12', ['expression11', ['expression10', ['expression9', ['expression8', ['expression7', ['expression6', ['expression5', ['expression4', ['expression3', ['expression2', ['expression1', template, '(', ['listableExpression', ['expression', ['parseExpression1', expr]]], ')']]]]]]]]]]]]:
                        main_component = template
                        match expr:
                            case ['expression12', ['expression11', ['expression10', ['expression9', ['expression8', ['expression7', ['expression6', ['expression5', ['expression4', ['expression3', ['expression2', ['expression1', ['expression0', num]]]]]]]]]]]]]:
                                call.append(num)
                            case _:
                                raise NotImplementedError(f'Unsupported argument for main function: {expr}')
            # other case
            # case _:
            #     print(i)
    
    data = {}
    # if return_public:
    #     # output public signals
    #     data['public'] = public
    # if return_private:
    #     # output private signals
    #     data['private'] = [s for s in private if s not in public]
    # if return_intermediate:
    #     # output intermediate signals
    #     data['intermediate'] = intermediate
    # if return_input:
    #     # output input signals
    #     data['input'] = input
    # if return_output:
    #     # output output signals
    #     data['output'] = output
    # if return_signal:
    #     # output all signals
    #     data['signal'] = signal
    # if return_var:
    #     # output variables
    #     data['var'] = var

    if data:
        with open(file_name + '_info.json', 'w') as json_file:
            json.dump(data, json_file, indent=4)

    if return_c_files:
        write(template_lst, main_component, file_name, call)

def run():
    # invoke translator/circom/backend/translator.py with arguments
    ap = argparse.ArgumentParser(description="Circom translator that converts Circom to C, with options to output specific signals or variables to a JSON file.")
    ap.add_argument("--input", default=None, type=str, help="input Circom file path")
    ap.add_argument("--ins", action='store_true', help="return input signals")
    ap.add_argument("--outs", action='store_true', help="return output signals")
    ap.add_argument("--s", action='store_true', help="return all signals")
    ap.add_argument("--v", action='store_true', help="return variables")
    ap.add_argument("--pub", action='store_true', help="return public signals")
    ap.add_argument("--pri", action='store_true', help="return private signals")
    ap.add_argument("--inter", action='store_true', help="return intermediate signals")
    ap.add_argument("--c", action='store_true', help="generate C files")
    args = ap.parse_args()
    if len(sys.argv) == 1:
        ap.print_help(sys.stderr)
        sys.exit(1)
    # set corresponding arguments
    file_name = args.input
    return_input = args.ins
    return_output = args.outs
    return_signal = args.s
    return_var = args.v
    return_public = args.pub
    return_private = args.pri
    return_intermediate = args.inter
    return_c_files = args.c
    
    translate(file_name, return_input, return_output, return_signal, return_var, return_public, return_private, return_intermediate, return_c_files)

if __name__ == "__main__":
    run()