#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2021.02.04

@author: chenyingbo
"""

import socket
import time
import sys
import numpy as np
import struct
import soundfile as sf


#-------------------------------------------------- defines  ----------------------------------------------------#

INVALID_SOCKET = -1
SOCKET_ERROR = -1
TRUE = 1

MICROPHONE_IPADDR = "192.168.0.1"
MICROPHONE_PORT_NUM = 8080
MICROPHONE_CH_NUM = 4
MICROPHONE_HTTP_REQUEST = "GET /stream/audio.wav HTTP/1.1\r\n"      \
                                  "User-Agent: XAvi/1.0.0\r\n"              \
                                  "Host: 192.168.0.1\r\n"                   \
                                  "Accept: */*\r\n"                         \
                                  "\r\n"


#-------------------------------------------------- variables  ----------------------------------------------------#
g_sock = socket.socket()


#-------------------------------------------------- local funcs  --------------------------------------------------#

"""
功能：发送一段字符串；
[i] sock: socket
[i] buf: 消息字符串
[o] int: 发送成功的字节数
"""
def ipc_sock_send(sock, buf):
    data_len = len(buf)
    send_bytes = 0

    while send_bytes < data_len:
        send_bytes = send_bytes + sock.send(buf[send_bytes : data_len].encode())

    if send_bytes != data_len:
        print("send not complete.")

    return send_bytes

"""
功能：接收http回复字符串。收到'\r\n'就停止
[i] sock: 套接字
[i] len: 最大长度，也可以小于这个
[o] string：接收的字符串
"""
def ipc_sock_recv_line(sock, max_len=512):
    ret_str = ''
    last_char = ''
    #tmp_char_origin = sock.recv(1)
    while 1:
        tmp_char = ''
        if len(ret_str) < max_len:
            tmp_char_origin = sock.recv(1)
            #print(str(sys._getframe().f_lineno) + " [line] " + str(tmp_char_origin))

            tmp_char = tmp_char_origin.decode()
            if len(tmp_char) == 0:
                print("Recv line failed: socket close.")
                exit(0)
        else:
            print("Recv line failed: buffer overflow.")
            exit(0)


        ret_str = ret_str + tmp_char
        if len(ret_str) >= 2 and ret_str[-2] == '\r' and ret_str[-1] == '\n':
            break

    return ret_str

"""
功能：发送请求
"""
def send_microphone_request(sock):
    #print("Send microphone request... ")

    try:
        ipc_sock_send(sock, MICROPHONE_HTTP_REQUEST)
    except socket.error:
        print("send MICROPHONE_HTTP_REQUEST failed...")
        exit(0)

    #print("send MICROPHONE_HTTP_REQUEST success.")

"""

