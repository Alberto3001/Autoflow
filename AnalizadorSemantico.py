def analizar_semantica(ast):
    errores = []
    automata_names = set()
    for automata in ast:
        if automata[0] != 'automaton':
            continue
        nombre = automata[1]
        definicion = automata[2]
        props = {}
        props_count = {}
        transiciones = []
        estados = set()
        alfabeto = set()
        stack_alphabet = set()
        tape_alphabet = set()
        accept_states = set()
        initial_state = None
        blank_symbol = None
        tipo = None

        # Identificador duplicado de autómata
        if nombre in automata_names:
            errores.append({'message': f"Identificador duplicado de autómata: '{nombre}'", 'tipo': 'semántico'})
        automata_names.add(nombre)

        # Extraer propiedades y detectar duplicadas
        if isinstance(definicion, tuple) and definicion[0] == 'definicion':
            propiedades = definicion[1]
            transiciones = definicion[2][1] if definicion[2][0] == 'transitions' else []
        else:
            propiedades = []
            transiciones = []

        for prop in propiedades:
            if isinstance(prop, tuple):
                key = prop[0]
                props_count[key] = props_count.get(key, 0) + 1
                if props_count[key] > 1:
                    errores.append({'message': f"Propiedad duplicada: '{key}' en autómata '{nombre}'", 'tipo': 'semántico'})
                props[key] = prop[1]

        tipo = props.get('type')
        if tipo and tipo not in ['DFA', 'NFA', 'PDA', 'TM']:
            errores.append({'message': f"Tipo de autómata no válido: '{tipo}' en '{nombre}'", 'tipo': 'semántico'})

        estados_lista = props.get('states', [])
        estados = set(estados_lista)
        alfabeto_lista = props.get('alphabet', [])
        alfabeto = set(alfabeto_lista)
        stack_alphabet_lista = props.get('stack_alphabet', [])
        stack_alphabet = set(stack_alphabet_lista)
        tape_alphabet_lista = props.get('tape_alphabet', [])
        tape_alphabet = set(tape_alphabet_lista)
        accept_states_lista = props.get('accept', [])
        accept_states = set(accept_states_lista)
        initial_state = props.get('initial')
        blank_symbol = props.get('blank')

        # Identificador duplicado de estado
        if len(estados) != len(estados_lista):
            errores.append({'message': f"Identificadores de estado duplicados en states en '{nombre}'", 'tipo': 'semántico'})
        if len(alfabeto) != len(alfabeto_lista):
            errores.append({'message': f"Símbolos duplicados en alphabet en '{nombre}'", 'tipo': 'semántico'})

        # Estado inicial invalido
        if initial_state and initial_state not in estados:
            errores.append({'message': f"Estado inicial '{initial_state}' no está en states en '{nombre}'", 'tipo': 'semántico'})

        # Estado de aceptacion invalido
        for st in accept_states:
            if st not in estados:
                errores.append({'message': f"Estado de aceptación '{st}' no está en states en '{nombre}'", 'tipo': 'semántico'})

        # Lista de elementos vacía en un conjunto
        for conjunto, nombre_conjunto in [(alfabeto, 'alphabet'), (estados, 'states'), (accept_states, 'accept')]:
            if isinstance(conjunto, set) and len(conjunto) == 0:
                errores.append({'message': f"El conjunto '{nombre_conjunto}' está vacío en '{nombre}'", 'tipo': 'semántico'})

        # símbolo blanco
        if blank_symbol and blank_symbol not in tape_alphabet:
            errores.append({'message': f"El símbolo blank '{blank_symbol}' no está en tape_alphabet en '{nombre}'", 'tipo': 'semántico'})

        # Definición de stack_alphabet/tape_alphabet
        if tipo in ['DFA', 'NFA'] and (stack_alphabet or props.get('stack_start')):
            errores.append({'message': f"Propiedad de pila definida en un {tipo} ('{nombre}')", 'tipo': 'semántico'})
        if tipo in ['DFA', 'NFA', 'PDA'] and (tape_alphabet or blank_symbol):
            errores.append({'message': f"Propiedad de cinta definida en un {tipo} ('{nombre}')", 'tipo': 'semántico'})

        # Múltiples estados iniciales
        if isinstance(initial_state, (list, set)) and len(initial_state) > 1:
            errores.append({'message': f"Múltiples estados iniciales en '{nombre}'", 'tipo': 'semántico'})

        # Revisar transiciones
        for trans in transiciones:
            if not isinstance(trans, tuple) or trans[0] != 'transicion':
                continue
            origen, destino, atributos = trans[1], trans[2], trans[3]
            if origen not in estados:
                errores.append({'message': f"Estado origen '{origen}' no declarado en states en '{nombre}'", 'tipo': 'semántico'})
            if destino not in estados:
                errores.append({'message': f"Estado destino '{destino}' no declarado en states en '{nombre}'", 'tipo': 'semántico'})
            if not atributos or len(atributos) == 0:
                errores.append({'message': f"Transición de '{origen}' a '{destino}' sin atributos en '{nombre}'", 'tipo': 'semántico'})
                continue
            input_count = 0
            read_count = 0
            attr_names = set()
            for attr in atributos:
                attr_name, attr_val = attr
                if attr_name in attr_names:
                    errores.append({'message': f"Atributo duplicado '{attr_name}' en transición de '{origen}' a '{destino}' en '{nombre}'", 'tipo': 'semántico'})
                attr_names.add(attr_name)
                # Símbolo de alfabeto no declarado
                if attr_name in ['input', 'read'] and attr_val not in alfabeto:
                    errores.append({'message': f"Símbolo '{attr_val}' en atributo '{attr_name}' no está en alphabet en '{nombre}'", 'tipo': 'semántico'})
                if attr_name in ['pop', 'push']:
                    # Permitir EPSILON
                    if isinstance(attr_val, str) and attr_val.upper() == 'EPSILON':
                        continue
                
                    for simbolo in attr_val:
                        if simbolo not in stack_alphabet:
                            errores.append({'message': f"Símbolo '{simbolo}' en atributo '{attr_name}' no está en stack_alphabet en '{nombre}'", 'tipo': 'semántico'})
                if attr_name in ['write', 'read', 'move'] and attr_name != 'move' and attr_val not in tape_alphabet:
                    errores.append({'message': f"Símbolo '{attr_val}' en atributo '{attr_name}' no está en tape_alphabet en '{nombre}'", 'tipo': 'semántico'})
                # Atributos de transición incorrectos para el tipo de autómata
                if tipo in ['DFA', 'NFA'] and attr_name in ['pop', 'push', 'read', 'write', 'move']:
                    errores.append({'message': f"Atributo '{attr_name}' no permitido en transición de un {tipo} ('{nombre}')", 'tipo': 'semántico'})
                if tipo == 'PDA' and attr_name in ['read', 'write', 'move']:
                    errores.append({'message': f"Atributo '{attr_name}' no permitido en transición de un PDA ('{nombre}')", 'tipo': 'semántico'})
                if tipo == 'TM' and attr_name in ['pop', 'push']:
                    errores.append({'message': f"Atributo '{attr_name}' no permitido en transición de una TM ('{nombre}')", 'tipo': 'semántico'})
                # Valor de atributo incorrecto para move
                if attr_name == 'move' and attr_val not in ['L', 'R', 'S', 'LEFT', 'RIGHT', 'STAY']:
                    errores.append({'message': f"Valor de atributo 'move' inválido: '{attr_val}' en transición de '{origen}' a '{destino}' en '{nombre}'", 'tipo': 'semántico'})
                # Contar atributos de lectura/input
                if attr_name == 'input':
                    input_count += 1
                if attr_name == 'read':
                    read_count += 1
                # INPUT como identificador de atributo irreconocido
                if attr_name not in ['input', 'pop', 'push', 'read', 'write', 'move']:
                    errores.append({'message': f"Atributo irreconocido '{attr_name}' en transición de '{origen}' a '{destino}' en '{nombre}'", 'tipo': 'semántico'})
            if input_count > 1 or read_count > 1:
                errores.append({'message': f"Transición de '{origen}' a '{destino}' tiene múltiples atributos de lectura/input en '{nombre}'", 'tipo': 'semántico'})
            # Transiciones incompletas para TM
            if tipo == 'TM':
                required = {'read', 'write', 'move'}
                attrs = set(a[0] for a in atributos)
                if not required.issubset(attrs):
                    errores.append({'message': f"Transición de TM de '{origen}' a '{destino}' incompleta (faltan atributos obligatorios) en '{nombre}'", 'tipo': 'semántico'})
    return errores