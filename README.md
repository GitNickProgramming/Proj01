# Proj01
# CS 3210
## Principles of Programming Languages
Nick Gagliardi, Spring 2020

### Parser

A lexical analyzer and bottom-up parser for a 'C-lite' language.
The goal of this assignment is to have you write a lexical and syntax analyzer for a hypothetical programming language (roughly based on C).  The input of your parser is a source code written in the programming language’s grammar.  If the source code is syntactically correct your parser should display the corresponding parse tree.  An appropriate error message should be provided otherwise. 

The expectation for this programming assignment is that you will be coding a complete parser from scratch.  You can choose between the two approaches discussed in class: top-down or bottom-up.  I will NOT grade solutions based on any parser generator like YACC or JavaCC, for example. 

---
The grammar in EBNF:
Below is the grammar for the CLite programming language specified using EBNF notation.  Special words and symbols are highlighted for easy identification (better seen in color).  Assume that this PL is NOT case-sensitive. 

```
<program>           →   int main ( ) { <declaration>+ <statement>+ }
<declaration>       →   <type> <identifier> [ [ <int_literal> ] ] { , <identifier> [ [ <int_literal> ] ] } ;
<statement>         →   <assignment> | <if> | <while> | { <statement>+ }
<assignment>        →   <identifier> [ [ <expression> ] ] = <expression> ;
<if>                →   if ( <expression> ) <statement> [ else <statement> ]
<while>             →   while ( <expression> ) <statement> 
<expression>        →   <conjunction> { || <conjunction> } 
<conjunction>       →   <equality> { && <equality> }
<equality>          →   <relation> [ <eq_neq_op> <relation> ]
<eq_neq_op>         →   == | != 
<relation>          →   <addition> [ <rel_op> <addition> ]
<rel_op>            →   < | <= | > | >=
<addition>          →   <term> { <add_sub_op> <term> }
<add_sub_op>        →   + | -
<term>              →   <factor> { <mul_div_op> <factor> }
<mul_div_op>        →   * | / 
<factor>            →   <identifier> [ [ <expression> ] ] | <literal> | ( <expression> ) 
<type>              →   int | bool | float | char 
<identifier>        →   <letter> { <letter> | <digit> }
<letter>            →   a | b | … | z | A | B | … | Z 
<digit>             →   0 | 1 | … | 9
<literal>           →   <int_literal> | <bool_literal> | <float_literal> | <char_literal> 
<int_literal>       →   <digit> { <digit> } 
<bool_literal>      →   true | false 
<float_literal>     →   <int_literal> . <int_literal>
<char_literal>      →   ' <letter> '
```
---
Translated into SLR table-ready productions:

```
P -> INT MAIN ( ) { D S }
D -> D'
D' -> D' D
D' -> T IDENTIFIER ;
D' -> T IDENTIFIER D* ;
D' -> T IDENTIFIER [ INT_LITERAL ] D* ;
D* -> , IDENTIFIER
D* -> , IDENTIFIER D*
D* -> , IDENTIFIER [ INT_LITERAL ]
D* -> , IDENTIFIER [ INT_LITERAL ] D*
S -> S'
S -> S' S
S' -> A
S' -> G'
S' -> G*
S' -> { S }
A -> IDENTIFIER = E ;
A -> IDENTIFIER [ E ] = E ;
E -> C
E -> C E'
E' -> || C
E' -> || C E'
C -> U
C -> U C'
C' -> && U
C' -> && U C'
U -> R
U -> R Q R
R -> Y
R -> Y O Y
Y -> M
Y -> M Y'
Y' -> H M
Y' -> H M Y'
M -> F
M -> F M'
M' -> W F
M' -> W F M'
F -> IDENTIFIER
F -> IDENTIFIER [ E ]
F -> L
F -> ( E )
G' -> IF ( E ) S
G' -> IF ( E ) S ELSE S
G* -> WHILE ( E ) { S }
L -> INT_LITERAL
L -> TRUE
L -> FALSE
L -> FLOAT_LITERAL
L -> CHAR_LITERAL
W -> *
W -> /
H -> +
H -> -
O -> <
O -> <=
O -> >
O -> >=
Q -> ==
Q -> !=
T -> INT
T -> BOOL
T -> FLOAT
T -> CHAR
```
---
Deliverables and Submission

Below is the list of minimum deliverables for this project:
parser.xxx source code (e.g., parser.py or parser.java) 
grammar.txt file, and
slr_table.csv file. 

Files grammar.txt and slr_table.csv are only required if your parser is based on the shift-reduce (bottom-up) algorithm discussed in class.  The format of those files must match the one used in class.  

If you are writing your parser in a PL other than Python or Java you MUST provide specific instructions on how to properly setup your development environment, including IDE/compiler used (with version numbers) and how to compile/run your code.  I should be able to test your code using MacOS.  So if you are using a different platform I encourage you to contact me ahead of the deadline so I can properly set up my computer.  If I cannot run your parser from the source code I cannot grade it!

Your source code MUST have a comment section in the beginning with the name(s) of the author(s) of the project.  You are allowed to work together with another classmate.  Teams of more than two students will NOT be accepted (NO exceptions).  Only one of the members of the team needs to submit on Blackboard. 

Please use ZIP format when submitting your project (no Z, RAR, or any other format will be accepted). 

---
Rubric

This programming assignment is worth 100 points, distributed in the following way: 

+3    command-line validation
+32   lexical analyzer works as expected 
    +5 token codes match specification
    +1 recognizes EOF
    +3 recognizes identifiers
    +3 recognizes literals
    +5 recognizes special words
    +1 recognizes assignment operator
    +3 recognizes arithmetic operator
    +3 recognizes relational operators 
    +2 recognizes logical operators
    +3 recognizes punctuators
    +2 recognizes delimiters
    +1 raises exception with proper error message when it fails
+60    syntax analyzer works as expected
    +10 grammar used matches specification 
    +10 parser error codes match
    +20 parse tree is built correctly
    +30 parser properly shows syntactic errors 
+5    submission follows instructions (student names identified in a comment section, zip format, source/grammar/slr table submitted, specific instructions provided when using different development platforms etc.)

10 points will be deducted for each day of late submission. I will not accept submissions that are five days (or more) late. 