"""
def recv_microphone_reply_header(sock):
    #print("receiving server reply... \n")

    ret_str = ipc_sock_recv_line(sock, 512)
    len_1 = len("HTTP/1.1 ")
    len_2 = len("200")
    #print(ret_str)
    if ret_str[len_1: len_1 + len_2] == "200":
        while 1:
            ret_str = ipc_sock_recv_line(sock, 512)
            #print(ret_str)
            if ret_str[0] == '\r' and ret_str[1] == '\n':
                print("receive reply header success\n")
                return 0
    else:
        print("receive reply header failed. ret_str=" + ret_str)
        exit(0)

    return 0

"""
"""
def get_chunk_size(sock):
    ret_str = ipc_sock_recv_line(sock)

    if len(ret_str) == 0:
        print("failed")
        return -1

    # 获取chunk的大小
    chunk_size = 0
    for i in range(len(ret_str) - 1):
        num = ord(ret_str[i])
        if num >= ord('a') and num <= ord('f'):
            chunk_size = chunk_size * 16 + (num - ord('a') + 10)
        elif num >= ord('A') and num <= ord('F'):
            chunk_size = chunk_size * 16 + (num - ord('A') + 10)
        elif num >= ord('0') and num <= ord('9'):
            chunk_size = chunk_size * 16 + (num - ord('0'))

    print(str(sys._getframe().f_lineno) + " [line] " + str(chunk_size))
    return chunk_size

"""
功能：接收一个chunk的data数据
"""
def recv_microphone_data(sock, dst_len):

    left_bytes = dst_len

    #while left_bytes > 0:
    #    tmp_str = sock.recv(left_bytes)
    #    print(tmp_str)

    ret_str = sock.recv(dst_len)
    print(str(sys._getframe().f_lineno)  + "ret_str=" + str(ret_str))

    #while len(ret_str) < dst_len:
    #    ret_str = ret_str + sock.recv()

    #tmp_str = ipc_sock_recv_line(sock, dst_len)
    #print(str(sys._getframe().f_lineno) + " [line] " + tmp_str)
    #sock.recv(2)
    """
    if len(tmp_str) == 0:
        print("failed to read chunk ending.")
        exit(0)
    """

    return ret_str

"""
功能：初始化套接字并成功建立连接
[i] ipaddr: (type: string) 地址
[i] port:  (type: num)端口
[o] socket
"""
def ipc_sock_init(ipaddr, port):
    sock = socket.socket()

    try:
        sock.connect((ipaddr, port))
    except socket.error:
        print("Connect server failed." + str(socket.error))
        exit(0)

    print("Connect server success.")
    return sock


"""
功能：关闭套接字
[i] sock: (socket)
[o] none
"""
def ipc_sock_close(sock):
    return


#-------------------------------------------------- global funcs  --------------------------------------------------#

"""
功能：初始化x20接口
"""
def socket_x20_init():
    sock = ipc_sock_init(MICROPHONE_IPADDR, MICROPHONE_PORT_NUM)
    send_microphone_request(sock)
    recv_microphone_reply_header(sock)

    print("socket_x20_init OK !!!!----------------------------------------------")

    str0 = sock.recv(4)
    str1 = sock.recv(44)
    str2 = sock.recv(2)
    #print(str0)
    #print(str1)
    #print(str2)
    time.sleep(0.016)
    return sock

"""
取得256点数据帧，返回np.array数组，类型是int16
"""
def socket_x20_get(sock):
    data_list = np.zeros((4, 256), dtype='int16')

    str0 = sock.recv(5)
    str1 = sock.recv(2048)
    str2 = sock.recv(2)

    for i in range(256):
        data_four = struct.unpack("hhhh", str1[i * 2 * 4: (i + 1) * 2 * 4])
        for j in range(4):
            data_list[j][i] = data_four[j]
    time.sleep(0.016)
    return data_list

    """
    chunk_size = get_chunk_size(sock)
    if chunk_size <= 0:
        return ''
    elif chunk_size > 3000:
        print("warning, receive size > 3000")

    str = recv_microphone_data(sock, chunk_size)
    """

def socket_x20_get2(sock):
    ret_str = ipc_sock_recv_line(sock)

    chunk_size = 0
    for i in range(len(ret_str) - 1):
        num = ord(ret_str[i])
        if num >= ord('a') and num <= ord('f'):
            chunk_size = chunk_size * 16 + (num - ord('a') + 10)
        elif num >= ord('A') and num <= ord('F'):
            chunk_size = chunk_size * 16 + (num - ord('A') + 10)
        elif num >= ord('0') and num <= ord('9'):
            chunk_size = chunk_size * 16 + (num - ord('0'))

    ret_data = sock.recv(chunk_size)
    ret_inter = sock.recv(2)    # 这个是末尾的 '\r\n'
    print(str(sys._getframe().f_lineno) + " [line] " + str(ret_inter))
    return ret_data

#-------------------------------------------------- main  ----------------------------------------------------#
if __name__ == "__main__":
    frame_count = 60 * 8   # 帧数

    data_binary = np.zeros((1024))
    #data_list = [np.zeros((512,)), np.zeros((512,)), np.zeros((512,)), np.zeros((512,))]
    data_list = np.zeros((4, 256), dtype='int16')
    sock = socket_x20_init()

    for i in range(100):
        str0 = sock.recv(5)
        str1 = sock.recv(2048)
        str2 = sock.recv(2)
        print(i)
        print("str0: " + str(str0))
        print("str1: " + str(str1))
        print("str2: " + str(str2))

    input()


    while frame_count > 0:
        bstr = socket_x20_get2(sock)
        data_tmp = [np.zeros((256,)), np.zeros((256,)), np.zeros((256,)), np.zeros((256,))]
        data_tmp = np.zeros((4, 256))
        #print(len(bstr))

        if len(bstr) == 44:
            time.sleep(0.1)
            print("receive head 44")
        elif len(bstr) != 2048:
            print("data len != 2048, error !!!!!")
        elif len(bstr) == 2048:
            for i in range(256):
                data_four = struct.unpack("hhhh", bstr[i * 2 * 4 : (i + 1) * 2 * 4])
                for j in range(4):
                    data_tmp[j][i] = data_four[j]
        data_list = np.concatenate((data_list, data_tmp), axis=1)
        #print(data_list.shape)

        # 解析二进制流
        frame_count = frame_count - 1
        #time.sleep(0.016)
        #time.sleep(0.001)

    # 保存音频
    data_list.astype("float32")
    data_list = data_list / 32768
    sf.write("0.wav", data_list[0], 16000)
    sf.write("1.wav", data_list[1], 16000)
    sf.write("2.wav", data_list[2], 16000)
    sf.write("3.wav", data_list[3], 16000)
