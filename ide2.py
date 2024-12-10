import json
import tkinter as tk
from tkinter import Text, ttk, filedialog
from analisador import Lexer
from PIL import Image, ImageTk
import subprocess
from anytree import Node
from arbol import create_tree_node
import pickle
from sintaxis import SymbolTable
import json
import os
import pickle

    
class IDE(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Compilador")
        self.geometry("1300x600")
        self.resizable(False, False)

        #Menú
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Abrir", command=self.open_file)
        self.file_menu.add_command(label="Cerrar", command=self.close_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Guardar", command=self.save_file)
        self.file_menu.add_command(label="Guardar como", command=self.save_as_file)
    
        self.menu_bar.add_cascade(label="Archivo", menu=self.file_menu)
        
        self.options_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Opciones", menu=self.options_menu)
        
        self.lex_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Lexico", menu=self.lex_menu)
        self.syn_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Sintactico", menu=self.syn_menu)
        self.sem_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Semantico", menu=self.sem_menu)
        self.comp_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Compilar", menu=self.comp_menu, command=self.compilar)

        self.left_panel = tk.Frame(self, bg="lightgray")
        self.left_panel.grid(row=0, column=0, sticky="nsew")
        self.left_panel.grid_columnconfigure(0, weight=1)

        self.right_panel = tk.Frame(self, bg="lightblue")
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        self.right_panel.grid_columnconfigure(0, weight=1)

        self.bottom_panel = tk.Frame(self, bg="white")
        self.bottom_panel.grid(row=1, column=0, sticky="nsew")
        self.bottom_panel.grid_columnconfigure(0, weight=1)

        self.bottom_right = tk.Frame(self, bg="white")
        self.bottom_right.grid(row=1, column=1, sticky="nsew")
        self.bottom_right.grid_columnconfigure(0, weight=1)

        self.bottom_notebook = ttk.Notebook(self.bottom_panel, height=150)
        self.bottom_notebook.grid(row=0, column=0, sticky="nsew")
        self.bottom_notebook.pack(fill=tk.BOTH, expand=True)

        lex_error_tab = tk.Frame(self.bottom_notebook)
        syn_error_tab = tk.Frame(self.bottom_notebook)
        sem_error_tab = tk.Frame(self.bottom_notebook)
        result_tab = tk.Frame(self.bottom_notebook)
        hash_tab = tk.Frame(self.bottom_notebook)

        self.bottom_notebook.add(lex_error_tab, text="Errores Lexicos")
        self.bottom_notebook.add(syn_error_tab, text="Errores Sintacticos")
        self.bottom_notebook.add(sem_error_tab, text="Errores Semanticos")
        self.bottom_notebook.add(result_tab, text="Resultados")
        self.bottom_notebook.add(hash_tab, text="Hash Table")

        columns = ('Registro', 'Nombre', 'Tipo', 'Valor', 'Lineas')
        self.hash_table = ttk.Treeview(hash_tab, columns=columns, show='headings')
        
        self.hash_table.heading('Registro', text='Registro')
        self.hash_table.heading('Nombre', text='Nombre')
        self.hash_table.heading('Tipo', text='Tipo')
        self.hash_table.heading('Valor', text='Valor')
        self.hash_table.heading('Lineas', text='Lineas')

        # Definir el tamaño de las columnas
        self.hash_table.column('Registro', width=50)
        self.hash_table.column('Nombre', width=100)
        self.hash_table.column('Tipo', width=100)
        self.hash_table.column('Valor', width=100)
        self.hash_table.column('Lineas', width=200,  anchor='w', stretch=True)
        scrollbar_vertical = ttk.Scrollbar(hash_tab, orient=tk.VERTICAL, command=self.hash_table.yview)
        self.hash_table.configure(yscrollcommand=scrollbar_vertical.set)
        self.hash_table.pack(expand=1, fill='both')

        self.error_display = tk.Text(lex_error_tab, wrap="word", state="normal")
        self.error_display.pack(fill="both", expand=True)
        
        self.error_sintact = tk.Text(syn_error_tab, wrap="word", state="normal")
        self.error_sintact.pack(fill="both", expand=True)
        
        self.error_semant = tk.Text(sem_error_tab, wrap="word", state="normal")
        self.error_semant.pack(fill="both", expand=True)
        
        self.tabla_hash = tk.Text(sem_error_tab, wrap="word", state="normal")
        self.tabla_hash.pack(fill="both", expand=True)

        self.error_scrollbar = tk.Scrollbar(lex_error_tab, orient=tk.VERTICAL, command=self.error_display.yview)
        self.error_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)        
        self.error_display.config(yscrollcommand=self.error_scrollbar.set)
        
        self.error_scrollbar_sintact = tk.Scrollbar(syn_error_tab, orient=tk.VERTICAL, command=self.error_sintact.yview)
        self.error_scrollbar_sintact.pack(side=tk.RIGHT, fill=tk.Y)
        self.error_sintact.config (yscrollcommand=self.error_scrollbar_sintact.set)

        self.error_scrollbar_semantico = tk.Scrollbar(sem_error_tab, orient=tk.VERTICAL, command=self.tabla_hash.yview)
        self.error_scrollbar_semantico.pack(side=tk.RIGHT, fill=tk.Y)
        self.tabla_hash.config (yscrollcommand=self.error_scrollbar_semantico.set)
        
        self.editor_frame = tk.Frame(self.left_panel)
        self.editor_frame.grid(row=0, column=0, sticky="nsew")
        self.editor_frame.grid_columnconfigure(1, weight=1)
        self.editor_frame.grid_rowconfigure(0, weight=1)

        self.text_editor = tk.Text(self.editor_frame, bg="white", wrap="none", width=70)
        self.text_editor.grid(row=0, column=1, sticky="nsew")

        self.horizontal_scroll = tk.Scrollbar(self.editor_frame, orient=tk.HORIZONTAL, command=self.text_editor.xview)
        self.horizontal_scroll.grid(row=1, column=1, sticky="ew")
        self.text_editor.config(xscrollcommand=self.horizontal_scroll.set)

        self.vertical_scroll = tk.Scrollbar(self.editor_frame, orient=tk.VERTICAL, command=self.text_editor.yview)
        self.vertical_scroll.grid(row=0, column=2, sticky="ns")
        self.text_editor.config(yscrollcommand=self.vertical_scroll.set)

        self.line_number = tk.Text(self.editor_frame, width=4, padx=4, takefocus=0, border=0, background="lightgrey", state="disabled")
        self.line_number.grid(row=0, column=0, sticky="nsew")

        self.position_frame = tk.Frame(self.left_panel)
        self.position_frame.grid(row=1, column=0, sticky="ew")

        self.position_label = tk.Label(self.position_frame, text="Línea: 1, Columna: 0", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.position_label.grid(row=0, column=0, sticky="ew")

        self.notebook = ttk.Notebook(self.right_panel,height=400)
        self.notebook.grid(row=0, column=0, sticky="nsew")
        self.notebook.pack(fill=tk.BOTH, expand=True)

        tab1 = tk.Frame(self.notebook)
        tab2 = tk.Frame(self.notebook)
        tab3 = tk.Frame(self.notebook)
        tab4 = tk.Frame(self.notebook)
        tab5 = tk.Frame(self.notebook)

        self.notebook.add(tab1, text="Lexico")
        self.notebook.add(tab2, text="Sintactico")
        self.notebook.add(tab3, text="Semantico")
        #self.notebook.add(tab4, text="Semantico")
        self.notebook.add(tab5, text="Codigo Intermedio")

        self.token_display = tk.Text(tab1, wrap="word", width=80)
        self.token_display.pack(fill="both", expand=True)
        
        self.sintact_display = tk.Text(tab2,wrap="word",width=80)
        self.sintact_display.pack(fill="both", expand=True)
        
        # Treeview para el árbol sintáctico
        self.arbol_display = ttk.Treeview(tab3)
        self.arbol_display.pack(fill="both", expand=True)

        # Barra de desplazamiento para la área de visualización de tokens
        self.token_scrollbar = tk.Scrollbar(tab1, orient=tk.VERTICAL, command=self.token_display.yview)
        self.sintact_scrollbar = tk.Scrollbar(tab2, orient=tk.VERTICAL, command=self.sintact_display.yview)
        
        self.token_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sintact_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.token_display.config(yscrollcommand=self.token_scrollbar.set)
        self.sintact_display.config(yscrollcommand=self.sintact_scrollbar.set)

        button_container = tk.Frame(self.bottom_right, bg="white", width=40)
        button_container.pack(fill=tk.BOTH, expand=True)

        abrir_img= Image.open("abrir.png")
        guardar_img= Image.open("guardar.png")
        guardarcomo_img= Image.open("guardarcomo.png")
        cerrar_img=Image.open("cerrar.png")
        compilar_img= Image.open("compilar.png")

        ancho=30
        alto= 30

        abrir_img= abrir_img.resize((ancho,alto ))
        guardar_img= guardar_img.resize((ancho, alto))
        guardarcomo_img= guardarcomo_img.resize((ancho, alto))
        cerrar_img= cerrar_img.resize((ancho, alto))
        compilar_img = compilar_img.resize((ancho,alto))

        self.open_img = ImageTk.PhotoImage(abrir_img)
        self.save_img = ImageTk.PhotoImage(guardar_img)
        self.save_as_img = ImageTk.PhotoImage(guardarcomo_img)
        self.close_img = ImageTk.PhotoImage(cerrar_img)
        self.compilar_img = ImageTk.PhotoImage(compilar_img)

        self.button1 = tk.Button(button_container, image=self.open_img, command=self.open_file)
        self.button1.grid(row=0, column=0, padx=5, pady=5, sticky="ew", columnspan=2)

        self.button2 = tk.Button(button_container, image=self.save_img, command=self.save_file)
        self.button2.grid(row=0, column=2, padx=5, pady=5, sticky="ew", columnspan=2)

        self.button3 = tk.Button(button_container, image=self.save_as_img, command=self.save_as_file)
        self.button3.grid(row=0, column=4, padx=5, pady=5, sticky="ew", columnspan=2)

        self.button4 = tk.Button(button_container, image=self.close_img, command=self.close_file)
        self.button4.grid(row=0, column=6, padx=5, pady=5, sticky="ew", columnspan=2)
        
        self.button9 = tk.Button(button_container, image=self.compilar_img, command=self.compilar)
        self.button9.grid(row=0, column=8, padx=5, pady=5, sticky="ew", columnspan=2)

        self.label5 = tk.Label(button_container, text="Abrir")
        self.label5.grid(row=1, column=0, padx=5, pady=5, sticky="ew", columnspan=2)

        self.label6 = tk.Label(button_container, text="Guardar")
        self.label6.grid(row=1, column=2, padx=5, pady=5, sticky="ew", columnspan=2)

        self.label7 = tk.Label(button_container, text="Guardar como")
        self.label7.grid(row=1, column=4, padx=5, pady=5, sticky="ew", columnspan=2)

        self.label8 = tk.Label(button_container, text="Cerrar")
        self.label8.grid(row=1, column=6, padx=5, pady=5, sticky="ew", columnspan=2)

        self.label9 = tk.Label(button_container, text="Compilar")
        self.label9.grid(row=1, column=8, padx=5, pady=5, sticky="ew", columnspan=2)


        self.text_editor.bind("<KeyRelease>", lambda event: (self.update_position_label(), self.update_line_number(), self.on_editor_scroll(), self.highlight_tokens()))
        self.text_editor.bind("<ButtonRelease>", lambda event: (self.update_position_label(), self.update_line_number(), self.on_editor_scroll(), self.highlight_tokens()))
        self.text_editor.bind("<FocusIn>", lambda event: (self.update_position_label(), self.update_line_number(), self.on_editor_scroll(), self.highlight_tokens()))
        self.text_editor.bind("<MouseWheel>", lambda event: (self.update_position_label(), self.update_line_number(), self.on_editor_scroll(), self.highlight_tokens()))
        self.text_editor.bind("<Configure>", lambda event: (self.update_position_label(), self.update_line_number(), self.on_editor_scroll(), self.highlight_tokens()))
        self.bind("<Configure>", self.on_window_configure)

        # Configura las etiquetas para resaltar los tokens
        self.text_editor.tag_configure("PALABRA_RESERVADA", foreground="dark orange")
        self.text_editor.tag_configure("OPERADOR_RELACIONAL", foreground="deep pink")
        self.text_editor.tag_configure("OPERADOR_LOGICO", foreground="light sea green")
        self.text_editor.tag_configure("OPERADOR_ARITMETICO", foreground="violet red")
        self.text_editor.tag_configure("NUMERO", foreground="blue")
        self.text_editor.tag_configure("ID", foreground="purple")
        self.text_editor.tag_configure("COMENTARIO", foreground="black")
        self.text_editor.tag_configure("ERROR", foreground="red")
        self.text_editor.tag_configure("SIMBOLO", foreground="cyan4")
        self.text_editor.tag_configure("ASIGNACION", foreground="maroon")
    
        self.vertical_scroll.bind("<B1-Motion>", self.update_line_numbers_with_scroll)
        self.vertical_scroll.bind("<ButtonRelease-1>", self.update_line_numbers_with_scroll)

        self.file_path = None



    def load_symbol_table(self):
        try:
            self.hash_table.delete(*self.hash_table.get_children())  # Limpiar el Treeview

            with open('tabla_simbolos.json', 'r') as file:
                entries = json.load(file)  # Cargar el contenido como una lista

                for entry in entries:
                    registro = entry['Registro']
                    nombre = entry['Nombre']
                    tipo = entry['Tipo']
                    valor = entry['Valor']
                    lineas = entry['Linea']  # Suponiendo que esto ya es una lista

                # Verificar el contenido de las líneas para depuración
                    print(f"Líneas procesadas para {nombre}: {lineas}")

                # Insertar en el Treeview
                    self.hash_table.insert('', 'end', values=(registro, nombre, tipo, valor, ", ".join(map(str, lineas))))

        except FileNotFoundError:
            print("El archivo 'tabla_simbolos.json' no fue encontrado.")
        except json.JSONDecodeError:
            print("Error al decodificar el archivo JSON.")
        except Exception as e:
            print(f"Ocurrió un error al cargar la tabla de símbolos: {e}")

    def analisis_lexico(self):
        text = self.text_editor.get(1.0, tk.END)
        lexer = Lexer(text)
        while True:
            token = lexer.get_next_token()  # Obtén el siguiente token
            if token.token_type == 'EOF':
                break
            # Aquí maneja los tokens según tus necesidades
            print(f'Tipo: {token.token_type}, Valor: {token.value}, Línea: {token.line}, Columna: {token.column}')

    def on_window_configure(self, event=None):
        self.left_panel.grid_propagate(False)
        self.right_panel.grid_propagate(False)
        self.bottom_panel.grid_propagate(False)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                content = file.read()
            self.text_editor.delete(1.0, tk.END)
            self.text_editor.insert(1.0, content)
            self.update_position_label()
            self.update_line_number()
            self.file_path = file_path

    def close_file(self):
        self.text_editor.delete(1.0, tk.END)
        self.file_path = None

    def save_file(self):
        if self.file_path:
            content = self.text_editor.get(1.0, tk.END)
            with open(self.file_path, "w") as file:
                file.write(content)
        else:
            self.save_as_file()

    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            content = self.text_editor.get(1.0, tk.END)
            with open(file_path, "w") as file:
                file.write(content)
            self.file_path = file_path
            
    def compilar(self):
        input_file = self.file_path
        self.save_file()
        try:
            result = subprocess.run(
                ['python', 'sintaxis.py', input_file],
                check=True,
                text=True,
                capture_output=True
            )
            lexico = subprocess.run(
                ['python', 'sintactico.py', input_file],
                check=True,
                text=True,
                capture_output=True
            )

        # Limpiar áreas antes de mostrar nuevos resultados
            self.sintact_display.delete("1.0", tk.END)
            self.arbol_display.delete(*self.arbol_display.get_children())  # Limpiar el Treeview
            self.error_sintact.delete("1.0", tk.END)
            self.tabla_hash.delete("1.0", tk.END)
            self.error_semant.delete("1.0",tk.END)

        # Mostrar información de tokens y árbol sintáctico si es necesario
            with open('token_info.txt', 'r') as file:
                content = file.read()
                self.sintact_display.insert(tk.END, content)

            #with open('ast_info.txt', 'r', encoding='utf-8') as arbol:
            #   lines = arbol.readlines()
        
            # Crear el árbol en el Treeview
            self.crear_arbol()
            self.load_symbol_table()

        # Mostrar errores sintácticos encontrados
            error_messages = result.stdout.splitlines()
            for error_message in error_messages:
                if error_message.startswith("SEMANTICO:"):
                    # Quitar el prefijo "SEMANTICO: " del mensaje
                    cleaned_message = error_message.replace("SEMANTICO: ", "")
                    self.error_semant.insert(tk.END, cleaned_message + "\n")
                else: 
                    self.error_sintact.insert(tk.END, error_message + "\n")
            
            

        except subprocess.CalledProcessError as e:
            # Manejar errores durante la ejecución del analizador sintáctico
            error_message = f"Error ejecutando analizador sintáctico: {e}"
            print(error_message)
            # Podrías agregar lógica para mostrar este mensaje en la interfaz de usuario
        

    def crear_arbol(self):
        try:
            # Verificar si el archivo existe y no está vacío
            if not os.path.exists('ast_info.pkl') or os.stat('ast_info.pkl').st_size == 0:
                raise EOFError("El archivo 'ast_info.pkl' está vacío o no fue encontrado.")
            
            with open('ast_info.pkl', 'rb') as file:  # Abrir el archivo en modo binario
                root_node = pickle.load(file)  # Deserializa el objeto

            # Insertar el árbol en el Treeview
            if root_node:
                self.build_tree('', root_node) 
        except FileNotFoundError:
            print("Archivo 'ast_info.pkl' no encontrado.")
        except EOFError as e:
            print(f"Error al leer el archivo: {e}")
        except Exception as e:
            print(f"Error inesperado: {e}")
            raise



    def build_tree(self, parent, node):
        node_name = str(node.name)
        additional_text = f" (Tipo: {getattr(node, 'var_type', 'desconocido')}, Valor:{getattr(node, 'value', 'desconocido')} )"
        item_id = self.arbol_display.insert(parent, 'end', text=node_name + additional_text)
        self.arbol_display.item(item_id, open=True)  # Expandir el nodo actual
        for child in node.children:
            self.build_tree(item_id, child) 
        

    def update_position_label(self, event=None):
        cursor_pos = self.text_editor.index(tk.INSERT)
        line, column = cursor_pos.split('.')
        self.position_label.config(text=f"Línea: {line}, Columna: {column}")

    def update_line_number(self, event=None):
        lines = self.text_editor.get(1.0, "end").count('\n')
        self.line_number.config(state="normal")
        self.line_number.delete(1.0, "end")
        self.line_number.insert("end", '\n'.join(str(i) for i in range(1, lines + 1)))
        self.line_number.config(state="disabled")

    def on_editor_scroll(self, event=None):
        yview = self.text_editor.yview()
        self.line_number.yview_moveto(yview[0])

    def update_line_numbers_with_scroll(self, event):
        # Obtener la fracción de la posición de la barra de desplazamiento
        fraction = self.vertical_scroll.get()
        # Configurar la posición de la barra de números de línea según la fracción
        self.line_number.yview_moveto(fraction[0])

    def highlight_tokens(self, event=None):
        # Obtener el texto completo del editor
        text = self.text_editor.get("1.0", tk.END)

        # Limpiar cualquier resaltado anterior
        for tag_name in ["PALABRA_RESERVADA", "OPERADOR_ARITMETICO","OPERADOR_LOGICO","OPERADOR_RELACIONAL", "NUMERO", "ID", "COMENTARIO", "ERROR", "ASIGNACION", "SIMBOLO"]:
            self.text_editor.tag_remove(tag_name, "1.0", tk.END)  # Configurar todos los tags para que el texto sea negro

        # Instanciar un objeto Lexer
        lexer = Lexer(text)
        tokens = []
        errors = []

        # Resaltar los tokens
        in_comment = False
        while True:
            token = lexer.get_next_token()
            if token.token_type == 'EOF':
                break
            
            if token.token_type == 'COMENTARIO':
                if token.value.startswith("/*"):
                    in_comment = True
                
                if token.value.endswith("*/"):
                    in_comment = False
                if in_comment:
                    tokens.append(token)
                    continue

            if token.token_type=='ERROR':
                errors.append(token)
            else:
                tokens.append(token)

            start_line = token.line 
            start_column = token.column - 1  # Ajustar la columna inicial
            end_line = token.line
            end_column = start_column + len(str(token.value))

            # Agregar etiqueta de resaltado al token
            start_pos = f"{start_line}.{start_column}"
            end_pos = f"{end_line}.{end_column}"
            tag_name = self.get_tag_name(token.token_type)
            print("Tipo: " + tag_name)
            self.text_editor.tag_add(tag_name, start_pos, end_pos)

        self.mostrar_errors(errors)
        self.mostrar_tokens(tokens)

    
    def mostrar_errors(self, errors):
        self.error_display.delete("1.0", tk.END)

        # Mostrar los tokens de error en el widget de errores léxicos
        for token in errors:
            token_info = f"Tipo: {token.token_type}, Valor: {token.value}, Línea: {token.line}, Columna: {token.column-1}\n"
            self.error_display.insert(tk.END, token_info)


    def mostrar_tokens(self, tokens):
        self.token_display.delete("1.0", tk.END)

        for token in tokens:
            token_info = f"Tipo: {token.token_type}, Valor: {token.value}, Línea: {token.line}, Columna: {token.column-1}\n"
            self.token_display.insert(tk.END, token_info)


    def get_tag_name(self, token_type):
        # Devuelve el nombre de la etiqueta para resaltar el token
        tag_names = {
            "PALABRA_RESERVADA": "PALABRA_RESERVADA",
            "OPERADOR_RELACIONAL": "OPERADOR_RELACIONAL",
            "OPERADOR_LOGICO": "OPERADOR_LOGICO",
            "OPERADOR_ARITMETICO":"OPERADOR_ARITMETICO",
            "NUMERO": "NUMERO",
            "ERROR" : "ERROR",
            "ASIGNACION": "ASIGNACION",
            "SIMBOLO": "SIMBOLO",
            "ID": "ID",
            "COMENTARIO": "COMENTARIO"
        }
        return tag_names.get(token_type, "DEFAULT")


if __name__ == "__main__":
    ide = IDE()
    ide.mainloop()
