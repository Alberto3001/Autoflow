# GeneradorEnsambladorEmu8086.py

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
    asm_code += "    input_buffer db 255, ?, 255 dup('$')\n"
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

    # Tabla de estados de aceptación
    asm_code += "    accept_states_list db "
    asm_code += ', '.join(str(idx) for idx in accept_state_indices)
    asm_code += ", -1\n"

    # Tabla de transiciones
    if tipo_automata in ('DFA', 'NFA'):
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
        asm_code += "    pda_stack dw 256 dup(0)\n"
        asm_code += "    sp_offset dw 0\n"
        asm_code += "    pda_transitions db "
        trans_lines = []
        for c in cuadruplas:
            if c[0] == 'ADD_PDA_TRANSITION':
                origen_idx = state_map.get(c[1], -1)
                destino_idx = state_map.get(c[2], -1)
                input_char = c[3].get('input', '')
                pop_symbol = c[3].get('pop', '')
                push_symbols = c[3].get('push', '')
                push_len = len(push_symbols)
                push_bytes = ', '.join([f"'{s}'" for s in push_symbols]) if push_len > 0 else "0"
                if origen_idx != -1 and destino_idx != -1:
                    trans_lines.append(f"{origen_idx}, '{input_char}', '{pop_symbol}', {destino_idx}, {push_len}, {push_bytes}")
        asm_code += ', '.join(trans_lines) + ", -1\n"
    elif tipo_automata == 'TM':
        asm_code += f"    tm_tape db 256 dup('{blank_symbol}')\n"
        asm_code += "    tm_head_ptr dw 0\n"
        asm_code += f"    blank_symbol db '{blank_symbol}'\n"
        asm_code += "    tm_transitions db "
        trans_lines = []
        for c in cuadruplas:
            if c[0] == 'ADD_TM_TRANSITION':
                origen_idx = state_map.get(c[1], -1)
                destino_idx = state_map.get(c[2], -1)
                read_char = c[3].get('read', '')
                write_char = c[3].get('write', '')
                move_dir = 0
                if c[3].get('move', '') == 'R': move_dir = 1
                elif c[3].get('move', '') == 'S': move_dir = 2
                if origen_idx != -1 and destino_idx != -1:
                    trans_lines.append(f"{origen_idx}, '{read_char}', '{write_char}', {move_dir}, {destino_idx}")
        asm_code += ', '.join(trans_lines) + ", -1\n"

    # ===================
    # Sección de código
    # ===================
    asm_code += "\n.code\n"
    asm_code += "main proc\n"
    asm_code += "    mov ax, @data\n"
    asm_code += "    mov ds, ax\n"
    asm_code += "    mov es, ax\n\n"
    asm_code += "    mov ah, 09h\n"
    asm_code += "    mov dx, offset input_prompt\n"
    asm_code += "    int 21h\n\n"
    asm_code += "    mov ah, 0Ah\n"
    asm_code += "    mov dx, offset input_buffer\n"
    asm_code += "    int 21h\n\n"
    asm_code += f"    mov al, {initial_state_idx}\n"
    asm_code += "    mov [current_state], al\n"
    asm_code += "    mov word [input_ptr], 0\n\n"
    asm_code += "simulation_loop:\n"
    asm_code += "    mov cl, [input_buffer + 1]\n"
    asm_code += "    mov ch, 0\n"
    asm_code += "    cmp word [input_ptr], cx\n"
    asm_code += "    jge end_simulation\n\n"
    asm_code += "    mov al, [current_state]\n"
    asm_code += "    mov bx, [input_ptr]\n"
    asm_code += "    mov bl, [input_buffer + 2 + bx]\n\n"
    if tipo_automata in ('DFA', 'NFA'):
        asm_code += "    mov si, offset dfa_transitions\n"
        asm_code += "find_transition_loop:\n"
        asm_code += "    cmp byte [si], -1\n"
        asm_code += "    je reject_no_transition\n"
        asm_code += "    cmp byte [si], al\n"
        asm_code += "    jne next_dfa_entry\n"
        asm_code += "    cmp byte [si+1], bl\n"
        asm_code += "    jne next_dfa_entry\n"
        asm_code += "    mov al, [si+2]\n"
        asm_code += "    mov [current_state], al\n"
        asm_code += "    inc word [input_ptr]\n"
        asm_code += "    jmp simulation_loop\n"
        asm_code += "next_dfa_entry:\n"
        asm_code += "    add si, 3\n"
        asm_code += "    jmp find_transition_loop\n\n"
        asm_code += "reject_no_transition:\n"
        asm_code += "    jmp reject_final\n"
    elif tipo_automata == 'PDA':
        # Lógica de simulación para PDA
        asm_code += "    mov si, offset pda_transitions\n"
        asm_code += "    mov bx, [input_ptr]\n"
        asm_code += "    mov bl, [input_buffer + 2 + bx]\n"  # bl = input actual
        asm_code += "    mov di, [sp_offset]\n"
        asm_code += "    mov dl, [pda_stack + di - 1]\n"  # dl = tope de la pila
        asm_code += "find_pda_transition:\n"
        asm_code += "    cmp byte [si], -1\n"
        asm_code += "    je reject_no_transition\n"
        asm_code += "    cmp byte [si], al\n"
        asm_code += "    jne next_pda_entry\n"
        asm_code += "    cmp byte [si+1], bl\n"
        asm_code += "    jne next_pda_entry\n"
        asm_code += "    cmp byte [si+2], dl\n"
        asm_code += "    jne next_pda_entry\n"
        asm_code += "    mov al, [si+3]\n"
        asm_code += "    mov [current_state], al\n"
        asm_code += "    dec word [sp_offset]\n"
        asm_code += "    mov cl, [si+4]\n"
        asm_code += "    cmp cl, 0\n"
        asm_code += "    je skip_push\n"
        asm_code += "    mov bx, [sp_offset]\n"
        asm_code += "    mov di, si\n"
        asm_code += "    add di, 5\n"
        asm_code += "push_loop:\n"
        asm_code += "    mov dl, [di]\n"
        asm_code += "    mov [pda_stack + bx], dl\n"
        asm_code += "    inc bx\n"
        asm_code += "    inc di\n"
        asm_code += "    dec cl\n"
        asm_code += "    jnz push_loop\n"
        asm_code += "    mov [sp_offset], bx\n"
        asm_code += "skip_push:\n"
        asm_code += "    inc word [input_ptr]\n"
        asm_code += "    jmp simulation_loop\n"
        asm_code += "next_pda_entry:\n"
        asm_code += "    mov cl, [si+4]\n"
        asm_code += "    add si, 5\n"
        asm_code += "    add si, cx\n"
        asm_code += "    jmp find_pda_transition\n"
        asm_code += "reject_no_transition:\n"
        asm_code += "    jmp reject_final\n"
    elif tipo_automata == 'TM':
        # Lógica de simulación para TM
        asm_code += "    mov bx, [tm_head_ptr]\n"
        asm_code += "    mov dl, [tm_tape + bx]\n"
        asm_code += "    mov si, offset tm_transitions\n"
        asm_code += "find_tm_transition:\n"
        asm_code += "    cmp byte [si], -1\n"
        asm_code += "    je reject_no_transition\n"
        asm_code += "    cmp byte [si], al\n"
        asm_code += "    jne next_tm_entry\n"
        asm_code += "    cmp byte [si+1], dl\n"
        asm_code += "    jne next_tm_entry\n"
        asm_code += "    mov dl, [si+2]\n"
        asm_code += "    mov [tm_tape + bx], dl\n"
        asm_code += "    mov cl, [si+3]\n"
        asm_code += "    cmp cl, 0\n"
        asm_code += "    je move_left\n"
        asm_code += "    cmp cl, 1\n"
        asm_code += "    je move_right\n"
        asm_code += "    jmp tm_move_done\n"
        asm_code += "move_left:\n"
        asm_code += "    dec word [tm_head_ptr]\n"
        asm_code += "    jmp tm_move_done\n"
        asm_code += "move_right:\n"
        asm_code += "    inc word [tm_head_ptr]\n"
        asm_code += "tm_move_done:\n"
        asm_code += "    mov al, [si+4]\n"
        asm_code += "    mov [current_state], al\n"
        asm_code += "    jmp simulation_loop\n"
        asm_code += "next_tm_entry:\n"
        asm_code += "    add si, 5\n"
        asm_code += "    jmp find_tm_transition\n"
        asm_code += "reject_no_transition:\n"
        asm_code += "    jmp reject_final\n"
    asm_code += "end_simulation:\n"
    asm_code += "    mov al, [current_state]\n"
    asm_code += "    mov bx, 0\n"
    asm_code += "check_accept_loop:\n"
    asm_code += "    mov si, offset accept_states_list\n"
    asm_code += "    add si, bx\n"
    asm_code += "    cmp byte [si], -1\n"
    asm_code += "    je reject_final\n"
    asm_code += "    cmp byte [si], al\n"
    asm_code += "    je accept_final\n"
    asm_code += "    add bx, 1\n"
    asm_code += "    jmp check_accept_loop\n"
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