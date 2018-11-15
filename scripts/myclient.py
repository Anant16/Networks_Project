#!/usr/bin/env python3
"""Script for Tkinter GUI chat client."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter 
from tkinter import filedialog, Tk
import os
import time

def recv_file():
    print("file request from ")
    fname = client_socket.recv(BUFSIZ).decode("utf8")
    print ("recieving file " + fname )
    fsize = client_socket.recv(BUFSIZ)
    fsize = int(fsize)
    data_len = 0
    print("fsize: {}".format(fsize))
    local_file = "../received_files/" + fname
    with open(local_file, 'wb') as f:
        print ('opened file')
        while data_len<fsize:
            data = client_socket.recv(BUFSIZ)
            if not data:
                break
            data_len += len(data)
            f.write(data)
        print("Done writing file at client")
    return fname, fsize

def private_recv_file(pclient_socket):
    print("file request from ")
    fname = pclient_socket.recv(BUFSIZ).decode("utf8")
    print ("recieving file " + fname )
    fsize = pclient_socket.recv(BUFSIZ)
    fsize = int(fsize)
    data_len = 0
    print("fsize: {}".format(fsize))
    local_file = "../received_files/" + fname
    with open(local_file, 'wb') as f:
        print ('opened file')
        while data_len<fsize:
            data = pclient_socket.recv(BUFSIZ)
            if not data:
                break
            data_len += len(data)
            f.write(data)
        print("Done writing file at client")
    return fname, fsize

def send_file():
    fpath = filedialog.askopenfilename(initialdir = "/",title = "Select file")
    fname = fpath.split('/')[-1]
    fsize = os.path.getsize(fpath)
    client_socket.send(bytes('{file}', "utf8"))
    time.sleep(0.5)
    client_socket.send(bytes(fname, "utf8"))
    time.sleep(0.5)
    client_socket.send(bytes(str(fsize), "utf8"))
    time.sleep(0.5)
    with open(fpath, 'rb') as f:
        while True:
            data = f.read(BUFSIZ)
            if not data:
                break
            client_socket.sendall(data)
    print("File sent to server")
    time.sleep(0.5)

def private_send_file(pclient_socket):
    fpath = filedialog.askopenfilename(initialdir = "/",title = "Select file")
    fname = fpath.split('/')[-1]
    fsize = os.path.getsize(fpath)
    pclient_socket.send(bytes('{file}', "utf8"))
    time.sleep(0.5)
    pclient_socket.send(bytes(fname, "utf8"))
    time.sleep(0.5)
    pclient_socket.send(bytes(str(fsize), "utf8"))
    time.sleep(0.5)
    with open(fpath, 'rb') as f:
        while True:
            data = f.read(BUFSIZ)
            if not data:
                break
            pclient_socket.sendall(data)
    print("File sent to server")
    time.sleep(0.5)

def private_receive(pmsg_list, pclient_socket):
    """Handles receiving of messages."""
    # pmsg_list = ptop.messages_frame.msg_list
    while True:
        try:
            msg = pclient_socket.recv(BUFSIZ)
            if msg == bytes("{file}", "utf8"):
                pmsg_list.insert(tkinter.END, "Receiving File")
                fname, fsize = private_recv_file(pclient_socket)
                pmsg_list.insert(tkinter.END, "File Recieved")
            elif msg == bytes("{quit}", "utf8"):
                break
            else:
                msg = msg.decode('utf8')
                pmsg_list.insert(tkinter.END, msg)

        except OSError:  # Possibly client has left the chat.
            break



def receive():
    """Handles receiving of messages."""

    buttons_frame = tkinter.Frame(top)
    while True:

        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            # print(msg)
            if msg == '{quit}':
                break
            elif '{prequest}' in msg[0:12]:
                name = msg[11:]
                handle_connection_request(name)
            elif '{name}' in msg[0:6]:
                print(msg)
                uname.insert(tkinter.END, msg[7:])
            elif '{namelist}' in msg[0:12]:
                nlist = msg.split('_')[1]
                name_list = nlist.split(',')[1:]
                print(name_list)


                buttons_frame.destroy()
                buttons_frame = tkinter.Frame(top)
                for name in name_list:
                    private_button = tkinter.Button(buttons_frame, text=name, command=lambda user=name: create_private(user))
                    private_button.pack(side=tkinter.LEFT)
                buttons_frame.pack(side=tkinter.LEFT)

            else:
                msg_list.insert(tkinter.END, msg)
        except OSError:  # Possibly client has left the chat.
            break



def private_send(client_socket_no, pmy_msg, pmsg_list, event=None):  # event is passed by binders.
    """Handles sending of messages."""
    print("socket")
    print(client_socket_no)
    print(pmy_msg)
    print(pmsg_list)
    msg = pmy_msg.get()
    pmy_msg.delete(0, 100)  # Clears input field.
    print("message sent is: " + msg)
    try:
        client_socket_no.send(bytes(msg, "utf8"))
    except BrokenPipeError:
        error_msg = "Unable to send"
        pmsg_list.insert(tkinter.END, error_msg)
    
    if msg == "{quit}":
        client_socket_no.close()
        top.quit()


def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    print("socket")
    print(client_socket)
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.
    try:
        client_socket.send(bytes(msg, "utf8"))
    except BrokenPipeError:
        error_msg = "Unable to send"
        msg_list.insert(tkinter.END, error_msg)
    
    if msg == "{quit}":
        client_socket.close()
        top.quit()
    
def create_private(name):
    print("create_private")
    print(name)
    new_name = uname.get('1.0', tkinter.END) + '_' + name
    new_name = new_name.replace('\n', '')
    print(new_name)
    Thread(target=private_client, args=(new_name,)).start()

def private_client(name):
    pclient_socket = socket(AF_INET, SOCK_STREAM)
    pclient_socket.connect(ADDR)

    pclient_socket.send(bytes(name, "utf8"))

    ptop = tkinter.Tk()
    ptop.title("Private Chat - " + uname.get('1.0', tkinter.END))

    messages_frame = tkinter.Frame(ptop)
    my_msg = tkinter.StringVar()  # For the messages to be sent.
    # my_msg.set("Type your messages here.")
    scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
    # Following will contain the messages.
    msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
    msg_list.pack()
    messages_frame.pack()

    print(my_msg)

    entry_field = tkinter.Entry(ptop, textvariable=my_msg)
    entry_field.bind("<Return>", lambda event, temp = pclient_socket: private_send(temp, entry_field, msg_list))
    entry_field.pack()
    send_button = tkinter.Button(ptop, text="Send", command=lambda: private_send(pclient_socket, entry_field, msg_list))
    send_button.pack()

    send_file_button = tkinter.Button(ptop, text="Send File", command= lambda: private_send_file(pclient_socket))
    send_file_button.pack()

    receive_thread = Thread(target=private_receive, args=(msg_list, pclient_socket,))
    receive_thread.start()
    ptop.mainloop()  # Starts GUI execution.

def handle_connection_request(name):
    new_name = uname.get('1.0', tkinter.END) + '_' + name + '_'
    new_name = new_name.replace('\n', '')
    Thread(target=private_client, args=(new_name,)).start()

# def on_closing(event=None):
#     """This function is to be called when the window is closed."""
#     my_msg.set("{quit}")
#     try:
#         send()
#     except BrokenPipeError:
#         print("BrokenPipeError")
#         top.quit()


#----Now comes the sockets part----
HOST = input('Enter host: ')
PORT = input('Enter port: ')
if not PORT:
    PORT = 35000
else:
    PORT = int(PORT)
if not HOST:
    HOST = '127.0.0.1'

BUFSIZ = 1024
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)


top = tkinter.Tk()
top.title("Group Chat")

uname = tkinter.Text(top)
# uname.pack()

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()  # For the messages to be sent.
# my_msg.set("Type your messages here.")
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
msg_list = tkinter.Listbox(messages_frame, height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

entry_field = tkinter.Entry(top, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tkinter.Button(top, text="Send", command=send)
send_button.pack()

send_file_button = tkinter.Button(top, text="Send File", command=send_file)
send_file_button.pack()

# top.protocol("WM_DELETE_WINDOW", on_closing)

# #----Now comes the sockets part----
# HOST = input('Enter host: ')
# PORT = input('Enter port: ')
# if not PORT:
#     PORT = 33000
# else:
#     PORT = int(PORT)

# BUFSIZ = 1024
# ADDR = (HOST, PORT)

# client_socket = socket(AF_INET, SOCK_STREAM)
# client_socket.connect(ADDR)

receive_thread = Thread(target=receive)
receive_thread.start()
top.mainloop()  # Starts GUI execution.