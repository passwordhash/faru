"""
Tic tac toe game for two players in the console.

Players take turns entering row and column numbers (1 to 3) to place their marks (X or O) on the board.
The game checks for wins, draws, and allows players to quit at any time.
"""

from typing import Optional, List, NamedTuple

PLAYERS = ("X", "O")
QUIT_COMMAND = "quit"
WELCOME_MESSAGE = """
Game "Tic Tac Toe" for two players.
Input "quit" to exit.
Format of input: two numbers — row and column (1..3):
"""
BOARD_HEADER = "   1   2   3"
LINE_SEPARATOR = "  ---+---+---"


def make_empty_board() -> List[List[str]]:
    return [[" " for _ in range(3)] for _ in range(3)]


def draw_board(board: List[List[str]]) -> None:
    print(BOARD_HEADER)
    for i, row in enumerate(board, start=1):
        print(f"{i}  {row[0]} | {row[1]} | {row[2]}")
        if i < 3:
            print(LINE_SEPARATOR)
    print()


def check_winner(board: List[List[str]]) -> Optional[str]:
    for row in board:
        if row[0] != " " and row[0] == row[1] == row[2]:
            # winner by row
            return row[0]
    for col in range(3):
        if board[0][col] != " " and board[0][col] == board[1][col] == board[2][col]:
            # winner by column
            return board[0][col]
    if board[0][0] != " " and board[0][0] == board[1][1] == board[2][2]:
        # winner by main diagonal
        return board[0][0]
    if board[0][2] != " " and board[0][2] == board[1][1] == board[2][0]:
        # winner by second diagonal
        return board[0][2]
    return None


def board_full(board: List[List[str]]) -> bool:
    """Checks if there is no empty cell on the board"""
    return all(cell != " " for row in board for cell in row)


class ParseResult(NamedTuple):
    """Result of parsing user input."""

    ok: bool
    msg: str
    row: Optional[int]
    col: Optional[int]


def parse_input(i: str) -> ParseResult:
    """Parses user input into row and column indices."""

    i = i.strip()
    if i.lower() == QUIT_COMMAND:
        return ParseResult(True, QUIT_COMMAND, None, None)

    parts = i.split()
    if len(parts) != 2:
        msg = "Expected two numbers: row and column (separated by space)"
        return ParseResult(False, msg, None, None)

    if not (parts[0].isdigit() and parts[1].isdigit()):
        msg = "Both inputs must be numbers"
        return ParseResult(False, msg, None, None)

    row, col = int(parts[0]), int(parts[1])
    if not (1 <= row <= 3 and 1 <= col <= 3):
        msg = "Both numbers must be in the range 1..3"
        return ParseResult(False, msg, None, None)

    return ParseResult(True, "", row - 1, col - 1)


def main() -> None:
    board = make_empty_board()
    current = PLAYERS[0]
    move_number = 0

    print(WELCOME_MESSAGE)

    try:
        while True:
            draw_board(board)
            print(f"Move №{move_number + 1}. Player {current}.")

            user = input("Input coordinates (row column): ").strip()
            ok, msg, row, col = parse_input(user)
            if not ok:
                print("Incorrect input:", msg)
                continue
            if msg == QUIT_COMMAND:
                return
            if row is None or col is None:
                raise ValueError("Unexpected parse result with None row or col")

            if board[row][col] != " ":
                print("Cell is already occupied")
                continue

            board[row][col] = current
            move_number += 1

            winner = check_winner(board)
            if winner:
                draw_board(board)
                print(f"Player {winner} wins! Congratulations!")
                return

            if board_full(board):
                draw_board(board)
                print("Game over! It's a draw")
                return

            # player change
            current = PLAYERS[move_number % 2]
    except (KeyboardInterrupt, ValueError):
        return
    finally:
        print("\nGame ended. Goodbye!")


if __name__ == "__main__":
    main()
