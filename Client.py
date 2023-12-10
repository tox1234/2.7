"""
Author: Ido Shema
Date: 10/12/2023
Description: client
"""

import socket
import base64
from io import BytesIO
from PIL import Image


MAX_PACKET = 1024

commands = ["Delete", "Copy", "Execute", "Screenshot", "Dir", "Exit"]


def command(message):
    """
    checks to see if message is a valid command
    :param message: the command the user has entered
    :type: string
    :return: if the message is a command then it will return the message and if it isn't it will return 'not valid'
    """
    if message not in commands:
        message = 'not valid'
    return message


def convert_string_to_image(string):
    """
        converts a string to an image and saves the image
        :param string: the string of the image to convert
        :type: string
        :return: "image has been successfully saved" if success and the error if it didn't
    """
    try:
        decoded_image = base64.b64decode(string)
        image_data = BytesIO(decoded_image)
        image = Image.open(image_data)
        image.save(r'decoded_img.jpg')
        return "image has been successfully saved"

    except Exception as e:
        return f"Error: {str(e)}"


def send_protocol(cmd, msg):
    cmd_len = len(cmd)
    msg_len = len(msg)
    total_message = str(cmd_len) + '$' + cmd + str(msg_len) + '$' + msg
    total_message = total_message.encode()
    return total_message


def receive_protocol(client_socket):
    special_character = ''
    cmd_len = ''
    msg_len = ''
    try:
        while special_character != '$':
            special_character = client_socket.recv(1).decode()
            cmd_len += special_character
        cmd_len = cmd_len[:-1]

        cmd = client_socket.recv(int(cmd_len)).decode()

        special_character = ''

        while special_character != '$':
            special_character = client_socket.recv(1).decode()
            msg_len += special_character
        msg_len = msg_len[:-1]

        msg = client_socket.recv(int(msg_len)).decode()

        final_message = (cmd, msg)
    except socket.error:
        final_message = ('There was an error', '')
    return final_message


def main():
    print("The allowed commands are:")
    string = ""
    for i in commands:
        string += i + ","
    print(string[:-1])
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect(('127.0.0.1', 1729))
        while True:
            cmd = input("Enter command:")
            cmd = command(cmd)
            if cmd == "Copy":
                path1 = input("Enter original path:")
                path2 = input("Enter path to copy to:")
                msg = path1 + "!" + path2
            elif cmd == "Screenshot" or cmd == "Exit":
                msg = ""
            else:
                msg = input("enter path/program:")

            if cmd != 'not valid':
                client_socket.send(send_protocol(cmd, msg))
                response = receive_protocol(client_socket)
                if cmd != "Screenshot":
                    print(response[1])
                elif cmd == "Screenshot":
                    convert_string_to_image(response[1])
                    print("Screenshot has been taken!")

                if response[0] == 'You were disconnected from the server':
                    print("Exiting....")
                    break
            else:
                print('not a valid command')
    except socket.error as err:
        print("Received socket error " + str(err))
    finally:
        client_socket.close()


if __name__ == '__main__':
    main()
