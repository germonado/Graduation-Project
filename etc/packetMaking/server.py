import socket
import argparse
import threading
import time

host = "127.0.0.1"
port = 8080
user_list = {}
notice_flag = 0

def handle_receive(client_socket, addr, user):
    while 1:
        data = client_socket.recv(1024)
        string = data.decode()

        if string == "종료" : break
        string = "%s : %s"%(user, string)
        print(string)
        for con in user_list.values():
            try:
                con.sendall(string.encode())
            except:
                print("연결이 비 정상적으로 종료된 소켓 발견")

    del user_list[user]
    client_socket.close()

def handle_notice(client_socket, addr, user):
    pass

def accept_func():
    print("server open")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # exception handling
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))

    server_socket.listen(5)

    while 1:
        try:
            client_socket, addr = server_socket.accept()
            print("client login")
            
        except KeyboardInterrupt:
            for user, con in user_list:
                con.close()
            server_socket.close()
            print("Keyboard interrupt")
            break
        
        user = client_socket.recv(1024)
        user_list[user] = client_socket

        notice_thread = threading.Thread(target=handle_notice, args=(client_socket, addr, user))
        notice_thread.daemon = True
        notice_thread.start()

        receive_thread = threading.Thread(target=handle_receive, args=(client_socket, addr,user))
        receive_thread.daemon = True
        receive_thread.start()


if __name__ == '__main__':
    accept_func()
