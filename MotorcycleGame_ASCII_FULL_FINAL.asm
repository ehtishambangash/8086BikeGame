.MODEL SMALL
.STACK 100h

.DATA
    msg1        DB 'ASCII Motorcycle Game$'
    msg2        DB 'Use W/S to move, ESC to quit$'
    msg3        DB 'GAME OVER! Press ENTER to restart$'
    bike        DB '^o$'              ; Using ASCII 94 (^) and 111 (o)
    blankBike   DB '   $'
    line        DB 196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,196,'$'
    border      DB 175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,175,'$'
    scoreLabel  DB 'Score: $'
    scoreStr    DB '00000$'
    score       DW 0

    obs1X       DB 75
    obs2X       DB 75
    obs3X       DB 75

    currentLane DB 2
    gameState   DB 0                  ; 0 = playing, 1 = game over
    bikeX       DB 35                 ; X position of motorcycle

.CODE
MAIN:
    MOV AX, @DATA
    MOV DS, AX

StartGame:
    MOV gameState, 0          ; Set to playing state
    MOV score, 0              ; Reset score
    MOV currentLane, 2        ; Reset to middle lane
    MOV bikeX, 35             ; Reset bike position
    MOV obs1X, 75             ; Reset obstacles
    MOV obs2X, 75
    MOV obs3X, 75
    CALL CLS
    CALL DrawUI
    CALL DrawBorders
    CALL DrawLanes

GameLoop:
    CMP gameState, 1          ; Check if game over
    JE GameOverLoop
    
    CALL EraseBike
    CALL DrawMotorcycle
    CALL DrawObstacles
    CALL ConvertScore
    CALL DrawScore
    CALL UpdateObstacles
    CALL CheckCollision
    CALL WaitForKey
    CALL AnimateBike           ; Move bike to the right
    CALL Delay                 ; Add delay for game speed control
    JMP GameLoop

GameOverLoop:
    CALL ShowGameOver
    CALL WaitForRestart
    JMP GameOverLoop

; -------------------------
DrawUI PROC
    MOV DH, 0
    MOV DL, 25
    CALL SetCursor
    LEA DX, msg1
    CALL PrintStr

    MOV DH, 1
    MOV DL, 22
    CALL SetCursor
    LEA DX, msg2
    CALL PrintStr
    RET
DrawUI ENDP

DrawBorders PROC
    ; Top border
    MOV DH, 3
    MOV DL, 5
    CALL SetCursor
    LEA DX, border
    CALL PrintStr
    
    ; Bottom border
    MOV DH, 15
    MOV DL, 5
    CALL SetCursor
    LEA DX, border
    CALL PrintStr
    
    ; Left border
    MOV CX, 12          ; Height of playing area
    MOV DH, 4
BorderLeft:
    MOV DL, 4
    CALL SetCursor
    MOV AL, 175         ; ASCII 175
    CALL PrintChar
    INC DH
    LOOP BorderLeft
    
    ; Right border  
    MOV CX, 12
    MOV DH, 4
BorderRight:
    MOV DL, 53
    CALL SetCursor
    MOV AL, 175         ; ASCII 175
    CALL PrintChar
    INC DH
    LOOP BorderRight
    RET
DrawBorders ENDP

DrawLanes PROC
    MOV DH, 6
    MOV DL, 5
    CALL SetCursor
    LEA DX, line
    CALL PrintStr

    MOV DH, 10
    MOV DL, 5
    CALL SetCursor
    LEA DX, line
    CALL PrintStr

    MOV DH, 14
    MOV DL, 5
    CALL SetCursor
    LEA DX, line
    CALL PrintStr
    RET
DrawLanes ENDP

EraseBike PROC
    MOV DH, 5
    MOV DL, bikeX
    CALL SetCursor
    LEA DX, blankBike
    CALL PrintStr

    MOV DH, 9
    MOV DL, bikeX
    CALL SetCursor
    LEA DX, blankBike
    CALL PrintStr

    MOV DH, 13
    MOV DL, bikeX
    CALL SetCursor
    LEA DX, blankBike
    CALL PrintStr
    RET
EraseBike ENDP

DrawMotorcycle PROC
    CMP currentLane, 1
    JE Lane1
    CMP currentLane, 2
    JE Lane2
    JMP Lane3

Lane1: MOV DH, 5
    JMP ShowBike
Lane2: MOV DH, 9
    JMP ShowBike
Lane3: MOV DH, 13

ShowBike:
    MOV DL, bikeX
    CALL SetCursor
    LEA DX, bike
    CALL PrintStr
    RET
DrawMotorcycle ENDP

DrawObstacles PROC
    MOV DH, 5
    MOV DL, obs1X
    CALL SetCursor
    MOV AL, 219
    CALL PrintChar

    MOV DH, 9
    MOV DL, obs2X
    CALL SetCursor
    MOV AL, 219
    CALL PrintChar

    MOV DH, 13
    MOV DL, obs3X
    CALL SetCursor
    MOV AL, 219
    CALL PrintChar
    RET
DrawObstacles ENDP

