# Importar módulo yacc
import ply.yacc as yacc
# Importar tokens del analizador léxico
from AnalizadorLexico import tokens

errores_Sinc_Desc = []

def limpiar_errores():
    global errores_Sinc_Desc
    errores_Sinc_Desc = []

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

# Manejo de errores sintácticos
# Importar módulo yacc
import ply.yacc as yacc
# Importar tokens del analizador léxico
from AnalizadorLexico import tokens

errores_Sinc_Desc = []

def limpiar_errores():
    global errores_Sinc_Desc
    errores_Sinc_Desc = []

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

# Manejo de errores sintácticos
def p_error(p):
    global errores_Sinc_Desc
    if p:
        # Calcular la columna
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
        
        # Analizar posibles causas específicas
        sugerencia = ""
        error_detallado = "Error de sintaxis"
        
        # Errores comunes basados en el token y su posición
        if p.type == 'IDENTIFICADOR':
            # Verificar si se esperaba un token específico
            if p.value == 'automaton':
                sugerencia = "Debe especificar un nombre después de 'automaton'"
            else:
                # Posible uso incorrecto de identificador
                token_previo = parser.symstack[-2].type if len(parser.symstack) > 1 else None
                if token_previo == 'AUTOMATON':
                    sugerencia = "Después del nombre del autómata debe venir '{'"
                elif token_previo in ['TYPE', 'INITIAL']:
                    sugerencia = f"Después de '{token_previo.lower()}' debe usar '='"
                elif token_previo == 'ASIGNACION':
                    token_previo_2 = parser.symstack[-3].type if len(parser.symstack) > 2 else None
                    if token_previo_2 == 'TYPE':
                        sugerencia = "El tipo debe ser DFA, NFA, PDA o TM"
        
        elif p.type in ['LLAVE_A', 'LLAVE_C']:
            if p.type == 'LLAVE_A':
                sugerencia = "Verifique que las propiedades estén correctamente definidas dentro de las llaves"
            else:
                sugerencia = "Verifique que todas las propiedades terminen con ';'"
        
        elif p.type in ['CORCHETE_A', 'CORCHETE_B']:
            if p.type == 'CORCHETE_A':
                sugerencia = "Después de '[' debe venir una lista de elementos separados por comas"
            else:
                sugerencia = "Verifique que todos los elementos estén correctamente separados por comas"
        
        elif p.type == 'PUNTOCOMA':
            sugerencia = "Verifique que la propiedad anterior esté correctamente definida"
        
        elif p.type == 'ASIGNACION':
            sugerencia = "Después de '=' debe especificar un valor válido"
        
        elif p.type == 'TRANSICION':
            sugerencia = "La transición debe estar en el formato: estado_origen -> estado_destino [atributos];"
        
        # Construir mensaje de error
        if sugerencia:
            error_detallado = f"{error_detallado}. {sugerencia}"
        
        error_info = {
            'message': f"{error_detallado} en '{p.value}'",
            'line': p.lineno,
            'col': col,
            'value': p.value,
            'context': context,
            'token_type': p.type,
            'suggestion': sugerencia
        }
        
        errores_Sinc_Desc.append(error_info)
        
        # Modo de recuperación de pánico
        while True:
            token = parser.token()
            if not token or token.type in ['PUNTOCOMA', 'LLAVE_C']:
                break
        
        if token:
            return token
    else:
        errores_Sinc_Desc.append({
            'message': "Error de sintaxis al final del archivo. Posiblemente falten llaves de cierre '}'",
            'line': -1,
            'col': -1
        })
# Construir el analizador sintáctico
parser = yacc.yacc()

def test_parser(codigo, lexer=None):
    if lexer is not None:
        lexer.lineno = 1
    result = parser.parse(codigo, lexer=lexer)
    return result

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
# Construir el analizador sintáctico
parser = yacc.yacc()

def test_parser(codigo, lexer=None):
    if lexer is not None:
        lexer.lineno = 1
    result = parser.parse(codigo, lexer=lexer)
    return result

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