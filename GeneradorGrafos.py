import subprocess
import os

def generar_dibujo_automata(cuadruplas, nombre_automata, tipo_automata, output_dir="."):
    dot_content = []
    dot_content.append(f'digraph "Automata {nombre_automata}" {{')
    dot_content.append('    rankdir=LR; // Dirección del grafo: de izquierda a derecha')

    states = set()
    initial_state = None
    accept_states = set()
    transitions = []

    for op, arg1, arg2, res in cuadruplas:
        if op == 'ADD_STATE':
            states.add(arg2)
        elif op == 'SET_INITIAL_STATE':
            initial_state = arg2
        elif op == 'ADD_ACCEPT_STATE':
            accept_states.add(arg2)
        elif op.startswith('ADD_') and 'TRANSITION' in op:
            origen = arg1
            destino = arg2
            atributos = res
            transitions.append({'origen': origen, 'destino': destino, 'atributos': atributos, 'tipo': op})

    # Nodos (estados)
    for state in states:
        node_shape = 'doublecircle' if state in accept_states else 'circle'
        dot_content.append(f'    "{state}" [label="{state}", shape={node_shape}];')

    # Estado inicial
    if initial_state:
        dot_content.append(f'    node [shape=none, width=0, height=0]; start_node;')
        dot_content.append(f'    start_node -> "{initial_state}";')

    # Aristas (transiciones)
    for t in transitions:
        origen = t['origen']
        destino = t['destino']
        atributos = t['atributos']
        tipo = t['tipo']
        label = ""
        if tipo == 'ADD_FA_TRANSITION':
            label = atributos.get('input', '')
        elif tipo == 'ADD_PDA_TRANSITION':
            input_sym = atributos.get('input', '')
            pop_sym = atributos.get('pop', '')
            push_sym = atributos.get('push', '')
            label = f"{input_sym},{pop_sym}/{push_sym}"
        elif tipo == 'ADD_TM_TRANSITION':
            read_sym = atributos.get('read', '')
            write_sym = atributos.get('write', '')
            move_dir = atributos.get('move', '')
            label = f"{read_sym}/{write_sym},{move_dir}"
        dot_content.append(f'    "{origen}" -> "{destino}" [label="{label}"];')

    dot_content.append('}')
    final_dot_string = "\n".join(dot_content)

    dot_file_path = os.path.join(output_dir, f"{nombre_automata}.dot")
    png_file_path = os.path.join(output_dir, f"{nombre_automata}.png")

    try:
        with open(dot_file_path, "w", encoding="utf-8") as f:
            f.write(final_dot_string)
        print(f"Archivo DOT generado: {dot_file_path}")
    except IOError as e:
        print(f"Error al escribir el archivo DOT: {e}")
        return None

    try:
        subprocess.run(['dot', '-Tpng', dot_file_path, '-o', png_file_path], check=True, capture_output=True, text=True)
        print(f"Dibujo del autómata generado en: {png_file_path}")
        return png_file_path
    except FileNotFoundError:
        print("\nERROR: La herramienta 'dot' (Graphviz) no se encontró.")
        print("Asegúrate de que Graphviz esté instalado y en el PATH.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"\nERROR al ejecutar 'dot':\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}")
        return None
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        return None

def abrir_imagen_automata(png_file_path):
    try:
        os.startfile(png_file_path)
    except Exception as e:
        print(f"No se pudo abrir la imagen: {e}")
