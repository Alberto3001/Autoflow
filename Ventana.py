import ply.lex as lex
import ply.yacc as yacc
from tkinter import *
from tkinter import filedialog,scrolledtext, ttk, messagebox
import tkinter.font as tkFont
import AnalizadorLexico as AL
from AnalizadorLexico import limpiar_errores_lex
import AnalizadorSintactico as AS
from AnalizadorSintactico import limpiar_errores
import tkinter as tk
import re
import AnalizadorSemantico as ASEM
from CodigoIntermedio import generar_tripletas_cuadruplas
from GeneradorCodigoObjeto import generar_ensamblador_emu8086, generar_pseudoensamblador
from guardar import guardar_y_abrir_codigo


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
        self.create_widgets()
        self.filename = None  # Variable para almacenar el nombre del archivo actual

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
        self.btn_codigo_intermedio = ttk.Button(self.buttons_compiler_panel, text="Código Intermedio", command=self.mostrar_codigo_intermedio, state="disabled")
        self.btn_codigo_intermedio.pack(side="left", padx=5)
        self.btn_generar_codigo_objeto = ttk.Button(self.buttons_compiler_panel, text="Generar Código Objeto", command=self.generar_codigo_objeto, state="disabled")
        self.btn_generar_codigo_objeto.pack(side="left", padx=5)

        # Consola de salida
        self.console_frame = ttk.Frame(self, width=30)
        self.console_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.output_console = scrolledtext.ScrolledText(self.console_frame, wrap=WORD)
        self.output_console.pack(expand=True, fill="both")

        # Configurar tags ANTES de usar los eventos
        self.configure_tags()

        # Asociar eventos
        self.text_editor.bind("<KeyRelease>", self.update_line_numbers_and_highlight)
        self.text_editor.bind("<MouseWheel>", self.update_line_numbers)
        self.text_editor.bind("<Button-4>", self.update_line_numbers)
        self.text_editor.bind("<Button-5>", self.update_line_numbers)
        self.text_editor.bind("<Configure>", self.update_line_numbers)

        # Agregar estos bindings para Ctrl+Z y Ctrl+Y
        self.text_editor.bind("<Control-z>", self.deshacer)
        self.text_editor.bind("<Control-y>", self.rehacer)

    def deshacer(self, event=None):
        """Deshacer la última acción"""
        try:
            self.text_editor.edit_undo()
            self.update_line_numbers_and_highlight()
            return "break"  # Previene que el evento se propague
        except TclError:  # Si no hay más acciones para deshacer
            return

    def rehacer(self, event=None):
        """Rehacer la última acción deshecha"""
        try:
            self.text_editor.edit_redo()
            self.update_line_numbers_and_highlight()
            return "break"  # Previene que el evento se propague
        except TclError:  # Si no hay más acciones para rehacer
            return

    def configure_tags(self):
        """Configurar todos los tags de una vez"""
        font_str = self.text_editor.cget("font")
        font = tkFont.Font(font=font_str)
        font_tuple = (font.actual()["family"], font.actual()["size"], "bold")
        self.text_editor.tag_configure('reservadas', foreground='blue', font=font_tuple)
        self.text_editor.tag_configure('error_lexico', background='yellow', underline=True)
        self.text_editor.tag_configure('tooltip', background='lightyellow')
        self.output_console.tag_configure("error_link_style", foreground="blue", underline=True)
        self.output_console.tag_configure("success_style", foreground="green")
        self.text_editor.tag_configure("line_error_highlight", background="yellow")

    def resaltar_palabras_reservadas(self):
        """Versión mejorada del resaltado de palabras reservadas"""
        # Limpia tags anteriores
        self.text_editor.tag_remove('reservadas', '1.0', END)
        self.text_editor.tag_remove('error_lexico', '1.0', END)
        self.text_editor.tag_remove('tooltip', '1.0', END)
        
        texto = self.text_editor.get('1.0', END)
        
        # Verificar que AL.palabras_reservadas existe y tiene contenido
        if not hasattr(AL, 'palabras_reservadas'):
            print("Warning: AL.palabras_reservadas no encontrado")
            return
            
        palabras_reservadas = AL.palabras_reservadas
        if not palabras_reservadas:
            print("Warning: AL.palabras_reservadas está vacío")
            return

        print(f"Palabras reservadas encontradas: {palabras_reservadas}")  # Debug

        # Método alternativo sin regex para buscar palabras reservadas
        for palabra in palabras_reservadas:
            # Convertir palabra a string en caso de que sea otro tipo
            palabra_str = str(palabra).lower()
            texto_lower = texto.lower()
            
            start_pos = 0
            while True:
                # Buscar la palabra en el texto
                pos = texto_lower.find(palabra_str, start_pos)
                if pos == -1:
                    break
                
                # Verificar que sea una palabra completa (no parte de otra palabra)
                es_palabra_completa = True
                
                # Verificar carácter anterior
                if pos > 0:
                    char_anterior = texto[pos - 1]
                    if char_anterior.isalnum() or char_anterior == '_':
                        es_palabra_completa = False
                
                # Verificar carácter siguiente
                if pos + len(palabra_str) < len(texto):
                    char_siguiente = texto[pos + len(palabra_str)]
                    if char_siguiente.isalnum() or char_siguiente == '_':
                        es_palabra_completa = False
                
                if es_palabra_completa:
                    # Convertir posición a índice de Tkinter
                    inicio_linea = texto[:pos].count('\n') + 1
                    inicio_col = pos - texto[:pos].rfind('\n') - 1 if '\n' in texto[:pos] else pos
                    
                    inicio_idx = f"{inicio_linea}.{inicio_col}"
                    fin_idx = f"{inicio_linea}.{inicio_col + len(palabra_str)}"
                    
                    # Aplicar el tag
                    self.text_editor.tag_add('reservadas', inicio_idx, fin_idx)
                    print(f"Resaltando '{palabra_str}' en {inicio_idx} - {fin_idx}")  # Debug
                
                start_pos = pos + 1

        # Resaltar errores léxicos
        if hasattr(AL, 'errores_Desc') and AL.errores_Desc:
            for error in AL.errores_Desc:
                if isinstance(error, dict) and 'line' in error and 'col' in error:
                    linea = error['line']
                    col = error['col']
                    idx = f"{linea}.{max(0, col-1)}"
                    end = f"{linea}.{col}"
                    self.text_editor.tag_add('error_lexico', idx, end)
                    
                    # Crear tooltip para errores
                    def crear_tooltip(mensaje):
                        return lambda e: self.mostrar_tooltip(e, mensaje)
                    
                    self.text_editor.tag_bind('error_lexico', '<Enter>', crear_tooltip(error.get('message', 'Error léxico')))
                    self.text_editor.tag_bind('error_lexico', '<Leave>', self.ocultar_tooltip)

    def mostrar_tooltip(self, event, mensaje):
        try:
            x = event.x_root + 20
            y = event.y_root + 10
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
            
            self.tooltip = tk.Toplevel(self)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{x}+{y}")
            label = tk.Label(self.tooltip, text=mensaje, background="lightyellow", relief='solid', borderwidth=1, font=("Arial", 9))
            label.pack()
        except Exception as e:
            print(f"Error mostrando tooltip: {e}")

    def ocultar_tooltip(self, event):
        try:
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()
                del self.tooltip
        except Exception as e:
            print(f"Error ocultando tooltip: {e}")

    def update_line_numbers_and_highlight(self, event=None):
        """Actualizar números de línea y resaltado"""
        # Usar after_idle para asegurar que se ejecute después de otras operaciones
        self.after_idle(self.update_line_numbers)
        self.after_idle(self.resaltar_palabras_reservadas)

    def _navigate_to_error(self, target_line, target_col, event=None):
        """Navega el editor a la línea y columna especificadas y resalta la línea."""
        print(f"Navegando a línea {target_line}, columna {target_col}")  # Debug
        if target_line != -1:
            # Asegurarse de que la línea sea visible
            self.text_editor.see(f"{target_line}.0")
            
            # Mover el cursor
            self.text_editor.mark_set("insert", f"{target_line}.{target_col}")
            
            # Dar foco al editor
            self.text_editor.focus_set()
            
            # Resaltar la línea
            line_start = f"{target_line}.0"
            line_end = f"{target_line}.end"
            
            # Remover resaltados anteriores
            self.text_editor.tag_remove("line_error_highlight", "1.0", END)
            
            # Aplicar nuevo resaltado
            self.text_editor.tag_add("line_error_highlight", line_start, line_end)
            
            # Remover el resaltado después de 2 segundos
            self.after(2000, lambda: self.text_editor.tag_remove("line_error_highlight", line_start, line_end))

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
        self.resaltar_palabras_reservadas()

    def guardar_archivo(self):
        if self.filename:
            with open(self.filename, "w") as file:
                content = self.text_editor.get(1.0, END)
                file.write(content)
            self.text_editor.edit_modified(False)
        else:
            self.guardar_como_archivo()
        
    def tamañoMas(self):
        font_str = self.text_editor.cget("font")
        font = tkFont.Font(font=font_str)
        font.configure(size=font.actual()["size"] + 2)
        self.text_editor.config(font=font)
        self.line_numbers_text.config(font=font)
        self.output_console.config(font=font)
        self.text_editor.config(height=1, width=1)
        self.line_numbers_text.config(height=1, width=4)
        self.console_frame.config(width=30)
        self.output_console.config(height=0.1, width=1)
        self.after_idle(self.configure_tags)

    def tamañoMenos(self):
        font_str = self.text_editor.cget("font")
        font = tkFont.Font(font=font_str)
        font.configure(size=font.actual()["size"] - 2)
        self.text_editor.config(font=font)
        self.line_numbers_text.config(font=font)
        self.output_console.config(font=font)
        self.text_editor.config(height=1, width=1)
        self.line_numbers_text.config(height=1, width=2)
        self.output_console.config(height=0.1, width=1)
        self.after_idle(self.configure_tags)

    def Tokens(self):
        app2 = VentanaTokens()
        app2.mainloop()

    def update_line_numbers(self, event=None):
        # Accede a lista_errores_lexicos a través de una instancia de Compilador
        error_line = AL.lista_errores_lexicos if hasattr(AL, 'lista_errores_lexicos') else []
        # Actualiza los números de línea en función del número de líneas en el editor
        lines = self.text_editor.get(1.0, "end-1c").count("\n")
        
        self.line_numbers_text.config(state="normal")
        self.line_numbers_text.delete(1.0, "end")
        
        for line in range(1, lines + 2):
            if line in error_line:
                # Si la línea es la línea del error, establecer el color de fondo en rojo
                self.line_numbers_text.insert("end", str(line) + "\n", 'error_line')
            else:
                self.line_numbers_text.insert("end", str(line) + "\n")
                
        self.line_numbers_text.tag_configure('error_line', foreground='red')
        self.line_numbers_text.config(state="disabled")

        # Sincronizar los scrolls de los números de línea con el editor de código
        try:
            self.line_numbers_text.yview_moveto(self.text_editor.yview()[0])
        except:
            pass

    def mostrar_errores_inteligentes(self):
        self.output_console.delete(1.0, END)
        
        errores_combinados = []
        
        # Errores léxicos
        if hasattr(AL, 'errores_Desc'):
            for error in AL.errores_Desc:
                if isinstance(error, dict):
                    error['tipo'] = 'léxico'
                    errores_combinados.append(error)
        
        # Errores sintácticos
        if hasattr(AS, 'errores_Sinc_Desc'):
            for error in AS.errores_Sinc_Desc:
                if isinstance(error, dict):
                    error['tipo'] = 'sintáctico'
                    errores_combinados.append(error)

        #Errores Semanticos
        if hasattr(self, 'errores_semanticos_detectados'):
            for error in self.errores_semanticos_detectados:
                if isinstance(error, dict):
                    error['tipo'] = 'semántico'
                    errores_combinados.append(error)
        
        # Ordenar por línea para mostrar en orden
        errores_combinados.sort(key=lambda x: x.get('line', 0))
        
        # Eliminar duplicados (errores en la misma línea)
        errores_filtrados = []
        lineas_vistas = set()
        
        for error in errores_combinados:
            linea = error.get('line', -1)
            mensaje = error.get('message', '')
            
            # Evitar mensajes duplicados
            if (linea, mensaje) not in lineas_vistas:
                errores_filtrados.append(error)
                lineas_vistas.add((linea, mensaje))
        
        # Mostrar errores filtrados
        if not errores_filtrados:
            self.output_console.insert(END, "Compilación exitosa. No se encontraron errores.\n", "success_style")
        else:
            for error in errores_filtrados:
                linea = error.get('line', -1)
                col = error.get('col', 0)
                mensaje = error.get('message', '')
                tipo = error.get('tipo', '')
                
                # Mostrar mensaje
                self.output_console.insert(END, f"Error {tipo}: {mensaje} ")
                
                # Agregar parte clickeable
                if linea != -1:
                    link_start_idx = self.output_console.index(END + "-1c")
                    self.output_console.insert(END, f"(Línea: {linea}, Columna: {col})\n")
                    link_end_idx = self.output_console.index(END + "-1c")
                    
                    self.output_console.tag_add("error_link_style", link_start_idx, link_end_idx)
                    self.output_console.tag_bind(
                        "error_link_style",
                        "<Button-1>", 
                        lambda e, l=linea, c=col: self._navigate_to_error(l, c)
                    )
                    
                    self.output_console.tag_bind(
                        "error_link_style",
                        "<Enter>", 
                        lambda e: self.output_console.config(cursor="hand2")
                    )
                    self.output_console.tag_bind(
                        "error_link_style",
                        "<Leave>", 
                        lambda e: self.output_console.config(cursor="")
                    )
                else:
                    self.output_console.insert(END, "\n") 
            
            # Mostrar un mensaje adicional si no se pudo completar el análisis
            if not resultadosSintactico:
                self.output_console.insert(END, "\nNo se pudo completar el análisis sintáctico debido a errores.\n")

    #Función para mostrar codigo intermedio
    def mostrar_codigo_intermedio(self):
        from VentanaCodigoIntermedio import VentanaCodigoIntermedio
        ventana = VentanaCodigoIntermedio(tripletas=getattr(self, "tripletas", []), cuadruplas=getattr(self, "cuadruplas", []))
        ventana.grab_set()

    def compilar(self):
        self.errores_semanticos_detectados = []
        lin = self.text_editor.get(1.0, "end-1c").count("\n")+1
        limpiar_errores_lex()
        limpiar_errores()  # Reiniciar también las variables de errores sintácticos
        self.output_console.delete(1.0, END)
        codigo = self.text_editor.get("1.0", END)
        
        # Análisis léxico
        global resultados
        resultados = AL.analisis(codigo)
        self.update_line_numbers()
        self.resaltar_palabras_reservadas()
        
        # Análisis sintáctico
        global resultadosSintactico
        lexer = AL.lexer
        lexer.lineno = 1
        resultadosSintactico = AS.test_parser(codigo, lexer=lexer)
        print("AST generado:", resultadosSintactico)

        # Recuperar errores semánticos
        if resultadosSintactico:
            self.errores_semanticos_detectados = ASEM.analizar_semantica(resultadosSintactico)
        
        # Imprimir resultados y errores para depuración
        print("Errores léxicos:", AL.errores_Desc)
        print("Errores sintácticos:", AS.errores_Sinc_Desc)
        
        # Usar la función mejorada para mostrar errores
        self.mostrar_errores_inteligentes()
        
        # Verificar explícitamente si hay errores
        if (hasattr(AL, 'errores_Desc') and AL.errores_Desc) or (hasattr(AS, 'errores_Sinc_Desc') and AS.errores_Sinc_Desc):
            # Hay errores, no mostrar "compilación exitosa" adicional
            if not resultadosSintactico:
                self.output_console.insert(END, "\nNo se pudo completar el análisis sintáctico debido a errores.\n")

        if resultadosSintactico and not self.errores_semanticos_detectados:
            tripletas, cuadruplas = generar_tripletas_cuadruplas(resultadosSintactico)
            self.tripletas = tripletas
            self.cuadruplas = cuadruplas
            self.btn_codigo_intermedio.config(state="normal")
            self.btn_generar_codigo_objeto.config(state="normal")
        else:
            self.btn_codigo_intermedio.config(state="disabled")
            self.btn_generar_codigo_objeto.config(state="disabled")

    def generar_codigo_objeto(self, nombre_automata="automata", tipo_automata="DFA"):
        """
        Genera y guarda automáticamente el código ensamblador (.asm) y pseudoensamblador (.txt),
        y los abre al finalizar.
        """
        if not hasattr(self, "cuadruplas") or not self.cuadruplas:
            messagebox.showerror("Error", "No hay cuádruplas generadas.")
            return
        # Ensamblador EMU8086
        asm_code = generar_ensamblador_emu8086(self.cuadruplas, nombre_automata, tipo_automata)
        guardar_y_abrir_codigo(asm_code, f"{nombre_automata}.asm")
        # Pseudoensamblador
        pseudo_code = generar_pseudoensamblador(self.cuadruplas)
        guardar_y_abrir_codigo(pseudo_code, f"{nombre_automata}_pseudo.txt")
        messagebox.showinfo("Éxito", "Código ensamblador y pseudoensamblador generados y abiertos.")

if __name__ == "__main__":
    app = Compilador()
    app.mainloop()