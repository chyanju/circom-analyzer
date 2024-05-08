parser grammar CircomParser;

options {
	tokenVocab = CircomLexer;
}


identifierList: (IDENTIFIER ',')* IDENTIFIER;

// ====================================================================
// Body
// ====================================================================

pragma
	: 'pragma' 'circom' version ';'
	| 'pragma' 'custom_templates' ';';

include: 'include' STRING ';';

program: pragma* include* definition* mainComponent? EOF;

// ====================================================================
// Definitions
// ====================================================================

publicList: '{' 'public' '[' identifierList ']' '}';

mainComponent:
	'component' 'main' publicList? '=' expression ';';

definition: functionDefinition | templateDefinition;

functionDefinition:
	'function' IDENTIFIER '(' identifierList? ')' block;
templateDefinition:
	'template' 'custom_templates'? 'parallel'? IDENTIFIER '(' identifierList? ')' block;

// ====================================================================
// VariableDefinitions
// ====================================================================

tagsList: '{' identifierList '}';

signalType
  : 'input'
  | 'output';

signalHearder
  : 'signal' signalType? tagsList?;

// ====================================================================
// Statements
// ====================================================================

simpleSymbol: IDENTIFIER arrayAcc*;

complexSymbol: IDENTIFIER arrayAcc* expression;

signalConstraintSymbol: IDENTIFIER arrayAcc* '<==' expression;

signalSimpleSymbol: IDENTIFIER arrayAcc* '<--' expression;

tupleInitialization
  : '<==' expression
  | '<--' expression
  | '=' expression;

someSymbol: complexSymbol | simpleSymbol;

signalSymbol: simpleSymbol | signalConstraintSymbol; // TODO: should this be simpleSymbol or signalSimpleSymbol?

declaration
  : 'var' '(' (simpleSymbol ',')* simpleSymbol ')' tupleInitialization?
  | signalHearder '(' (signalSymbol ',')* signalSymbol ')' tupleInitialization?
  | 'component' '(' (simpleSymbol ',')* simpleSymbol ')' tupleInitialization?
  | 'var'  (someSymbol ',')* someSymbol
  | 'component' (someSymbol ',')* someSymbol
  | signalHearder (signalSymbol ',')* signalSymbol
  | signalHearder (signalSimpleSymbol ',')* signalSimpleSymbol;

substition
	: expression assignOp expression
  | expression '-->' expression
  | expression '\\=' expression
  | expression '**=' expression
  | expression '+=' expression
  | expression '-=' expression
  | expression '*=' expression
  | expression '/=' expression
  | expression '%=' expression
  | expression '<<=' expression
  | expression '>>=' expression
  | expression '&=' expression
  | expression '|=' expression
  | expression '^=' expression
  | expression '++'
  | expression '--'
  | '++' expression
  | '--' expression;

block: '{' statement3* '}';

statement: statement0;

parseElseStmt0NB: 'else' stmt0NB;
parseElseStatement1: 'else' statement1;

statement0: stmt0NB | statement1;

stmt0NB
  : 'if' '(' expression ')' stmt0NB
  | 'if' '(' expression ')' statement1
  | 'if' '(' expression ')' statement1 parseElseStmt0NB;

statement1
  : 'if' '(' expression ')' statement1 parseElseStatement1
  | statement2;

statement2
  : 'for' '(' declaration ';' expression ';' substition ')' statement2
  | 'for' '(' substition ';' expression ';' substition ')' statement2
  | 'while' '(' expression ')' statement2
  | 'return' expression ';'
  | substition ';'
  | expression '===' expression ';'
  | statementLog
  | 'assert' '(' expression ')' ';'
  | expressionAnonymous ';'
  | block;

statementLog
  : 'log' '(' logListable ')' ';'
  | 'log' '(' ')' ';';

statement3
  : declaration ';'
  | statement;

// ====================================================================
// Variable
// ====================================================================

varAccess
  : arrayAcc
  | componentAcc;

arrayAcc: '[' expression ']';

componentAcc
  : '.' IDENTIFIER;

variable
  : IDENTIFIER varAccess*;

// ====================================================================
// Expression
// ====================================================================

listableExpression: (expression ',')* expression;

listableWithInputNames
  : (IDENTIFIER assignOp expression ',')* IDENTIFIER assignOp expression;

listableAnon
  : listableWithInputNames
  | listableExpression;

parseString: STRING;

logExpression: expression;

logArgument: logExpression | parseString;

logListable: (logArgument ',')* logArgument;

twoElemsListable: expression ',' expression (',' expression)*;

expression
  : expression14
  | parseExpression1;

parseExpression1
  : expression13
  | expression12;

// parallel expr
expression14
  : 'parallel' parseExpression1;

// ops: e ? a : i
expression13
  : expression12 '?' expression12 ':' expression12;

expression12
  : expression11 ('||' expression11)*;

expression11
  : expression10 ('&&' expression10)*;

expression10
  : expression9 (cmpOpCodes expression9)*;

expression9
  : expression8 ('|' expression8)*;

expression8
  : expression7 ('^' expression7)*;

expression7
  : expression6 ('&' expression6)*;

expression6
  : expression5 (shiftOp expression5)*;

expression5
  : expression4 (addSubOp expression4)*;

expression4
  : expression3 (mulDivOp expression3)*;

expression3
  : expression2 ('**' expression2)*;

expression2 // TODO: strange, why not inductive?
  : expressionPrefixOp expression1
  | expression1;

expressionAnonymous
  : IDENTIFIER '(' listableExpression? ')' '(' listableAnon? ')';

expression1
  : expressionAnonymous
  | IDENTIFIER '(' listableExpression? ')'
  | '[' listableExpression ']'
  | '(' twoElemsListable ')'
  | expression0;

expression0
  : variable
  | '_'
  | DECNUMBER
  | HEXNUMBER
  | '(' expression ')';

// ====================================================================
// Terminals
// ====================================================================

assignOp
  : '='
  | '<--'
  | '<==';

cmpOpCodes
  : '=='
  | '!='
  | '<'
  | '>'
  | '<='
  | '>=';

shiftOp
  : '<<'
  | '>>';

addSubOp
  : '+'
  | '-';

mulDivOp
  : '*'
  | '/'
  | '\\'
  | '%';

expressionPrefixOp
  : '-'
  | '!'
  | '~';

// Version used by pragma to describe the compiler, its syntax is Number1.Number2.Number3...
version: DECNUMBER '.' DECNUMBER '.' DECNUMBER;
