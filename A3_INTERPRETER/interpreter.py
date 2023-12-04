import re






# DEFINE TOKEN TYPES AND PATTERNS

TOKEN_TYPES = {
    'WHITESPACE': r'\s+',
    'PROGRAM': r'Program',
    'NUM': r'\d+',
    'TYPE': r'\bint\b|\bfloat\b|\bvoid\b',
    'ADDOP': r'\+|-',
    'MULOP': r'\*|/',
    'RELOP': r'<=|>=|>|<|==|!=',
    "ASSIGN": r'=',
    'IF': r'if',
    'ELSE': r'else',
    'WHILE': r'while',
    'SEMI': r';',
    'COMMA': r',',
    'LPAREN': r'\(',
    'RPAREN': r'\)',
    'LBRACKET': r'\[',
    'RBRACKET': r'\]',
    'LBRACE': r'\{',
    'RBRACE': r'\}',
    'ID': r'[a-zA-Z_]\w*'
}

# Token class
class Token:
    def __init__(self, type, value, line_no = None, char_pos = None):
        self.type = type
        self.value = value
        self.line_no = line_no
        self.char_pos = char_pos

    def __str__(self):
        return f"Token({self.type}, {repr(self.value)}, Line: {self.line_no}, Char: {self.char_pos})"

    def __repr__(self):
        return self.__str__()
    

# The token pattern is a combination of all the token regexes
token_pattern = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_TYPES.items())

# updated Lexer function
def lexer(code):
    lineno = 1
    line_start = 0
    for mo in re.finditer(token_pattern, code):
        kind = mo.lastgroup
        value = mo.group(kind)
        char_pos = mo.start() - line_start
        if kind == 'WHITESPACE':
            # Update line number and line start position
            newline_count = value.count('\n')
            if newline_count > 0:
                line_start = mo.end() - value.rfind('\n') - 1
                lineno += newline_count
            continue
        yield Token(kind, value, lineno, char_pos)

class SyntaxError(Exception):
    def __init__(self, expected, current_token):
        self.expected = expected
        self.current_token = current_token
        self.message = (
            f"Syntax error: Expected {expected} but found '{current_token.type}' "
            f"at line {current_token.line_no}, char {current_token.char_pos}"
        )
        super().__init__(self.message)

class SymbolTableEntry:
    def __init__(self, name, type, value=None, additional_info=None):
        self.name = name
        self.type = type
        self.value = value
        self.additional_info = additional_info

class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.scope_stack = []

    def enter_scope(self):
        self.scope_stack.append({})

    def exit_scope(self):
        self.scope_stack.pop()

    def add(self, name, type, value=None, additional_info=None):
        # Check if the variable has already been declared in the current scope
        if name in self.symbols:
            raise SyntaxError(f"Variable '{name}' is already declared.", self.current_token)
        
        if not value:
            value = -1
            print(f"Value: {value}")
        self.symbols[name] = SymbolTableEntry(name, type, value, additional_info)


    def update(self, name, value=None):
        # Check if the variable has been declared
        if name not in self.symbols:
            raise SyntaxError(f"Undeclared variable '{name}'", self.current_token)
        self.symbols[name].value = value

    def lookup(self, name):
        return self.symbols.get(name)


    def print_table(self):
        print("Symbol Table:")
        print(f"{'Name':<20} {'Type':<15} {'Value':<10} {'Additional Info':<20}")
        print("-" * 65)
        for name, entry in self.symbols.items():
            additional_info = entry.additional_info if entry.additional_info else ''
            print(f"{entry.name:<20} {entry.type:<15} {entry.value:<10} {additional_info:<20}")

