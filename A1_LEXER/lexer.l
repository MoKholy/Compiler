%{
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

int lines = 0; // To keep track of the current line
int ch = 1;  // To keep track of the current character position (initialized to 1)
int flag = 0;
int singleFlag =0;
int commentError = 0; // Flag to track if a comment is open
int isPrint = 0;
%}

letter [a-zA-Z]
digit [0-9]
eney [Ee]
LINE \n
space " "
tab "\t"
semiColon ";"
comma ","
bracket (\(|\))
squareBracket ("["|"]")
braces ("{"|"}")
begComment "/*"
endComment "*/"
singleComment "//"

arithmeticOp [-+*/]
relationalOp (==|<=|>=|<|>|!=)
assignmentOp "="

mainKeyword "main"
mainKeyword2 "main()"
voidKeyword "void"
ifKeyword "if"
elseKeyword "else"
whileKeyword "while"
intKeyword "int"
charKeyword "char"
floatKeyword "float"
doubleKeyword "double"
returnKeyword "return"
printKeyword "printf"

ID  {letter}({letter}|{digit})*(("."|"#"|"$"|"_")?({letter}|{digit})+)?
NUM (({digit}+)|(({digit}+)"."({digit}*)))(("E"|"e")(\+|\-)?({digit}+))?

wrongID1 [^a-zA-Z" "\t\n]{ID}
wrongID2 {ID}[^a-zA-Z0-9" "\t\n]
wrongID3 {letter}({letter}|{digit})*[^\.#\$_a-zA-Z0-9" "\n\t](({letter}|{digit})+)?

wrongNUM1 (({digit}+)|(({digit}+)"."({digit}*)))(("E"|"e")(\+|\-)?)[^0-9\n\t" "]
wrongNUM2 [^0-9a-zA-Z" "\t\n]{NUM}
wrongNUM3 {NUM}[^0-9a-zA-Z" "\t\n]

nonAlphabet [^-\+\*/=;,\{\}\(\)\[\]\/*\*/a-zA-Z0-9\n\t" "><!]

%%
{LINE} { printf("Newline encountered, Line: %d, Character: %d\n", lines + 1, ch); ++lines; ch=1; singleFlag = 0; isPrint = 0; }

{singleComment} { if (flag == 0) printf("Single line comment, Line: %d, Character: %d\n", lines + 1, ch); ch = ch + yyleng; singleFlag = 1; }

{semiColon} { if (flag == 0 && singleFlag == 0) printf("Semicolon, Line: %d, Character: %d\n", lines + 1, ch); ch++; }

{comma} { if (flag == 0 && singleFlag == 0) printf("Comma, Line: %d, Character: %d\n", lines + 1, ch); ch++; }

{bracket} { if (flag == 0 && singleFlag == 0) printf("Bracket, Line: %d, Character: %d\n", lines + 1, ch); ch++; }

{squareBracket} { if (flag == 0 && singleFlag == 0) printf("Square bracket, Line: %d, Character: %d\n", lines + 1, ch); ch++; }

{braces} { if (flag == 0 && singleFlag == 0) printf("Brace, Line: %d, Character: %d\n", lines + 1, ch); ch++; }

{arithmeticOp} { if (flag == 0 && singleFlag == 0 && isPrint==0) printf("Arithmetic operation, Line: %d, Character: %d\n", lines + 1, ch); ch++; }

{relationalOp} { if (flag == 0 && singleFlag == 0 && isPrint==0) printf("Relational operation, Line: %d, Character: %d\n", lines + 1, ch); ch = ch + yyleng; }

{assignmentOp} { if (flag == 0 && singleFlag == 0 && isPrint==0) printf("Assignment operation, Line: %d, Character: %d\n", lines + 1, ch); ch++; }

{elseKeyword} {if (flag == 0 && singleFlag == 0 && isPrint==0) printf("Else keyword, Line: %d, Character: %d\n", lines + 1, ch); ch = ch + yyleng;}

{ifKeyword} {if (flag == 0 && singleFlag == 0 && isPrint==0) printf("If keyword, Line: %d, Character: %d\n", lines + 1, ch); ch = ch + yyleng;}

{intKeyword} {if (flag == 0 && singleFlag == 0 && isPrint==0) printf("Int keyword, Line: %d, Character: %d\n", lines + 1, ch); ch = ch + yyleng;}

{charKeyword} {if (flag == 0 && singleFlag == 0 && isPrint==0) printf("Char keyword, Line: %d, Character: %d\n", lines + 1, ch); ch = ch + yyleng;}

{floatKeyword} {if (flag == 0 && singleFlag == 0 && isPrint==0) printf("Float keyword, Line: %d, Character: %d\n", lines + 1, ch); ch = ch + yyleng;}

{doubleKeyword} {if (flag == 0 && singleFlag == 0 && isPrint==0) printf("Double keyword, Line: %d, Character: %d\n", lines + 1, ch); ch = ch + yyleng;}

{returnKeyword} {if (flag == 0 && singleFlag == 0 && isPrint==0) printf("Return keyword, Line: %d, Character: %d\n", lines + 1, ch); ch = ch + yyleng;}

{voidKeyword} {if (flag == 0 && singleFlag == 0 && isPrint==0) printf("Void keyword, Line: %d, Character: %d\n", lines + 1, ch); ch = ch + yyleng;}

{whileKeyword} {if (flag == 0 && singleFlag == 0 && isPrint==0) printf("While keyword, Line: %d, Character: %d\n", lines + 1, ch); ch = ch + yyleng;}

{printKeyword} {if (flag == 0 && singleFlag == 0) printf("Print keyword, Line: %d, Character: %d\n", lines + 1, ch); ch = ch + yyleng; isPrint = 1;}

{mainKeyword} {if (flag == 0 && singleFlag == 0 && isPrint==0) printf("Main keyword, Line: %d, Character: %d\n", lines + 1, ch); ch = ch + yyleng;}

{mainKeyword2} {if (flag == 0 && singleFlag == 0 && isPrint==0) printf("Main keyword, Line: %d, Character: %d\n", lines + 1, ch); ch = ch + yyleng;}

{begComment} {
    if (flag == 0)
        printf("Comment Opening: %s, Line: %d, Character: %d\n", yytext, lines + 1, ch);
    flag = 1;
    commentError = lines + 1;
    ch = ch + yyleng;
}

{endComment} {
    if (flag == 1)
        printf("Comment Ending: %s, Line: %d, Character: %d\n", yytext, lines + 1, ch);
    ch = ch + yyleng;
    flag = 0;
}

{ID} {if (flag == 0 && singleFlag == 0 && isPrint==0) printf("Identifier: %s, Line: %d, Character: %d\n", yytext, lines + 1, ch); ch = ch + yyleng; }

{NUM} {if (flag == 0 && singleFlag == 0 && isPrint==0) printf("Number: %s, Line: %d, Character: %d\n", yytext, lines + 1, ch);  ch = ch + yyleng; }

{nonAlphabet} {if (flag == 0 && singleFlag == 0) printf("A non Alphabet error occurs at Line: %d, Character: %d\n", lines + 1, ch); ch = ch + yyleng; }

{wrongNUM1} {if (flag == 0 && singleFlag == 0 && isPrint==0) printf("Number error occurs at Line: %d, Character: %d\n", lines + 1, ch); ch = ch + yyleng; }

{wrongNUM2} {if (flag == 0 && singleFlag == 0 && isPrint==0) printf("Number error occurs at Line: %d, Character: %d\n", lines + 1, ch); ch = ch + yyleng; }

{wrongNUM3} {if (flag == 0 && singleFlag == 0 && isPrint==0) printf("Number error occurs at Line: %d, Character: %d\n", lines + 1, ch); ch = ch + yyleng; }

{wrongID1} {if (flag == 0 && singleFlag == 0 && isPrint==0) printf("ID error occurs at Line: %d, Character: %d\n", lines + 1, ch); ch = ch + yyleng; }

{wrongID2} {if (flag == 0 && singleFlag == 0 && isPrint==0) printf("ID error occurs at Line: %d, Character: %d\n", lines + 1, ch); ch = ch + yyleng; }

{wrongID3} {if (flag == 0 && singleFlag == 0 && isPrint==0) printf("ID error occurs at Line: %d, Character: %d\n", lines + 1, ch); ch = ch + yyleng; }

[^\t" "\n] { ch++; }

%%

int main() {
    yyin = fopen("input.txt", "r");
    yylex();
    fclose(yyin);

    if (flag == 1)
        printf("Comment error occurs at Line: %d, Character: %d \n", commentError, ch);

    return 0;
}

