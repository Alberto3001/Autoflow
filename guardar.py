import os

def guardar_y_abrir_codigo(codigo, nombre_archivo):
    with open(nombre_archivo, 'w', encoding='utf-8') as f:
        f.write(codigo)
    os.startfile(nombre_archivo)
