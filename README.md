# PL/0 Compiler

This Python-based Compiler converts PL/0 source code into CL/0 virtual machine code. Both are educational languages with the aim to get faster to the real handwork of compiler-construction.

This project is the outcome of the Compilerconstruction module at the HTW Dresden.

## Usage

    python3 cpl0.py [--ast] <inputFile>

The outcoming virtual machine codefile can be run with the vm of my supervising Professor which can be found here [here](http://www.informatik.htw-dresden.de/~beck/Compiler/bin/rlinux) (compiled for linux 32-bit). It can be used like ``./rlinux <cl0-file>``.


## PL0-Features

PL/0 provides a bunch of features such as:

* Arithmetic expressions
* I/O Operations including printing a value and receiving it as user input
* Conditions
* While-Loop
* Procedures/Constants/Variables with different scopes 

Additional Features

* Output string
* Block comments
* For-Loop
* Procedures with Parameters
* Arrays
* Logical Expressions

## Examples

### Hello World
```basic
! "Hello World!".
```

### Arithmetic expressions
```basic
!- 3+ (-4).
```

### I/O
```basic
VAR input;
BEGIN
    ?input;
    !input
END.
```

### If
```basic
VAR a,b;
BEGIN
    ?a;
    ?b;
    IF a = b THEN !0;
    IF a # b THEN !1;
    
    IF a >= b THEN !3;
    IF a > b THEN !4;
    
    IF a < b THEN !5;
    IF a <= b THEN !6;

    IF ODD a THEN !7
END.
```

### If-Else

If-Else Odd-Number tester
```basic
VAR input;
PROCEDURE main;
BEGIN
    !" >>>>>>>>> ODD Tester >>>>>>>>>";
    !"Input 0 to exit.";
    !"Input Number:";
    ?input;
    WHILE input # 0 DO
    BEGIN
        IF ODD input THEN !"ODD"
        ELSE !"EVEN";
        !"Input Number:";
        ?input
    END
END;
CALL main.
```

Extended If-Else with a third case using Else-If.
```basic
CONST pHNeutral=7;
VAR input;
PROCEDURE main;
BEGIN
    !"Input pH Value:";
    ?input;
    IF input = pHNeutral THEN !"Neutral"
    ELSE IF input > pHNeutral THEN !"Alkaline"
    ELSE !"Acid"
END;
CALL main.
```

### While-Loop
```basic
VAR a, fak;
BEGIN
 ?a;
 fak:=1;
 WHILE a > 0 do
   BEGIN
    fak:= fak*a;
    a:=a-1;
    ! a;
    ! fak
   END
END .
```

### Define Procedures/ Constants/ Variables
```basic
CONST a=5;
VAR b;
PROCEDURE main;
  BEGIN
    !b;
    b := a;
    !b
  END;
CALL main.
```

### Procedures with parameters
```basic
PROCEDURE f(x);
    !x;
CALL f(7331).
```

Exponentiation programm using a self implemented pow function
```basic
VAR result,i,a,b;
PROCEDURE pow(base,power);
BEGIN
  result := 1;
  FOR(i:=0;i<power;i:=i+1)
    result := result * base;
  !"Result:"
  !result
END;
BEGIN
!"Base:";
?a;
!"Power:";
?b;
CALL pow(a,b)
END.
```

### For-Loop
```basic
CONST k=5;
VAR i,j;
PROCEDURE main;
BEGIN
    FOR(i:=0;i<k;i:=i+1)
        BEGIN
            !i
        END
END;
CALL main.
```

### Arrays
```basic
VAR x[4],i;
BEGIN
    FOR(i:=0; i < 4; i:=i+1)
    BEGIN
        x[i] := i;
        !x[i]
    END
END.
```

Sorting numbers
```basic
VAR x[5],i,j,tmp;
BEGIN
    /* Initialize "random" int vector*/
    x[0] := 4;
    x[1] := 2;
    x[2] := 1;
    x[3] := 5;
    x[4] := 3;

    /* Sort */
    FOR(i:=4; i >= 0; i:=i-1)
        FOR(j:=1; j <= i; j:=j+1)
            IF x[j-1] > x[j] THEN
            BEGIN
                tmp := x[j-1];
                x[j-1] := x[j];
                x[j] := tmp
            END;

    /* Display */
    FOR(i:=0; i < 5; i:=i+1)
        !x[i]
END.
```

### Recursion
```basic
CONST a=5;
VAR b;
PROCEDURE sub;
    BEGIN
      IF b > 0 THEN CALL sub
      b := b-1;
      !b;
    END;
PROCEDURE main;
  BEGIN
    b := a;
    CALL sub
  END;
CALL main.
```

### Logical Expressions
```basic
BEGIN
  IF  { ODD 1 AND NOT ODD 1} OR NOT ODD 1 THEN
  !1
  ELSE
  !2
END.
```

### Number guessing game
```basic
/*
 * Number-Guessing Game
 *
 * 1) Enter random seed (we don't have a random function)
 * 2) Happy guessing!
 */
CONST MAXTRIES=5;
VAR in,goal,done,tries;
PROCEDURE calculateGoal;
BEGIN
   goal := (in*3)+2;
   IF goal < 0 THEN goal := -goal
END;
PROCEDURE main;
BEGIN
   done:=0;
   tries:=0;
   !"       GUESS";
   !"           THE";
   !"             NUMBER";
   !"Enter random number:";
   ?in;
   CALL calculateGoal;
   WHILE done = 0 DO
   BEGIN
       !"Your guess:";
       ?in;
       IF in = goal THEN
       BEGIN
           !"You won!";
           done := 1
       END;

       IF in>goal THEN
       BEGIN
           !"Smaller!";
           tries := tries+1
       END;

       IF in<goal THEN
       BEGIN
           !"Larger!";
           tries := tries+1
       END;

       IF tries < MAXTRIES THEN
       BEGIN
           !"Tries left:";
           !MAXTRIES-tries
       END;

       IF tries = MAXTRIES THEN
       BEGIN
           !"No tries left...";
           !"   G A M E";
           !"    O V E R";
           done := 1
       END
   END
END;
CALL main.
```

## Language specification
```ebnf
<PROGRAM>                    ::= <BLOCK> '.'.
<BLOCK>                      ::= [ <CONSTANT_LIST> ]
                                 [ <VARIABLE_LIST> ] 
                                 { <PROCEDURE> } <STATEMENT> .
<CONSTANT_LIST>              ::= 'CONST' <CONSTANT_DECLARATION> { ',' <CONSTANT_DECLARATION> } ';' .
<CONSTANT>                   ::= ident '=' number .
<VARIABLE_LIST>              ::= 'VAR' <VAR_DECLARATION> { ',' <VAR_DECLARATION> } ';' .
<VARIABLE_DECLARATION>       ::= ident [ '[' number ']' ] .
<PROCEDURE>                  ::= 'PROCEDURE' ident [ '(' [ <PARAMETER_LIST_DECLARATION> ] ')' ] ';' <BLOCK> ';' .
<PROCEDURE_CALL>             ::= 'CALL' ident [ '(' [ <PARAMETER_LIST_CALL> ] ')' ]
<PARAMETER_LIST_DECLARATION> ::= ident { ',' ident }
<PARAMETER_LIST_CALL>        ::= <EXPRESSION> { ',' <EXPRESSION> }
<STATEMENT>                  ::= <ASSIGNMENT> 
                                 | <PROCEDURE_CALL>
                                 | <INPUT_STATEMENT>
                                 | <OUTPUT_STATEMENT>
                                 | <COMPOUND_STATEMENT>
                                 | <CONDITIONAL_STATEMENT>
                                 | <LOOP_STATEMENT>
                                 | <FOR_STATEMENT>
                                 | 'RETURN' .
<COMPOUND_STATEMENT>         ::= 'BEGIN' <STATEMENT> { ';' STATEMENT } 'END' .
<INPUT_STATEMENT>            ::= '?' ident .
<OUTPUT_STATEMENT>           ::= '!' ( string | <EXPRESSION> ) .
<ASSIGNMENT>                 ::= ident ':=' <EXPRESSION> .
<ARRAY_INDEX>                ::= '[' <EXPRESSION> ']' .
<CONDITIONAL_STATEMENT>      ::=  'IF' <LOGICAL_EXPRESSION> 'THEN' <STATEMENT> [ 'ELSE' <STATEMENT> ] .
<CONDITION>                  ::= 'ODD' <EXPRESSION> 
                                 | <EXPRESSION> ( '=' | '#' | '<' | '<=' | '>' | '>=' ) <EXPRESSION> .
<LOOP_STATEMENT>             ::= 'WHILE' <LOGICAL_EXPRESSION> 'DO' <STATEMENT> .
<FOR_STATEMENT>              ::= 'FOR' '(' <ASSIGNMENT> ';' <LOGICAL_EXPRESSION> ';' <ASSIGNMENT>  ')' <STATEMENT> .
<EXPRESSION>                 ::= [ '+' | '-' ] term { ( '+' | '-' ) <TERM> } .
<TERM>                       ::= <FAKTOR> { ( '*' | '/' ) <FAKTOR> } .
<FACTOR>                     ::= ident [ <ARRAY_INDEX> ] 
                                 | number 
                                 | '(' <EXPRESSION> ')' .
<LOGICAL_EXPRESSION>         ::= LOGICAL_TERM { 'OR' LOGICAL_TERM } .
<LOGICAL_TERM>               ::= [ 'NOT' ] LOGICAL_FACTOR { 'AND' [ 'NOT' ] LOGICAL_FACTOR } .
<LOGICAL_FACTOR>             ::= CONDITION 
                                 | ( '{' LOGICAL_EXPRESSION '}' ) .
```


## Architecture

The compiler has four main components:

    - Lexer ([pl0lexer.py](pl0lexer.py))
    - Parser ([pl0parser.py](pl0parser.py))
    - Namelist ([pl0namelist.py](pl0namelist.py))
    - Code-Generator ([pl0codegen.py](pl0codegen.py))


### Lexer
The lexical analyzer (short: lexer) transforms source code into tokens and provide them to the parser.
It does this transformation on-demand, when the parser asks for the next token.
One token can be a symbol, number, or a whole variable identifier.
Let's take the Hello-World programm as an example:
```basic
!"Hello World".
```

The lexer would identify and transform this program into the following three tokens:
- SYMBOL (!)
- STRING (Hello World)
- END (.)

### Parser
The syntactical analyzer (or parser) tries to resolve the incoming tokens using the syntax-rules of PL/0.
It is designed as a graph-controlled top-down parser with edge-functions. This means that the rules itself
are expressed using a graph and each edge of the graph can have a function which gets called on success.

Those functions trigger the code generation or prepare it by for example creating a new variable or checking
if the currently read identifier is already defined. In conclusion it is also possible to detect a few semantical
errors.

### Namelist
It manages all procedures, variables and constants of a program. This includes adding and looking for them.

### Code-Generation
Provides all commands of the target-language CL/0 such as functions to create jump labels or correct addresses (backpatching).

## Vision

The following features/additions came up to my mind while developing the compiler.
Due to a lack of time, they couldn't (and maybe will never) be implemented.
EDIT: The crossed out features managed itself to get to the actual feature list.

* ~~ Procedures with arguments ~~
* ~~ Add Return keyword to leave procedure earlier ~~
* ~~ Arrays ~~
* ~~ Connect multiple conditions using logical expressions with AND/OR/NOT ~~
* Procedures with return value
* Modulo division
* Multiple conditions in one If-Condition seperated by AND/OR
* Include other PL/0 files
* Types
* Own VM where with more features (for example more I/O Features to read/write from file/network)
* Real executables instead of vm code (implement x86/x64 code generator)
* Switch-Case
* Break for loops and Switch-Case

## Bugs

* ~~ Conditional Statement error on wrong condition. The jmpnot jumps probably to the wrong address ~~
* ~~ Call doesn't work properly. Check out BL5/BL6 ~~
* ~~ Procedure can't access variables of the main programm ~~
* ~~ Procedures with parameters won't work with more than one parameter ~~
* ~~ Order of parameters in Procedures with parameters is wrong ~~ 
* AST will only be written correctly to xml-file if the compiling process succeeded. On Error some 
  tags are missing and the xml-file is corrupted.
* (The VM has some segmentation faults under MacOS)

## License

(C) 2019 [Raphael Pour](https://raphaelpour.de), licensed under [GPL v3](http://www.gnu.de/documents/gpl-3.0.de.html)