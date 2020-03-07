# Proj01
# CS 3210
## Principles of Programming Languages
Nick Gagliardi, Spring 2020

### Parser

A lexical analyzer and bottom-up parser for a 'C-lite' language.

The grammar in EBNF:

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
