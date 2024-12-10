import ply.lex as lex
import ply.yacc as yacc
from anytree import Node, RenderTree
import sys
import tkinter as tk
from tkinter import ttk
import pickle
import json
class SymbolTable:
    def __init__(self):
        # Inicializamos la tabla como un diccionario de listas
        self.table = {}
        self.registro_counter = 0
    def hash(self, key):
        # Función hash simple
        return hash(key) % 10  # Cambia 10 al tamaño que desees

    def define(self, name, type_, value, line_number):
        index = self.hash(name)
        # Si la clave no existe, inicializamos una lista
        if index not in self.table:
            self.table[index] = []
        
        # Verificamos si la variable ya existe en la lista
        for entry in self.table[index]:
            if entry['Nombre'] == name:
                # Si existe, la actualizamos
                entry['Tipo'] = type_
                entry['Valor'] = value
                
                entry['Linea'].append(line_number)
                return
        
        # Si no existe, la añadimos a la lista
        self.table[index].append({
            'Registro': self.registro_counter,
            'Nombre': name, 
            'Tipo': type_, 
            'Valor': value,
            'Linea': [line_number]
            })
        self.registro_counter += 1

    def lookup(self, name):
        index = self.hash(name)
        # Comprobamos si hay entradas en el índice correspondiente
        if index in self.table:
            for entry in self.table[index]:
                if entry['Nombre'] == name:
                    return entry  # Retorna la información de la variable encontrada
        return None  # Retorna None si no se encuentra la variable

    def update(self, name, value, line_number):
        index = self.hash(name)
        # Buscamos la variable en la lista correspondiente
        if index in self.table:
            for entry in self.table[index]:
                if entry['Nombre'] == name:
                    # Si la encontramos, actualizamos el valor
                    entry['Valor'] = value
                    
                    entry['Linea'].append(line_number)
                    return

    def __str__(self):
        # Método para imprimir el contenido de la tabla
        result = []
        for index in self.table:
            for entry in self.table[index]:
                result.append(f"Registro: {entry['Registro']}, Nombre: {entry['Nombre']}, Tipo: {entry['Tipo']}, Valor: {entry['Valor']}, Linea: {entry['Linea']}")
        return "\n".join(result)


    def save_to_file(self, filename):
        # Guardar el contenido de la tabla en un archivo JSON
        with open(filename, 'w') as f:
            # Convertimos la tabla en una lista de entradas
            entries = []
            for index in self.table:
                for entry in self.table[index]:
                    entries.append(entry)
            json.dump(entries, f, indent=4)  # Guardamos como una lista


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
symbol_table = SymbolTable()
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
    p[0] = Node('main', children=[p[3]])

def p_listaDeclaracion(p):
    '''listaDeclaracion : listaDeclaracion declaracion
                        | declaracion'''
    if len(p) == 3:
        p[0] = p[1]
        p[2].parent = p[0]
    else:
        p[0] = Node('', children=[p[1]])

def p_declaracion(p):
    '''declaracion : declaracionVariable
                | listaSentencias'''
    p[0] = p[1]

def p_declaracionVariable(p):
    'declaracionVariable : tipo listaIdentificadores SEMICOLON'

    var_type = p[1].name  # Tipo de la variable (por ejemplo, 'int')

    # Procesar todos los identificadores en la lista
    if hasattr(p[2], 'children'):
        for ident in p[2].children:
            # Capturamos el número de línea de cada identificador
            line_number = ident.line
            symbol_table.define(ident.name, var_type, None, line_number)  # Definir en la tabla de símbolos
            ident.var_type = var_type  # Asignar el tipo

    # Crear el nodo de declaración
    p[0] = Node('', children=[p[1], p[2]], var_type=var_type)
    # También asignamos el tipo a `p[2]` para que se propague a `listaIdentificadores`
    p[2].var_type = var_type

