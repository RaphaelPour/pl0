if exists("b:current_syntax")
  finish
endif

"Keywords
syn keyword defaultKeywords IF THEN WHILE DO FOR ODD CONST VAR
syn keyword procedure PROCEDURE CALL
syn keyword braces BEGIN END

syn region comment start='/\*' end='\*/'
syn region string start='"' end='"'

syn match operator "[:><]="
syn match operator "[><=#]"

"Highlight
hi def link defaultKeywords     STATEMENT
hi def link string              CONSTANT
hi def link procedure           FUNCTION
hi def link operator            STATEMENT
hi def link braces              DELIMITER
hi def link comment             COMMENT
