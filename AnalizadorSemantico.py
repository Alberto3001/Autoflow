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
            duplicados = set([x for x in estados_lista if estados_lista.count(x) > 1])
            for dup in duplicados:
                errores.append({'message': f"Estado duplicado '{dup}' en states en '{nombre}'", 'tipo': 'semántico'})

        if len(alfabeto) != len(alfabeto_lista):
            duplicados = set([x for x in alfabeto_lista if alfabeto_lista.count(x) > 1])
            for dup in duplicados:
                errores.append({'message': f"Símbolo duplicado '{dup}' en alphabet en '{nombre}'", 'tipo': 'semántico'})

        # Estados duplicados en accept
        if len(accept_states) != len(accept_states_lista):
            duplicados = set([x for x in accept_states_lista if accept_states_lista.count(x) > 1])
            for dup in duplicados:
                errores.append({'message': f"Estado duplicado '{dup}' en accept en '{nombre}'", 'tipo': 'semántico'})

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

        # Validar propiedades de cinta y pila seung el tipo
        if tipo in ['DFA', 'NFA']:
            if stack_alphabet:
                errores.append({'message': f"Propiedad 'stack_alphabet' no permitida en un {tipo} ('{nombre}')", 'tipo': 'semántico'})
            if props.get('stack_start'):
                errores.append({'message': f"Propiedad 'stack_start' no permitida en un {tipo} ('{nombre}')", 'tipo': 'semántico'})
        if tipo in ['DFA', 'NFA', 'PDA']:
            if tape_alphabet:
                errores.append({'message': f"Propiedad 'tape_alphabet' no permitida en un {tipo} ('{nombre}')", 'tipo': 'semántico'})
            if blank_symbol:
                errores.append({'message': f"Propiedad 'blank' no permitida en un {tipo} ('{nombre}')", 'tipo': 'semántico'})
        else:
            if blank_symbol and blank_symbol not in tape_alphabet:
                errores.append({'message': f"El símbolo blank '{blank_symbol}' no está en tape_alphabet en '{nombre}'", 'tipo': 'semántico'})

        # Varios estados iniciales
        if isinstance(initial_state, (list, set)) and len(initial_state) > 1:
            errores.append({'message': f"Múltiples estados iniciales en '{nombre}'", 'tipo': 'semántico'})

        # Validar que todos los símbolos del alfabeto sean de un solo carácter
        for simbolo in alfabeto:
            if not isinstance(simbolo, str) or len(simbolo) != 1:
                errores.append({'message': f"Símbolo inválido '{simbolo}' en alphabet en '{nombre}'. Cada símbolo debe ser un solo carácter.", 'tipo': 'semántico'})

        for simbolo in stack_alphabet:
            if not isinstance(simbolo, str) or len(simbolo) != 1:
                errores.append({'message': f"Símbolo inválido '{simbolo}' en stack_alphabet en '{nombre}'. Cada símbolo debe ser un solo carácter.", 'tipo': 'semántico'})

        for simbolo in tape_alphabet:
            if not isinstance(simbolo, str) or len(simbolo) != 1:
                errores.append({'message': f"Símbolo inválido '{simbolo}' en tape_alphabet en '{nombre}'. Cada símbolo debe ser un solo carácter.", 'tipo': 'semántico'})

        # Transiciones
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

                if tipo in ['DFA', 'NFA'] and attr_name in ['pop', 'push', 'read', 'write', 'move']:
                    errores.append({'message': f"Atributo '{attr_name}' no permitido en transición de un {tipo} ('{nombre}')", 'tipo': 'semántico'})
                    continue 

                if tipo == 'PDA' and attr_name in ['read', 'write', 'move']:
                    errores.append({'message': f"Atributo '{attr_name}' no permitido en transición de un PDA ('{nombre}')", 'tipo': 'semántico'})
                    continue

                if tipo == 'TM' and attr_name in ['pop', 'push']:
                    errores.append({'message': f"Atributo '{attr_name}' no permitido en transición de una TM ('{nombre}')", 'tipo': 'semántico'})
                    continue

                if attr_name in attr_names:
                    errores.append({'message': f"Atributo duplicado '{attr_name}' en transición de '{origen}' a '{destino}' en '{nombre}'", 'tipo': 'semántico'})
                attr_names.add(attr_name)
                if attr_name in ['input', 'read'] and attr_val not in alfabeto:
                    errores.append({'message': f"Símbolo '{attr_val}' en atributo '{attr_name}' no está en alphabet en '{nombre}'", 'tipo': 'semántico'})
                if attr_name in ['pop', 'push']:
                    # Permite EPSILON
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
                # Contar atributos de lectura o input
                if attr_name == 'input':
                    input_count += 1
                if attr_name == 'read':
                    read_count += 1
                # INPUT como identificador de atributo no conocido
                if attr_name not in ['input', 'pop', 'push', 'read', 'write', 'move']:
                    errores.append({'message': f"Atributo irreconocido '{attr_name}' en transición de '{origen}' a '{destino}' en '{nombre}'", 'tipo': 'semántico'})

                 # Validar que input, read, write sean de un solo carácter
                if attr_name in ['input', 'read', 'write']:
                    if not isinstance(attr_val, str) or len(attr_val) != 1:
                        errores.append({'message': f"El valor de '{attr_name}' en la transición de '{origen}' a '{destino}' debe ser un solo carácter en '{nombre}'", 'tipo': 'semántico'})
                    elif attr_val not in alfabeto and attr_name == 'input':
                        errores.append({'message': f"Símbolo '{attr_val}' en atributo '{attr_name}' no está en alphabet en '{nombre}'", 'tipo': 'semántico'})
                    elif attr_val not in tape_alphabet and attr_name in ['read', 'write']:
                        errores.append({'message': f"Símbolo '{attr_val}' en atributo '{attr_name}' no está en tape_alphabet en '{nombre}'", 'tipo': 'semántico'})

                # Validar push y pop en PDA
                if attr_name in ['pop', 'push']:
                    if isinstance(attr_val, str) and attr_val.upper() == 'EPSILON':
                        continue
                    for simbolo in attr_val:
                        if len(simbolo) != 1:
                            errores.append({'message': f"Símbolo '{simbolo}' en atributo '{attr_name}' no es un solo carácter en '{nombre}'", 'tipo': 'semántico'})
                        if simbolo not in stack_alphabet:
                            errores.append({'message': f"Símbolo '{simbolo}' en atributo '{attr_name}' no está en stack_alphabet en '{nombre}'", 'tipo': 'semántico'})

            if input_count > 1 or read_count > 1:
                errores.append({'message': f"Transición de '{origen}' a '{destino}' tiene múltiples atributos de lectura/input en '{nombre}'", 'tipo': 'semántico'})
            # Transiciones incompletas para TM
            if tipo == 'TM':
                required = {'read', 'write', 'move'}
                attrs = set(a[0] for a in atributos)
                if not required.issubset(attrs):
                    errores.append({'message': f"Transición de TM de '{origen}' a '{destino}' incompleta (faltan atributos obligatorios) en '{nombre}'", 'tipo': 'semántico'})
    return errores