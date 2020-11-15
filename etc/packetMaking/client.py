import socket
import argparse
import threading

host = '127.0.0.1'
port = 8080

def handle_receive(num, lient_socket, user):
    while 1:
        try:
            data = client_socket.recv(1024)
        except:
            print("연결 끊김")
            break
        
        data = data.decode()
        if not user in data:
            print(data)

def handle_send(num, client_socket):
    while 1:
        data = input()
        client_socket.sendall(data.encode())
        if data == "종료":
            break
    client_socket.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Client\n-s string")
    parser.add_argument('-u', help="user", required=True)

    args = parser.parse_args()
    user = str(args.u)
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))

    client_socket.sendall(user.encode())

    receive_thread = threading.Thread(target=handle_receive, args=(1, client_socket, user))
    receive_thread.daemon = True
    receive_thread.start()

    send_thread = threading.Thread(target=handle_send, args=(2, client_socket))
    send_thread.daemon = True
    send_thread.start()

    send_thread.join()
    receive_thread.join()
