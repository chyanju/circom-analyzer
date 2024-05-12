import sys
from Listener import Listener
from antlr4 import FileStream, CommonTokenStream, ParseTreeWalker
sys.path.append('..')
from CircomLexer import CircomLexer
from CircomParser import CircomParser

def main():
    # Load the Circom program
    if (len(sys.argv) != 2):
        print('Enter file name!')
        return

    file_name = sys.argv[1]
    input_stream = FileStream(file_name)
    
    # Lexing
    lexer = CircomLexer(input_stream)
    stream = CommonTokenStream(lexer)
    
    # Parsing
    parser = CircomParser(stream)
    tree = parser.program()  # Start parsing at the 'file' rule
    # Print the parse tree (for demonstration)
    print(tree.toStringTree(recog=parser))

    walker = ParseTreeWalker()
    walker.walk(Listener(file_name), tree)

if __name__ == '__main__':
    main()
