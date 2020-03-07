"""
    CS 3210 - Principles of Programming Languages - Spring 2020
    Nick Gagliardi
    3.7.2020
    Time Spent: 15+ hours
    Resources:
        - https://github.com/thyagomota/20SCS2050
            Course Github Page, used Activity 8 for the majority of python code.
        - http://jsmachines.sourceforge.net/machines/slr.html
            SLR Parser Generator, used to generate the SLR Table
        - Discussed with multiple students how to properly generate the grammar
    Description:
        A bottom-up parser for an expression, example inputs are done in C and labeled source 1 to 16. Grammar and
        SLR table are labeled accordingly. pep8 typo and scope warnings were suppressed but need still remain todo.
"""

from enum import IntEnum
import sys

# enables parser's debugging
DEBUG = False


# all char classes
class CharClass(IntEnum):
    EOF = 0
    LETTER = 1
    DIGIT = 2
    OPERATOR = 3
    DOT = 4
    QUOTE = 5
    BLANK = 6
    DELIMITER = 7
    FLOAT_DOT = 8
    COMPARE = 9
    OTHER = 10


# all tokens
class Token(IntEnum):
    EOF = 0
    INT_TYPE = 1
    MAIN = 2
    OPEN_PAR = 3
    CLOSE_PAR = 4
    OPEN_CURLY = 5
    CLOSE_CURLY = 6
    OPEN_BRACKET = 7
    CLOSE_BRACKET = 8
    COMMA = 9
    ASSIGNMENT = 10
    SEMICOLON = 11
    IF = 12
    ELSE = 13
    WHILE = 14
    OR = 15
    AND = 16
    EQUALITY = 17
    INEQUALITY = 18
    LESS = 19
    LESS_EQUAL = 20
    GREATER = 21
    GREATER_EQUAL = 22
    ADD = 23
    SUBTRACT = 24
    MULTIPLY = 25
    DIVIDE = 26
    BOOL_TYPE = 27
    FLOAT_TYPE = 28
    CHAR_TYPE = 29
    IDENTIFIER = 30
    INT_LITERAL = 31
    TRUE = 32
    FALSE = 33
    FLOAT_LITERAL = 34
    CHAR_LITERAL = 35


# a tree-like data structure
class Tree:
    TAB = "   "

    def __init__(self):
        self.data = None
        self.children = []

    def add(self, child):
        self.children.append(child)

    def print(self, tab=""):
        if self.data is not None:
            print(tab + self.data)
            tab += self.TAB
            for child in self.children:
                if isinstance(child, Tree):
                    child.print(tab)
                else:
                    print(tab + child)


# error code to message conversion function
def errorMessage(code):
    msg = "Error " + str(code).zfill(2) + ": "
    if code == 1:
        return msg + "source file missing"
    if code == 2:
        return msg + "couldn't open source file"
    if code == 3:
        return msg + "lexical error"
    if code == 4:
        return msg + "digit expected"
    if code == 5:
        return msg + "symbol missing"
    if code == 6:
        return msg + "EOF expected"
    if code == 7:
        return msg + "'}' expected"
    if code == 8:
        return msg + "'{' expected"
    if code == 9:
        return msg + "')' expected"
    if code == 10:
        return msg + "'(' expected"
    if code == 11:
        return msg + "main expected"
    if code == 12:
        return msg + "int type expected"
    if code == 13:
        return msg + "']' expected"
    if code == 14:
        return msg + "int literal expected"
    if code == 15:
        return msg + "'[' expected"
    if code == 16:
        return msg + "identifier expected"
    if code == 17:
        return msg + "';' expected"
    if code == 18:
        return msg + "'=' expected"
    if code == 19:
        return msg + "identifier, if, or while expected"
    if code == 20:
        return msg + "digit or ';' expected"
    if code == 99:
        return msg + "syntax error"


