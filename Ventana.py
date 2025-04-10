import ply.lex as lex
import ply.yacc as yacc
from tkinter import *
from tkinter import filedialog,scrolledtext, ttk, messagebox
import tkinter.font as tkFont
import AnalizadorLexico as AL
from AnalizadorLexico import limpiar_errores_lex
import AnalizadorSintactico as AS
from AnalizadorSintactico import limpiar_errores



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
        self.text_editor = scrolledtext.ScrolledText(self.editor_frame, wrap=WORD)
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

        # Consola de salida
        self.console_frame = ttk.Frame(self, width=30)
        self.console_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.output_console = scrolledtext.ScrolledText(self.console_frame, wrap=WORD)
        self.output_console.pack(expand=True, fill="both")

        # Asociar eventos
        self.text_editor.bind("<KeyRelease>", self.update_line_numbers)
        self.text_editor.bind("<MouseWheel>", self.update_line_numbers)
        self.text_editor.bind("<Button-4>", self.update_line_numbers)
        self.text_editor.bind("<Button-5>", self.update_line_numbers)
        self.text_editor.bind("<Configure>", self.update_line_numbers)
        
        # Configuración del tag antes de usarlo
        self.text_editor.tag_configure('reservadas', foreground='blue')
        self.text_editor.bind("<KeyRelease>", self.update_line_numbers_and_highlight)

    def update_line_numbers_and_highlight(self, event=None):
        self.update_line_numbers()
        # self.resaltar_palabras_reservadas()

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
         # Obtiene la fuente actual del editor de texto
        font_str = app.text_editor.cget("font")
        # Crea un objeto de fuente Tkinter a partir de la cadena de la fuente
        font = tkFont.Font(font=font_str)
        # Incrementa el tamaño de la fuente
        font.configure(size=font.actual()["size"] + 2)
        # Aplica la nueva fuente al editor de texto
        app.text_editor.config(font=font)
        app.line_numbers_text.config(font=font)
        app.output_console.config(font=font)
        
        self.text_editor.config(height=1, width=1)
        self.line_numbers_text.config(height=1, width=4)
        self.console_frame.config(width=30)
        self.output_console.config(height=0.1, width=1)
        

    def tamañoMenos(self):
         # Obtiene la fuente actual del editor de texto
        font_str = app.text_editor.cget("font")
        # Crea un objeto de fuente Tkinter a partir de la cadena de la fuente
        font = tkFont.Font(font=font_str)
        # Incrementa el tamaño de la fuente
        font.configure(size=font.actual()["size"] - 2)
        # Aplica la nueva fuente al editor de texto
        app.text_editor.config(font=font)
        app.line_numbers_text.config(font=font)
        app.output_console.config(font=font)
        
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
        lin = self.text_editor.get(1.0, "end-1c").count("\n")+1
        # Limpia la lista de errores antes de cada compilación
        limpiar_errores_lex()
        # Limpiar la salida de consola
        self.output_console.delete(1.0, END)

        # Obtiene todo el código del editor
        codigo = self.text_editor.get("1.0", END)

        # Realiza la compilación utilizando el analizador léxico
        global resultados
        resultados = AL.analisis(codigo)

        # Llama a update_line_numbers y pasa la lista de errores léxicos
        self.update_line_numbers()

        # Mostrar los errores léxicos en la consola de salida
        errores_lexicos = AL.errores_Desc
        for error in errores_lexicos:
            self.output_console.insert(END, error + "\n")

        # # Análisis Sintáctico
        limpiar_errores()
        global resultadosSintactico
        resultadosSintactico = AS.test_parser(codigo)

        # Imprimir resultados sintácticos en la consola de Python para depuración
        print("Resultado del análisis sintáctico:", resultadosSintactico)

        # Mostrar los errores sintácticos en la consola de salida
        errores_Sinc_Desc = AS.errores_Sinc_Desc
        for error in errores_Sinc_Desc:
            self.output_console.insert(END, error + "\n")

        # # Mostrar los errores Semanticos en la consola de salida
        # errores_Sem_Desc = AS.errores_Sem_Desc
        # for error in errores_Sem_Desc:
        #     self.output_console.insert(END, error + "\n")


if __name__ == "__main__":
    app = Compilador()
    app.mainloop()

