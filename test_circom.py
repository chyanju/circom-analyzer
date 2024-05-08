from antlr4 import FileStream, CommonTokenStream
from CircomLexer import CircomLexer
from CircomParser import CircomParser

def main():
    # Load the Circom program
    input_stream = FileStream('demo.circom')
    
    # Lexing
    lexer = CircomLexer(input_stream)
    stream = CommonTokenStream(lexer)
    
    # Parsing
    parser = CircomParser(stream)
    tree = parser.program()  # Start parsing at the 'file' rule
    
    # Print the parse tree (for demonstration)
    print(tree.toStringTree(recog=parser))

if __name__ == '__main__':
    main()
