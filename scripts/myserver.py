#!/usr/bin/env python3
"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

def recv_file(client, name):
    print("file request from " + name)
    fname = client.recv(BUFSIZ).decode("utf8")
    print ("recieving file " + fname + " from " + str(name))
    fsize = client.recv(BUFSIZ)
    fsize = int(fsize)
    data_len = 0
    print("fsize: {}".format(fsize))
    local_file = "../shared_files/" + name + '_' + fname
    with open(local_file, 'wb') as f:
        print ('opened file')
        while data_len<fsize:
            data = client.recv(BUFSIZ)
            if not data:
                break
            data_len += len(data)
            f.write(data)
        print("Done writing file")
    return fname, fsize

def send_file(client, name, fname, fsize):
    print("Sending a file to " + name)
    local_file = "../shared_files/" + fname
    print("Opening file to send and sending...")
    with open(local_file, 'rb') as f:
        while True:
            data = f.read(BUFSIZ)
            if not data:
                break
            client.sendall(data)
    print("File sent")



def accept_incoming_connections():
    """Sets up handling for incoming clients."""
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes("Greetings from the cave! Now type your name and press enter!", "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""

    name = client.recv(BUFSIZ).decode("utf8")
    welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit.' % name
    client.send(bytes(welcome, "utf8"))
    msg = "%s has joined the chat!" % name
    broadcast(bytes(msg, "utf8"))
    clients[client] = name

    while True:
        try:
            msg = client.recv(BUFSIZ)
            print(msg)
            print(len(msg))
            if msg == "":
                break
            if msg == bytes("{file}", "utf8"):
                fname, fsize = recv_file(client, name)
                print(fname + ": "+ str(fsize))
                # print("file request from " + name)
                # fname = client.recv(BUFSIZ).decode("utf8")
                # print ("recieving file " + fname + " from " + str(name))
                # fsize = client.recv(BUFSIZ)
                # fsize = int(fsize)
                # data_len = 0
                # print("fsize: {}".format(fsize))
                # local_file = "../shared_files/" + name + '_' + fname
                # with open(local_file, 'wb') as f:
                #     print ('opened file')
                #     while data_len<fsize:
                #         data = client.recv(BUFSIZ)
                #         data_len += len(data)
                #         f.write(data)
                #     print("Done writing file")
            elif msg == bytes("{quit}", "utf8"):
                client.send(bytes("{quit}", "utf8"))
                client.close()
                del clients[client]
                broadcast(bytes("%s has left the chat." % name, "utf8"))
                break
            else:
                broadcast(msg, name+": ")
        except OSError:
            break


def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""

    clients_who_left = []
    for client in clients:
        try:
            client.sendall(bytes(prefix, "utf8")+msg)
        except:
            client.close()
            print(clients[client] + " left the chat")
            # del clients[client]
            clients_who_left.append(client)

    for client in clients_who_left:
        del clients[client]


        
clients = {}
addresses = {}

HOST = ''
PORT = 35000
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
