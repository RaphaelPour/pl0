
#ifndef PL0LEXER_H
#define PL0LEXER_H

#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
// Data and tables


// Char Vector to classify the first 128 ASCII Chars

/* Classes:
    0 - Valid special chars
    1 - Number
    2 - Letter
    3 - :
    4 - =
    5 - <
    6 - >
    7 - else 
*/

// Functions
void lex_init(char *fileName);
void printCharVector();

/*
lex();

lex_read();
lex_read_upperwrite();
lex_read_write();
lex_read_write_end();
lex_end();

typedef void (LEXF*) (void);
static LEXF lex_actions[] = {
    lex_read,
    lex_read_upperwrite,
    lex_read_write,
    lex_read_write_end,
    lex_end
};*/    

#endif // PL0LEXER_H
