import tkinter as tk
from tkinter import ttk

# Definición de la clase TreeNode para el árbol
class TreeNode:
    def __init__(self, name, children=None):
        self.name = name
        self.children = children or []

# Función para crear nodos a partir de la información del archivo
def create_tree_node(lines, current_indent=0, record_num=1):
    if not lines:
        return None, []

    root = None
    children = []
    i = 0

    # Leer las líneas hasta que se cambie el nivel de indentación
    while i < len(lines):
        line = lines[i]
        indent_level = len(line) - len(line.lstrip())  # Contar los espacios en blanco al principio

        if indent_level == current_indent:
            # Crear el nodo raíz si aún no está definido
            node_name = line.strip()
            if root is None:
                root = TreeNode(node_name)
            else:
                # Agregar hijo a la lista de hijos
                children.append(TreeNode(node_name))

                # *** Aquí detectamos un identificador de variable ***
                if node_name.isidentifier():  # isidentifier() detecta si es un nombre de variable válido
                    symbol_table.insert(
                        name=node_name,
                        type="int",  # Aquí deberías poner el tipo real de la variable
                        value=None,  # El valor puede ser None por ahora
                        record=record_num,  # Número de registro
                        line=i + 1  # Número de línea en la que está la variable
                    )
                    record_num += 1  # Actualizar número de registro

            i += 1
        elif indent_level > current_indent:
            # Crear hijos recursivamente
            child_node, remaining_lines = create_tree_node(lines[i:], indent_level, record_num)
            if child_node:  # Solo añadir el nodo si se ha creado correctamente
                children.append(child_node)
            i += len(lines[i:]) - len(remaining_lines)
        else:
            break

    if root is not None:  # Asegurarse de que el nodo raíz sea no nulo
        root.children = children
    return root, lines[i:]



class HashTable:
    def __init__(self, size=10):
        self.size = size
        self.table = [[] for _ in range(size)]  # Usamos listas para manejar colisiones (encadenamiento)

    def hash_function(self, key):
        return hash(key) % self.size

    def insert(self, name, type, value, record, line):
        index = self.hash_function(name)
        self.table[index].append({
            'name': name,
            'type': type,
            'value': value,
            'record': record,
            'line': line
        })

    def lookup(self, name):
        index = self.hash_function(name)
        for entry in self.table[index]:
            if entry['name'] == name:
                return entry
        return None
    def display(self):
        print("Contenido de la Tabla Hash:")
        for index, entries in enumerate(self.table):
            if entries:  # Si hay elementos en esta posición de la tabla
                print(f"Índice {index}:")
                for entry in entries:
                    print(f"  {entry}")
# Crear la tabla hash global para almacenar variables
symbol_table = HashTable()



