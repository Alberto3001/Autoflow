#Importar módulo lex
import ply.lex as lex
import difflib

#Definir dos variables para los errores
errores_Desc = []
lista_errores_lexicos = []

#Definir método para vaciar listas
def limpiar_errores_lex():
    global errores_Desc, lista_errores_lexicos
    errores_Desc = []
    lista_errores_lexicos = []

# Tokens para AutoFlow
tokens = [
    'ASIGNACION',       # = 
    'TRANSICION',       # ->
    'LLAVE_A',          # {
    'LLAVE_C',          # }
    'CORCHETE_A',       # [
    'CORCHETE_B',       # ]
    'COMA',             # ,
    'PUNTOCOMA',        # ;
    'IDENTIFICADOR',    # Nombres de estados y autómatas
    'SIMBOLO',          # Símbolos de entrada
    'EPSILON',          # ε (epsilon para transiciones vacías)
    'COMENTARIO_LINEA', # // comentario
    'COMENTARIO_BLOQUE' # /* comentario */
]

# Palabras reservadas de AutoFlow
palabras_reservadas = {
    'automaton': 'AUTOMATON',
    'type': 'TYPE',
    'alphabet': 'ALPHABET',
    'states': 'STATES',
    'initial': 'INITIAL',
    'accept': 'ACCEPT',
    'transitions': 'TRANSITIONS',
    'stack_alphabet': 'STACK_ALPHABET',
    'stack_start': 'STACK_START',
    'tape_alphabet': 'TAPE_ALPHABET',
    'blank': 'BLANK',
    'DFA': 'DFA',
    'NFA': 'NFA',
    'PDA': 'PDA',
    'TM': 'TM',
    'input': 'INPUT',
    'pop': 'POP',
    'push': 'PUSH',
    'read': 'READ',
    'write': 'WRITE',
    'move': 'MOVE',
    'L': 'LEFT',
    'R': 'RIGHT',
    'S': 'STAY'
}

# Agregar palabras reservadas a los tokens
tokens = tokens + list(palabras_reservadas.values())

# Definir reglas para tokens simples
t_ASIGNACION = r'='
t_TRANSICION = r'->'
t_LLAVE_A = r'\{'
t_LLAVE_C = r'\}'
t_CORCHETE_A = r'\['
t_CORCHETE_B = r'\]'
t_COMA = r','
t_PUNTOCOMA = r';'
t_EPSILON = r'ε|\\epsilon'  # Acepta tanto ε como \epsilon

# Caracteres ignorados (espacios y tabs)
t_ignore = ' \t'

# Método para identificadores no válidos
def t_IDError(t):
    r'\d+[a-zA-ZñÑ][a-zA-Z0-9ñÑ_]*'
    global errores_Desc
    errores_Desc.append("Identificador no válido en la línea "+str(t.lineno))

# Manejo de comentarios de línea
def t_COMENTARIO_LINEA(t):
    r'//.*'
    pass  # No devolver token para comentarios

# Manejo de comentarios de bloque
def t_COMENTARIO_BLOQUE(t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')  # Actualizar contador de líneas
    pass  # No devolver token para comentarios

# Método para identificadores
def t_IDENTIFICADOR(t):
    r'[a-zA-Z][a-zA-Z0-9_]*'
    # Verificar si es una palabra reservada
    if t.value in palabras_reservadas:
        t.type = palabras_reservadas[t.value]
        return t
    # Sugerir si es similar a una reservada
    close = difflib.get_close_matches(t.value, palabras_reservadas.keys(), n=1, cutoff=0.8)
    if close:
        col = t.lexpos - t.lexer.lexdata.rfind('\n', 0, t.lexpos)
        error_info = {
            'message': f"¿Quizás quiso decir '{close[0]}' en vez de '{t.value}'? Palabra no reconocida.",
            'line': t.lineno,
            'col': col,
            'value': t.value
        }
        errores_Desc.append(error_info)
        if t.lineno not in lista_errores_lexicos:
            lista_errores_lexicos.append(t.lineno)
        return  # No retorna token, lo trata como error léxico
    t.type = 'IDENTIFICADOR'
    return t

# Método para símbolos (caracteres individuales o secuencias para alfabetos)
def t_SIMBOLO(t):
    r'[a-zA-Z0-9_]'
    return t

# Contador de líneas
def t_SALTOLINEA(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Manejo de errores
def t_error(t):
    global errores_Desc, lista_errores_lexicos
    col = 0
    if t.lexer.lexdata: 
        line_start_pos = t.lexer.lexdata.rfind('\n', 0, t.lexpos) + 1
        col = (t.lexpos - line_start_pos) + 1

    error_info = {
        'message': f"Símbolo no válido '{t.value[0]}' en la línea {t.lineno}, columna {col}",
        'line': t.lineno,
        'col': col,
        'value': t.value[0]
    }
    errores_Desc.append(error_info)
    if t.lineno not in lista_errores_lexicos:
        lista_errores_lexicos.append(t.lineno)
    t.lexer.skip(1)

# Construir el analizador léxico
lexer = lex.lex()

# Función para analizar una cadena
def analisis(cadena):
    lexer.input(cadena)
    tokens = []
    # Inicia el número de línea en 1
    lexer.lineno = 1
    for tok in lexer:
        columna = tok.lexpos - cadena.rfind('\n', 0, tok.lexpos)
        tokens.append((tok.value, tok.type, tok.lineno, columna))
    return tokens
