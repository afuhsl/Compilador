import ply.lex as lex
import ply.yacc as yacc
import json

# Lista de tokens y palabras reservadas
tokens = (
    'ID', 'NUMBER', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD', 'POWER',
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE', 'COMMA', 'SEMICOLON',
    'EQUAL', 'LESS', 'LESSEQUAL', 'GREATER', 'GREATEREQUAL', 'DEQUAL', 'NEQUAL',
    'IF', 'ELSE', 'DO', 'WHILE', 'SWITCH', 'CASE', 'INT', 'DOUBLE', 'MAIN', 'CIN', 'COUT',
    'PLUSPLUS', 'MINUSMINUS', 'AND', 'OR', 'END'
)

reserved = {
    'if': 'IF', 'else': 'ELSE', 'do': 'DO', 'while': 'WHILE', 'switch': 'SWITCH', 'case': 'CASE', 
    'int': 'INT', 'double': 'DOUBLE', 'main': 'MAIN', 'cin': 'CIN', 'cout': 'COUT', 'and': 'AND', 
    'or': 'OR', 'end': 'END'
}

# Expresiones regulares para tokens simples
t_PLUSPLUS = r'\+\+'
t_MINUSMINUS = r'\-\-'
t_PLUS = r'\+'
t_MINUS = r'\-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_MOD = r'%'
t_POWER = r'\^'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COMMA = r','
t_SEMICOLON = r';'
t_EQUAL = r'='
t_LESS = r'<'
t_LESSEQUAL = r'<='
t_GREATER = r'>'
t_GREATEREQUAL = r'>='
t_DEQUAL = r'=='
t_NEQUAL = r'!='

# Ignorar espacios y tabulaciones
t_ignore = ' \t'

# Expresión regular para números
def t_NUMBER(t):
    r'\d+(\.\d+)?'
    if '.' in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t

# Expresión regular para identificadores y palabras reservadas
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')
    return t

# Expresión regular para saltos de línea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Manejo de errores de caracteres ilegales
def t_error(t):
    print(f"Caracter erroneo: '{t.value[0]}' en la línea: {t.lineno}")
    t.lexer.skip(1)

# Comentarios de una sola línea (//...)
def t_COMMENT_SINGLELINE(t):
    r'//.*'
    pass  # Ignorar el comentario

# Comentarios de múltiples líneas (/*...*/)
def t_COMMENT_MULTILINE(t):
    r'/\*([^*]|\*[^/])*\*/'
    t.lexer.lineno += t.value.count('\n')
    pass  # Ignorar el comentario

# Construcción del lexer
lexer = lex.lex()

