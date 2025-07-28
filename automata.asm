.model small
.stack 100h

.data
    msg_accept db 'Cadena ACEPTADA', 0Dh, 0Ah, '$'
    msg_reject db 'Cadena RECHAZADA', 0Dh, 0Ah, '$'
    input_prompt db 'Ingrese cadena: $'
    input_buffer db 255, ?, 255 dup('$')
    current_state db 0
    input_ptr dw 0
    accept_states_list db 2, -1
    pda_stack db 256 dup(0)
    sp_offset dw 1
    stack_start db 'Z'
    last_char db 0
    pda_transitions db 0, 'a', 'Z', 1, 2, 'A', 'Z', 1, 'a', 'A', 1, 2, 'A', 'A', 1, 'b', 'A', 2, 0, 0, 2, 'b', 'A', 2, 0, 0, -1

.code
main proc
    mov ax, @data
    mov ds, ax
    mov es, ax

    mov ah, 09h
    mov dx, offset input_prompt
    int 21h

    mov ah, 0Ah
    mov dx, offset input_buffer
    int 21h

    mov al, 0
    mov [current_state], al
    mov [input_ptr], 0
    ; Inicializar la pila del PDA
    mov al, [stack_start]
    mov [pda_stack], al
    mov [sp_offset], 1

simulation_loop:
    mov cl, [input_buffer + 1]
    mov ch, 0
    cmp [input_ptr], cx
    jge check_final_state

find_transition:
    mov si, offset pda_transitions
    mov bx, [input_ptr]
    mov bl, [input_buffer + 2 + bx]
    mov di, [sp_offset]
    mov dl, byte [pda_stack + di - 1]
check_transition:
    cmp byte [si], -1
    je reject_final
    push dx
    push bx
    mov al, [current_state]
    cmp [si], al
    jne next_transition
    pop bx
    cmp [si+1], bl
    jne next_transition_with_pop
    pop dx
    cmp [si+2], dl
    jne next_transition
    mov al, [si+3]
    mov [current_state], al
    dec word ptr [sp_offset]
    mov cl, [si+4]
    cmp cl, 0
    je transition_complete
    mov di, [sp_offset]
    add si, 5
push_symbols:
    mov al, [si]
    inc di
    mov [pda_stack + di - 1], al
    inc si
    dec cl
    jnz push_symbols
    mov [sp_offset], di
transition_complete:
    inc word ptr [input_ptr]
    jmp simulation_loop
next_transition_with_pop:
    pop dx
next_transition:
    mov cl, [si+4]
    add si, 5
    add si, cx
    jmp check_transition

    mov al, [current_state]
    mov bx, [input_ptr]
    mov bl, [input_buffer + 2 + bx]

    ; Verificar si hemos llegado al fin de la entrada
    mov cx, [input_ptr]
    mov al, [input_buffer + 1]
    cmp cl, al
    jge check_final_state
    mov si, offset pda_transitions
    mov bx, [input_ptr]
    mov bl, [input_buffer + 2 + bx]
    mov di, [sp_offset]
    cmp di, 0
    je reject_final
    mov dl, byte [pda_stack + di - 1]
find_pda_transition:
    cmp byte [si], -1
    je reject_no_transition
    mov al, [current_state]
    cmp byte [si], al
    jne next_pda_entry
    cmp byte [si+1], bl
    jne next_pda_entry
    cmp byte [si+2], dl
    jne next_pda_entry
    mov al, [si+3]
    push ax
    mov cl, [si+4]
    push cx
    push si
    ; Hacer pop del símbolo actual
    dec di
    mov [sp_offset], di
    ; Verificar si hay símbolos para push
    pop si
    pop cx
    cmp cl, 0
    je update_state
    ; Hacer push de nuevos símbolos
    mov di, [sp_offset]
    add si, 5
    xor ch, ch
push_loop:
    mov dl, [si]
    inc di
    mov [pda_stack + di - 1], dl
    inc si
    dec cl
    jnz push_loop
    mov [sp_offset], di
update_state:
    pop ax
    mov [current_state], al
skip_push:
    inc [input_ptr]
    jmp simulation_loop
next_pda_entry:
    mov cl, [si+4]
    add si, 5
    add si, cx
    jmp find_pda_transition
reject_no_transition:
    jmp reject_final
check_final_state:
    ; Verificar que hayamos consumido toda la entrada
    mov cx, [input_ptr]
    mov al, [input_buffer + 1]
    cmp cl, al
    jl reject_final
end_simulation:
    mov al, [current_state]
    mov bx, 0
check_accept_loop:
    mov si, offset accept_states_list
    add si, bx
    cmp byte [si], -1
    je reject_final
    cmp byte [si], al
    je accept_final
    add bx, 1
    jmp check_accept_loop
accept_final:
    mov ah, 09h
    mov dx, offset msg_accept
    int 21h
    jmp exit_program

reject_final:
    mov ah, 09h
    mov dx, offset msg_reject
    int 21h

exit_program:
    mov ah, 4ch
    int 21h
main endp

end main
