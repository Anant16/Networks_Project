#!/usr/bin/env python3
"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import time

def recv_file(client, name):
    print("file request from " + name)
    fname = client.recv(BUFSIZ).decode("utf8")
    print ("recieving file " + fname + " from " + str(name))
    fsize = client.recv(BUFSIZ).decode('utf8')
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
    full_fname = name + '_' + fname
    return full_fname, fsize

def send_file(client, name, fname, fsize):
    client.send(bytes(fname, 'utf8'))
    time.sleep(0.5)
    client.send(bytes(str(fsize), "utf8"))
    time.sleep(0.5)
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
        client.send(bytes("Welcome to Group Chat. Now type your name and press enter!", "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()

def update_users():
    name_list = "{namelist}_"
    for client in clients:
        if '_' in clients[client]:
            continue
        name_list += "," + clients[client]
    broadcast(bytes(name_list, 'utf8'))


def handle_client(client):  # Takes client socket as argument.
    """Handles a single client connection."""

    name = client.recv(BUFSIZ).decode("utf8")
    msg = "{name}_%s" % name
    print(msg)
    client.send(bytes(msg, "utf8"))
    time.sleep(1)
    
    print("client detected: " + name)
    if('_' in name):
        print("private request : " + name)
        Thread(target=handle_private_client, args=(client, name,)).start()
        return

    welcome = 'Welcome %s! If you ever want to quit, type {quit} to exit.' % name
    client.send(bytes(welcome, "utf8"))
    msg = "%s has joined the chat!" % name
    broadcast(bytes(msg, "utf8"))
    name = name.replace('\n', '')
    clients[client] = name
    names[name] = client

    time.sleep(0.5)
    update_users()

    while True:
        try:
            msg = client.recv(BUFSIZ)
            if msg == "":
                break
            if msg == bytes("{file}", "utf8"):
                print("group client")
                fname, fsize = recv_file(client, name)
                print(fname + ": "+ str(fsize))
            elif msg == bytes("{quit}", "utf8"):
                client.send(bytes("{quit}", "utf8"))
                client.close()
                del clients[client]
                del names[name]
                broadcast(bytes("%s has left the chat." % name, "utf8"))
                update_users()
                break
            else:
                broadcast(msg, name+": ")
        except OSError:
            break

def handle_private_client(client, name):  # Takes client socket as argument.
    """Handles a single private client connection."""
    print("Private client is: " + name)
    if name[-1] == '_':
        print("response of request")
        name = name[:-1]
        name1, name2 = name.split('_');
        print("names: " + name1 + " " + name2)
        client2 = names[name2 + '_' + name1]

        msg = "%s is ready for connection. Please go ahead." % name1
        client2.send(bytes(msg, "utf8"))
        print(client2)
        name = name.replace('\n', '')
        print("Updating tables: if")
        print(name)
        clients[client] = name
        names[name] = client
        name2p = name2 + '_' + name1

    else:
        name1, name2 = name.split('_');
        print("pr request in : " + name1 + " - " + name2)
        msg = '{prequest}_' + name1
        client2 = names[name2]
        client2.send(bytes(msg, "utf8"))
        
        name = name.replace('\n', '')
        print("Updating tables: else")
        print(name)
        clients[client] = name
        names[name] = client

        name2p = name2 + '_' + name1
        count = 10
        while count > 0:
            if name2p in names:
                client2 = names[name2p]
                break
            else:
                time.sleep(1)
            count -=1
        if count == 0:
            client.send(bytes("{quit}", "utf8"))
            client.close()
            del clients[client]
            del names[name]
            return
        # msg = client2.recv(BUFSIZ)
        # if msg == bytes("Yes", "utf8"):
        #     msg = "%s is ready for connection. Please go ahead." % name2
        #     client.send(bytes(msg, "utf8"))
        # else:
        #     msg = "%s is not available for connection now. Please try later." % name2
        #     client.send(bytes(msg, "utf8"))
        #     return

    while True:
        try:
            msg = client.recv(BUFSIZ)
            print(msg)
            print(len(msg))
            if msg == "":
                break
            if msg == bytes("{file}", "utf8"):
                print(clients[client])
                print(name)
                fname, fsize = recv_file(client, name)
                print(fname + ": "+ str(fsize))
                client2.send(bytes("{file}", "utf8"))
                time.sleep(0.5)
                send_file(client2, name2p, fname, fsize)
            elif msg == bytes("{quit}", "utf8"):
                client.send(bytes("{quit}", "utf8"))
                client.close()
                del clients[client]
                del names[name]
                client2.send(bytes("%s has left the chat." % name1, "utf8"))
                break
            else:
                print(msg)
                client2.send(bytes(name1 + ": ", "utf8") + msg)
                client.send(bytes(name1 + ": ", "utf8") + msg)
        except OSError:
            break

def broadcast(msg, prefix=""):  # prefix is for name identification.
    """Broadcasts a message to all the clients."""

    clients_who_left = []
    for client in clients:
        if '_' in clients[client]:
            continue
        try:
            client.sendall(bytes(prefix, "utf8")+msg)
        except:
            client.close()
            print(clients[client] + " has left the chat")
            # del clients[client]
            clients_who_left.append(client)

    for client in clients_who_left:
        del clients[client]


        
clients = {}
addresses = {}
names = {}

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