def p_listaIdentificadores(p):
    '''listaIdentificadores : ID
                            | ID COMMA listaIdentificadores'''
    if len(p) == 2:
        # Crear un nodo para el primer identificador
        id_node = Node(p[1], var_type=None, value=None, line=p.lineno(1))  # Captura el número de línea del ID
        p[0] = Node('', children=[id_node])
    else:
        # Crear un nodo para cada identificador en la lista y concatenarlos
        id_node = Node(p[1], var_type=None, value=None, line=p.lineno(1))  # Captura el número de línea del ID
        if hasattr(p[3], 'children'):
            # Concatenar los nodos hijos (lista de identificadores) correctamente
            p[0] = Node('', children=[id_node] + list(p[3].children))
        else:
            # En caso de que no haya más identificadores
            p[0] = Node('', children=[id_node])

def p_tipo(p):
    '''tipo : INT
            | DOUBLE'''
    p[0] = Node(p[1],var_type=p[1])

def p_listaSentencias(p):
    '''listaSentencias : listaSentencias sentencia
                    | sentencia
                    | empty'''
    if len(p) == 3:
        p[0] = p[1]
        p[2].parent = p[0]
    elif len(p) == 2:
        p[0] = Node('', children=[p[1]],var_type=p[1].var_type, value=p[1].value)
    else:
        p[0] = Node('',var_type=p[1].var_type, value=p[1].value)

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
    'asignacion : ID EQUAL expresion SEMICOLON'
    bandera=True
    var_info = symbol_table.lookup(p[1])  # Buscamos la variable en la tabla
    line_number = p.lineno(1)

    if var_info is not None:
        # Verificar si el tipo de la variable y el valor coinciden
        if (var_info['Tipo'] =='double' and p[3].var_type=='int')or(var_info['Tipo'] =='double' and p[3].var_type=='double')or(var_info['Tipo'] =='int' and p[3].var_type=='int'):
            symbol_table.update(p[1], p[3].value, line_number)  # Actualizamos el valor en la tabla de símbolos
            
        elif isinstance(p[3].value, int):
                    symbol_table.update(p[1], p[3].value, line_number)  # Actualizamos el valor en la tabla de símbolos
        else: 
            bandera=False
            print(f"SEMANTICO: Error: Asignación incompatible, se esperaba {var_info['Tipo']} pero se recibió {p[3].var_type}.")
    else:
        bandera=False
        print(f"SEMANTICO: Error: variable '{p[1]}' no está definida en linea {line_number}.")
        
    if bandera:
     p[0] = Node('=', children=[Node(p[1],var_type=var_info['Tipo'],value=p[3].value), p[3]],value=p[3].value, var_type=var_info['Tipo'])  # Creamos un nodo para la asignación
    else:
     p[0] = Node('=', children=[Node(p[1],var_type="Error",value="Error"), p[3]],value="Error", var_type="Error")  # Creamos un nodo para la asignación
