import board
import digitalio

pins = [board.D1, board.D2, board.D3, board.D4,
        board.D5, board.D6, board.D7, board.D8,
        board.D9, board.D10, board.D11, board.D12,
        board.D13, board.D14, board.D15, board.D16,
        board.D17, board.D18, board.D19, board.D20,
        board.D21, board.D22, board.D23, board.D24,
        board.D25, board.D26, board.D27]

try:
    for pin in pins:
        digitalio.DigitalInOut(pin).switch_to_input(pull=digitalio.Pull.DOWN)
except Exception as e:
    print(e)
