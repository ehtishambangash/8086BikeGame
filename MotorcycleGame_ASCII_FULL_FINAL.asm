
.MODEL SMALL
.STACK 100h

.DATA
    msg1        DB 'ASCII Motorcycle Game$'
    msg2        DB 'Use W/S to move, ESC to quit$'
    bike        DB ' o^o$'
    blankBike   DB '     $'
    line        DB '──────────────────────────────────────────────$'
    scoreLabel  DB 'Score: $'
    scoreStr    DB '00000$'
    score       DW 0

    obs1X       DB 75
    obs2X       DB 75
    obs3X       DB 75

    currentLane DB 2

.CODE
MAIN:
    MOV AX, @DATA
    MOV DS, AX

    CALL CLS
    CALL DrawUI
    CALL DrawLanes

GameLoop:
    CALL EraseBike
    CALL DrawMotorcycle
    CALL DrawObstacles
    CALL ConvertScore
    CALL DrawScore
    CALL UpdateObstacles
    CALL WaitForKey
    JMP GameLoop

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

DrawLanes PROC
    MOV DH, 4
    MOV DL, 5
    CALL SetCursor
    LEA DX, line
    CALL PrintStr

    MOV DH, 9
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
    MOV DH, 2
    MOV DL, 35
    CALL SetCursor
    LEA DX, blankBike
    CALL PrintStr

    MOV DH, 7
    MOV DL, 35
    CALL SetCursor
    LEA DX, blankBike
    CALL PrintStr

    MOV DH, 12
    MOV DL, 35
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

Lane1: MOV DH, 2
    JMP ShowBike
Lane2: MOV DH, 7
    JMP ShowBike
Lane3: MOV DH, 12

ShowBike:
    MOV DL, 35
    CALL SetCursor
    LEA DX, bike
    CALL PrintStr
    RET
DrawMotorcycle ENDP

DrawObstacles PROC
    MOV DH, 2
    MOV DL, obs1X
    CALL SetCursor
    MOV AL, 219
    CALL PrintChar

    MOV DH, 7
    MOV DL, obs2X
    CALL SetCursor
    MOV AL, 219
    CALL PrintChar

    MOV DH, 12
    MOV DL, obs3X
    CALL SetCursor
    MOV AL, 219
    CALL PrintChar
    RET
DrawObstacles ENDP

UpdateObstacles PROC
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
WaitLoop:
    MOV AH, 1
    INT 21h
    CMP AL, 'w'
    JE MoveUp
    CMP AL, 's'
    JE MoveDown
    CMP AL, 27
    JE ExitGame
    RET
WaitLoop ENDP

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
