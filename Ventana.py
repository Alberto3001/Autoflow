import ply.lex as lex
import ply.yacc as yacc
from tkinter import *
from tkinter import filedialog,scrolledtext, ttk, messagebox
import tkinter.font as tkFont
import AnalizadorLexico as AL
from AnalizadorLexico import limpiar_errores_lex
import AnalizadorSintactico as AS
from AnalizadorSintactico import limpiar_errores
import re




resultados = []
resultadosSintactico = [] 

class VentanaTokens(Tk):
    def __init__(self):
        super().__init__()
        self.centrar_ventana1(400, 400)
        self.title("Ventana Secundaria")

        # Crear Treeview
        self.tree = ttk.Treeview(self)
        self.tree["columns"] = ("Lexema", "Token", "Linea", "Columna")

        # Configurar columnas
        self.tree.column("#0", width=0, stretch=False)  # columna de índice
        self.tree.column("Lexema", anchor='center', width=100)
        self.tree.column("Token", anchor='center', width=100)
        self.tree.column("Linea", anchor='center', width=100)
        self.tree.column("Columna", anchor='center', width=100)

        # Encabezados de columnas
        self.tree.heading("#0", text="", anchor='w')
        self.tree.heading("Lexema", text="Lexema", anchor='center')
        self.tree.heading("Token", text="Token", anchor='center')
        self.tree.heading("Linea", text="Linea", anchor='center')
        self.tree.heading("Columna", text="Columna", anchor='center')

        # Insertar datos
        global resultados
        for resultado in resultados:
            self.tree.insert("", "end", text="1", values=(resultado[0], resultado[1], resultado[2], resultado[3]))

        # Añadir Treeview a la ventana
        self.tree.pack(expand=True, fill='both')

    def centrar_ventana1(self, ancho, alto):
        # Obtener las dimensiones de la pantalla
        pantalla_ancho = self.winfo_screenwidth()
        pantalla_alto = self.winfo_screenheight()

        # Calcular la posición x e y para centrar la ventana
        x = (pantalla_ancho - ancho) // 2
        y = (pantalla_alto - alto) // 2

        # Establecer las dimensiones de la ventana y posicionarla
        self.geometry(f'{ancho}x{alto}+{x}+{y}')


