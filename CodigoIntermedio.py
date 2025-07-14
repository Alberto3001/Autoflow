def generar_tripletas_cuadruplas(ast):
    tripletas = []
    cuadruplas = []
    instruccion_num = 1

    for automata in ast:
        if automata[0] != 'automaton':
            continue

        nombre_automata = automata[1]
        definicion_automa = automata[2] # ('definicion', propiedades, transiciones_def)

        propiedades_ast = definicion_automa[1]
        # Asegúrate de extraer las transiciones correctamente, ya que es una tupla ('transitions', [lista])
        transiciones_ast = definicion_automa[2][1] if definicion_automa[2][0] == 'transitions' else []

        # --- Lógica de GENERACIÓN DE TRIPLETAS ---
        # Agrega una tripleta al inicio de cada autómata
        tripletas.append((instruccion_num, 'PARSE_AUTOMATON', nombre_automata, None))
        instruccion_num += 1

        # Itera sobre las propiedades para generar tripletas de identificación de elementos
        tripletas.append((instruccion_num, 'BEGIN_PROPERTIES', nombre_automata, None))
        instruccion_num += 1
        for prop in propiedades_ast:
            prop_key = prop[0]
            prop_value = prop[1]
            # Para propiedades que son conjuntos (alphabet, states, accept, etc.), itera sobre sus elementos.
            # Para otras propiedades (type, initial, blank), usa el valor directamente.
            if isinstance(prop_value, set): # Manejo de conjuntos
                for item in prop_value:
                    if prop_key == 'alphabet':
                        tripletas.append((instruccion_num, 'IDENTIFY_SYMBOL', item, 'ALPHABET'))
                        instruccion_num += 1
                    elif prop_key == 'tape_alphabet':
                        tripletas.append((instruccion_num, 'IDENTIFY_SYMBOL', item, 'TAPE_ALPHABET'))
                        instruccion_num += 1
                    elif prop_key == 'stack_alphabet':
                        tripletas.append((instruccion_num, 'IDENTIFY_SYMBOL', item, 'STACK_ALPHABET'))
                        instruccion_num += 1
                    elif prop_key == 'states':
                        tripletas.append((instruccion_num, 'IDENTIFY_STATE', item, None))
                        instruccion_num += 1
                    elif prop_key == 'accept':
                        tripletas.append((instruccion_num, 'IDENTIFY_ACCEPT', item, None))
                        instruccion_num += 1
            else: # Manejo de valores simples (type, initial, blank)
                if prop_key == 'type':
                    tripletas.append((instruccion_num, 'IDENTIFY_TYPE', prop_value, None))
                    instruccion_num += 1
                elif prop_key == 'initial':
                    tripletas.append((instruccion_num, 'IDENTIFY_INITIAL', prop_value, None))
                    instruccion_num += 1
                elif prop_key == 'blank':
                    tripletas.append((instruccion_num, 'IDENTIFY_BLANK', prop_value, None))
                    instruccion_num += 1
        tripletas.append((instruccion_num, 'END_PROPERTIES', nombre_automata, None))
        instruccion_num += 1

        # Itera sobre las transiciones para generar tripletas de enlaces y atributos identificados
        tripletas.append((instruccion_num, 'BEGIN_TRANSITIONS', nombre_automata, None))
        instruccion_num += 1
        for trans in transiciones_ast:
            origen = trans[1]
            destino = trans[2]
            atributos = trans[3] # Lista de tuplas (attr_name, attr_val)

            tripletas.append((instruccion_num, 'TRANSITION_LINK', origen, destino)) # Tripleta de enlace básico
            instruccion_num += 1

            for attr_name, attr_val in atributos:
                tripletas.append((instruccion_num, 'ATTR_VALUE', attr_name, attr_val)) # Tripleta de identificación de atributo/valor
                instruccion_num += 1
        tripletas.append((instruccion_num, 'END_TRANSITIONS', nombre_automata, None))
        instruccion_num += 1


        # --- Lógica de GENERACIÓN DE CUÁDRUPLOS ---
        # Cuádruplo para el inicio de la definición del autómata
        cuadruplas.append(('START_AUTOMATON_DEF', nombre_automata, None, None))

        # Itera sobre las propiedades para generar cuádruplos detallados de configuración
        for prop in propiedades_ast:
            prop_key = prop[0]
            prop_value = prop[1]

            if prop_key == 'type':
                cuadruplas.append(('SET_TYPE', nombre_automata, prop_value, None))
            elif prop_key == 'alphabet':
                for symbol in prop_value:
                    cuadruplas.append(('ADD_ALPHABET_SYMBOL', nombre_automata, symbol, 'ALPHABET_SET'))
            elif prop_key == 'tape_alphabet':
                for symbol in prop_value:
                    cuadruplas.append(('ADD_TAPE_SYMBOL', nombre_automata, symbol, 'TAPE_ALPHABET_SET'))
            elif prop_key == 'stack_alphabet':
                for symbol in prop_value:
                    cuadruplas.append(('ADD_STACK_SYMBOL', nombre_automata, symbol, 'STACK_ALPHABET_SET'))
            elif prop_key == 'states':
                for state in prop_value:
                    cuadruplas.append(('ADD_STATE', nombre_automata, state, 'STATES_SET'))
            elif prop_key == 'initial':
                cuadruplas.append(('SET_INITIAL_STATE', nombre_automata, prop_value, 'INITIAL_STATE_REF'))
            elif prop_key == 'accept':
                for state in prop_value:
                    cuadruplas.append(('ADD_ACCEPT_STATE', nombre_automata, state, 'ACCEPT_STATES_SET'))
            elif prop_key == 'blank':
                cuadruplas.append(('SET_BLANK_SYMBOL', nombre_automata, prop_value, 'BLANK_SYMBOL_REF'))

        # Obtener el tipo de autómata para generar el cuádruplo de transición específico
        tipo_automata = None
        for p_k, p_v in propiedades_ast:
            if p_k == 'type':
                tipo_automata = p_v
                break

        # Itera sobre las transiciones para generar cuádruplos completos de transición
        for trans in transiciones_ast:
            origen = trans[1]
            destino = trans[2]
            atributos_dict = {attr_name: attr_val for attr_name, attr_val in trans[3]} # Convertir a diccionario

            if tipo_automata == 'DFA' or tipo_automata == 'NFA':
                cuadruplas.append(('ADD_FA_TRANSITION', origen, destino, atributos_dict))
            elif tipo_automata == 'PDA':
                cuadruplas.append(('ADD_PDA_TRANSITION', origen, destino, atributos_dict))
            elif tipo_automata == 'TM':
                cuadruplas.append(('ADD_TM_TRANSITION', origen, destino, atributos_dict))
            else:
                cuadruplas.append(('ADD_GENERIC_TRANSITION', origen, destino, atributos_dict))

        # Cuádruplo para el fin de la definición del autómata
        cuadruplas.append(('END_AUTOMATON_DEF', nombre_automata, None, None))

    return tripletas, cuadruplas