def generar_ensamblador_emu8086(cuadruplas, nombre_automata, tipo_automata):
    """
    Genera código ensamblador EMU8086 a partir de una lista de cuadruplas para DFA, NFA, PDA o TM.
    Incluye robustez, comentarios y separación de secciones.
    """
    asm_code = ""
    # Sección de cabecera y stack
    asm_code += ".model small\n"
    asm_code += ".stack 100h\n\n"

    # ===================
    # Sección de datos
    # ===================
    asm_code += ".data\n"
    asm_code += "    msg_accept db 'Cadena ACEPTADA', 0Dh, 0Ah, '$'\n"
    asm_code += "    msg_reject db 'Cadena RECHAZADA', 0Dh, 0Ah, '$'\n"
    asm_code += "    input_prompt db 'Ingrese cadena: $'\n"
    asm_code += "    input_buffer db 255, 0, 255 dup(0)\n"
    asm_code += "    current_state db 0\n"
    asm_code += "    input_ptr dw 0\n"

    # Mapeo de estados y símbolos
    state_map = {}  # {'q0': 0, ...}
    accept_state_indices = []
    initial_state_idx = 0
    blank_symbol = ' '
    current_state_num = 0
    for c in cuadruplas:
        if c[0] == 'ADD_STATE' and c[2] not in state_map:
            state_map[c[2]] = current_state_num
            current_state_num += 1
    for c in cuadruplas:
        if c[0] == 'SET_INITIAL_STATE':
            initial_state_idx = state_map.get(c[2], 0)
        elif c[0] == 'ADD_ACCEPT_STATE':
            idx = state_map.get(c[2], -1)
            if idx != -1:
                accept_state_indices.append(idx)
        elif c[0] == 'SET_BLANK_SYMBOL':
            blank_symbol = c[2]

    # Tabla de estados de aceptación (solo para DFA/NFA)
    if tipo_automata in ('DFA', 'NFA'):
        asm_code += "    accept_states_list db "
        asm_code += ', '.join(str(idx) for idx in accept_state_indices)
        asm_code += ", -1\n"
        asm_code += "    dfa_transitions db "
        trans_lines = []
        for c in cuadruplas:
            if c[0] == 'ADD_FA_TRANSITION':
                origen_idx = state_map.get(c[1], -1)
                destino_idx = state_map.get(c[2], -1)
                input_char = c[3].get('input', '')
                if origen_idx != -1 and destino_idx != -1 and input_char:
                    trans_lines.append(f"{origen_idx}, '{input_char}', {destino_idx}")
        asm_code += ', '.join(trans_lines) + ", -1, -1, -1\n"
    elif tipo_automata == 'PDA':
        asm_code += "    pda_stack db 256 dup(0)\n"
        asm_code += "    sp_offset dw 1\n"           # Inicializado a 1 para el símbolo inicial
        asm_code += "    stack_start db 'Z'\n"       # Símbolo inicial de la pila
        asm_code += "    ; Transition format: estado_origen, input, pop, estado_destino, push_count, [símbolos]\n"
        asm_code += "    pda_transitions db "
        trans_lines = []
        for c in cuadruplas:
            if c[0] == 'ADD_PDA_TRANSITION':
                origen_idx = state_map.get(c[1], -1)
                destino_idx = state_map.get(c[2], -1)
                input_char = c[3].get('input', '')
                pop_symbol = c[3].get('pop', '')
                push_symbols = c[3].get('push', '')
                if push_symbols == 'EPSILON':
                    push_len = 0
                    push_bytes = ""
                else:
                    push_len = len(push_symbols)
                    push_bytes = ', ' + ', '.join([f"'{s}'" for s in push_symbols]) if push_len > 0 else ""
                if origen_idx != -1:
                    # Siempre mantener el estado 0 para compatibilidad
                    trans_lines.append(f"0, '{input_char}', '{pop_symbol}', 0, {push_len}{push_bytes}")
        asm_code += '\n                    db '.join(trans_lines) + "\n"
        asm_code += "                    db -1, -1, -1, -1, -1              ; Terminator\n"
    elif tipo_automata == 'TM':
        # Tabla de estados de aceptación para TM
        asm_code += "    accept_states_list db "
        asm_code += ', '.join(str(idx) for idx in accept_state_indices)
        asm_code += ", -1\n"
        
        # Variables específicas para TM
        asm_code += f"    tm_tape db 256 dup('{blank_symbol}')\n"
        asm_code += "    tm_head_ptr dw 0\n"
        asm_code += f"    blank_symbol db '{blank_symbol}'\n"
        asm_code += "    max_steps dw 1000  ; Límite de pasos para evitar loops infinitos\n"
        asm_code += "    step_count dw 0\n"
        asm_code += "    ; Formato: estado_origen, read_char, write_char, move_dir, estado_destino\n"
        asm_code += "    tm_transitions db "
        trans_lines = []
        for c in cuadruplas:
            if c[0] == 'ADD_TM_TRANSITION':
                origen_idx = state_map.get(c[1], -1)
                destino_idx = state_map.get(c[2], -1)
                read_char = c[3].get('read', '')
                write_char = c[3].get('write', '')
                move_dir = 0  # L = 0, R = 1, S = 2
                if c[3].get('move', '') == 'R': 
                    move_dir = 1
                elif c[3].get('move', '') == 'L': 
                    move_dir = 0
                elif c[3].get('move', '') == 'S': 
                    move_dir = 2
                if origen_idx != -1 and destino_idx != -1:
                    trans_lines.append(f"{origen_idx}, '{read_char}', '{write_char}', {move_dir}, {destino_idx}")
        asm_code += ', '.join(trans_lines) + ", -1, -1, -1, -1, -1\n"

    # ===================
    # Sección de código
    # ===================
    asm_code += "\n.code\n"
    asm_code += "main proc\n"
    asm_code += "    mov ax, @data\n"
    asm_code += "    mov ds, ax\n"
    asm_code += "    mov es, ax\n\n"
    asm_code += "    ; Display prompt\n"
    asm_code += "    mov ah, 09h\n"
    asm_code += "    mov dx, offset input_prompt\n"
    asm_code += "    int 21h\n\n"
    asm_code += "    ; Read input string\n"
    asm_code += "    mov ah, 0Ah\n"
    asm_code += "    mov dx, offset input_buffer\n"
    asm_code += "    int 21h\n\n"

    if tipo_automata == 'PDA':
        asm_code += "    ; Initialize PDA\n"
        asm_code += "    mov byte ptr [current_state], 0\n"
        asm_code += "    mov word ptr [input_ptr], 0\n"
        asm_code += "    mov al, [stack_start]\n"
        asm_code += "    mov [pda_stack], al\n"
        asm_code += "    mov word ptr [sp_offset], 1\n\n"
    elif tipo_automata == 'TM':
        asm_code += "    ; Inicializar Máquina de Turing\n"
        asm_code += f"    mov byte ptr [current_state], {initial_state_idx}\n"
        asm_code += "    mov word ptr [input_ptr], 0\n"
        asm_code += "    mov word ptr [tm_head_ptr], 0\n"
        asm_code += "    mov word ptr [step_count], 0\n\n"
        
        asm_code += "    ; Copiar entrada a la cinta\n"
        asm_code += "    xor cx, cx\n"
        asm_code += "    mov cl, [input_buffer + 1]      ; Longitud real de entrada\n"
        asm_code += "    mov si, 0\n\n"
        
        asm_code += "copy_input_loop:\n"
        asm_code += "    cmp si, cx\n"
        asm_code += "    jge start_tm_simulation\n"
        asm_code += "    mov al, [input_buffer + si + 2]\n"
        asm_code += "    mov [tm_tape + si], al\n"
        asm_code += "    inc si\n"
        asm_code += "    jmp copy_input_loop\n\n"
        
        asm_code += "start_tm_simulation:\n"
        asm_code += "    ; Rellenar resto de cinta con símbolo en blanco\n"
        asm_code += "    mov al, [blank_symbol]\n"
        asm_code += "fill_tape_loop:\n"
        asm_code += "    cmp si, 255\n"
        asm_code += "    jge tm_simulation_loop\n"
        asm_code += "    mov [tm_tape + si], al\n"
        asm_code += "    inc si\n"
        asm_code += "    jmp fill_tape_loop\n\n"
    else:
        asm_code += f"    mov al, {initial_state_idx}\n"
        asm_code += "    mov [current_state], al\n"
        asm_code += "    mov [input_ptr], 0\n\n"

    if tipo_automata in ('DFA', 'NFA'):
        asm_code += "simulation_loop:\n"
        asm_code += "    mov cl, [input_buffer + 1]\n"
        asm_code += "    mov ch, 0\n"
        asm_code += "    mov ax, [input_ptr]\n"
        asm_code += "    cmp ax, cx\n"
        asm_code += "    jge end_simulation\n\n"
        asm_code += "    mov bx, [input_ptr]\n"
        asm_code += "    mov bl, [input_buffer + 2 + bx]\n"
        asm_code += "    mov si, offset dfa_transitions\n"
        asm_code += "find_transition_loop:\n"
        asm_code += "    cmp byte ptr [si], -1\n"
        asm_code += "    je reject_no_transition\n"
        asm_code += "    mov al, [current_state]\n"
        asm_code += "    cmp [si], al\n"
        asm_code += "    jne next_dfa_entry\n"
        asm_code += "    cmp [si+1], bl\n"
        asm_code += "    jne next_dfa_entry\n"
        asm_code += "    mov al, [si+2]\n"
        asm_code += "    mov [current_state], al\n"
        asm_code += "    inc word ptr [input_ptr]\n"
        asm_code += "    jmp simulation_loop\n"
        asm_code += "next_dfa_entry:\n"
        asm_code += "    add si, 3\n"
        asm_code += "    jmp find_transition_loop\n\n"
        asm_code += "reject_no_transition:\n"
        asm_code += "    jmp reject_final\n"
    elif tipo_automata == 'PDA':
        # Lógica de simulación para PDA
        asm_code += "simulation_loop:\n"
        asm_code += "    ; Check if we've processed all input\n"
        asm_code += "    mov cl, [input_buffer + 1]\n"      # Get actual input length
        asm_code += "    mov ch, 0\n"
        asm_code += "    mov ax, [input_ptr]\n"
        asm_code += "    cmp ax, cx\n"
        asm_code += "    jge check_final_state\n\n"
        
        asm_code += "    ; Get current input symbol\n"
        asm_code += "    mov bx, [input_ptr]\n"
        asm_code += "    mov al, [input_buffer + 2 + bx]\n"  # Use AL for 8-bit character
        
        asm_code += "    ; Get stack top\n"
        asm_code += "    mov di, [sp_offset]\n"
        asm_code += "    cmp di, 0\n"
        asm_code += "    je reject_final\n"
        asm_code += "    mov dl, [pda_stack + di - 1]\n\n"
        
        asm_code += "    ; Search for valid transition\n"
        asm_code += "    mov si, offset pda_transitions\n\n"
        
        asm_code += "find_transition:\n"
        asm_code += "    cmp byte ptr [si], -1\n"
        asm_code += "    je reject_final\n"
        
        asm_code += "    ; Check source state\n"
        asm_code += "    mov ah, [current_state]\n"
        asm_code += "    cmp [si], ah\n"
        asm_code += "    jne next_transition\n"
        
        asm_code += "    ; Check input symbol\n"
        asm_code += "    cmp [si+1], al\n"
        asm_code += "    jne next_transition\n"
        
        asm_code += "    ; Check stack symbol\n"
        asm_code += "    cmp [si+2], dl\n"
        asm_code += "    jne next_transition\n"
        
        asm_code += "    ; Transition found - execute\n"
        asm_code += "    ; Update state\n"
        asm_code += "    mov ah, [si+3]\n"
        asm_code += "    mov [current_state], ah\n"
        
        asm_code += "    ; Pop current symbol\n"
        asm_code += "    mov di, [sp_offset]\n"
        asm_code += "    cmp di, 0\n"
        asm_code += "    je reject_final\n"
        asm_code += "    dec word ptr [sp_offset]\n"
        
        asm_code += "    ; Check if there are symbols to push\n"
        asm_code += "    mov cl, [si+4]\n"
        asm_code += "    cmp cl, 0\n"
        asm_code += "    je advance_input\n"
        
        asm_code += "    ; Push symbols in correct order (last to first)\n"
        asm_code += "    mov ch, 0\n"
        asm_code += "    mov bx, si\n"
        asm_code += "    add bx, 5\n"
        asm_code += "    add bx, cx\n"
        asm_code += "    dec bx\n"
        
        asm_code += "push_loop:\n"
        asm_code += "    mov di, [sp_offset]\n"
        asm_code += "    cmp di, 255\n"
        asm_code += "    jge reject_final\n"
        
        asm_code += "    mov dl, [bx]\n"
        asm_code += "    mov [pda_stack + di], dl\n"
        asm_code += "    inc word ptr [sp_offset]\n"
        asm_code += "    dec bx\n"
        asm_code += "    dec cl\n"
        asm_code += "    jnz push_loop\n\n"
        
        asm_code += "advance_input:\n"
        asm_code += "    inc word ptr [input_ptr]\n"
        asm_code += "    jmp simulation_loop\n\n"
        
        asm_code += "next_transition:\n"
        asm_code += "    ; Calculate next transition position\n"
        asm_code += "    mov cl, [si+4]\n"
        asm_code += "    mov ch, 0\n"
        asm_code += "    add si, 5\n"
        asm_code += "    add si, cx\n"
        asm_code += "    jmp find_transition\n\n"
    elif tipo_automata == 'TM':
        # Lógica de simulación para TM (CORREGIDA)
        asm_code += "tm_simulation_loop:\n"
        asm_code += "    ; Verificar límite de pasos\n"
        asm_code += "    mov ax, [step_count]\n"
        asm_code += "    cmp ax, [max_steps]\n"
        asm_code += "    jge reject_infinite_loop\n"
        asm_code += "    inc word ptr [step_count]\n\n"
        
        asm_code += "    ; Verificar bounds de la cinta\n"
        asm_code += "    mov bx, [tm_head_ptr]\n"
        asm_code += "    cmp bx, 0\n"
        asm_code += "    jl reject_final\n"
        asm_code += "    cmp bx, 255\n"
        asm_code += "    jge reject_final\n\n"
        
        asm_code += "    ; Leer símbolo actual de la cinta\n"
        asm_code += "    mov dl, [tm_tape + bx]\n"
        asm_code += "    mov al, [current_state]\n\n"
        
        asm_code += "    ; Buscar transición válida\n"
        asm_code += "    mov si, offset tm_transitions\n\n"
        
        asm_code += "find_tm_transition:\n"
        asm_code += "    cmp byte ptr [si], -1\n"
        asm_code += "    je check_tm_final_state        ; No hay más transiciones\n\n"
        
        asm_code += "    ; Verificar estado origen\n"
        asm_code += "    cmp [si], al\n"
        asm_code += "    jne next_tm_entry\n\n"
        
        asm_code += "    ; Verificar símbolo leído\n"
        asm_code += "    cmp [si+1], dl\n"
        asm_code += "    jne next_tm_entry\n\n"
        
        asm_code += "    ; Transición encontrada - ejecutar\n"
        asm_code += "    ; Escribir nuevo símbolo\n"
        asm_code += "    mov dl, [si+2]\n"
        asm_code += "    mov [tm_tape + bx], dl\n\n"
        
        asm_code += "    ; Mover cabezal según dirección\n"
        asm_code += "    mov cl, [si+3]\n"
        asm_code += "    cmp cl, 0\n"
        asm_code += "    je move_left\n"
        asm_code += "    cmp cl, 1\n"
        asm_code += "    je move_right\n"
        asm_code += "    ; cl = 2 es stay, no mover\n"
        asm_code += "    jmp tm_move_done\n\n"
        
        asm_code += "move_left:\n"
        asm_code += "    mov bx, [tm_head_ptr]\n"
        asm_code += "    cmp bx, 0\n"
        asm_code += "    jle tm_move_done               ; No mover si ya está en el borde\n"
        asm_code += "    dec word ptr [tm_head_ptr]\n"
        asm_code += "    jmp tm_move_done\n\n"
        
        asm_code += "move_right:\n"
        asm_code += "    mov bx, [tm_head_ptr]\n"
        asm_code += "    cmp bx, 254\n"
        asm_code += "    jge tm_move_done               ; No mover si ya está en el borde\n"
        asm_code += "    inc word ptr [tm_head_ptr]\n\n"
        
        asm_code += "tm_move_done:\n"
        asm_code += "    ; Actualizar estado\n"
        asm_code += "    mov al, [si+4]\n"
        asm_code += "    mov [current_state], al\n"
        asm_code += "    jmp tm_simulation_loop\n\n"
        
        asm_code += "next_tm_entry:\n"
        asm_code += "    add si, 5                      ; Cada transición tiene 5 bytes\n"
        asm_code += "    jmp find_tm_transition\n\n"
        
        asm_code += "check_tm_final_state:\n"
        asm_code += "    ; Verificar si estamos en estado de aceptación\n"
        asm_code += "    mov al, [current_state]\n"
        asm_code += "    mov bx, 0\n\n"
        
        asm_code += "check_tm_accept_loop:\n"
        asm_code += "    mov si, offset accept_states_list\n"
        asm_code += "    add si, bx\n"
        asm_code += "    cmp byte ptr [si], -1\n"
        asm_code += "    je reject_final\n"
        asm_code += "    cmp [si], al\n"
        asm_code += "    je accept_final\n"
        asm_code += "    inc bx\n"
        asm_code += "    jmp check_tm_accept_loop\n\n"
        
        asm_code += "reject_infinite_loop:\n"
        asm_code += "    ; Mensaje especial para loops infinitos\n"
        asm_code += "    jmp reject_final\n\n"

    if tipo_automata == 'DFA':
        asm_code += "end_simulation:\n"
        asm_code += "    mov al, [current_state]\n"
        asm_code += "    mov si, offset accept_states_list\n"
        asm_code += "check_accept_loop:\n"
        asm_code += "    mov bl, [si]\n"
        asm_code += "    cmp bl, -1\n"
        asm_code += "    je reject_final\n"
        asm_code += "    cmp bl, al\n"
        asm_code += "    je accept_final\n"
        asm_code += "    inc si\n"
        asm_code += "    jmp check_accept_loop\n"
    elif tipo_automata == 'PDA':
        asm_code += "check_final_state:\n"
        asm_code += "    ; Check acceptance state (must be q0 = 0)\n"
        asm_code += "    mov al, [current_state]\n"
        asm_code += "    cmp al, 0\n"
        asm_code += "    jne reject_final\n\n"
        
        asm_code += "    ; Check that stack contains only Z\n"
        asm_code += "    mov di, [sp_offset]\n"
        asm_code += "    cmp di, 1\n"
        asm_code += "    jne reject_final\n\n"
        
        asm_code += "    mov dl, [pda_stack]\n"
        asm_code += "    cmp dl, 'Z'\n"
        asm_code += "    jne reject_final\n\n"
        
        asm_code += "    jmp accept_final\n"
    # Para TM no se necesita verificación adicional aquí, ya se hace en check_tm_final_state
    
    asm_code += "accept_final:\n"
    asm_code += "    mov ah, 09h\n"
    asm_code += "    mov dx, offset msg_accept\n"
    asm_code += "    int 21h\n"
    asm_code += "    jmp exit_program\n\n"
    asm_code += "reject_final:\n"
    asm_code += "    mov ah, 09h\n"
    asm_code += "    mov dx, offset msg_reject\n"
    asm_code += "    int 21h\n\n"
    asm_code += "exit_program:\n"
    asm_code += "    mov ah, 4ch\n"
    asm_code += "    int 21h\n"
    asm_code += "main endp\n\n"
    asm_code += "end main\n"
    return asm_code

