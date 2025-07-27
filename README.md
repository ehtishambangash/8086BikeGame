# 8086 Bike Game

An ASCII-based motorcycle game written in 8086 assembly language.

## Game Description

The game features a motorcycle that can be controlled to avoid obstacles in a three-lane highway setting.

## Features

- **Motorcycle Display**: Uses ASCII characters 94 (^) and 111 (o) to represent the motorcycle
- **Three Lane System**: The motorcycle can move between three lanes
- **Controls**: 
  - 'W' key: Move up to higher lane
  - 'S' key: Move down to lower lane  
  - 'ESC' key: Exit game
  - 'ENTER' key: Restart game after game over
- **Obstacles**: Continuous stream of blocks (ASCII 219) appear from the right
- **Scoring**: Score is displayed and incremented when obstacles are passed
- **Collision Detection**: Game ends when motorcycle hits an obstacle
- **Game Restart**: Press ENTER after game over to restart
- **Visual Elements**:
  - Lane separators using ASCII 196 (─)
  - Border markings using ASCII 175 (¯)
  - Rightward movement animation

## Game Layout

```
                ASCII Motorcycle Game
              Use W/S to move, ESC to quit
  ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
¯│                                         │¯                Score: 00000
¯│              ^o                         │¯
¯│ ────────────────────────────────────────│¯
¯│                                         │¯
¯│                                         │¯
¯│ ────────────────────────────────────────│¯
¯│                                      ■  │¯
¯│                                         │¯
¯│ ────────────────────────────────────────│¯
¯│                                         │¯
  ¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯¯
```

## Technical Requirements

- **Platform**: 8086/8088 processor
- **Assembler**: Microsoft MASM or compatible
- **Environment**: DOS or DOS emulator (like DOSBox)

## Building and Running

1. Assemble the code using MASM:
   ```
   ml MotorcycleGame_ASCII_FULL_FINAL.asm
   ```

2. Run the generated executable:
   ```
   MotorcycleGame_ASCII_FULL_FINAL.exe
   ```

## Game Mechanics

- The motorcycle starts in the middle lane
- Obstacles move from right to left
- Score increases each time an obstacle passes off the left side
- Game over occurs when the motorcycle collides with an obstacle
- The motorcycle appears to move right through animation while staying in a fixed screen position

## ASCII Characters Used

- **94 (^)**: Motorcycle front
- **111 (o)**: Motorcycle wheel
- **219 (■)**: Obstacles
- **196 (─)**: Lane separators  
- **175 (¯)**: Border markings

## Game States

1. **Playing**: Normal gameplay with obstacle avoidance
2. **Game Over**: Collision detected, waiting for restart

The game implements proper collision detection, non-blocking keyboard input, and smooth animation through carefully timed display updates.