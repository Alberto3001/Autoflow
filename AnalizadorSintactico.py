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

# Definición de un atributo
def p_atributo(p):
    """
    atributo : IDENTIFICADOR ASIGNACION valor
    """
    p[0] = (p[1], p[3])

# Definición de un valor (puede ser un símbolo, EPSILON o identificador)
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

# Errores sintácticos
def p_error(p):
    if p:
        errores_Sinc_Desc.append(f"Error de sintaxis en '{p.value}' en la línea {p.lineno}")
    else:
        errores_Sinc_Desc.append("Error de sintaxis al final del archivo")

# Construir el analizador
parser = yacc.yacc()

def test_parser(codigo):
    result = parser.parse(codigo)
    return result

# Ejemplo de uso
if __name__ == "__main__":
    codigo = '''
    automaton AFD_Ejemplo {
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