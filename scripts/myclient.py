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
        print("Done writing file")
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

def private_receive(pclient_socket):
    """Handles receiving of messages."""
    while True:
        try:
            msg = pclient_socket.recv(BUFSIZ)
            if msg == bytes("{file}", "utf8"):
                fname, fsize = recv_file()
            else:
                msg = msd.decode('utf8')
                msg_list.insert(tkinter.END, msg)
        except OSError:  # Possibly client has left the chat.
            break



def receive():
    """Handles receiving of messages."""
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            if msg == '{quit}':
                break
            msg_list.insert(tkinter.END, msg)
        except OSError:  # Possibly client has left the chat.
            break


def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
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
    Thread(target=private_client, args=(name,)).start()

def private_client(name):
    pclient_socket = socket(AF_INET, SOCK_STREAM)
    pclient_socket.connect(ADDR)

    ptop = tkinter.Tk()
    ptop.title("Private Chat")


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
    PORT = 33000
else:
    PORT = int(PORT)

BUFSIZ = 1024
ADDR = (HOST, PORT)

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)


top = tkinter.Tk()
top.title("Chatter")

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
tkinter.mainloop()  # Starts GUI execution.