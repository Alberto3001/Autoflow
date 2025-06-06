# Importar módulo yacc
import ply.yacc as yacc
# Importar tokens del analizador léxico
from AnalizadorLexico import tokens

errores_Sinc_Desc = []
ultimo_error_linea = -1
seccion_actual = None

def limpiar_errores():
    global errores_Sinc_Desc, ultimo_error_linea
    errores_Sinc_Desc = []
    ultimo_error_linea = -1

# Regla inicial - programa puede tener uno o más autómatas
def p_programa(p):
    """
    programa : automata_def
             | programa automata_def
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

# Definición de un autómata
def p_automata_def(p):
    """
    automata_def : AUTOMATON IDENTIFICADOR LLAVE_A definicion_automa LLAVE_C
    """
    p[0] = ('automaton', p[2], p[4])

# Definición del cuerpo de un autómata
def p_definicion_automa(p):
    """
    definicion_automa : propiedades transiciones_def
    """
    p[0] = ('definicion', p[1], p[2])

# Lista de propiedades
def p_propiedades(p):
    """
    propiedades : propiedad
                | propiedades propiedad
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

# Definición de una propiedad
def p_propiedad(p):
    """
    propiedad : type_def
              | alphabet_def
              | states_def
              | initial_def
              | accept_def
              | stack_alphabet_def
              | stack_start_def
              | tape_alphabet_def
              | blank_def
    """
    p[0] = p[1]

# Definición del tipo de autómata
def p_type_def(p):
    """
    type_def : TYPE ASIGNACION tipo_automa PUNTOCOMA
    """
    p[0] = ('type', p[3])

# Tipos de autómata
def p_tipo_automa(p):
    """
    tipo_automa : DFA
                | NFA
                | PDA
                | TM
    """
    p[0] = p[1]

# Definición del alfabeto
def p_alphabet_def(p):
    """
    alphabet_def : ALPHABET ASIGNACION conjunto_simbolos PUNTOCOMA
    """
    p[0] = ('alphabet', p[3])

# Definición de estados
def p_states_def(p):
    """
    states_def : STATES ASIGNACION conjunto_ids PUNTOCOMA
    """
    p[0] = ('states', p[3])

# Definición del estado inicial
def p_initial_def(p):
    """
    initial_def : INITIAL ASIGNACION IDENTIFICADOR PUNTOCOMA
    """
    p[0] = ('initial', p[3])

# Definición de estados de aceptación
def p_accept_def(p):
    """
    accept_def : ACCEPT ASIGNACION conjunto_ids PUNTOCOMA
    """
    p[0] = ('accept', p[3])

# Definición del alfabeto de pila (para PDA)
def p_stack_alphabet_def(p):
    """
    stack_alphabet_def : STACK_ALPHABET ASIGNACION conjunto_simbolos PUNTOCOMA
    """
    p[0] = ('stack_alphabet', p[3])

# Definición del símbolo inicial de pila
def p_stack_start_def(p):
    """
    stack_start_def : STACK_START ASIGNACION SIMBOLO PUNTOCOMA
                    | STACK_START ASIGNACION IDENTIFICADOR PUNTOCOMA
    """
    p[0] = ('stack_start', p[3])

# Definición del alfabeto de cinta (para TM)
def p_tape_alphabet_def(p):
    """
    tape_alphabet_def : TAPE_ALPHABET ASIGNACION conjunto_simbolos PUNTOCOMA
    """
    p[0] = ('tape_alphabet', p[3])

# Definición del símbolo blanco de cinta
def p_blank_def(p):
    """
    blank_def : BLANK ASIGNACION SIMBOLO PUNTOCOMA
              | BLANK ASIGNACION IDENTIFICADOR PUNTOCOMA
    """
    p[0] = ('blank', p[3])

# Definición de transiciones
def p_transiciones_def(p):
    """
    transiciones_def : TRANSITIONS LLAVE_A lista_transiciones LLAVE_C
    """
    p[0] = ('transitions', p[3])