class Parser:
    def __init__(self, tokens):
        self.tokens = iter(tokens)
        self.current_token = None
        self.symbol_table = SymbolTable()
        self.get_next_token()

    def get_next_token(self):
        """
        Advance to the next token in the stream.
        """
        self.current_token = next(self.tokens, None)
        print(f"curr_token: {self.current_token}")


    def match(self, expected_type):
        """
        Match the current token type against the expected type.
        """
        if self.current_token is None:
            raise SyntaxError(f'Unexpected end of input, expected {expected_type}')

        if self.current_token.type == expected_type:
            self.get_next_token()  # Consume the token
        else:
            raise SyntaxError(f'{expected_type}, but found {self.current_token.type}', self.current_token)

    def addop(self):
        # addop -> + | -
        if self.current_token.type =="ADDOP":
            value = self.current_token.value
            self.match('ADDOP')
            return value
        else:
            raise SyntaxError('Expected "+" or "-"', self.current_token)

    def term(self):
        # term -> factor term-prime
        factor_value = self.factor()
        term_prime_value = self.term_prime()
        # Combine factor and term-prime values
        return (factor_value, term_prime_value)

    def term_prime(self):
        # term-prime -> mulop factor term-prime | epsilon
        if self.current_token and self.current_token.type == 'MULOP':
            mulop_value = self.mulop()
            factor_value = self.factor()
            term_prime_value = self.term_prime()
            return (mulop_value, factor_value, term_prime_value)
        else:
            return None  # epsilon case

    def mulop(self):
        # mulop -> * | /
        if self.current_token.type in ['*', '/']:
            value = self.current_token.value
            self.match('MULOP')
            return value
        else:
            raise SyntaxError('Expected "*" or "/"', self.current_token)

    def factor(self):
        # factor -> ( expression ) | var | NUM
        if self.current_token.type == 'LPAREN':
            self.match('LPAREN')
            expr_value = self.expression()
            self.match('RPAREN')
            return expr_value
        elif self.current_token.type in ['NUM', 'ID']:
            value = self.current_token.value
            self.match(self.current_token.type)  # Consuming NUM or ID
            return value
        else:
            raise SyntaxError('Expected "(", variable, or number', self.current_token)
    def expression(self):
        # expression -> additive-expression expression-prime
        additive_expression_value = self.additive_expression()
        expression_prime_value = self.expression_prime()
        return (additive_expression_value, expression_prime_value)

    def expression_prime(self):
        # expression-prime -> relop additive-expression expression-prime | epsilon
        if self.current_token and self.current_token.type == 'RELOP':
            relop_value = self.relop()
            additive_expression_value = self.additive_expression()
            expression_prime_value = self.expression_prime()
            return (relop_value, additive_expression_value, expression_prime_value)
        else:
            return None  # epsilon case

    def relop(self):
        # relop -> <= | < | > | >= | == | !=
        if self.current_token.type == 'RELOP':
            value = self.current_token.value
            self.match('RELOP')
            return value
        else:
            raise SyntaxError('Expected relational operator', self.current_token)

    def additive_expression(self):
        # additive-expression -> term additive-expression-prime
        term_value = self.term()
        additive_expression_prime_value = self.additive_expression_prime()
        return (term_value, additive_expression_prime_value)

    def additive_expression_prime(self):
        # additive-expression-prime -> addop term additive-expression-prime | epsilon
        if self.current_token and self.current_token.type == 'ADDOP':
            addop_value = self.addop()
            term_value = self.term()
            additive_expression_prime_value = self.additive_expression_prime()
            return (addop_value, term_value, additive_expression_prime_value)
        else:
            return None  # epsilon case
    
    def selection_statement_prime(self):
        # selection-statement-prime -> epsilon | else statement
        if self.current_token and self.current_token.type == 'ELSE':
            self.match('ELSE')
            else_statement_value = self.statement()
            return else_statement_value
        else:
            return None  # epsilon case

    def iteration_statement(self):
        # Iteration-statement -> while ( expression ) statement ;
        self.match('WHILE')
        self.match('LPAREN')
        expression_value = self.expression()
        self.match('RPAREN')
        statement_value = self.statement()
        self.match('SEMI')
        return ('WHILE', expression_value, statement_value)

    def add_variable_declaration(self, var_name, var_type, additional_info=None):
        # This method should be called where variable declarations are parsed.
        if self.symbol_table.lookup(var_name) is not None:
            raise SyntaxError(f"Variable '{var_name}' already declared.", self.current_token)
        self.symbol_table.add(var_name, var_type, additional_info)

    def assignment_statement(self):
        var_name, var_prime_value = self.var()
        # Check if the variable has been declared
        var_entry = self.symbol_table.lookup(var_name)
        if var_entry is None:
            raise SyntaxError(f"Undeclared variable '{var_name}'", self.current_token)
            
        self.match('ASSIGN')
        expression_value = self.expression()
        self.symbol_table.update(var_name, value=expression_value)
        print(f"Symbol table updated: {var_name} = {self.symbol_table.lookup(var_name).value}")
        self.match('SEMI')
        return ('ASSIGN', var_name, var_prime_value, expression_value)

    def var(self):
        if self.current_token.type == 'ID':
            var_name = self.current_token.value
            self.match('ID')
            var_prime_value = self.var_prime()
            return var_name, var_prime_value
        else:
            raise SyntaxError('Expected identifier', self.current_token)

    def var_prime(self):
        if self.current_token and self.current_token.type == 'LBRACKET':
            self.match('LBRACKET')
            expression_value = self.expression()
            self.match('RBRACKET')
            return ('ARRAY_ACCESS', expression_value)
        else:
            return None  # epsilon case

    def param_prime(self):
        # param-prime -> epsilon | [ ]
        if self.current_token and self.current_token.type == 'LBRACKET':
            self.match('LBRACKET')
            self.match('RBRACKET')
            return 'ARRAY'
        else:
            return None  # epsilon case

    def compound_stmt(self):
        # compound-stmt -> { statement-list }
        self.match('LBRACE')
        statement_list_value = self.statement_list()
        self.match('RBRACE')
        return {'COMPOUND': statement_list_value}

    def statement_list(self):
        # statement-list -> statement statement-list | epsilon
        statements = []
        while self.current_token and self.current_token.type not in ['RBRACE', 'EOF']:
            statements.append(self.statement())
        return statements

    def statement(self):
        # statement -> assignment-statement | compound-statement | selection-statement | iteration-statement
        if self.current_token.type == 'ID':  # assuming an assignment-statement starts with an ID
            return self.assignment_statement()
        elif self.current_token.type == 'LBRACE':  # start of compound-statement
            return self.compound_stmt()
        elif self.current_token.type == 'IF':  # start of selection-statement
            return self.selection_statement()
        elif self.current_token.type == 'WHILE':  # start of iteration-statement
            return self.iteration_statement()
        else:
            raise SyntaxError('Unrecognized statement', self.current_token)

    def selection_statement(self):
        # selection-statement -> if (expression ) statement selection-statement-prime

        print(f"Selection stmt")
        self.match('IF')
        self.match('LPAREN')
        expression_value = self.expression()
        self.match('RPAREN')
        statement_value = self.statement()
        selection_statement_prime_value = self.selection_statement_prime()
        return {'IF': expression_value, 'THEN': statement_value, 'ELSE': selection_statement_prime_value}

    def type_specifier(self):
        # type-specifier -> int | float
        if self.current_token.type =="TYPE":
            type_spec = self.current_token.type
            self.match(self.current_token.type)
            return type_spec
        else:
            raise SyntaxError('Expected type specifier', self.current_token)

    def params(self):
        # params -> param-list | void
        if self.current_token.value == 'void':
            self.match('VOID')
            return 'VOID'
        else:
            return self.param_list()

    def param_list(self):
        # param-list -> param param-list-prime
        params = [self.param()]
        params.extend(self.param_list_prime())
        return params

    def param_list_prime(self):
        # param-list-prime -> , param param-list-prime | epsilon
        if self.current_token and self.current_token.type == 'COMMA':
            self.match('COMMA')
            return [self.param()] + self.param_list_prime()
        else:
            return []  # epsilon case

    def param(self):
        # param -> type-specifier ID param-prime
        type_spec = self.type_specifier()
        if self.current_token.type == 'ID':
            id_value = self.current_token.value
            self.match('ID')
            param_prime_value = self.param_prime()
            return {'type': type_spec, 'id': id_value, 'param_prime': param_prime_value}
        else:
            raise SyntaxError('Expected identifier', self.current_token)
    
    def program(self):
        # program -> Program ID { declaration-list statement-list }
        self.match('PROGRAM')
        program_name = self.current_token.value
        self.match('ID')
        self.match('LBRACE')
        declaration_list_value = self.declaration_list()
        statement_list_value = self.statement_list()
        self.match('RBRACE')
        return {'PROGRAM': program_name, 'DECLARATIONS': declaration_list_value, 'STATEMENTS': statement_list_value}

    def declaration_list(self):
        # declaration-list -> declaration declaration-list-prime
        declarations = [self.declaration()]
        declarations.extend(self.declaration_list_prime())
        return declarations

    def declaration_list_prime(self):
        # declaration-list-prime -> declaration declaration-list-prime | epsilon
        if self.current_token and self.current_token.type =="TYPE":  # Assuming types start declarations
            return [self.declaration()] + self.declaration_list_prime()
        else:
            return []  # epsilon case

    def declaration(self):
        # declaration -> var-declaration
        return self.var_declaration()

    def var_declaration(self):
        # var-declaration -> type-specifier ID var-declaration-prime
        type_spec = self.type_specifier()
        var_name = self.current_token.value
        self.match('ID')
        var_decl_prime_value = self.var_declaration_prime()
        
        # Check if var_decl_prime_value is a dictionary with an 'ARRAY_SIZE' key
        array_size = None
        if isinstance(var_decl_prime_value, dict):
            array_size = var_decl_prime_value['ARRAY_SIZE']
        
        # Add the variable to the symbol table
        self.symbol_table.add(var_name, type_spec, additional_info=array_size)
        
        return {'TYPE': type_spec, 'ID': var_name, 'VAR_DECL_PRIME': var_decl_prime_value}


    def var_declaration_prime(self):
        # var-declaration-prime -> ; | [ NUM ] ;
        if self.current_token.type == 'SEMI':
            self.match('SEMI')
            return 'SIMPLE'
        elif self.current_token.type == 'LBRACKET':
            self.match('LBRACKET')
            num_value = self.current_token.value
            self.match('NUM')
            self.match('RBRACKET')
            self.match('SEMI')
            return {'ARRAY_SIZE': num_value}
        else:
            raise SyntaxError('Expected ";" or "["', self.current_token)
        
    def parse(self):
        # This is the entry point of the parser
        try:
            self.symbol_table.enter_scope()  # Start in the global scope
            self.program()
            self.symbol_table.exit_scope()
            print("Parsing successful.")
            # Print the symbol table
            self.symbol_table.print_table()
            return True
        except SyntaxError as e:
            print(f"Syntax error: {e}")
            return False



if __name__ == "__main__":

    code = """
    Program X {

    int a;
    int b;
    float c;

    a = 10;
    b = 20;
    c = a+b;

    if (a >= b) {
        c = a;
    }
    }
    """
    
    tokens = list(lexer(code))

    # ##### PRINT TOKENS #####
    # for token in tokens:
    # 	print(token)

    ##### PARSE #####


    parser = Parser(tokens)
    parser.parse()