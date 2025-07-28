.model small
.stack 100h

.data
    msg_accept db 'Cadena ACEPTADA', 0Dh, 0Ah, '$'
    msg_reject db 'Cadena RECHAZADA', 0Dh, 0Ah, '$'
    msg_accept_lcd db 'ACEPTADA', 0
    msg_reject_lcd db 'RECHAZADA', 0
    input_prompt db 'Ingrese cadena: $'
    input_buffer db 255, 0, 255 dup(0)
    current_state db 0
    input_ptr dw 0
    pda_stack db 256 dup(0)
    sp_offset dw 1
    stack_start db 'Z'
    ; Transition format: estado_origen, input, pop, estado_destino, push_count, [símbolos]
    pda_transitions db 0, 'a', 'Z', 0, 2, 'A', 'Z'
                    db 0, 'a', 'A', 0, 2, 'A', 'A'
                    db 0, 'b', 'A', 0, 0
                    db 0, 'b', 'A', 0, 0
                    db -1, -1, -1, -1, -1              ; Terminator

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

    ; Initialize PDA
    mov byte ptr [current_state], 0
    mov word ptr [input_ptr], 0
    mov al, [stack_start]
    mov [pda_stack], al
    mov word ptr [sp_offset], 1

simulation_loop:
    ; Check if we've processed all input
    mov cl, [input_buffer + 1]
    mov ch, 0
    mov ax, [input_ptr]
    cmp ax, cx
    jge check_final_state

    ; Get current input symbol
    mov bx, [input_ptr]
    mov al, [input_buffer + 2 + bx]
    ; Get stack top
    mov di, [sp_offset]
    cmp di, 0
    je reject_final
    mov dl, [pda_stack + di - 1]

    ; Search for valid transition
    mov si, offset pda_transitions

find_transition:
    cmp byte ptr [si], -1
    je reject_final
    ; Check source state
    mov ah, [current_state]
    cmp [si], ah
    jne next_transition
    ; Check input symbol
    cmp [si+1], al
    jne next_transition
    ; Check stack symbol
    cmp [si+2], dl
    jne next_transition
    ; Transition found - execute
    ; Update state
    mov ah, [si+3]
    mov [current_state], ah
    ; Pop current symbol
    mov di, [sp_offset]
    cmp di, 0
    je reject_final
    dec word ptr [sp_offset]
    ; Check if there are symbols to push
    mov cl, [si+4]
    cmp cl, 0
    je advance_input
    ; Push symbols in correct order (last to first)
    mov ch, 0
    mov bx, si
    add bx, 5
    add bx, cx
    dec bx
push_loop:
    mov di, [sp_offset]
    cmp di, 255
    jge reject_final
    mov dl, [bx]
    mov [pda_stack + di], dl
    inc word ptr [sp_offset]
    dec bx
    dec cl
    jnz push_loop

advance_input:
    inc word ptr [input_ptr]
    jmp simulation_loop

next_transition:
    ; Calculate next transition position
    mov cl, [si+4]
    mov ch, 0
    add si, 5
    add si, cx
    jmp find_transition

check_final_state:
    ; Check acceptance state (must be q0 = 0)
    mov al, [current_state]
    cmp al, 0
    jne reject_final

    ; Check that stack contains only Z
    mov di, [sp_offset]
    cmp di, 1
    jne reject_final

    mov dl, [pda_stack]
    cmp dl, 'Z'
    jne reject_final

    jmp accept_final
; Procedimiento para inicializar el LCD
init_lcd proc
    mov dx, 2030h       ; Puerto de comandos del LCD
    mov al, 38h         ; Modo 8 bits, 2 líneas, 5x7
    out dx, al
    mov al, 0Ch         ; Display ON, cursor OFF
    out dx, al
    mov al, 06h         ; Incremento automático, sin shift
    out dx, al
    mov al, 01h         ; Clear display
    out dx, al
    ret
init_lcd endp

accept_final:
    ; Inicializar LCD
    call init_lcd
    ; Posicionar cursor al inicio
    mov dx, 2030h       ; Puerto de comandos
    mov al, 80h         ; Comando Set DDRAM Address
    out dx, al
    ; Mostrar mensaje en el LCD Display
    mov dx, 2031h       ; Puerto de datos del LCD
    mov si, offset msg_accept_lcd
write_accept_lcd:
    mov al, [si]        ; Cargar carácter
    cmp al, 0           ; Verificar fin de cadena
    je done_accept_lcd  ; Si es 0, terminamos
    out dx, al          ; Enviar al LCD
    ; Pequeño delay
    push cx
    mov cx, 1000
delay1:
    loop delay1
    pop cx
    inc si              ; Siguiente carácter
    jmp write_accept_lcd
done_accept_lcd:
    ; Mostrar mensaje en consola
    mov ah, 09h
    mov dx, offset msg_accept
    int 21h
    jmp exit_program

reject_final:
    ; Inicializar LCD
    call init_lcd
    ; Posicionar cursor al inicio
    mov dx, 2030h       ; Puerto de comandos
    mov al, 80h         ; Comando Set DDRAM Address
    out dx, al
    ; Mostrar mensaje en el LCD Display
    mov dx, 2031h       ; Puerto de datos del LCD
    mov si, offset msg_reject_lcd
write_reject_lcd:
    mov al, [si]        ; Cargar carácter
    cmp al, 0           ; Verificar fin de cadena
    je done_reject_lcd  ; Si es 0, terminamos
    out dx, al          ; Enviar al LCD
    ; Pequeño delay
    push cx
    mov cx, 1000
delay2:
    loop delay2
    pop cx
    inc si              ; Siguiente carácter
    jmp write_reject_lcd
done_reject_lcd:
    ; Mostrar mensaje en consola
    mov ah, 09h
    mov dx, offset msg_reject
    int 21h

exit_program:
    mov ah, 4ch
    int 21h
main endp

end main