def p_incremento(p):
    '''incremento : ID PLUSPLUS SEMICOLON
                  | ID MINUSMINUS SEMICOLON
                  | PLUSPLUS ID SEMICOLON
                  | MINUSMINUS ID SEMICOLON'''
    valor = 0  # Valor predeterminado
    tipo = "None"
    line_number = p.lineno(1)  # Obtener el número de línea

    if p[1] == '++':
        # Pre-incremento
        var_info = symbol_table.lookup(p[2])  # Buscar variable
        if var_info is not None:
            valor = var_info['Valor'] if var_info['Valor'] is not None else 0
            tipo = var_info['Tipo']
            symbol_table.update(p[2], valor + 1, line_number)
        else:
            print(f"SEMANTICO: Error: variable '{p[2]}' no está definida en línea {line_number}.")
        
        p[0] = Node('=', children=[
            Node(p[2], value=valor + 1, var_type=tipo),
            Node('+', children=[Node(p[2], value=valor, var_type=tipo), Node('1', value=1, var_type="int")])
        ])
    
    elif p[1] == '--':
        # Pre-decremento
        var_info = symbol_table.lookup(p[2])  # Buscar variable
        if var_info is not None:
            valor = var_info['Valor'] if var_info['Valor'] is not None else 0
            tipo = var_info['Tipo']
            symbol_table.update(p[2], valor - 1, line_number)
        else:
            print(f"SEMANTICO: Error: variable '{p[2]}' no está definida en línea {line_number}.")
        
        p[0] = Node('=', children=[
            Node(p[2], value=valor - 1, var_type=tipo),
            Node('-', children=[Node(p[2], value=valor, var_type=tipo), Node('1', value=1, var_type="int")])
        ])
    
    elif p[2] == '++':
        # Post-incremento
        var_info = symbol_table.lookup(p[1])  # Buscar variable
        if var_info is not None:
            valor = var_info['Valor'] if var_info['Valor'] is not None else 0
            tipo = var_info['Tipo']
            symbol_table.update(p[1], valor + 1, line_number)
        else:
            print(f"SEMANTICO: Error: variable '{p[1]}' no está definida en línea {line_number}.")
        
        p[0] = Node('=', children=[
            Node(p[1], value=valor + 1, var_type=tipo),
            Node('+', children=[Node(p[1], value=valor, var_type=tipo), Node('1', value=1, var_type="int")])
        ])
    
    elif p[2] == '--':
        # Post-decremento
        var_info = symbol_table.lookup(p[1])  # Buscar variable
        if var_info is not None:
            valor = var_info['Valor'] if var_info['Valor'] is not None else 0
            tipo = var_info['Tipo']
            symbol_table.update(p[1], valor - 1, line_number)
        else:
            print(f"SEMANTICO: Error: variable '{p[1]}' no está definida en línea {line_number}.")
        
        p[0] = Node('=', children=[
            Node(p[1], value=valor - 1, var_type=tipo),
            Node('-', children=[Node(p[1], value=valor, var_type=tipo), Node('1', value=1, var_type="int")])
        ])