# Lista de transiciones
def p_lista_transiciones(p):
    """
    lista_transiciones : transicion_def
                       | lista_transiciones transicion_def
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

# Definición de una transición
def p_transicion_def(p):
    """
    transicion_def : IDENTIFICADOR TRANSICION IDENTIFICADOR CORCHETE_A atributos CORCHETE_B PUNTOCOMA
    """
    p[0] = ('transicion', p[1], p[3], p[5])

# Lista de atributos en una transición
def p_atributos(p):
    """
    atributos : atributo
              | atributos COMA atributo
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

# Definición de un atributo, se acepta tanto si la palabra es reconocida como IDENTIFICADOR
def p_atributo(p):
    """
    atributo : IDENTIFICADOR ASIGNACION valor
    """
    p[0] = (p[1], p[3])

# Permitir que ciertos nombres reservados (por ejemplo, "input") sean reconocidos en atributos.
def p_atributo_reserved(p):
    """
    atributo : INPUT ASIGNACION valor
    """
    p[0] = (p[1], p[3])

# Definición de un valor (puede ser un símbolo, EPSILON, identificador o direcciones)
def p_valor(p):
    """
    valor : SIMBOLO
          | EPSILON
          | IDENTIFICADOR
          | LEFT
          | RIGHT
          | STAY
    """
    p[0] = p[1]

# Definición de conjuntos de símbolos
def p_conjunto_simbolos(p):
    """
    conjunto_simbolos : LLAVE_A elementos_conjunto LLAVE_C
    """
    p[0] = p[2]

# Definición de conjuntos de identificadores
def p_conjunto_ids(p):
    """
    conjunto_ids : LLAVE_A elementos_conjunto LLAVE_C
    """
    p[0] = p[2]

