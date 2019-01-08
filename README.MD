#PL/0 Compiler

This Python-based Compiler converts PL/0 source code into CL/0 virtual machine code. Both are educational languages with the aim to get faster to the real handwork of compiler-construction.

This project is the outcome of the Compilerconstruction Module at the HTW Dresden.

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

## Examples

### Hello World
```
! "Hello World!".
```

### Arithmetic expressions
~~~~
!- 3+ (-4).
~~~~

### I/O
~~~~
VAR input;
BEGIN
    ?input;
    !input
END.
~~~~

### Conditions
```
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

### While-Loop
```
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

```
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

### For-Loop
```
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

### Recursion
```
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

### Number guessing game
```
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

## Vision

The following features/additions came up to my mind while developing the compiler.
Due to a lack of time, they couldn't (and maybe will never) be implemented.

* Procedures with Arguments
* Arrays
* Include other PL/0 files
* Types
* Own VM where with more features (for example more I/O Features to read/write from file/network)
* Real Executables instead of vm code (implement x86/x64 code generator)
* Switch-Case
* Break for Loops and Switch-Case

## Bugs

* ~~ Conditional Statement error on wrong condition. The jmpnot jumps probably to the wrong address ~~
* ~~ Call doesn't work properly. Check out BL5/BL6 ~~
* ~~ Procedure can't access variables of the main programm ~~

## License

(C) 2019 Raphael Pour, licensed under [GPL v3](http://www.gnu.de/documents/gpl-3.0.de.html)