                                      .model small
.stack 100h

.data
    msg_accept db 'Cadena ACEPTADA', 0Dh, 0Ah, '$'
    msg_reject db 'Cadena RECHAZADA', 0Dh, 0Ah, '$'
    input_prompt db 'Ingrese cadena: $'
    input_buffer db 255, ?, 255 dup('$')
    current_state db 0
    input_ptr dw 0
    accept_states_list db 0, -1
    pda_stack db 256 dup(0)
    sp_offset dw 1
    stack_start db 'Z'
    ; Transiciones corregidas - formato: estado_origen, input, pop, estado_destino, push_count, [símbolos]
    pda_transitions db 0, 'a', 'Z', 0, 2, 'A', 'Z'    ; q0 + a + Z -> q0, push AZ
                    db 0, 'a', 'A', 0, 2, 'A', 'A'    ; q0 + a + A -> q0, push AA  
                    db 0, 'a', 'B', 0, 0, 0            ; q0 + a + B -> q0, pop B
                    db 0, 'b', 'Z', 0, 2, 'B', 'Z'    ; q0 + b + Z -> q0, push BZ
                    db 0, 'b', 'B', 0, 2, 'B', 'B'    ; q0 + b + B -> q0, push BB
                    db 0, 'b', 'A', 0, 0, 0            ; q0 + b + A -> q0, pop A
                    db -1, -1, -1, -1, -1              ; Terminador

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

    ; Inicializar
    mov byte ptr [current_state], 0
    mov word ptr [input_ptr], 0
    mov al, [stack_start]
    mov [pda_stack], al
    mov word ptr [sp_offset], 1

simulation_loop:
    ; Verificar si terminamos la entrada
    mov cl, [input_buffer + 1]
    mov ch, 0
    mov ax, [input_ptr]
    cmp ax, cx
    jge check_final_state

    ; Obtener símbolo de entrada actual
    mov bx, [input_ptr]
    mov bl, [input_buffer + 2 + bx]
    
    ; Obtener tope de la pila
    mov di, [sp_offset]
    cmp di, 0
    je reject_final
    mov dl, [pda_stack + di - 1]

    ; Buscar transición válida
    mov si, offset pda_transitions

find_transition:
    cmp byte ptr [si], -1
    je reject_final
    
    ; Verificar estado origen
    mov al, [current_state]
    cmp [si], al
    jne next_transition
    
    ; Verificar símbolo de entrada  
    cmp [si+1], bl
    jne next_transition
    
    ; Verificar símbolo de pila
    cmp [si+2], dl
    jne next_transition
    
    ; Transición encontrada - ejecutar
    ; Actualizar estado
    mov al, [si+3]
    mov [current_state], al
    
    ; Pop del símbolo actual
    dec word ptr [sp_offset]
    
    ; Verificar si hay símbolos para push
    mov cl, [si+4]
    cmp cl, 0
    je advance_input
    
    ; Push de símbolos en orden correcto
    mov di, [sp_offset]
    mov ch, 0
    ; Calcular posición del último símbolo para push inverso
    mov bx, si
    add bx, 5
    add bx, cx
    dec bx  ; bx apunta al último símbolo

push_loop:
    mov dl, [bx]
    inc di
    mov [pda_stack + di - 1], dl
    dec bx
    dec cl
    jnz push_loop
    
    mov [sp_offset], di

advance_input:
    inc word ptr [input_ptr]
    jmp simulation_loop

next_transition:
    ; Calcular posición de siguiente transición
    mov cl, [si+4]  ; número de símbolos push
    mov ch, 0
    add si, 5       ; saltar cabecera
    add si, cx      ; saltar símbolos push
    jmp find_transition

check_final_state:
    ; Verificar estado de aceptación (debe ser q0 = 0)
    mov al, [current_state]
    cmp al, 0
    jne reject_final
    
    ; Verificar que la pila contenga solo Z
    mov di, [sp_offset]
    cmp di, 1
    jne reject_final
    
    mov dl, [pda_stack]
    cmp dl, 'Z'
    jne reject_final
    
    jmp accept_final

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
