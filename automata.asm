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
    dfa_transitions db 0, 'a', 1, 1, 'b', 2, 2, 'a', 2, 2, 'b', 1, -1, -1, -1

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
    mov word [input_ptr], 0

simulation_loop:
    mov cl, [input_buffer + 1]
    mov ch, 0
    cmp word [input_ptr], cx
    jge end_simulation

    mov al, [current_state]
    mov bx, [input_ptr]
    mov bl, [input_buffer + 2 + bx]

    mov si, offset dfa_transitions
find_transition_loop:
    cmp byte [si], -1
    je reject_no_transition
    cmp byte [si], al
    jne next_dfa_entry
    cmp byte [si+1], bl
    jne next_dfa_entry
    mov al, [si+2]
    mov [current_state], al
    inc word [input_ptr]
    jmp simulation_loop
next_dfa_entry:
    add si, 3
    jmp find_transition_loop

reject_no_transition:
    jmp reject_final
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
