#include "pl0lexer.h"


void lex_init(char *fileName){
    printCharVector();
}

void printCharVector()
{
    printf("     | 0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F\n" );
    printf("-----+-----------------------------------------------\n" );
    int j;
    for(i=0;i<128;i+=0x10)
    {
        printf("0x%02X |",i);

        for(j=i;j<i+0x10; j++)
            printf("%2d ", charVector[j]);

        printf("\n");
    }
}


//lex();

//lex_read();
//lex_read_upperwrite();
//lex_read_write();
//lex_read_write_end();
//lex_end();
