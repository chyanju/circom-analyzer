lexer grammar CircomLexer;

PRAGMA: 'pragma';
CIRCOM: 'circom';
CUSTOM_TEMPLATES: 'custom_templates';
INCLUDE: 'include';
COMPONENT: 'component';
FUNCTION: 'function';
TEMPLATE: 'template';
PUBLIC: 'public';
VAR: 'var';
SIGNAL: 'signal';
INPUT: 'input';
OUTPUT: 'output';
IF: 'if';
ELSE: 'else';
FOR: 'for';
WHILE: 'while';
RETURN: 'return';
ASSERT: 'assert';
LOG: 'log';
PARALLEL: 'parallel';
MAIN: 'main';


OR: '||';

AND: '&&';

EQ: '==';
NEQ: '!=';
LT: '<';
GT: '>';
LE: '<=';
GE: '>=';

OR_BIT: '|';

AND_BIT: '&';

SHIFTL: '<<';
SHIFTR: '>>';

PLUS: '+';
MINUS: '-';
// note that the '-' is also used for the unary minus

MUL: '*';
DIV: '/';
INTDIV: '\\';
MOD: '%';

POW: '**';

XOR_BIT: '^';

NOT: '!';
COMPLEMENT: '~';


ASSIGN_VAR: '=';
ASSIGN_SIGNAL: '<--';
ASSIGN_CONSTRAINT_SIGNAL: '<==';

RIGHT_ASSIGN_SIGNAL: '-->';
RIGHT_ASSIGN_CONSTRAINT_SIGNAL: '==>';
CONSTRAINT_EQUALITY: '===';

QUESTION: '?';
COLON: ':';

DOT: '.';
UNDERLINE: '_';

LPAREN: '(';
RPAREN: ')';
LBRACE: '{';
RBRACE: '}';
LSQUARE: '[';
RSQUARE: ']';
COMMA: ',';
SEMICOLON: ';';

INTDIVEQ: '\\=';
POWEQ: '**=';
PLUSEQ: '+=';
MINUSEQ: '-=';
MULTEQ: '*=';
DIVEQ: '/=';
MODEQ: '%=';
SHIFTLEQ: '<<=';
SHIFTREQ: '>>=';
AND_BITEQ: '&=';
OR_BITEQ: '|=';
XOR_BITEQ: '^=';
INCREMENT: '++';
DECREMENT: '--';


DECNUMBER: [0-9]+; // TODO: `DECNUMBER: BigInt` and `SMALL_DECNUMBER: usize` both use this token
HEXNUMBER: '0x' [0-9A-Fa-f]*; // TODO: why is this not [0-9A-Fa-f]+?
IDENTIFIER: [$_]*[a-zA-Z][a-zA-Z$_0-9]*;
STRING : '"' ~('\n' | '"')* '"' ;

// non-greedy matching
WHITESPACE: [ \t\r\n]+ -> skip;
COMMENT: '//' .*? '\n' -> skip;
MULTILINE_COMMENT: '/*' .*? '*/' -> skip;