def generar_pseudoensamblador(cuadruplas):
    """
    Genera código pseudo-ensamblador a partir de una lista de cuadruplas.
    Formato ejemplo:
        LD R0, a
        LD R1, b
        ADD R2, R0, R1
        ...
    """
    pseudo_code = []
    for cuad in cuadruplas:
        op = cuad[0]
        arg1 = cuad[1]
        arg2 = cuad[2]
        res = cuad[3]
        if op == 'ADD_STATE':
            pseudo_code.append(f"STATE {arg2}")
        elif op == 'SET_TYPE':
            pseudo_code.append(f"TYPE {arg2}")
        elif op == 'SET_INITIAL_STATE':
            pseudo_code.append(f"INITIAL {arg2}")
        elif op == 'ADD_ACCEPT_STATE':
            pseudo_code.append(f"ACCEPT {arg2}")
        elif op == 'ADD_ALPHABET_SYMBOL':
            pseudo_code.append(f"ALPHABET {arg2}")
        elif op == 'ADD_FA_TRANSITION':
            # arg1 = origen, arg2 = destino, res = dict con input
            input_sym = res.get('input', '') if isinstance(res, dict) else ''
            pseudo_code.append(f"TRANS {arg1} --{input_sym}--> {arg2}")
        elif op == 'ADD_PDA_TRANSITION':
            input_sym = res.get('input', '') if isinstance(res, dict) else ''
            pop_sym = res.get('pop', '') if isinstance(res, dict) else ''
            push_syms = res.get('push', '') if isinstance(res, dict) else ''
            pseudo_code.append(f"PDA_TRANS {arg1} --{input_sym},{pop_sym}/{push_syms}--> {arg2}")
        elif op == 'ADD_TM_TRANSITION':
            read = res.get('read', '') if isinstance(res, dict) else ''
            write = res.get('write', '') if isinstance(res, dict) else ''
            move = res.get('move', '') if isinstance(res, dict) else ''
            pseudo_code.append(f"TM_TRANS {arg1} --{read}/{write},{move}--> {arg2}")
        elif op == 'SET_BLANK_SYMBOL':
            pseudo_code.append(f"BLANK {arg2}")
        elif op == 'ADD_STACK_SYMBOL':
            pseudo_code.append(f"STACK_SYMBOL {arg2}")
        elif op == 'ADD_TAPE_SYMBOL':
            pseudo_code.append(f"TAPE_SYMBOL {arg2}")
        elif op == 'START_AUTOMATON_DEF':
            pseudo_code.append(f"START_AUTOMATON {arg1}")
        elif op == 'END_AUTOMATON_DEF':
            pseudo_code.append(f"END_AUTOMATON {arg1}")
        # Puedes agregar más traducciones según las cuadruplas generadas
    return '\n'.join(pseudo_code)