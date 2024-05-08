# To generate the lexer and parser files

```bash
antlr4 -Dlanguage=Python3 CircomLexer.g4
antlr4 -Dlanguage=Python3 CircomParser.g4
```

# To run the parser

```bash
python test_circom.py
```

The test circom program is in the file `demo.circom`