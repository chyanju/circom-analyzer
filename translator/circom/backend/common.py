from ..parser.CircomLexer import CircomLexer
from ..parser.CircomParser import CircomParser

from antlr4 import CommonTokenStream, Parser
from antlr4.Utils import escapeWhitespace
from antlr4.tree.Trees import Trees, Tree


# ref: toStringTree method
#      https://github.com/parrt/antlr4-python3/blob/master/src/antlr4/tree/Trees.py#L48
@classmethod
def toJsonTree(cls, t: Tree, ruleNames: list=None, recog: Parser=None):
    '''Get s-expression of the parse tree in json'''
    if recog is not None:
        ruleNames = recog.ruleNames
    s = escapeWhitespace(cls.getNodeText(t, ruleNames), False)
    if t.getChildCount() == 0:
        return s
    ret = [s]
    for i in range(0, t.getChildCount()):
        ret.append(cls.toJsonTree(t.getChild(i), ruleNames))
    return ret
# install class method
Trees.toJsonTree = toJsonTree

def tree2json(input_stream):
    lexer = CircomLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = CircomParser(stream)
    tree = parser.program()
    return Trees.toJsonTree(tree, None, parser)