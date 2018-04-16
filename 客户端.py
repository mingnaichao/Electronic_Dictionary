from socket import *
from signal import *
from time import *
import sys
import os


def do_register(sockfd):
    name = input('请输入您的用户名：')
    passwd = input('请输入您的密码：')
    msg = 'R %s %s' % (name, passwd)

    sockfd.send(msg.encode())
    msg = sockfd.recv(1024).decode()

    if msg[0:2] == 'OK':
        return 0
    else:
        return -1


def do_login(sockfd, msg):
    name = input('请输入您的姓名：')
    passwd = input('请输入您的密码：')
    msg = 'L %s %s' % (name, passwd)

    sockfd.send(msg.encode())
    msg = sockfd.recv(1024).decode()

    if msg[0:2] == 'OK':
        return name
    else:
        return -1


def do_query(sockfd, name):
    while True:
        word = input('请输入您要查询的单词：')

        if word == '##':
            return
        msg = 'Q %s %s' % (word, name)

        sockfd.send(msg.encode())
        msg2 = sockfd.recv(1024).decode()

        if msg2[0:2] == 'OK':
            msg3 = sockfd.recv(1024).decode()
            if msg3[0:9] == 'not found':
                print('没有找到这个单词！')
                continue
            print(msg3)  # 打印单词翻译
        else:
            print('查询失败！')
            continue


def do_history(sockfd, name):
    msg = 'H %s' % name
    sockfd.send(msg.encode())
    msg = sockfd.recv(1024).decode()

    if msg[0:2] == 'OK':
        while True:
            data = sockfd.recv(1024).decode()
            if data == 'over':  # 接收到'over'后退出
                break
            print(data)
    else:
        print('查询历史信息失败！')
        return


def main():
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    ADDR = (HOST, PORT)
    msg = None

    sockfd = socket()  # 创建流式套接字
    sockfd.connect(ADDR)  # 连接服务器

    def login(name):
        '''二级界面操作'''
        while True:
            print('''
            ==========query commend=========
            ---1:查词  2:历史记录  3:退出---
            ================================
            ''')
            try:
                cmd = int(input('请输入您要执行的操作：'))
            except:
                print('输入错误！')  # 拦截非数字操作
                continue
            if cmd not in [1, 2, 3]:
                print('输入错误')  # 拦截数字不在选项中操作
                sys.stdin.flush()
                continue
            if cmd == 1:
                do_query(sockfd, name)
            if cmd == 2:
                do_history(sockfd, name)
            if cmd == 3:
                break
        return

    while True:
        print('''
        =============Welcome=============
        ----1: 注册  2: 登陆  3: 退出----
        =================================
        ''')
        try:
            cmd = int(input('请输入您要执行的操作：'))
        except:
            print('输入错误！')  # 拦截非数字操作
            continue
        if cmd not in [1, 2, 3]:
            print('输入错误')  # 拦截数字不在选项中操作
            sys.stdin.flush()
            continue
        if cmd == 1:
            if do_register(sockfd) == 0:
                print('注册成功！')
            else:
                print('注册失败！')
        if cmd == 2:
            name = do_login(sockfd, msg)
            if name != -1:
                print('登录成功！')
                login(name)
            else:
                print('登录失败！')
        if cmd == 3:
            msg = 'E'
            sockfd.send(msg.encode())
            sockfd.close()
            sys.exit(0)  # 退出


if __name__ == "__main__":
    main()
