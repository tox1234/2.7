"""
Author: Ido Shema
Date: 10/12/2023
Description: server
"""

import socket
import glob
import os
import shutil
import subprocess
import pyautogui
import base64

MAX_PACKET = 1024
QUEUE_LEN = 1


def dir(path):
    """
        copies a file from the orginial_path into the copy_path
        :param path: the path to check
        :type: function
        :return: the files within a folder and "couldn't find the path" if it didn't find the path
    """
    try:
        files_list = glob.glob(path + "/*.*")
        final_dir = ', '.join(files_list).replace('\\', '/')
        print(final_dir)
    except FileNotFoundError:
        final_dir = "couldn't find the path"
    return final_dir


def delete(path_file):
    """
        deletes a file from a certain path
        :param path_file: the path string
        :type: function
        :return: "successfully deleted file" if file has been successfully delete and "File doesn't exist" if it didn't
    """
    try:
        os.remove(path_file)
        return "successfully deleted file"
    except FileNotFoundError:
        return "File doesn't exist"


def copy(original_path, copy_path):
    """
        copies a file from the orginial_path into the copy_path
        :param original_path: the original path string
        :param copy_path: the to copy path string
        :type: function
        :return: "File has been successfully copied" if file has been successfully copied and "File hasn't been copied" if it didn't
    """
    try:
        shutil.copy(original_path, copy_path)
        return "File has been successfully copied"

    except FileNotFoundError:
        return "File hasn't been copied"


def execute(process_name):
    """
        executes a program from system32
        :param process_name: the process name to execute
        :type: function
        :return: "file has been successfully executed" if program has been successfully executed and "Couldn't run process" if it didn't
    """
    try:
        subprocess.call('C:/Windows/System32/' + process_name)
        return "program has been successfully executed"

    except ProcessLookupError:
        return "Couldn't run process"


def screenshot():
    """
        takes a screenshot and converts it into string
        :param
        :type: function
        :return: the converted string if it could convert it and returns the error if it didn't
    """
    try:
        image = pyautogui.screenshot()
        image.save(r'screen.jpg')
        with open('screen.jpg', 'rb') as image_file:
            encoded_image = base64.b64encode(image_file.read())
            encoded_string = encoded_image.decode("utf-8")
            return encoded_string

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
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind(('0.0.0.0', 1729))
        server_socket.listen(QUEUE_LEN)
        while True:
            client_socket, client_address = server_socket.accept()
            try:
                while True:
                    request = receive_protocol(client_socket)
                    cmd = request[0]
                    other = request[1]
                    if request[0] == 'Dir':
                        sent_message = dir(other)
                    elif request[0] == 'Delete':
                        sent_message = delete(other)
                    elif request[0] == 'Copy':
                        lst = other.split("!")
                        part1 = lst[0]
                        part2 = lst[1]
                        sent_message = copy(part1, part2)

                    elif request[0] == 'Execute':
                        sent_message = execute(other)

                    elif request[0] == "Screenshot":
                        sent_message = screenshot()

                    elif request[0] == 'Exit':
                        client_socket.send(send_protocol('You were disconnected from the server', ''))
                        break
                    else:
                        sent_message = 'not a valid command'
                    client_socket.send(send_protocol(cmd, sent_message))
            except socket.error as err:
                print('received socket error on client socket' + str(err))
            finally:
                client_socket.close()
    except socket.error as err:
        print('received socket error on server socket' + str(err))
    finally:
        server_socket.close()


if __name__ == '__main__':
    main()
