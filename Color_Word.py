import RPi.GPIO as GPIO
#import GPIOmock as GPIO
import threading
import time
import random
import os

LIGHTS = [33, 37, 35, 31]
BUTTONS = [11, 15, 13, 12]
COLORS = ["Green", "Blue", "Red", "Yellow"]
COLORS_PATTERN = []
pattern2 = []

speed = 0.5

is_displaying_pattern = False
is_won_current_level = False
is_game_over = False
attempt = 0

pattern = []
player_input = []
term_output = [0,0,0,0]

def initialize_gpio():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(LIGHTS, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    for i in range(4):
        GPIO.add_event_detect(BUTTONS[i], GPIO.FALLING, verify_player_selection, 250)


def verify_player_selection(channel):
    global is_game_over, is_won_current_level
    one_round(channel)
        
def one_round(channel):
    global is_game_over, is_won_current_level, attempt, player_input, pattern, term_output
    flash_led_for_button(channel)
    if len(player_input) < 4 :
        player_input.append(channel)
    if pattern == player_input:
        is_game_over = True
        is_won_current_level = True
        return
    if len(player_input) == 4:
        pattern_check = pattern.copy()
    
        for i in range(4):
            if pattern_check[i] == player_input[i]:
                term_output[i] = "X"
                pattern_check[i] = "X"

                
        for i in range(4):
            if player_input[i] in pattern_check and term_output[i] != "X":
                term_output[i] = "O"
                pattern_check[pattern_check.index(player_input[i])] = "O"
        for i in range(4): 
            if term_output[i] not in ["X", "O"]:
                term_output[i] = "*"
            player_input[i] = COLORS[BUTTONS.index(player_input[i])]
        
        print (player_input)
        player_input = []
        print (term_output)
        term_output = [0,0,0,0]
        attempt += 1
        print("\n")
    
        


def flash_led_for_button(button_channel):
    led = LIGHTS[BUTTONS.index(button_channel)]
    GPIO.output(led, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(led, GPIO.LOW)

def add_new_color_to_pattern():
    for i in range(4):
        next_color = random.randint(0, 3)
        next_color = BUTTONS[next_color]
        pattern.append(next_color)


def wait_for_player_to_repeat_pattern():
    global is_game_over
    while not is_won_current_level and not is_game_over and attempt < 5:
        time.sleep(0.1)
        if attempt == 4:
            is_game_over = True
            break
def display_pattern():
 

    for i in range(4):
        
        GPIO.output(LIGHTS[(BUTTONS.index(pattern[i]))], GPIO.HIGH)
        time.sleep(speed)
        GPIO.output(LIGHTS[(BUTTONS.index(pattern[i]))], GPIO.LOW)
        time.sleep(speed)

def reset_board_for_new_game():
    global is_won_current_level, is_game_over
    global  pattern, attempt
    is_won_current_level = False
    is_game_over = False
    attempt = 0
    pattern = []
    GPIO.output(LIGHTS, GPIO.LOW)


def start_game():
    global pattern2
    add_new_color_to_pattern()
    while True:
        wait_for_player_to_repeat_pattern()
        if is_game_over:
            if is_won_current_level:
                print("Congrats you won")
                for i in range(4):
                    pattern2.append(COLORS[(BUTTONS.index(pattern[i]))])
            else:
                print("You Lost")
                for i in range(4):
                    pattern2.append(COLORS[(BUTTONS.index(pattern[i]))])
                print("The actual pattern is: \n")
                print(pattern2)
                display_pattern()
            pattern2 = []
            play_again = input("Enter 'Y' to play again, or just press [ENTER] to exit.\n")
            if play_again == "Y" or play_again == "y":
                reset_board_for_new_game()
                print("Begin new round!\n")
                start_game()
            else:
                print("Thanks for playing!\n")
                break
        time.sleep(2)

def start_game_monitor():
    t = threading.Thread(target=start_game)
    t.daemon = True
    t.start()
    t.join()

def main():
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("Welcome to Color Wordle!\n\n Try and Guess the Pattern \n If the color that you chose has a X then it is in the right spot in the pattern\n\n") 
        print("If the color that you chose has a O then it is the right color but in the wrong spot\n\nIf the color is an * then that color is not in the pattern")
        initialize_gpio()
        start_game_monitor()
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    main()