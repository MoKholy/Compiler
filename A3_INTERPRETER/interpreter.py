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
    def __init__(self, expected, current_token, custom_message=None):
        self.expected = expected
        self.current_token = current_token
        if custom_message is not None:
            self.message = custom_message
        else:
            if current_token is None:
                self.message = f"Expected {expected} but found end of input."
            else:
                self.message = (
                    f"Expected {expected} but found '{current_token.type}' "
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

    def declare(self, name, var_type):
        if name in self.symbols:
            raise Exception(f"Error: Variable '{name}' already declared.")
        self.symbols[name] = SymbolTableEntry(name, var_type)

    def assign(self, name, value, value_type):
        if name not in self.symbols:
            raise Exception(f"Error: Variable '{name}' not declared.")
        if self.symbols[name].type != value_type:
            raise Exception(f"Type error: Cannot assign value of type {value_type} to variable '{name}' of type {self.symbols[name].type}.")
        self.symbols[name].value = value

    def lookup(self, name):
        return self.symbols.get(name)

    def print_table(self):
        print("Symbol Table:")
        print(f"{'Name':<10} {'Type':<10} {'Value':<10}")
        for name, entry in self.symbols.items():
            value = entry.value if entry.value is not None else ''
            print(f"{name:<10} {entry.type:<10} {value:<10}")

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


    def match(self, expected_type):
        """
        Match the current token type against the expected type.
        """
        if self.current_token is None:
            raise SyntaxError(f'Unexpected end of input, expected {expected_type}', None)

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
        left_value, left_type = self.factor()
        right_value, right_type = self.term_prime(left_value, left_type)
        # Type checking and value computation will be done inside term_prime
        return right_value, right_type

    def term_prime(self, left_value, left_type):
        if self.current_token and self.current_token.type == 'MULOP':
            operation = self.current_token.value
            self.match('MULOP')
            right_value, right_type = self.factor()
            if left_type != right_type:
                raise Exception(f"Type error: Cannot perform operation '{operation}' on types {left_type} and {right_type}.")
            # Perform the operation and return the result and type
            result_value = self.compute_mulop_result(operation, left_value, right_value)
            return result_value, left_type
        else:
            return left_value, left_type  # epsilon case; no operation to perform


    def mulop(self):
        # mulop -> * | /
        if self.current_token.type in ['*', '/']:
            value = self.current_token.value
            self.match('MULOP')
            return value
        else:
            raise SyntaxError('Expected "*" or "/"', self.current_token)

    def factor(self):
        if self.current_token.type == 'LPAREN':
            self.match('LPAREN')
            value, type = self.expression()  # Assuming expression returns a value and its type
            self.match('RPAREN')
            return value, type
        elif self.current_token.type == 'NUM':
            value = self.current_token.value
            # Determine if the value is integer or float based on its content
            type = 'int' if '.' not in value else 'float'
            self.match('NUM')
            return int(value) if type == 'int' else float(value), type
        elif self.current_token.type == 'ID':
            var_name, _ = self.var()  # var returns the variable name and array access if applicable
            var_entry = self.symbol_table.lookup(var_name)
            if var_entry is None:
                raise SyntaxError(f"Undeclared variable '{var_name}'", None)
            return var_entry.value, var_entry.type
        else:
            raise SyntaxError('Expected "(", variable, or number', self.current_token)
        
    def expression(self):
        # Assume the additive_expression method now also returns a type
        left_value, left_type = self.additive_expression()
        right_value, right_type = self.expression_prime(left_type, left_value)  # Pass the left operand's type for type checking
        # Type checking and value computation will be done inside expression_prime
        return left_value, left_type  # This assumes expression_prime may modify left_value based on the right side

    def expression_prime(self, left_type, left_value):
        # expression-prime -> relop additive-expression expression-prime | epsilon
        if self.current_token and self.current_token.type == 'RELOP':
            relop = self.current_token.value
            self.match('RELOP')
            right_value, right_type = self.additive_expression()
            # Perform type checking and compute the result value
            if left_type != right_type:
                raise Exception(f"Type error: Cannot perform '{relop}' operation between types {left_type} and {right_type}.")
            # Compute the result based on the relop and return it with the type
            result_value = self.compute_relop_result(relop, left_type, left_value, right_value)
            return result_value, left_type
        else:
            return None, left_type # epsilon case

    def relop(self):
        # relop -> <= | < | > | >= | == | !=
        if self.current_token.type == 'RELOP':
            value = self.current_token.value
            self.match('RELOP')
            return value
        else:
            raise SyntaxError('Expected relational operator', self.current_token)

    def additive_expression(self):
        # Assume the term method now also returns a type
        left_value, left_type = self.term()
        right_value, right_type = self.additive_expression_prime(left_value, left_type)  # Pass the left operand's type for type checking
        # Type checking and value computation will be done inside additive_expression_prime
        return left_value, left_type

    def additive_expression_prime(self, left_value, left_type):
        # additive-expression-prime -> addop term additive-expression-prime | epsilon
        if self.current_token and self.current_token.type == 'ADDOP':
            addop = self.current_token.value
            self.match('ADDOP')
            right_value, right_type = self.term()
            # Perform type checking and compute the result value
            if left_type != right_type:
                raise Exception(f"Type error: Cannot perform '{addop}' operation between types {left_type} and {right_type}.")
            # Compute the result based on the addop and return it with the type
            result_value = self.compute_addop_result(addop, left_type, left_value, right_value)
            return result_value, left_type
        else:
            return None, left_type
    
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
        return ('WHILE', expression_value, statement_value)

    def add_variable_declaration(self, var_name, var_type, additional_info=None):
        # This method should be called where variable declarations are parsed.
        if self.symbol_table.lookup(var_name) is not None:
            raise SyntaxError(f"Variable '{var_name}' already declared.", self.current_token)
        self.symbol_table.add(var_name, var_type, additional_info)

    def assignment_statement(self):
        var_name, var_prime_value = self.var()
        var_entry = self.symbol_table.lookup(var_name)
        if var_entry is None:
            raise SyntaxError(f"Undeclared variable '{var_name}'", self.current_token, custom_message=f"Undeclared variable '{var_name}'")
        self.match('ASSIGN')
        expression_value, expression_type = self.expression()
        
        # Convert token values to the proper type if necessary
        if expression_type == 'int':
            expression_value = int(expression_value)
        elif expression_type == 'float':
            expression_value = float(expression_value)
        
        # Check if the variable type matches the expression type
        if var_entry.type != expression_type:
            raise Exception(f"Type error: Cannot assign value of type {expression_type} to variable '{var_name}' of type {var_entry.type}.")

        # Update the symbol table with the new value
        self.symbol_table.assign(var_name, expression_value, expression_type)
        self.match('SEMI')
        
        # Return the assignment result in a structured way
        return {
            'statement_type': 'assignment',
            'variable': var_name,
            'value': expression_value,
            'value_type': expression_type
        }

    def var(self):
        if self.current_token.type == 'ID':
            var_name = self.current_token.value
            var_entry = self.symbol_table.lookup(var_name)
            if var_entry is None:
                raise SyntaxError(f"Undeclared variable '{var_name}'", self.current_token, custom_message=f"Undeclared variable '{var_name}'")
            self.match('ID')
            var_prime_value = self.var_prime()
            return var_name, var_entry.type
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
            raise SyntaxError('Unrecognized statement', self.current_token, custom_message=f"Unrecognized statement '{self.current_token.value}'")

    def selection_statement(self):
        # selection-statement -> if (expression ) statement selection-statement-prime
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
            type_spec = self.current_token.value
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
        self.symbol_table.declare(var_name, type_spec)
        var_decl_prime_value = self.var_declaration_prime()
        
        # Check if var_decl_prime_value is a dictionary with an 'ARRAY_SIZE' key
        array_size = None
        if isinstance(var_decl_prime_value, dict):
            array_size = var_decl_prime_value['ARRAY_SIZE']
        
        # Add the variable to the symbol table
        # self.symbol_table.add(var_name, type_spec, additional_info=array_size)
        
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
    

    def compute_relop_result(self, relop, operand_type, left_value, right_value):
        # Ensure that both operands are of the same type for simplicity
        if operand_type != type(left_value).__name__ or operand_type != type(right_value).__name__:
            raise Exception("Type error: Operand types do not match in relational operation.")
        
        # Evaluate the relational operation
        if relop == '==':
            return left_value == right_value
        elif relop == '!=':
            return left_value != right_value
        elif relop == '<':
            return left_value < right_value
        elif relop == '<=':
            return left_value <= right_value
        elif relop == '>':
            return left_value > right_value
        elif relop == '>=':
            return left_value >= right_value
        else:
            raise Exception(f"Unknown relational operator {relop}")

    def compute_addop_result(self, addop, operand_type, left_value, right_value):
        # Ensure that both operands are of the same type for simplicity
        if operand_type != type(left_value).__name__ or operand_type != type(right_value).__name__:
            raise Exception("Type error: Operand types do not match in addition operation.")
        
        # Evaluate the addition/subtraction operation
        if addop == '+':
            return left_value + right_value
        elif addop == '-':
            return left_value - right_value
        else:
            raise Exception(f"Unknown addition operator {addop}")


    def compute_mulop_result(self, operation, left_value, right_value):
        # Perform the multiplication or division based on the operation
        if operation == '*':
            return left_value * right_value
        elif operation == '/':
            # Handle division by zero and float division
            if right_value == 0:
                raise Exception("Runtime error: Division by zero.")
            return left_value / right_value
        else:
            raise Exception(f"Unknown multiplication operator {operation}")

    def parse(self):
        # This is the entry point of the parser
        try:
            self.program()
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
    int c;

    a = 10;
    b = 20;
    c = a+b;

    if (a >= b) {
        c = a;
    }
    }
    """
    
    tokens = list(lexer(code))
    ##### PARSE #####
    parser = Parser(tokens)
    parser.parse()