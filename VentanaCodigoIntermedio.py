import tkinter as tk
from tkinter import ttk
from tkinter import filedialog


class VentanaCodigoIntermedio(tk.Toplevel):
    def __init__(self, tripletas=None, cuadruplas=None):
        super().__init__()
        self.title("Código Intermedio")
        self.geometry("600x400")
        self.centrar_ventana(600, 400)

        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill="both")

        # Pestaña Tripletas
        frame_tripletas = ttk.Frame(notebook)
        notebook.add(frame_tripletas, text="Tripletas")

        # Columnas numeradas como en el ejemplo
        cols_tripletas = ("0", "1", "2", "3", "4")
        self.tree_tripletas = ttk.Treeview(frame_tripletas, columns=cols_tripletas, show="headings")
        for i, col in enumerate(cols_tripletas):
            self.tree_tripletas.heading(col, text=col)
            self.tree_tripletas.column(col, width=100, anchor="center")
        self.tree_tripletas.pack(expand=True, fill="both", padx=10, pady=(10,0))

        btn_tripletas_txt = ttk.Button(frame_tripletas, text="Crear TXT", command=self.exportar_tripletas)
        btn_tripletas_txt.pack(side="bottom", pady=10)

        # Pestaña Cuádruplas
        frame_cuadruplas = ttk.Frame(notebook)
        notebook.add(frame_cuadruplas, text="Cuádruplas")

        # SOLO 4 columnas para cuadruplas
        cols_cuadruplas = ("Op", "Arg1", "Arg2", "Resultado")
        self.tree_cuadruplas = ttk.Treeview(frame_cuadruplas, columns=cols_cuadruplas, show="headings")
        for i, col in enumerate(cols_cuadruplas):
            self.tree_cuadruplas.heading(col, text=col)
            self.tree_cuadruplas.column(col, width=120, anchor="center")
        self.tree_cuadruplas.pack(expand=True, fill="both", padx=10, pady=(10,0))

        btn_cuadruplas_txt = ttk.Button(frame_cuadruplas, text="Crear TXT", command=self.exportar_cuadruplas)
        btn_cuadruplas_txt.pack(side="bottom", pady=10)

        # Mostrar tripletas y cuadruplas en la tabla
        if tripletas:
            for fila in tripletas:
                fila = list(fila) + [''] * (5 - len(fila))
                self.tree_tripletas.insert("", "end", values=fila)
        if cuadruplas:
            for fila in cuadruplas:
                fila = list(fila) + [''] * (4 - len(fila))
                self.tree_cuadruplas.insert("", "end", values=fila)

    def exportar_tripletas(self):
        archivo = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivo de texto", "*.txt")])
        if archivo:
            with open(archivo, "w", encoding="utf-8") as f:
                for item in self.tree_tripletas.get_children():
                    valores = self.tree_tripletas.item(item)["values"]
                    f.write(" | ".join(str(v) for v in valores) + "\n")

    def exportar_cuadruplas(self):
        archivo = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Archivo de texto", "*.txt")])
        if archivo:
            with open(archivo, "w", encoding="utf-8") as f:
                for item in self.tree_cuadruplas.get_children():
                    valores = self.tree_cuadruplas.item(item)["values"]
                    f.write(" | ".join(str(v) for v in valores) + "\n")

    def centrar_ventana(self, ancho, alto):
        pantalla_ancho = self.winfo_screenwidth()
        pantalla_alto = self.winfo_screenheight()
        x = (pantalla_ancho - ancho) // 2
        y = (pantalla_alto - alto) // 2
        self.geometry(f'{ancho}x{alto}+{x}+{y}')