UpdateObstacles PROC
    ; Erase old obstacle positions
    MOV DH, 5
    MOV DL, obs1X
    CALL SetCursor
    MOV AL, ' '
    CALL PrintChar

    MOV DH, 9
    MOV DL, obs2X
    CALL SetCursor
    MOV AL, ' '
    CALL PrintChar

    MOV DH, 13
    MOV DL, obs3X
    CALL SetCursor
    MOV AL, ' '
    CALL PrintChar

    ; Update positions
    DEC obs1X
    CMP obs1X, 5
    JGE Skip1
    MOV obs1X, 75
    INC score
Skip1:

    DEC obs2X
    CMP obs2X, 5
    JGE Skip2
    MOV obs2X, 75
    INC score
Skip2:

    DEC obs3X
    CMP obs3X, 5
    JGE Skip3
    MOV obs3X, 75
    INC score
Skip3:
    RET
UpdateObstacles ENDP

DrawScore PROC
    MOV DH, 1
    MOV DL, 65
    CALL SetCursor
    LEA DX, scoreLabel
    CALL PrintStr

    LEA DX, scoreStr
    CALL PrintStr
    RET
DrawScore ENDP

ConvertScore PROC
    MOV AX, score
    MOV SI, OFFSET scoreStr + 4
    MOV CX, 5
ScoreLoop:
    XOR DX, DX
    MOV BX, 10
    DIV BX
    ADD DL, '0'
    MOV [SI], DL
    DEC SI
    LOOP ScoreLoop
    RET
ConvertScore ENDP

WaitForKey PROC
    MOV AH, 01h               ; Check if key available
    INT 16h
    JZ NoKey                  ; Jump if no key pressed
    
    MOV AH, 00h               ; Get key
    INT 16h
    
    CMP AL, 'w'
    JE MoveUp
    CMP AL, 's'
    JE MoveDown
    CMP AL, 27                ; ESC key
    JE ExitGame
NoKey:
    RET
WaitForKey ENDP

MoveUp PROC
    DEC currentLane
    CMP currentLane, 1
    JGE MU_Done
    MOV currentLane, 1
MU_Done: RET
MoveUp ENDP

MoveDown PROC
    INC currentLane
    CMP currentLane, 3
    JLE MD_Done
    MOV currentLane, 3
MD_Done: RET
MoveDown ENDP

CheckCollision PROC
    ; Check collision for lane 1
    CMP currentLane, 1
    JNE CheckLane2
    MOV AL, obs1X
    CMP AL, bikeX
    JL CheckLane2
    MOV BL, bikeX
    ADD BL, 2                 ; Length of motorcycle
    CMP AL, BL
    JG CheckLane2
    MOV gameState, 1          ; Game over
    RET

CheckLane2:
    CMP currentLane, 2
    JNE CheckLane3
    MOV AL, obs2X
    CMP AL, bikeX
    JL CheckLane3
    MOV BL, bikeX
    ADD BL, 2
    CMP AL, BL
    JG CheckLane3
    MOV gameState, 1          ; Game over
    RET

CheckLane3:
    CMP currentLane, 3
    JNE CollisionDone
    MOV AL, obs3X
    CMP AL, bikeX
    JL CollisionDone
    MOV BL, bikeX
    ADD BL, 2
    CMP AL, BL
    JG CollisionDone
    MOV gameState, 1          ; Game over

CollisionDone:
    RET
CheckCollision ENDP

AnimateBike PROC
    ; Create subtle rightward movement by cycling position
    MOV AL, bikeX
    ADD AL, 1
    CMP AL, 45             ; Limit rightward movement
    JLE SetNewPos
    MOV AL, 35             ; Reset to starting position
SetNewPos:
    MOV bikeX, AL
    RET
AnimateBike ENDP

ShowGameOver PROC
    MOV DH, 8
    MOV DL, 15
    CALL SetCursor
    LEA DX, msg3
    CALL PrintStr
    RET
ShowGameOver ENDP

WaitForRestart PROC
    MOV AH, 00h               ; Wait for key
    INT 16h
    CMP AL, 13                ; Enter key
    JNE WaitForRestart
    JMP StartGame             ; Restart the game
WaitForRestart ENDP

Delay PROC
    PUSH CX
    PUSH AX
    MOV CX, 5000h            ; Adjusted delay for better gameplay
DelayLoop:
    NOP
    NOP
    DEC CX
    JNZ DelayLoop
    POP AX
    POP CX
    RET
Delay ENDP

SetCursor PROC
    MOV BH, 0
    MOV AH, 02h
    INT 10h
    RET
SetCursor ENDP

PrintChar PROC
    MOV AH, 0Eh
    INT 10h
    RET
PrintChar ENDP

PrintStr PROC
    MOV AH, 09h
    INT 21h
    RET
PrintStr ENDP

CLS PROC
    MOV AX, 0600h
    MOV BH, 07
    MOV CX, 0000
    MOV DX, 184Fh
    INT 10h

    MOV AH, 02
    MOV BH, 0
    MOV DX, 0000
    INT 10h
    RET
CLS ENDP

ExitGame PROC
    MOV AH, 4Ch
    INT 21h
ExitGame ENDP

END MAIN