def p_sentExpresion(p):
    '''sentExpresion : expresion
                    | incremento
                    | SEMICOLON'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = Node('')

def p_seleccion(p):
    '''seleccion : IF expresion LBRACE listaSentencias RBRACE
                | IF expresion LBRACE listaSentencias RBRACE ELSE LBRACE listaSentencias RBRACE'''
    if len(p) == 6:
        p[0] = Node('if', children=[p[2], p[4]])
        p[0].var_type="boolean"
        p[4].var_type="boolean"
        if(p[2].value=="True"):
            p[0].value="True"
            p[4].value="True"
        else:
            p[0].value="False"
            p[4].value="False"
    else:
        p[0] = Node('if-else', children=[p[2], p[4], p[8]])
        p[0].var_type="boolean"
        p[4].var_type="boolean"
        p[8].var_type="boolean"
        if(p[2].value=="True"):
            p[0].value="True"
            p[4].value="True"
        else:
            p[0].value="False"
            p[4].value="False"
            p[8].value="True"
def p_iteracion(p):
    'iteracion : WHILE expresion LBRACE listaSentencias RBRACE'
    
    # Verificamos el resultado de la expresión antes de ejecutar las sentencias
    condition_result = p[2].value  # Suponiendo que p[2].value contiene el resultado de la expresión
    if condition_result == "True":
        p[0] = Node('while', children=[p[2], p[4]])
        # Se ejecutan las sentencias del bucle
    else:
        # Si la condición no se cumple, no se ejecutan las sentencias
        p[0] = Node('while', children=[p[2], Node('No se ejecuta el bucle')])
        p[0].var_type = "boolean"
        p[0].value = "False"  # O cualquier otro valor que desees asignar


def p_iteracion(p):
    'iteracion : WHILE expresion LBRACE listaSentencias RBRACE'
    p[0] = Node('while', children=[p[2], p[4]])

def p_repeticion(p):
    'repeticion : DO LBRACE listaSentencias RBRACE WHILE expresion'
    p[0] = Node('do-while', children=[p[3], p[6]])

def p_sentIn(p):
    'sentIn : CIN expresion SEMICOLON'
    p[0] = Node('cin', children=[p[2]])

def p_sentOut(p):
    'sentOut : COUT expresion SEMICOLON'
    p[0] = Node('cout', children=[p[2]])

def p_expresion(p):
    '''expresion : expresion PLUS expresion
                | expresion MINUS expresion
                | expresion TIMES expresion
                | expresion DIVIDE expresion
                | expresion MOD expresion
                | expresion POWER expresion
                | expresion LESS expresion
                | expresion LESSEQUAL expresion
                | expresion GREATER expresion
                | expresion GREATEREQUAL expresion
                | expresion DEQUAL expresion
                | expresion NEQUAL expresion
                | expresion AND expresion
                | expresion OR expresion
                | term'''
    line_number = p.lineno(1)
    if len(p) == 2:  # Manejo de términos como identificadores o números
        p[0] = p[1]
    
    else:
        left_type = getattr(p[1], 'var_type', None)
        right_type = getattr(p[3], 'var_type', None)
        
        # Verificación de tipos
        if left_type is None or right_type is None:
            print(f"SEMANTICO: Error: No es posible realizar la operación.")
            p[0] = Node(p[2],var_type="Error", value="Error")
            return 
        
        # Para operaciones aritméticas
        if p[2] in ('+', '-', '*', '/', '%', '**'):
            if left_type == right_type or (left_type == 'int' and right_type == 'double') or (left_type == 'double' and right_type == 'int'):
                result_type = 'double' if 'double' in (left_type, right_type) else 'int'
                try:
                    # Evaluar la operación
                    if p[2] == '+':
                        result_value = p[1].value + p[3].value
                    elif p[2] == '-':
                        result_value = p[1].value - p[3].value
                    elif p[2] == '*':
                        result_value = p[1].value * p[3].value
                    elif p[2] == '/':
                        result_value = p[1].value / p[3].value
                        # Si ambos operandos son enteros, redondear el resultado y convertir a entero
                        if left_type == 'int' and right_type == 'int':
                            result_value = int(round(result_value))
                            result_type = 'int'
                    elif p[2] == '%':
                        result_value = p[1].value % p[3].value
                    elif p[2] == '**':
                        result_value = p[1].value ** p[3].value
                    p[0] = Node(p[2], children=[p[1], p[3]], var_type=result_type, value=result_value)
                except TypeError:
                    print(f"SEMANTICO: Error: no se pueden realizar operaciones con tipos {left_type} y {right_type}")
                    p[0] = Node(p[2], children=[p[1], p[3]], var_type="Error", value="Error")
            else:
                print(f"SEMANTICO: Error: tipos incompatibles en la operación {p[2]} entre {left_type} y {right_type}")
                p[0] = Node(p[2], children=[p[1], p[3]], var_type="Error", value="Error")


        # Para operaciones relacionales
        elif p[2] in ('<', '<=', '>', '>=', '==', '!='):
            if left_type == right_type or (left_type == 'int' and right_type == 'double') or (left_type == 'double' and right_type == 'int'):
                try:
                    if p[2] == '<':
                        result_value = p[1].value < p[3].value
                    elif p[2] == '<=':
                        result_value = p[1].value <= p[3].value
                    elif p[2] == '>':
                        result_value = p[1].value > p[3].value
                    elif p[2] == '>=':
                        result_value = p[1].value >= p[3].value
                    elif p[2] == '==':
                        result_value = p[1].value == p[3].value
                    elif p[2] == '!=':
                        result_value = p[1].value != p[3].value
                    p[0] = Node(p[2], children=[p[1], p[3]], var_type='boolean', value=result_value)
                except TypeError:
                    print(f"SEMANTICO: Error: no se pueden realizar comparaciones con tipos {left_type} y {right_type}")
                    p[0] = Node(p[2], children=[p[1], p[3]], var_type=None, value=None)
            else:
                print(f"SEMANTICO: Error: tipos incompatibles en la comparación {p[2]} entre {left_type} y {right_type}")
                p[0] = Node(p[2], children=[p[1], p[3]], var_type=None, value=None)

        # Para operaciones lógicas
        elif p[2] in ('and', 'or'):
            if left_type == 'boolean' and right_type == 'boolean':
                try:
                    if p[2] == 'and':
                        result_value = p[1].value and p[3].value
                    elif p[2] == 'or':
                        result_value = p[1].value or p[3].value
                    p[0] = Node(p[2], children=[p[1], p[3]], var_type='boolean', value=result_value)
                except TypeError:
                    print(f"SEMANTICO: Error: no se pueden realizar operaciones lógicas con tipos {left_type} y {right_type}")
                    p[0] = Node(p[2], children=[p[1], p[3]], var_type=None, value=None)
            else:
                print(f"SEMANTICO: Error: las operaciones lógicas requieren booleanos, pero se encontraron {left_type} y {right_type}")
                p[0] = Node(p[2], children=[p[1], p[3]], var_type=None, value=None)

        else:
            print(f"SEMANTICO: Error: operación desconocida {p[2]}")
            p[0] = Node(p[2], children=[p[1], p[3]], var_type=None, value=None)

def p_term(p):
    '''term : ID
            | NUMBER
            | LPAREN expresion RPAREN'''    
    line_number = p.lineno(1)     
    if len(p) == 2:  # Manejo de ID y NUMBER
        if isinstance(p[1], Node):  # Si es un nodo, no se hace lookup
            p[0] = p[1]
        elif isinstance(p[1], (int)):  # Verifica si es un NUMBER
            p[0] = Node(p[1],var_type='int', value=p[1])  # Crea un nodo para el número
        elif isinstance(p[1], float):
            p[0] = Node(p[1], var_type='double', value=p[1])
        else:
            # Busca la variable en la tabla de símbolos
            var_info = symbol_table.lookup(p[1])
            line_number = p.lineno(1)
            if var_info is not None:
                symbol_table.update(p[1], var_info['Valor'], line_number)  # Actualizar línea de uso
                p[0] = Node(p[1], var_type=var_info['Tipo'], value=var_info['Valor'])
            else:
                print(f"SEMANTICO: Error: variable '{p[1]}' no está definida en linea {line_number}.")
    elif len(p) == 4:  # Manejo de expresiones entre paréntesis
        p[0] = p[2]  # Aquí, p[2] debería ser el nodo de la expresión que se evalúa

def p_empty(p):
    'empty :'
    p[0] = Node('empty')

def p_error(p):
    if p:
        print(f"Error de sintaxis en '{p.value}' en la línea: {p.lineno}. Token inesperado.")
    else:
        print("Error de sintaxis en EOF.")


# Construcción del parser
parser = yacc.yacc()

def parse(input_data):
    lexer.input(input_data)
    return parser.parse(input_data, lexer=lexer)

# Función para escribir información del AST en un archivo
def write_ast_info(root, output_file):
    with open(output_file, 'wb') as file:  # Guardar como binario
        pickle.dump(root, file)  # Serializa el objeto


# Función para limpiar el contenido de un archivo
def clear_file_content(output_file):
    with open(output_file, 'w') as file:
        file.write("")


if __name__ == "__main__":
    
    if len(sys.argv) != 2:
        #print("Uso: python sintaxis.py <input_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    ast_output_file = 'ast_info.pkl'  # Archivo en formato pickle

    try:
        with open(input_file, 'r') as file:
            input_data = file.read()
    except FileNotFoundError:
        print(f"Archivo '{input_file}' no encontrado.")
        sys.exit(1)
    except Exception as e:
        print(f"Error leyendo el archivo: {e}")
        sys.exit(1)

    result = parse(input_data)
    if result:
        clear_file_content(ast_output_file)
        write_ast_info(result, ast_output_file)
        #print(symbol_table)
        print(result)
        symbol_table.save_to_file('tabla_simbolos.json')
        # Crear ventana y TreeView con ttk
        #root = tk.Tk()
        #root.title("Árbol Sintáctico Abstracto")
        #tree = ttk.Treeview(root)
        #tree.pack(expand=tk.YES, fill=tk.BOTH)

        # Construir el árbol en el TreeView
        #def build_tree(parent, node):
        #    item_id = tree.insert(parent, 'end', text=node.name)
        #   for child in node.children:
        #      build_tree(item_id, child)

        #build_tree('', result)
        #root.mainloop()
    else:
        clear_file_content(ast_output_file)

