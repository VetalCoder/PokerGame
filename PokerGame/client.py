"""
    Program for clients. Provide game for users...
"""

import socket
import json

# function, that clear terminal
def clear_scr():
    import os
    os.system('cls' if os.name == 'nt' else 'clear')

# function, that can return only one char from keyboard 
def get_char():
    # figure out which function to use once, and store it in _func
    if "_func" not in get_char.__dict__:
        try:
            # for Windows-based systems
            import msvcrt # If successful, we are on Windows
            get_char._func=msvcrt.getch

        except ImportError:
            # for POSIX-based systems (with termios & tty support)
            import tty, sys, termios # raises ImportError if unsupported

            def _ttyRead():
                fd = sys.stdin.fileno()
                oldSettings = termios.tcgetattr(fd)

                try:
                    tty.setcbreak(fd)
                    answer = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, oldSettings)

                return answer

            get_char._func=_ttyRead

    return get_char._func()

def inp_name():
    return input("Enter your nickname: ")

def inp_stack():
    return input("Enter your amount of money: ")

def inp_ip():
    return input("Please enter server ip-address (ex. '127.0.0.1'): ")

def init_game():
    print("   Welcome to PokerGame Client!!!   ")
    name = inp_name()
    stack = 25000 # inp_stack()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    while True:
        ip = "192.168.1.42" # inp_ip()
        try:
            sock.connect((ip, 27030))
        except BaseException as error:
            print(f"Error {error} was occured. Try again!")
        else:
            break

    # send initial data
    data = json.dumps({'name' : name,
                       'stack' : stack,
                       })

    sock.send(data.encode())

    # reseive responses
    while True:
        try:
            resp = json.loads(sock.recv(1024).decode('utf-8'))
        except json.decoder.JSONDecodeError:
            print("Connection was closed...")
            break

        if resp['clear']:
            clear_scr()

        if resp['ask_ch']:
            print(resp['message'])
            
            data = get_char()
            sock.send(data)

        elif resp['ask']:           
            data = input(resp['message'])
            sock.send(data.encode())

        else:
            print(resp['message'])

def main():
    init_game()


main()