# Elementos de un conjunto (símbolos o identificadores)
def p_elementos_conjunto(p):
    """
    elementos_conjunto : elemento
                       | elementos_conjunto COMA elemento
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]

# Elemento de un conjunto
def p_elemento(p):
    """
    elemento : SIMBOLO
             | IDENTIFICADOR
    """
    p[0] = p[1]

# Regla para detectar 'type DFA' sin el signo igual
def p_propiedad_type_error(p):
    '''propiedad : TYPE IDENTIFICADOR PUNTOCOMA'''
    if p[2] in ['DFA', 'NFA', 'PDA', 'TM']:
        # Agregar explícitamente un error para este caso
        error_info = {
            'message': f"Falta el signo de igual (=) entre 'type' y '{p[2]}'",
            'line': p.lineno(1),
            'col': p.lexpos(1),
            'value': p[2],
            'context': f"type {p[2]};",
            'token_type': 'IDENTIFICADOR',
            'tipo': 'sintáctico'
        }
        errores_Sinc_Desc.append(error_info)
        
        # Manejar error pero permitir continuar
        p[0] = ('property', ('type', p[2]))

# Regla para detectar 'alphabet {a, b}' sin el signo igual
def p_propiedad_alphabet_error(p):
    '''propiedad : ALPHABET LLAVE_A elementos_conjunto LLAVE_C PUNTOCOMA'''
    # Manejar error pero permitir continuar
    p[0] = ('property', ('alphabet', p[3]))

# Reglas para detectar propiedades sin el signo igual
def p_propiedad_states_error(p):
    '''propiedad : STATES LLAVE_A elementos_conjunto LLAVE_C PUNTOCOMA'''
    # Manejar error pero permitir continuar
    p[0] = ('property', ('states', p[3]))

def p_propiedad_initial_error(p):
    '''propiedad : INITIAL IDENTIFICADOR PUNTOCOMA'''
    # Manejar error pero permitir continuar
    p[0] = ('property', ('initial', p[2]))

def p_propiedad_accept_error(p):
    '''propiedad : ACCEPT LLAVE_A elementos_conjunto LLAVE_C PUNTOCOMA'''
    # Manejar error pero permitir continuar
    p[0] = ('property', ('accept', p[3]))

# Manejo de errores sintácticos
def p_error(p):
    global errores_Sinc_Desc, ultimo_error_linea
    
    if p:
        # Calcular la columna y contexto (código existente)
        lexer_data = p.lexer.lexdata
        col = 0
        if lexer_data:
            line_start = lexer_data.rfind('\n', 0, p.lexpos) + 1
            col = p.lexpos - line_start + 1
        
        # Obtener contexto
        context = ""
        if lexer_data:
            lines = lexer_data.splitlines()
            if 0 <= p.lineno-1 < len(lines):
                context = lines[p.lineno-1]
        
        # Mejor detección de errores específicos
        sugerencia = ""
        es_error_especifico = False
        
        # Detectar error en 'type DFA' (sin el signo igual)
        if p.type == 'IDENTIFICADOR' and p.value in ['DFA', 'NFA', 'PDA', 'TM']:
            # Verificar si estamos en una definición de tipo sin el signo igual
            if context and 'type' in context and '=' not in context:
                sugerencia = f"Falta el signo de igual (=) entre 'type' y '{p.value}'"
                es_error_especifico = True
        
        # Detectar error en 'alphabet {' (sin el signo igual)
        elif p.type in ['LLAVE_A', 'CORCHETE_A'] or (p.type == 'IDENTIFICADOR' and 'alphabet' in context):
            if context and 'alphabet' in context and '=' not in context:
                sugerencia = "Falta el signo de igual (=) entre 'alphabet' y '{'"
                es_error_especifico = True
        
        # Detectar error en 'automato' vs 'automaton'
        elif p.type == 'IDENTIFICADOR' and p.value == 'automato':
            sugerencia = "La palabra clave correcta es 'automaton', no 'automato'"
            es_error_especifico = True
        
        # Si no es un error específico que podamos identificar con confianza
        if not es_error_especifico:
            # Verificar si podría ser un error común basado en el token
            if p.type == 'LLAVE_C':
                sugerencia = "Verifique que todas las propiedades terminen con ';'"
            elif p.type == 'PUNTOCOMA':
                sugerencia = "Falta un punto y coma para terminar la definición"
            else:
                # No reportar este error, solo recuperarse
                parser.errok()
                
                # Avanzar hasta un punto de sincronización
                while True:
                    token = parser.token()
                    if not token:
                        break
                        
                    if token.type in ['PUNTOCOMA', 'LLAVE_C']:
                        return token
                        
                return
        
        # Crear información de error
        error_info = {
            'message': f"Error de sintaxis. {sugerencia}" if sugerencia else f"Error de sintaxis en '{p.value}'",
            'line': p.lineno,
            'col': col,
            'value': p.value,
            'context': context,
            'token_type': p.type,
            'tipo': 'sintáctico'
        }
        
        # Verificar si ya hay un error similar
        ya_reportado = False
        for error in errores_Sinc_Desc:
            if isinstance(error, dict) and error.get('line') == p.lineno:
                ya_reportado = True
                break
        
        # Solo agregar si no está reportado
        if not ya_reportado:
            errores_Sinc_Desc.append(error_info)
        
        # Recuperación
        parser.errok()
        
        # Avanzar hasta un punto claro
        while True:
            token = parser.token()
            if not token:
                break
                
            if token.type in ['PUNTOCOMA', 'LLAVE_C', 'TYPE', 'ALPHABET', 'STATES', 'INITIAL', 'ACCEPT', 'TRANSITIONS']:
                return token
    else:
        # Error EOF
        error_info = {
            'message': "Error de sintaxis al final del archivo. Posiblemente falte cerrar alguna llave o falta un punto y coma.",
            'line': -1,
            'col': -1,
            'tipo': 'sintáctico'
        }
        errores_Sinc_Desc.append(error_info)
# Construir el analizador sintáctico
parser = yacc.yacc()

def restart():
    parser.errok()

# Añadir el método al parser
parser.restart = restart

# Modificar test_parser para mejorar la recuperación de errores
def test_parser(codigo, lexer=None):
    global errores_Sinc_Desc, ultimo_error_linea, seccion_actual
    
    # Reiniciar variables
    errores_Sinc_Desc = []
    ultimo_error_linea = -1
    seccion_actual = None
    
    # Inicializar variables de estado para el seguimiento de secciones
    inside_automaton = False
    inside_transiciones = False  # Esta es la variable que falta inicializar
    
    # Lista de propiedades válidas
    propiedades_validas = [
        'type', 'alphabet', 'states', 'initial', 'accept', 
        'stack_alphabet', 'stack_start', 'tape_alphabet', 'blank', 'transitions'
    ]
    
    # Búsqueda preliminar de errores comunes usando expresiones regulares
    import re
    
    # 1. Detectar propiedades no reconocidas
    lines = codigo.splitlines()
    inside_automaton = False
    inside_transiciones = False  # Nueva variable para rastrear si estamos dentro de la sección de transiciones

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Detectar si estamos dentro de un autómata
        if 'automaton' in line and '{' in line:
            inside_automaton = True
            continue
            
        if inside_automaton and '}' in line and line.strip() == '}':
            inside_automaton = False
            inside_transiciones = False  # Asegurarse de que se reinicie cuando termine el autómata
            continue
            
        # Detectar si estamos dentro de la sección de transiciones
        if inside_automaton and ('transition' in line or 'transitions' in line) and '{' in line:
            inside_transiciones = True
            continue
            
        if inside_automaton and inside_transiciones and '}' in line and line.strip() == '}':
            inside_transiciones = False
            continue
            
        # Verificar propiedades no reconocidas dentro del autómata PERO FUERA de la sección de transiciones
        if inside_automaton and not inside_transiciones and '=' in line:
            # Extraer el nombre de la propiedad (antes del signo igual)
            property_name = line.split('=')[0].strip()
            
            # Verificar si es una propiedad válida
            if property_name not in propiedades_validas and not property_name.startswith('}'):
                errores_Sinc_Desc.append({
                    'message': f"Propiedad no reconocida: '{property_name}'. Las propiedades válidas son: {', '.join(propiedades_validas)}",
                    'line': i + 1,
                    'col': line.find(property_name),
                    'value': property_name,
                    'tipo': 'sintáctico'
                })
    
    # 2. Detectar propiedades sin el signo igual (código existente)
    property_pattern = re.compile(r'\b(type|alphabet|states|initial|accept|stack_alphabet|stack_start|tape_alphabet|blank)\s+([^=\n;]+)(?:;|\n|$)')
    
    for match in property_pattern.finditer(codigo):
        property_name = match.group(1)
        property_value = match.group(2).strip()
        line_number = codigo[:match.start()].count('\n') + 1
        
        # Calcular la columna
        last_newline = codigo.rfind('\n', 0, match.start())
        col = match.start() - last_newline if last_newline != -1 else match.start() + 1
        
        # Mensaje específico según la propiedad
        if property_name == 'type':
            message = f"Falta el signo de igual (=) entre '{property_name}' y '{property_value}'"
        elif property_name in ['alphabet', 'states', 'accept']:
            if property_value.startswith('{'):
                message = f"Falta el signo de igual (=) entre '{property_name}' y '{'{'}'"
            else:
                message = f"Falta el signo de igual (=) en la propiedad '{property_name}'"
        else:
            message = f"Falta el signo de igual (=) en la propiedad '{property_name}'"
        
        errores_Sinc_Desc.append({
            'message': message,
            'line': line_number,
            'col': col,
            'value': property_value,
            'context': match.group(0),
            'token_type': 'IDENTIFICADOR',
            'tipo': 'sintáctico'
        })
    
    # 2. NUEVA detección mejorada de propiedades sin punto y coma
    lines = codigo.splitlines()
    
    # Buscar directamente líneas que contengan un conjunto pero no terminen con punto y coma
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # Si es una línea que tiene una propiedad y termina con un conjunto pero sin punto y coma
        if ('}' in line and not line.endswith(';') and 
            any(prop in line for prop in ['alphabet', 'states', 'accept'])):
            # Verificar que el último carácter no nulo sea un corchete de cierre
            if line.rstrip()[-1] == '}':
                errores_Sinc_Desc.append({
                    'message': f"Falta punto y coma (;) al final de la definición",
                    'line': i + 1,
                    'col': len(line),
                    'value': line,
                    'tipo': 'sintáctico'
                })
    
    # 3. Detectar transiciones sin flecha '->'
    inside_transiciones = False
    for i, line in enumerate(lines):
        line = line.strip()
        
        # Detectar si estamos dentro de la sección de transiciones
        if ('transition' in line or 'transitions' in line) and '{' in line:
            inside_transiciones = True
            continue
            
        if inside_transiciones and '}' in line:
            inside_transiciones = False
            continue
            
        # Si estamos dentro de la sección de transiciones, verificar el formato
        if inside_transiciones and line and not line.strip().startswith('}'):
            # Buscar patrones como "q0  q1" sin la flecha
            transition_no_arrow_match = re.search(r'^\s*(\w+)\s+(\w+)\s*\[', line)
            if transition_no_arrow_match:
                state1 = transition_no_arrow_match.group(1)
                state2 = transition_no_arrow_match.group(2)
                
                errores_Sinc_Desc.append({
                    'message': f"Falta la flecha de transición '->' entre '{state1}' y '{state2}'",
                    'line': i + 1,
                    'col': line.find(state2),
                    'value': f"{state1} {state2}",
                    'tipo': 'sintáctico'
                })
            
            # 4. NUEVO: Detección específica de atributos sin signo igual
            if '[' in line and ']' in line:
                # Extraer el contenido entre corchetes
                bracket_start = line.find('[')
                bracket_end = line.find(']')
                if bracket_start != -1 and bracket_end != -1:
                    bracket_content = line[bracket_start+1:bracket_end].strip()
                    
                    # Buscar patrones como "input a" sin el signo igual
                    attr_pattern = re.search(r'(\w+)\s+([^\s=;]+)', bracket_content)
                    if attr_pattern and '=' not in bracket_content:
                        attr_name = attr_pattern.group(1)
                        attr_value = attr_pattern.group(2)
                        
                        # Verificar que no sea un falso positivo
                        if not re.search(rf'{attr_name}\s*=', bracket_content):
                            errores_Sinc_Desc.append({
                                'message': f"Falta el signo de igual (=) entre '{attr_name}' y '{attr_value}' en el atributo de transición",
                                'line': i + 1,
                                'col': bracket_start + 1 + bracket_content.find(attr_name) + len(attr_name),
                                'value': f"{attr_name} {attr_value}",
                                'tipo': 'sintáctico'
                            })
    
    # Continuar con el análisis sintáctico normal
    if lexer is not None:
        lexer.lineno = 1
    
    try:
        result = parser.parse(codigo, lexer=lexer)
        return result
    except Exception as e:
        print(f"Error interno durante el análisis: {str(e)}")
        errores_Sinc_Desc.append({
            'message': f"Error interno durante el análisis: {str(e)}",
            'line': -1,
            'col': -1,
            'tipo': 'sintáctico'
        })
        return None
    
# Ejemplo de uso
if __name__ == "__main__":
    codigo = '''
    automato AFD_Ejemplo {
      type = DFA;
      alphabet = {a, b};
      states = {q0, q1, q2};
      initial = q0;
      accept = {q2};

      transitions {
        q0 -> q1 [input = a];
        q1 -> q2 [input = b];
        q2 -> q2 [input = a];
        q2 -> q1 [input = b];
      }
    }
    '''
    
    resultado = test_parser(codigo)
    print(resultado)
    print(errores_Sinc_Desc)