# Reglas de precedencia para los operadores aritméticos
precedence = (
    ('right', 'PLUSPLUS', 'MINUSMINUS'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('right', 'POWER'),
)

# Definición de las reglas de la gramática
def p_programa(p):
    'programa : MAIN LBRACE listaDeclaracion RBRACE'
    p[0] = p[3]

def p_listaDeclaracion(p):
    '''listaDeclaracion : listaDeclaracion declaracion
                        | declaracion'''
    if len(p) == 3:
        if isinstance(p[1], list):
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = [p[1], p[2]]
    else:
        p[0] = [p[1]]

def p_declaracion(p):
    '''declaracion : declaracionVariable
                | listaSentencias'''
    p[0] = p[1]

def p_declaracionVariable(p):
    'declaracionVariable : tipo listaIdentificadores SEMICOLON'
    p[0] = (p[1], p[2])

def p_listaIdentificadores(p):
    '''listaIdentificadores : ID
                            | ID COMMA listaIdentificadores'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_tipo(p):
    '''tipo : INT
            | DOUBLE'''
    p[0] = p[1]

def p_listaSentencias(p):
    '''listaSentencias : listaSentencias sentencia
                       | sentencia
                       | empty'''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    elif len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_sentencia(p):
    '''sentencia : seleccion
                 | iteracion
                 | repeticion
                 | sentIn
                 | sentOut
                 | asignacion
                 | incremento'''
    p[0] = p[1]

def p_asignacion(p):
    'asignacion : ID EQUAL sentExpresion SEMICOLON'
    p[0] = ('=', p[1], p[3])

def p_incremento(p):
    '''incremento : ID PLUSPLUS SEMICOLON
                  | ID MINUSMINUS SEMICOLON
                  | PLUSPLUS ID SEMICOLON
                  | MINUSMINUS ID SEMICOLON'''
    if len(p) == 4:
        p[0] = (p[2], p[1])
    else:
        p[0] = (p[1], p[2])

def p_sentExpresion(p):
    '''sentExpresion : expresion
                     | incremento
                     | SEMICOLON'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = None

def p_seleccion(p):
    '''seleccion : IF expresion LBRACE listaSentencias RBRACE
                 | IF expresion LBRACE listaSentencias RBRACE ELSE LBRACE listaSentencias RBRACE'''
    if len(p) == 6:
        p[0] = ('if', p[2], p[4], None)
    else:
        p[0] = ('if-else', p[2], p[4], p[8])

def p_iteracion(p):
    'iteracion : WHILE expresion LBRACE listaSentencias RBRACE'
    p[0] = ('while', p[2], p[4])

def p_repeticion(p):
    'repeticion : DO LBRACE listaSentencias RBRACE WHILE expresion'
    p[0] = ('do-while', p[3], p[6])

def p_sentIn(p):
    'sentIn : CIN ID SEMICOLON'
    p[0] = ('cin', p[2])

def p_sentOut(p):
    'sentOut : COUT expresion SEMICOLON'
    p[0] = ('cout', p[2])

def p_expresion(p):
    '''expresion : expresionSimple relacionOp expresionSimple
                 | expresionSimple'''
    if len(p) == 3:
        p[0] = (p[2], p[1], p[3])
    else:
        p[0] = p[1]

def p_relacionOp(p):
    '''relacionOp : LESS
                  | LESSEQUAL
                  | GREATER
                  | GREATEREQUAL
                  | DEQUAL
                  | NEQUAL'''
    p[0] = p[1]

def p_expresionSimple(p):
    '''expresionSimple : expresionSimple sumaOp termino
                       | termino'''
    if len(p) == 3:
        p[0] = (p[2], p[1], p[3])
    else:
        p[0] = p[1]

def p_sumaOp(p):
    '''sumaOp : PLUS
              | MINUS'''
    p[0] = p[1]

def p_termino(p):
    '''termino : termino multOp factor
               | factor'''
    if len(p) == 3:
        p[0] = (p[2], p[1], p[3])
    else:
        p[0]= p[1]

def p_multOp(p):
    '''multOp : TIMES
              | DIVIDE
              | MOD'''
    p[0] = p[1]

def p_factor(p):
    '''factor : factor potOp componente
            | componente'''
    if len(p) == 4:
        p[0] = (p[2], p[1], p[3])
    else:
        p[0] = p[1]

def p_potOp(p):
    'potOp : POWER'
    p[0] = p[1]

def p_componente(p):
    '''componente : LPAREN expresion RPAREN
                | NUMBER
                | ID'''
    if len(p) == 4:
        p[0] = ('componente', p[2])
    else:
        p[0] = ('componente', p[1])

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        line = getattr(p, 'lineno', 'unknown')
        token = getattr(p, 'value', 'unknown')
        
        error_message = f"Syntax error in '{token}' at line: {line}. "
        
        if token in ['+', '-', '*', '/']:
            error_message += f"Incorrect use of operator '{token}'."
        elif token == '(':
            error_message += "Possibly missing a closing parenthesis ')'."
        elif token == ')':
            error_message += "Possibly missing an opening parenthesis '('."
        elif token == ';':
            error_message += "Incorrect use of semicolon ';'."
        elif token == '{':
            error_message += "Possibly missing a closing brace '}' or a closing parenthesis ')'."
        elif token == 'else':
            error_message += "Possibly missing a closing brace '}'."
        elif token == '}':
            error_message += "Possibly missing an opening brace '{'."
        else:
            error_message += "Unexpected token."
        
        print(error_message)
        yacc.errok()
    else:
        print("Syntax error at EOF. Possibly missing a closing brace '}' or a semicolon ';'.")

# Construcción del parser
parser = yacc.yacc()

def parse(input_text):
    lexer.lineno = 1  # Resetear el número de línea
    result = parser.parse(input_text)
    return result if result is not None else None

def write_token_info(tokens, output_file):
    with open(output_file, 'w') as file:
        for token in tokens:
            file.write(f'Tipo: {token.type}, Valor: {token.value}, Línea: {token.lineno}\n')

def write_ast_info(ast, output_file):
    with open(output_file, 'w') as file:
        if ast is not None:
            file.write(json.dumps(ast, indent=2))
        else:
            file.write("")

def clear_file_content(output_file):
    with open(output_file, 'w') as file:
        file.write("")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        sys.exit(1)

    input_file = sys.argv[1]
    token_output_file = 'token_info.txt'
    ast_output_file = 'ast_info.txt'

    try:
        with open(input_file, 'r') as file:
            text = file.read()
    except FileNotFoundError:
        print(f"File '{input_file}' not found.")
        sys.exit(1)

    lexer.input(text)
    tokens = list(lexer)
    result = parse(text)
    
    if result is not None:
        write_token_info(tokens, token_output_file)
        #write_ast_info(result, ast_output_file)
        #print("Token information written to:", token_output_file)
        #print("AST written to:", ast_output_file)
    else:
        clear_file_content(token_output_file)
        #clear_file_content(ast_output_file)
        #print("Syntax errors encountered. Files have been cleaned.")
