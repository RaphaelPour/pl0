#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <ctype.h>

typedef struct Morphem{

    int code;	// Status of the Morphem
    double value;	// Numerical Result of our expression
    char operator;	// Current Operator
    size_t position;
}Morphem;

enum MorphemCodes
{
    MCODE_EMPTY,
    MCODE_OPERATOR,
    MCODE_VALUE
};

Morphem *m;
char *inputString;

void lex();
void error();

// Non-Terminals of the Grammar
double expression();
double term();
double factor();

int main(int argc, char* argv[])
{
    if(argc != 2)
    {
        printf("usage: %s <arithmetic expression>\n", argv[0]);
        exit(EXIT_FAILURE);
    }
    size_t inputLength = strlen(argv[1]);
    inputString = (char*)malloc(inputLength);
    strncpy(inputString, argv[1], inputLength);

    m = (Morphem*) malloc(sizeof(Morphem));

    m->code = MCODE_EMPTY;
    m->value = 0;
    m->position = 0;
    m->operator = '\0';

    // Test lexer without parsing 
    //do lex(inputString); while(m->code != MCODE_EMPTY);


    lex();
    printf(": %.2f\n", expression());

    free(inputString);
    free(m);
    return EXIT_SUCCESS;

}

void lex()
{

    // Is first char null?
    if(inputString[m->position] == '\0')
    {
        m->code = MCODE_EMPTY;
    }
    else
    {
        // Get rid of all whitespaces
        while(inputString[m->position] == ' ' ||
            inputString[m->position] == '\t')m->position++;

        // If first char is a digit or a decimal point
        if( isdigit(*(inputString+m->position)) || 
                inputString[m->position] == '.')
        {
            // We have a double value, let's convert it
            char *tmp = inputString+m->position;
            char *endptr;
            m->value = strtod(tmp, &endptr);
            m->code = MCODE_VALUE;
            m->position += (int)(endptr-tmp);
            printf("V(%.2f) ", m->value);
        }
        else
            switch(inputString[m->position])
            {
                case '+':
                case '*':
                case '(':
                case ')':
                    m->operator = inputString[m->position];
                    m->code = MCODE_OPERATOR;
                    m->position++;
                    printf("O(%c) ", m->operator);
                    break;
                default:
                    printf("Unknown symbol '%c'\n", 
                            inputString[m->position]);
                    exit(EXIT_FAILURE);
            }
    }

}

double expression()
{
    double value = term();
    if(m->code == MCODE_OPERATOR && m->operator == '+')
    {
        lex();
        value += expression();
    }

    return value;

}

double term()
{
    double value = factor();
    if(m->code == MCODE_OPERATOR && m->operator == '*')
    {
        lex();
        value *= term();
    }

    return value;
}

double factor()
{
    double value = 0;

    if(m->code == MCODE_OPERATOR && m->operator == '(')
    {
        lex();
        value = expression();
        if(m->code != MCODE_OPERATOR || m->operator != ')') error("Expected ')'");
        lex();
    }
    else if(m->code == MCODE_VALUE)
    {
        value = m->value;
        lex();
    }
    else error("Expected '(' or Value");

    return value;
}

void error(char *hint)
{
    printf("Error at position %ld '%c', MCode:%d, MOp:%c: %s\n", 
            m->position, 
            inputString[m->position], 
            m->code, 
            m->operator, 
            hint);
    exit(EXIT_FAILURE);
}
