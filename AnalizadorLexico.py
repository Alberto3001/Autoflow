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
# En AnalizadorLexico.py, reemplaza la función t_error
def t_error(t):
    global errores_Desc, lista_errores_lexicos
    col = 0
    context = ""
    sugerencia = ""
    error_type = "léxico"
    error_subtype = "desconocido"
    
    if t.lexer.lexdata:
        # Encuentra el inicio de la línea actual
        line_start_pos = t.lexer.lexdata.rfind('\n', 0, t.lexpos) + 1
        # Calcula la columna exacta
        col = (t.lexpos - line_start_pos) + 1
        
        # Extrae el contexto: la línea completa donde ocurrió el error
        next_newline = t.lexer.lexdata.find('\n', t.lexpos)
        if next_newline >= 0:
            context = t.lexer.lexdata[line_start_pos:next_newline]
        else:
            context = t.lexer.lexdata[line_start_pos:]
        
        # Contexto antes y después del error
        ctx_before = t.lexer.lexdata[max(0, t.lexpos-15):t.lexpos]
        ctx_after = t.lexer.lexdata[t.lexpos:min(len(t.lexer.lexdata), t.lexpos+15)]
        
        # Análisis del tipo de error léxico
        if t.value[0] in ['{', '}', '[', ']', ',', ';', '(', ')', '=', '>', '<']:
            # Podría ser un error de operador incompleto
            if t.value[0] == '-' and '>' in ctx_after:
                error_subtype = "operador_incompleto"
                sugerencia = "¿Quiso escribir '->' (operador de transición)?"
            elif t.value[0] == '=' and '=' in ctx_after:
                error_subtype = "operador_incompleto"
                sugerencia = "¿Quiso escribir '==' (operador de comparación)?"
            else:
                # Delimitadores fuera de contexto
                error_subtype = "delimitador_incorrecto"
                sugerencia = f"El símbolo '{t.value[0]}' no es válido en este contexto"
        
        elif t.value[0] in ['@', '#', '$', '&', '%', '!', '?', '~', '`']:
            # Caracteres especiales no válidos
            error_subtype = "caracter_especial_invalido"
            sugerencia = f"El símbolo '{t.value[0]}' no está permitido en AutoFlow"
        
        elif t.value[0].isdigit():
            # Número en lugar incorrecto
            if ctx_before and ctx_before[-1].isalpha():
                error_subtype = "identificador_mal_formado"
                sugerencia = "Los identificadores no pueden contener números en esta posición"
            else:
                error_subtype = "numero_mal_formado"
                sugerencia = "Uso incorrecto de un número"
        
        elif t.value[0] == '/':
            # Posible comentario mal formado
            if ctx_after and ctx_after[0] == '/':
                error_subtype = "comentario_mal_formado"
                sugerencia = "Los comentarios de línea deben comenzar con '//' (sin espacios entre las barras)"
            elif ctx_after and ctx_after[0] == '*':
                error_subtype = "comentario_mal_formado"
                sugerencia = "Los comentarios de bloque deben comenzar con '/*' y terminar con '*/' (sin espacios)"
            else:
                error_subtype = "operador_invalido"
                sugerencia = "El operador '/' no está definido en AutoFlow"
        
        elif t.value[0] == '"' or t.value[0] == "'":
            # Posible string sin cerrar
            error_subtype = "string_sin_cerrar"
            sugerencia = f"Falta cerrar la cadena con {t.value[0]}"
        
        elif t.value[0].isalpha():
            # Posible palabra reservada mal escrita
            palabras_cercanas = difflib.get_close_matches(t.value[0:min(len(t.value), 5)], palabras_reservadas.keys(), n=1, cutoff=0.6)
            if palabras_cercanas:
                error_subtype = "palabra_reservada_incorrecta"
                sugerencia = f"¿Quiso escribir '{palabras_cercanas[0]}'?"
            else:
                error_subtype = "identificador_invalido"
                sugerencia = "Identificador mal formado o carácter no permitido"
        
        elif t.value[0].isspace() and t.value[0] not in [' ', '\t', '\n', '\r']:
            # Espacios especiales o invisibles
            error_subtype = "espacio_invalido"
            sugerencia = "Hay un carácter de espacio especial o invisible no permitido"
        
        else:
            # Carácter desconocido o no soportado
            error_subtype = "caracter_desconocido"
            sugerencia = f"El carácter '{t.value[0]}' no está permitido en AutoFlow"
        
        # Contexto específico para AutoFlow
        if "automaton" in ctx_before[-15:]:
            if t.value[0] not in [' ', '\t', '\n', '{', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '_']:
                error_subtype = "error_nombre_automaton"
                sugerencia = "Después de 'automaton' debe venir un nombre de autómata válido seguido de '{'"
        
        elif "type" in ctx_before[-10:]:
            if "=" in ctx_before[-10:] and t.value[0] not in ['D', 'N', 'P', 'T']:
                error_subtype = "error_tipo_automaton"
                sugerencia = "El tipo de autómata debe ser 'DFA', 'NFA', 'PDA' o 'TM'"
        
        elif "alphabet" in ctx_before[-15:]:
            if "=" in ctx_before[-15:] and t.value[0] not in ['[', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '_', ',']:
                error_subtype = "error_alfabeto"
                sugerencia = "El alfabeto debe definirse como '[símbolo1, símbolo2, ...]'"
        
        elif "transitions" in ctx_before[-15:]:
            if t.value[0] != '{':
                error_subtype = "error_transiciones"
                sugerencia = "Después de 'transitions' debe venir '{'"
    
    # Crear mensaje de error detallado
    mensaje_base = f"Símbolo no válido '{t.value[0]}' en la línea {t.lineno}, columna {col}"
    mensaje_completo = mensaje_base
    
    if sugerencia:
        mensaje_completo = f"{mensaje_base}. {sugerencia}"
    
    # Crear una representación visual del error
    pointer = ' ' * (col - 1) + '^'
    context_visual = context + '\n' + pointer
    
    error_info = {
        'message': mensaje_completo,
        'line': t.lineno,
        'col': col,
        'value': t.value[0],
        'context': context_visual,
        'error_type': error_type,
        'error_subtype': error_subtype,
        'suggestion': sugerencia
    }
    
    errores_Desc.append(error_info)
    if t.lineno not in lista_errores_lexicos:
        lista_errores_lexicos.append(t.lineno)
    
    # Avanzar un carácter
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