class Compilador(Tk):
    contadorLinea = 0

    def __init__(self):
        super().__init__()
        self.centrar_ventana(800, 600)
        limpiar_errores_lex()
        self.title("IDE AutoFLow")
        self.filename = None  # Variable para almacenar el nombre del archivo actual
        self._error_link_id_counter = 0
        self.create_widgets()

        # Palabras reservadas principales del lenguaje AutoFlow
        base_font = tkFont.Font(font=self.text_editor['font'])
        italic_font = tkFont.Font(family=base_font.actual('family'), size=base_font.actual('size'), slant="italic")

        keywords_primary_color = 'blue'
        self.text_editor.tag_configure('AUTOMATON', foreground=keywords_primary_color)
        self.text_editor.tag_configure('TYPE', foreground=keywords_primary_color)
        self.text_editor.tag_configure('ALPHABET', foreground=keywords_primary_color)
        self.text_editor.tag_configure('STATES', foreground=keywords_primary_color)
        self.text_editor.tag_configure('INITIAL', foreground=keywords_primary_color)
        self.text_editor.tag_configure('ACCEPT', foreground=keywords_primary_color)
        self.text_editor.tag_configure('TRANSITIONS', foreground=keywords_primary_color)

        # Palabras reservadas para tipos de autómatas y propiedades específicas
        keywords_secondary_color = 'darkgreen'
        self.text_editor.tag_configure('DFA', foreground=keywords_secondary_color)
        self.text_editor.tag_configure('NFA', foreground=keywords_secondary_color)
        self.text_editor.tag_configure('PDA', foreground=keywords_secondary_color)
        self.text_editor.tag_configure('TM', foreground=keywords_secondary_color)
        self.text_editor.tag_configure('STACK_ALPHABET', foreground='teal')
        self.text_editor.tag_configure('STACK_START', foreground='teal')
        self.text_editor.tag_configure('TAPE_ALPHABET', foreground='purple')
        self.text_editor.tag_configure('BLANK', foreground='purple')

        # Palabras reservadas para atributos de transición
        attributes_color = 'orangered'
        self.text_editor.tag_configure('INPUT', foreground=attributes_color)
        self.text_editor.tag_configure('POP', foreground=attributes_color)
        self.text_editor.tag_configure('PUSH', foreground=attributes_color)
        self.text_editor.tag_configure('READ', foreground=attributes_color)
        self.text_editor.tag_configure('WRITE', foreground=attributes_color)
        self.text_editor.tag_configure('MOVE', foreground=attributes_color)
        self.text_editor.tag_configure('LEFT', foreground=attributes_color)
        self.text_editor.tag_configure('RIGHT', foreground=attributes_color)
        self.text_editor.tag_configure('STAY', foreground=attributes_color)

        # Otros tipos de tokens
        self.text_editor.tag_configure('IDENTIFICADOR', foreground='black')
        self.text_editor.tag_configure('SIMBOLO', foreground='maroon') # Para símbolos como 'a', '0' en alfabetos
        self.text_editor.tag_configure('EPSILON', foreground='saddlebrown', font=italic_font)

        # Operadores y delimitadores
        operators_color = 'darkblue'
        self.text_editor.tag_configure('ASIGNACION', foreground=operators_color)
        self.text_editor.tag_configure('TRANSICION', foreground=operators_color)
        self.text_editor.tag_configure('LLAVE_A', foreground=operators_color)
        self.text_editor.tag_configure('LLAVE_C', foreground=operators_color)
        self.text_editor.tag_configure('CORCHETE_A', foreground=operators_color)
        self.text_editor.tag_configure('CORCHETE_B', foreground=operators_color)
        self.text_editor.tag_configure('COMA', foreground=operators_color)
        self.text_editor.tag_configure('PUNTOCOMA', foreground=operators_color)

        # Comentarios
        self.text_editor.tag_configure('COMENTARIO_LINEA', foreground='green', font=italic_font)
        self.text_editor.tag_configure('COMENTARIO_BLOQUE', foreground='green', font=italic_font)
        
        # Lista de todas las etiquetas de sintaxis para facilitar su limpieza
        self.syntax_tags = [
            'AUTOMATON', 'TYPE', 'ALPHABET', 'STATES', 'INITIAL', 'ACCEPT', 'TRANSITIONS',
            'DFA', 'NFA', 'PDA', 'TM', 'STACK_ALPHABET', 'STACK_START', 'TAPE_ALPHABET', 'BLANK',
            'INPUT', 'POP', 'PUSH', 'READ', 'WRITE', 'MOVE', 'LEFT', 'RIGHT', 'STAY',
            'IDENTIFICADOR', 'SIMBOLO', 'EPSILON',
            'ASIGNACION', 'TRANSICION', 'LLAVE_A', 'LLAVE_C', 'CORCHETE_A', 'CORCHETE_B',
            'COMA', 'PUNTOCOMA',
            'COMENTARIO_LINEA', 'COMENTARIO_BLOQUE'
        ]
        # Llama a aplicar_resaltado_sintaxis después de que la ventana esté lista y el texto se modifique
        self.text_editor.bind("<KeyRelease>", self.on_key_release)

    def on_key_release(self, event=None):
        self.update_line_numbers(event)
        # Usamos after_idle para asegurar que el resaltado se haga después de que Tkinter procese el evento
        self.after_idle(self.aplicar_resaltado_sintaxis)


    def aplicar_resaltado_sintaxis(self, event=None):
        # Remover todas las etiquetas de resaltado previas
        for tag in self.syntax_tags:
            self.text_editor.tag_remove(tag, '1.0', END)

        codigo = self.text_editor.get('1.0', END + '-1c')
        for match in re.finditer(r'//.*', codigo):
            start = match.start()
            end = match.end()
            linea = codigo.count('\n', 0, start) + 1
            col_inicio = start - (codigo.rfind('\n', 0, start) + 1 if linea > 1 else 0)
            col_fin = col_inicio + (end - start)
            self.text_editor.tag_add('COMENTARIO_LINEA', f"{linea}.{col_inicio}", f"{linea}.{col_fin}")

        # --- Resaltado de comentarios de bloque ---
        for match in re.finditer(r'/\*(.|\n)*?\*/', codigo):
            start = match.start()
            end = match.end()
            linea_inicio = codigo.count('\n', 0, start) + 1
            col_inicio = start - (codigo.rfind('\n', 0, start) + 1 if linea_inicio > 1 else 0)
            linea_fin = codigo.count('\n', 0, end) + 1
            col_fin = end - (codigo.rfind('\n', 0, end) + 1 if linea_fin > 1 else 0)
            if linea_inicio == linea_fin:
                self.text_editor.tag_add('COMENTARIO_BLOQUE', f"{linea_inicio}.{col_inicio}", f"{linea_fin}.{col_fin}")
            else:
                self.text_editor.tag_add('COMENTARIO_BLOQUE', f"{linea_inicio}.{col_inicio}", f"{linea_inicio}.end")
                for l in range(linea_inicio + 1, linea_fin):
                    self.text_editor.tag_add('COMENTARIO_BLOQUE', f"{l}.0", f"{l}.end")
                self.text_editor.tag_add('COMENTARIO_BLOQUE', f"{linea_fin}.0", f"{linea_fin}.{col_fin}")
            if not codigo.strip():
                return

        # Reiniciar y alimentar el lexer
        AL.lexer.input(codigo)
        AL.lexer.lineno = 1

        while True:
            tok = AL.lexer.token()
            if not tok:
                break # Fin de los tokens

            # Calcular la posición de inicio y fin para Tkinter Text
            # tok.lexpos es el índice de caracteres desde el inicio del texto
            # Necesitamos convertirlo a formato "linea.columna"
            
            # Una forma de obtener línea y columna desde lexpos:
            linea_inicio_abs = codigo.count('\n', 0, tok.lexpos) + 1
            col_inicio_abs = tok.lexpos - (codigo.rfind('\n', 0, tok.lexpos) + 1 if linea_inicio_abs > 1 else 0)
            
            start_index = f"{linea_inicio_abs}.{col_inicio_abs}"
            end_index = f"{linea_inicio_abs}.{col_inicio_abs + len(tok.value)}"

            token_type = tok.type
            if token_type in self.syntax_tags: # Aplicar solo si la etiqueta está definida
                self.text_editor.tag_add(token_type, start_index, end_index)
            # else: # Para depuración, si encuentras tokens sin etiqueta configurada
                # print(f"Token no resaltado: {tok.value} (Tipo: {tok.type}) en {start_index}")


    def centrar_ventana(self, ancho, alto):
        # Obtener las dimensiones de la pantalla
        pantalla_ancho = self.winfo_screenwidth()
        pantalla_alto = self.winfo_screenheight()

        # Calcular la posición x e y para centrar la ventana
        x = (pantalla_ancho - ancho) // 2
        y = (pantalla_alto - alto) // 2

        # Establecer las dimensiones de la ventana y posicionarla
        self.geometry(f'{ancho}x{alto}+{x}+{y}')


    def create_widgets(self):
        # Frame principal
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(expand=True, fill="both")

        # Frame para los botones
        self.buttons_frame = ttk.Frame(self.main_frame)
        self.buttons_frame.pack(side="top", fill="x")

        self.btn_nuevo = ttk.Button(self.buttons_frame, text="Nuevo", command=self.nuevo_archivo)
        self.btn_nuevo.pack(side="left", padx=5)
        self.btn_abrir = ttk.Button(self.buttons_frame, text="Abrir", command=self.abrir_archivo)
        self.btn_abrir.pack(side="left", padx=5)
        self.btn_guardar = ttk.Button(self.buttons_frame, text="Guardar", command=self.guardar_archivo)
        self.btn_guardar.pack(side="left", padx=5)
        self.btn_guardar_como = ttk.Button(self.buttons_frame, text="Guardar como", command=self.guardar_como_archivo)
        self.btn_guardar_como.pack(side="left", padx=5)
        self.btn_tamañoMas = ttk.Button(self.buttons_frame, text="+", command=self.tamañoMas) 
        self.btn_tamañoMas.pack(side="left", padx=5)
        self.btn_tamañoMenos = ttk.Button(self.buttons_frame, text="-", command=self.tamañoMenos) 
        self.btn_tamañoMenos.pack(side="left", padx=5)

        # Frame para el editor de código y los números de línea
        self.editor_frame = ttk.Frame(self.main_frame)
        self.editor_frame.pack(expand=True, fill="both")

        # Editor de código
        self.text_editor = scrolledtext.ScrolledText(self.editor_frame, wrap=WORD, undo=True)
        self.text_editor.pack(expand=True, fill="both", side="right")

        # Hacer y Reahcer
        self.text_editor.bind("<Control-z>", self.deshacer_accion)
        self.text_editor.bind("<Control-y>", self.rehacer_accion)
        self.text_editor.bind("<Control-Shift-KeyPress-Z>", self.rehacer_accion)

        # Frame para los números de línea
        self.line_numbers_frame = ttk.Frame(self.editor_frame, width=30)
        self.line_numbers_frame.pack(side="left", fill="y")

        self.line_numbers_text = Text(self.line_numbers_frame, width=4, padx=5, pady=5, wrap="none", state="disabled")
        self.line_numbers_text.pack(side="left", fill="y", expand=True)

        # Botones para compilar y ejecutar
        self.buttons_compiler_panel = ttk.Frame(self.main_frame)
        self.buttons_compiler_panel.pack(side="bottom", fill="x")

        self.btn_compilar = ttk.Button(self.buttons_compiler_panel, text="Compilar", command=self.compilar)
        self.btn_compilar.pack(side="left", padx=5)
        self.btn_tokens = ttk.Button(self.buttons_compiler_panel, text="Tokens", command=self.Tokens)
        self.btn_tokens.pack(side="left", padx=5)

        # Consola de salida
        self.console_frame = ttk.Frame(self, width=30)
        self.console_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.output_console = scrolledtext.ScrolledText(self.console_frame, wrap=WORD)
        self.output_console.pack(expand=True, fill="both")

        self.output_console.tag_configure("error_link_style", foreground="blue", underline=True)

        # Opcional: estilo para encabezados de sección de error
        self.output_console.tag_configure("header_style", font=tkFont.Font(weight="bold"))

        #Mensaje de exito
        self.output_console.tag_configure("success_style", foreground="green")

        # Asociar eventos
        self.text_editor.bind("<KeyRelease>", self.update_line_numbers)
        self.text_editor.bind("<MouseWheel>", self.update_line_numbers)
        self.text_editor.bind("<Button-4>", self.update_line_numbers)
        self.text_editor.bind("<Button-5>", self.update_line_numbers)
        self.text_editor.bind("<Configure>", self.update_line_numbers)
        
        # Configuración del tag antes de usarlo
        self.text_editor.tag_configure('reservadas', foreground='blue')
        self.text_editor.bind("<KeyRelease>", self.update_line_numbers_and_highlight)

    def _navigate_to_error(self, target_line, target_col, event=None):
        """Navega el editor a la línea y columna especificadas."""
        if target_line != -1: # Asegurarse de que la línea es válida
            # Las columnas en mark_set y see son 0-indexed.
            # La columna que guardamos (de find_column o calculada) es 1-indexed.
            editor_col = max(0, target_col - 1) 
            
            self.text_editor.mark_set("insert", f"{target_line}.{editor_col}")
            self.text_editor.see(f"{target_line}.{editor_col}")
            self.text_editor.focus_set() # Poner el foco en el editor

            # Opcional: Resaltar temporalmente la línea del error en el editor
            line_start_index = f"{target_line}.0"
            line_end_index = f"{target_line}.end"
            self.text_editor.tag_add("line_error_highlight", line_start_index, line_end_index)
            self.text_editor.tag_configure("line_error_highlight", background="yellow")
            self.after(2000, lambda: self.text_editor.tag_remove("line_error_highlight", line_start_index, line_end_index))


    def update_line_numbers_and_highlight(self, event=None):
        self.update_line_numbers()
        # self.resaltar_palabras_reservadas()

    def deshacer_accion(self, event=None):
        try:
            self.text_editor.edit_undo()
        except TclError: # Ocurre si no hay nada que deshacer
            pass
        return "break" # Evita que el evento se propague más

    def rehacer_accion(self, event=None):
        try:
            self.text_editor.edit_redo()
        except TclError: # Ocurre si no hay nada que rehacer
            pass
        return "break" # Evita que el evento se propague más

    def nuevo_archivo(self):
        if self.text_editor.get("1.0", END).strip():
            if self.text_editor.edit_modified():
                respuesta = messagebox.askyesnocancel("Guardar", "¿Desea guardar el archivo antes de crear uno nuevo?")
                if respuesta:
                    if not self.guardar_como_archivo():
                        return  # Si el usuario cancela el diálogo de guardado, se detiene la ejecución
                elif respuesta is None:
                    return  # Si elige cancelar en el mensaje, se detiene la ejecución
        self.text_editor.delete(1.0, END)
        self.filename = None
        self.update_line_numbers()
        self.aplicar_resaltado_sintaxis()

    def guardar_como_archivo(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            with open(filename, "w") as file:
                content = self.text_editor.get(1.0, END)
                file.write(content)
            self.filename = filename
            self.text_editor.edit_modified(False)
            return True
        return False  # Devuelve False si el usuario cancela el diálogo de guardado

    def abrir_archivo(self):
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            with open(filename, "r") as file:
                content = file.read()
                self.text_editor.delete(1.0, END)
                self.text_editor.insert(1.0, content)
            self.filename = filename
        self.update_line_numbers()
        self.aplicar_resaltado_sintaxis()

    def guardar_archivo(self):
        if self.filename:
            with open(self.filename, "w") as file:
                content = self.text_editor.get(1.0, END)
                file.write(content)
            self.text_editor.edit_modified(False)
        else:
            self.guardar_como_archivo()
        
    def tamañoMas(self):
         # Obtiene la fuente actual del editor de texto
        font_str = self.text_editor.cget("font")
        # Crea un objeto de fuente Tkinter a partir de la cadena de la fuente
        font = tkFont.Font(font=font_str)
        # Incrementa el tamaño de la fuente
        font.configure(size=font.actual()["size"] + 2)
        # Aplica la nueva fuente al editor de texto
        self.text_editor.config(font=font)
        self.line_numbers_text.config(font=font)
        self.output_console.config(font=font)
        
        self.text_editor.config(height=1, width=1)
        self.line_numbers_text.config(height=1, width=4)
        self.console_frame.config(width=30)
        self.output_console.config(height=0.1, width=1)
        

    def tamañoMenos(self):
         # Obtiene la fuente actual del editor de texto
        font_str = self.text_editor.cget("font")
        # Crea un objeto de fuente Tkinter a partir de la cadena de la fuente
        font = tkFont.Font(font=font_str)
        # Incrementa el tamaño de la fuente
        font.configure(size=font.actual()["size"] - 2)
        # Aplica la nueva fuente al editor de texto
        self.text_editor.config(font=font)
        self.line_numbers_text.config(font=font)
        self.output_console.config(font=font)
        
        self.text_editor.config(height=1, width=1)
        self.line_numbers_text.config(height=1, width=2)
        self.output_console.config(height=0.1, width=1)

    def Tokens(self):
        app2 = VentanaTokens()
        app2.mainloop()

    def update_line_numbers(self, event=None):
        # Accede a lista_errores_lexicos a través de una instancia de Compilador
        error_line = AL.lista_errores_lexicos
        # Actualiza los números de línea en función del número de líneas en el editor
        lines = self.text_editor.get(1.0, "end-1c").count("\n")
        #AL.contador = self.text_editor.get(1.0, "end-1c").count("\n")+1
        #print(contador)
        self.line_numbers_text.config(state="normal")
        self.line_numbers_text.delete(1.0, "end")
        if not error_line:
            for line in range(1, lines + 2):
                self.line_numbers_text.insert("end", str(line) + "\n")
        else:
            for line in range(1, lines + 2):
                if line in error_line:
                    # Si la línea es la línea del error, establecer el color de fondo en rojo
                    self.line_numbers_text.insert("end", str(line) + "\n", 'error_line')
                else:
                    self.line_numbers_text.insert("end", str(line) + "\n")
        self.line_numbers_text.tag_configure('error_line', foreground='red')
        self.line_numbers_text.config(state="disabled")

        # Sincronizar los scrolls de los números de línea con el editor de código
        self.line_numbers_text.yview_moveto(self.text_editor.yview()[0])

    def compilar(self):
        self.output_console.config(state=NORMAL) # Habilitar para escribir
        self.output_console.delete(1.0, END)
        self._error_link_id_counter = 0 # Reiniciar contador para esta compilación

        codigo = self.text_editor.get("1.0", END + "-1c") # Corrección: END + "-1c" para evitar doble newline

        if not codigo.strip():
            self.output_console.insert(END, "No hay código para compilar.\n")
            self.output_console.config(state=DISABLED)
            return

        # --- Procesamiento de Errores Léxicos ---
        limpiar_errores_lex() # Limpia AL.errores_Desc y AL.lista_errores_lexicos
        AL.lexer.input(codigo)
        AL.lexer.lineno = 1

        global resultados
        resultados = []

        while True: # Forzar el recorrido del lexer para que se registren errores
            tok = AL.lexer.token()
            if not tok:
                break
            columna = tok.lexpos - codigo.rfind('\n', 0, tok.lexpos)
            resultados.append((tok.value, tok.type, tok.lineno, columna))

        errors_found = False

        lexical_errors_info = AL.errores_Desc # Ahora es una lista de diccionarios
        if lexical_errors_info:
            errors_found = True
            for error_info in lexical_errors_info:
                line = error_info['line']
                col = error_info['col']
                message = error_info['message']
                
                # Generar una etiqueta única para este error específico
                unique_link_tag = f"err_L{line}_C{col}_ID{self._error_link_id_counter}"
                self._error_link_id_counter += 1
                
                start_idx = self.output_console.index(END + "-1c") # Índice antes de insertar
                self.output_console.insert(END, message + "\n")
                end_idx = self.output_console.index(END + "-1c")   # Índice después de insertar

                self.output_console.tag_add(unique_link_tag, start_idx, end_idx)
                self.output_console.tag_add("error_link_style", start_idx, end_idx) # Aplicar estilo general

                # Vincular el evento de clic a esta etiqueta única
                self.output_console.tag_bind(
                    unique_link_tag, 
                    "<Button-1>", 
                    # Usar lambda para capturar los valores correctos de line y col
                    lambda event_data, l=line, c=col: self._navigate_to_error(l, c, event_data)
                )
                # Cambiar cursor al pasar sobre el enlace
                self.output_console.tag_bind(unique_link_tag, "<Enter>", lambda e: self.output_console.config(cursor="hand2"))
                self.output_console.tag_bind(unique_link_tag, "<Leave>", lambda e: self.output_console.config(cursor=""))

        self.update_line_numbers() # Para errores léxicos en los números de línea

        # --- Procesamiento de Errores Sintácticos ---
        limpiar_errores() # AS.limpiar_errores()
        # Es crucial resetear el lexer que usará el parser
        if hasattr(AS, 'al_lexer_instance') and AS.al_lexer_instance: # Si AS usa la instancia de AL
             AS.al_lexer_instance.lineno = 1
        elif hasattr(AL, 'lexer'): # Si no, y AS usa implícitamente AL.lexer
             AL.lexer.lineno = 1

        resultadosSintactico = AS.test_parser(codigo)
        syntax_errors_info = AS.errores_Sinc_Desc # Ahora es una lista de diccionarios

        if syntax_errors_info:
            errors_found = True
            for error_info in syntax_errors_info:
                line = error_info['line']
                col = error_info['col']
                message = error_info['message']

                unique_link_tag = f"err_L{line}_C{col}_ID{self._error_link_id_counter}"
                self._error_link_id_counter += 1

                start_idx = self.output_console.index(END + "-1c")
                self.output_console.insert(END, message + "\n")
                end_idx = self.output_console.index(END + "-1c")

                self.output_console.tag_add(unique_link_tag, start_idx, end_idx)
                self.output_console.tag_add("error_link_style", start_idx, end_idx)
                
                self.output_console.tag_bind(
                    unique_link_tag, 
                    "<Button-1>", 
                    lambda event_data, l=line, c=col: self._navigate_to_error(l, c, event_data)
                )
                self.output_console.tag_bind(unique_link_tag, "<Enter>", lambda e: self.output_console.config(cursor="hand2"))
                self.output_console.tag_bind(unique_link_tag, "<Leave>", lambda e: self.output_console.config(cursor=""))

        if not errors_found:
            self.output_console.insert(END, "¡Compilación exitosa!\n", "success_style")

        self.output_console.config(state=DISABLED) # Volver a solo lectura


if __name__ == "__main__":
    app = Compilador()
    app.mainloop()

