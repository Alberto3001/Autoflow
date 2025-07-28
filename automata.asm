.model small
.stack 100h

.data
    msg_accept db 'ACEPTADA', 0Dh, 0Ah, '$'
    msg_reject db 'RECHAZADA', 0Dh, 0Ah, '$'
    input_prompt db 'Ingrese cadena: $'
    input_buffer db 255, 0, 255 dup(0)
    current_state db 0
    input_ptr dw 0
    lcd_port dw 2040h  ; Puerto del LCD ASCII
    accept_states_list db 2, -1
    dfa_transitions db 0, 'a', 1, 1, 'b', 2, 2, 'a', 2, 2, 'b', 1, -1, -1, -1

.code
main proc
    mov ax, @data
    mov ds, ax
    mov es, ax

    ; Display prompt
    mov ah, 09h
    mov dx, offset input_prompt
    int 21h

    ; Read input string
    mov ah, 0Ah
    mov dx, offset input_buffer
    int 21h

    mov al, 0
    mov [current_state], al
    mov [input_ptr], 0

simulation_loop:
    mov cl, [input_buffer + 1]
    mov ch, 0
    mov ax, [input_ptr]
    cmp ax, cx
    jge end_simulation

    mov bx, [input_ptr]
    mov bl, [input_buffer + 2 + bx]
    mov si, offset dfa_transitions
find_transition_loop:
    cmp byte ptr [si], -1
    je reject_no_transition
    mov al, [current_state]
    cmp [si], al
    jne next_dfa_entry
    cmp [si+1], bl
    jne next_dfa_entry
    mov al, [si+2]
    mov [current_state], al
    inc word ptr [input_ptr]
    jmp simulation_loop
next_dfa_entry:
    add si, 3
    jmp find_transition_loop

reject_no_transition:
    jmp reject_final
end_simulation:
    mov al, [current_state]
    mov si, offset accept_states_list
check_accept_loop:
    mov bl, [si]
    cmp bl, -1
    je reject_final
    cmp bl, al
    je accept_final
    inc si
    jmp check_accept_loop
accept_final:
    ; Mostrar salto de línea
    mov ah, 02h
    mov dl, 0Dh
    int 21h
    mov dl, 0Ah
    int 21h

    ; Mostrar palabra 'Cadena' y espacio
    mov ah, 02h
    mov dl, 'C'
    int 21h
    mov dl, 'a'
    int 21h
    mov dl, 'd'
    int 21h
    mov dl, 'e'
    int 21h
    mov dl, 'n'
    int 21h
    mov dl, 'a'
    int 21h
    mov dl, ' '
    int 21h

    ; Mostrar mensaje de aceptación
    mov ah, 09h
    mov dx, offset msg_accept
    int 21h

    ; Mostrar 'A' en LCD ASCII
    mov dx, [lcd_port]
    mov al, 'A'
    out dx, al
    jmp exit_program

reject_final:
    ; Mostrar salto de línea
    mov ah, 02h
    mov dl, 0Dh
    int 21h
    mov dl, 0Ah
    int 21h

    ; Mostrar palabra 'Cadena' y espacio
    mov ah, 02h
    mov dl, 'C'
    int 21h
    mov dl, 'a'
    int 21h
    mov dl, 'd'
    int 21h
    mov dl, 'e'
    int 21h
    mov dl, 'n'
    int 21h
    mov dl, 'a'
    int 21h
    mov dl, ' '
    int 21h

    ; Mostrar mensaje de rechazo
    mov ah, 09h
    mov dx, offset msg_reject
    int 21h

    ; Mostrar 'R' en LCD ASCII
    mov dx, [lcd_port]
    mov al, 'R'
    out dx, al

exit_program:
    mov ah, 4ch
    int 21h
main endp

end main