# get error code from parse state
def getErrorCode(state):
    if state in []:
        return 3                    # 3 "lexical error"
    if state in [49]:
        return 4                    # 4 "digit expected"
    if state in []:
        return 5                    # 5 "symbol missing"
    if state in [24]:
        return 6                    # 6 "EOF expected"
    if state in [35, 57, 111]:
        return 7                    # 7 "'}' expected"
    if state in [4, 82]:
        return 8                    # 8 "'{' expected"
    if state in [3, 43]:
        return 9                    # 9 "')' expected"
    if state in [2, 21]:
        return 10                   # 10 "'(' expected"
    if state in [1]:
        return 11                   # 11 "main expected"
    if state in [0]:
        return 12                   # 12 "int type expected"
    if state in [55, 92]:
        return 13                   # 13 "']' expected"
    if state in [33]:
        return 14                   # 14 "int literal expected"
    if state in [19, 43]:
        return 15                   # 15 "'[' expected"
    if state in [9, 34, 106, 30, 18, 28, 94, 108, 27, 72, 78]:
        return 16                   # 16 "identifier expected"
    if state in [23, 46, 56, 103]:
        return 17                   # 17 "';' expected"
    if state in [5, 80]:
        return 18                   # 18 "'=' expected"
    if state in [57]:
        return 19                   # 19 "identifier, if, or, while expected"
    return 99


# lexeme to token conversion map
lookupToken = {
    "$": Token.EOF,
    "int": Token.INT_TYPE,
    "main": Token.MAIN,
    "(": Token.OPEN_PAR,
    ")": Token.CLOSE_PAR,
    "{": Token.OPEN_CURLY,
    "}": Token.CLOSE_CURLY,
    "[": Token.OPEN_BRACKET,
    "]": Token.CLOSE_BRACKET,
    ",": Token.COMMA,
    "=": Token.ASSIGNMENT,
    ";": Token.SEMICOLON,
    "if": Token.IF,
    "else": Token.ELSE,
    "while": Token.WHILE,
    "||": Token.OR,
    "&&": Token.AND,
    "==": Token.EQUALITY,
    "!=": Token.INEQUALITY,
    "<": Token.LESS,
    "<=": Token.LESS_EQUAL,
    ">": Token.GREATER,
    ">=": Token.GREATER_EQUAL,
    "+": Token.ADD,
    "-": Token.SUBTRACT,
    "*": Token.MULTIPLY,
    "/": Token.DIVIDE,
    "bool": Token.BOOL_TYPE,
    "float": Token.FLOAT_TYPE,
    "char": Token.CHAR_TYPE,
    "true": Token.TRUE,
    "false": Token.FALSE
}


# reads the next char from input and returns its class
# noinspection PyShadowingNames
def getChar(input):
    if len(input) == 0:
        return None, CharClass.EOF
    c = input[0].lower()
    if c.isalpha():
        return c, CharClass.LETTER
    if c.isdigit():
        return c, CharClass.DIGIT
    if c in ['"', "'"]:
        return c, CharClass.QUOTE
    if c in ['+', '-', '*', '/']:
        return c, CharClass.OPERATOR
    if c in [';']:
        return c, CharClass.DOT
    if c in [' ', '\n', '\t']:
        return c, CharClass.BLANK
    if c in ['(', ')']:
        return c, CharClass.DELIMITER
    if c in ['.']:
        return c, CharClass.FLOAT_DOT
    if c in ['=', '!', '<', '>']:
        return c, CharClass.COMPARE
    return c, CharClass.OTHER


# calls getChar and addChar until it returns a non-blank
# noinspection PyShadowingNames
def getNonBlank(input):
    ignore = ""
    while True:
        c, charClass = getChar(input)
        if charClass == CharClass.BLANK:
            input, ignore = addChar(input, ignore)
        else:
            return input


# adds the next char from input to lexeme, advancing the input by one char
# noinspection PyShadowingNames
def addChar(input, lexeme):
    if len(input) > 0:
        lexeme += input[0]
        input = input[1:]
    return input, lexeme


# returns the next (lexeme, token) pair or ("", EOF) if EOF is reached
# noinspection PyShadowingNames
def lex(input):
    input = getNonBlank(input)
    c, charClass = getChar(input)
    lexeme = ""

    # checks EOF
    if charClass == CharClass.EOF:
        return input, lexeme, Token.EOF

    # reads an identifier
    if charClass == CharClass.LETTER:
        input, lexeme = addChar(input, lexeme)
        while True:
            c, charClass = getChar(input)
            if charClass == CharClass.LETTER or charClass == CharClass.DIGIT:
                input, lexeme = addChar(input, lexeme)
            else:
                if lexeme in lookupToken:
                    return input, lexeme, lookupToken[lexeme]
                else:
                    return input, lexeme, Token.IDENTIFIER

    # reads digits
    if charClass == CharClass.DIGIT:
        input, lexeme = addChar(input, lexeme)
        while True:
            c, charClass = getChar(input)
            if charClass == CharClass.DIGIT:
                input, lexeme = addChar(input, lexeme)
            if charClass == CharClass.FLOAT_DOT:
                input, lexeme = addChar(input, lexeme)
                while True:
                    c, charClass = getChar(input)
                    if charClass == CharClass.DIGIT:
                        input, lexeme = addChar(input, lexeme)
                    else:
                        return input, lexeme, Token.FLOAT_LITERAL
            else:
                return input, lexeme, Token.INT_LITERAL

    # reads operator
    if charClass == CharClass.OPERATOR:
        input, lexeme = addChar(input, lexeme)
        if lexeme in lookupToken:
            return input, lexeme, lookupToken[lexeme]

    # reads delimiter
    if charClass == CharClass.DELIMITER:
        input, lexeme = addChar(input, lexeme)
        return input, lexeme, lookupToken[lexeme]

    # reads dots
    if charClass == CharClass.DOT:
        input, lexeme = addChar(input, lexeme)
        return input, lexeme, lookupToken[lexeme]

    # reads quote
    if charClass == CharClass.QUOTE:
        input, lexeme = addChar(input, lexeme)
        while True:
            c, charClass = getChar(input)
            if charClass == CharClass.QUOTE:
                input, lexeme = addChar(input, lexeme)
                return input, lexeme, Token.CHAR_LITERAL
            else:
                input, lexeme = addChar(input, lexeme)

    # read compare operators
    if charClass == CharClass.COMPARE:
        input, lexeme = addChar(input, lexeme)
        c, charClass = getChar(input)
        if c == "=":
            input, lexeme = addChar(input, lexeme)
            return input, lexeme, lookupToken[lexeme]
        else:
            return input, lexeme, lookupToken[lexeme]

    # reads other
    if charClass == CharClass.OTHER:
        input, lexeme = addChar(input, lexeme)
        if lexeme in lookupToken:
            return input, lexeme, lookupToken[lexeme]

    # anything else, raises an error
    raise Exception(errorMessage(3))


# reads the given input and returns the grammar as a list of productions
# noinspection PyShadowingNames
def loadGrammar(input):
    grammar = []
    for line in input:
        grammar.append(line.strip())
    return grammar


# returns the LHS (left hand side) of a given production
def getLHS(production):
    return production.split("->")[0].strip()


# returns the RHS (right hand side) of a given production
def getRHS(production):
    return production.split("->")[1].strip().split(" ")


# prints the productions of a given grammar, one per line
# noinspection PyShadowingNames
def printGrammar(grammar):
    i = 0
    for production in grammar:
        print(str(i) + ". " + getLHS(production), end=" -> ")
        print(getRHS(production))
        i += 1


# reads the given input containing an SLR parsing table and returns the "actions" and "gotos" as dictionaries
# noinspection PyShadowingNames
def loadTable(input):
    actions = {}
    gotos = {}
    header = input.readline().strip().split(",")
    end = header.index("$")
    tokens = []
    for field in header[1:end]:
        tokens.append(int(field))
    tokens.append(int(Token.EOF))  # '$' is replaced by token -1
    variables = header[end + 1:]
    for line in input:
        row = line.strip().split(",")
        state = int(row[0])
        for i in range(len(tokens)):
            token = tokens[i]
            key = (state, token)
            value = row[i + 1]
            if len(value) == 0:
                value = None
            actions[key] = value
        for i in range(len(variables)):
            variable = variables[i]
            key = (state, variable)
            value = row[i + len(tokens) + 1]
            if len(value) == 0:
                value = None
            gotos[key] = value
    return actions, gotos


# prints the given actions, one per line
# noinspection PyShadowingNames
def printActions(actions):
    for key in actions:
        print(key, end=" -> ")
        print(actions[key])


# prints the given gotos, one per line
# noinspection PyShadowingNames
def printGotos(gotos):
    for key in gotos:
        print(key, end=" -> ")
        print(gotos[key])


# given an input (source program), a grammar, actions, and gotos, returns the corresponding parse tree or raise an
# exception if syntax errors were found
# noinspection PyShadowingNames,PyListCreation
def parse(input, grammar, actions, gotos):
    # create a stack of trees
    trees = []
    # initialize the stack of (state, symbol) pairs
    stack = []
    stack.append(0)

    # initialize lexeme and token variables
    lexeme = ""
    token = None

    # main parser loop
    while True:
        # get lex info ONLY if token is None
        if token is None:
            input, lexeme, token = lex(input)
        state = stack[-1]
        # print debugging info
        if DEBUG:
            print("stack:", end=" ")
            print(stack, end=" ")
            print("(\"" + lexeme + "\", ", end=" ")
            print(token, end=",")
            print(" " + str(int(token)) + ")", end=" ")
        action = actions[(state, token)]
        if DEBUG:
            print("action:", end=" ")
            print(action)
        # if action is undefined, raise an approriate error
        if action is None:
            errorCode = getErrorCode(state)
            raise Exception(errorMessage(errorCode))
        if action[0] == 's':
            stack.append(int(token))
            state = int(action[1:])
            stack.append(state)
            tree = Tree()
            tree.data = lexeme
            trees.append(tree)
            # set token to None to acknowledge reading the input
            token = None
        elif action[0] == 'r':
            production = grammar[int(action[1:])]
            lhs = getLHS(production)
            rhs = getRHS(production)
            for i in range(len(rhs) * 2):
                stack.pop()
            state = stack[-1]
            stack.append(lhs)
            stack.append(int(gotos[(state, lhs)]))
            newTree = Tree()
            newTree.data = lhs
            for tree in trees[-len(rhs):]:
                newTree.add(tree)
            trees = trees[:-len(rhs)]
            trees.append(newTree)
        else:
            production = grammar[0]
            lhs = getLHS(production)
            newTree = Tree()
            newTree.data = lhs
            for tree in trees:
                newTree.add(tree)
            return newTree


# main
if __name__ == "__main__":

    # checks if source file was passed and if it exists
    try:
        if len(sys.argv) != 2:
            raise ValueError(errorMessage(1))
        sourceFile = None
        # noinspection PyBroadException
        try:
            sourceFile = open(sys.argv[1], "rt")
        except:
            pass
        if not sourceFile:
            raise IOError(errorMessage(2))
        input = sourceFile.read()
        sourceFile.close()
    except Exception as ex:
        print(ex)
        sys.exit(1)

    # load the grammar.txt file
    try:
        grammarFile = None
        # noinspection PyBroadException
        try:
            grammarFile = open("grammar.txt", "rt")
        except:
            pass
        if not grammarFile:
            raise IOError(errorMessage(1))
        grammar = loadGrammar(grammarFile)
        grammarFile.close()
        printGrammar(grammar)
    except Exception as ex:
        print(ex)
        sys.exit(1)

    # load SLR table
    try:
        slrTableFile = None
        # noinspection PyBroadException
        try:
            slrTableFile = open("slr_table.csv", "rt")
        except:
            pass
        if not slrTableFile:
            raise IOError(errorMessage(5))
        # noinspection SpellCheckingInspection
        actions, gotos = loadTable(slrTableFile)
        slrTableFile.close()
    except Exception as ex:
        print(ex)
        sys.exit(1)

    # parse the code
    try:
        tree = parse(input, grammar, actions, gotos)
        print("Input is syntactically correct!")
        print("Parse Tree:")
        tree.print("")
    except Exception as ex:
        print(ex)
        sys.exit(1)
