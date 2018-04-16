#!/usr/bin/python3
# coding=utf-8

from signal import *
from socket import *
from time import *
import sys
import os
from mysql_python import *

DICT_TEXT = './dict.txt'


def do_register(connfd, msg, db):
    '''实现注册功能'''
    print('进入注册...')
    s = msg.split(' ')
    name = s[1]
    passwd = s[2]

    sql = 'select * from user where name = "%s";' % name
    data = db.all(sql)  # 查不到时data=None
    print(data)

    if data != None:
        connfd.send('该姓名已被注册'.encode())
        return

    sql = 'insert into user values ("%s","%s");' % (name, passwd)

    try:
        db.implement(sql)  # 提交到数据库
        connfd.send('OK'.encode())
    except:
        connfd.send('FALL'.encode())
        db.rollback()  # 插入失败时回滚
        return
    else:
        print('插入成功')


def do_login(connfd, msg, db):
    '''实现登录功能'''
    global data
    print('进入登录...')
    s = msg.split(' ')
    name = s[1]
    passwd = s[2]

    try:
        sql = 'select * from user where name = "%s" and passwd = "%s";' % (
            name, passwd)
        data = db.all(sql)  # 查不到时data=None
        print('用户记录为：', data)
    except:
        print('数据库操作错误！')

    if data == None:
        connfd.send('FALL'.encode())
    else:
        connfd.send('OK'.encode())
    return


def do_query(connfd, msg, db):
    '''实现查询功能'''
    global buf
    print('进入查询...')
    s = msg.split(' ')
    word = s[1]
    name = s[2]

    try:
        f = open(DICT_TEXT, 'rb')
    except:
        print('打开文件失败！')
        connfd.send('FALL'.encode())
        return

    connfd.send('OK'.encode())
    sleep(0.1)  # 防止粘包
    while True:
        try:
            buf = f.readline().decode()
            f.flush()  # 刷新缓冲区
            temp = buf.split(' ')  # 进行字符串解析
        except Exception as e:
            print(e)

        # 第一个单词大于要搜索的单词时，不再查找
        if temp[0] > word:
            connfd.send('not found'.encode())
            f.close()
            break

        if temp[0] == word:
            connfd.send(buf.encode())

            insert_history(db, word, name)

            f.close()
            return


def insert_history(db, word, name):
    '''插入搜索单词到数据库'''
    time = ctime()
    sql = "insert into history values('%s','%s','%s')" % (name, word, time)
    try:
        db.implement(sql)  # 操作数据库
    except:
        print('插入失败！')
        db.rollback()  # 回滚
        return


def do_history(connfd, msg, db):
    '''实现历史查询功能'''
    global results
    print('进入历史记录...')
    s = msg.split(' ')
    name = s[1]

    sql = "select * from history where name = '%s'" % name

    try:
        # results是一个元组(（'name','word','time'）,('name','word','time')...)
        results = db.all(sql)
        connfd.send('OK'.encode())  # 如果可以正确搜索数据库，发送OK
    except:
        print("历史记录失败！")
        db.rollback()
        connfd.send('FALL'.encode())

    # results=(（'name','word','time'）,('name','word','time')...)
    for name, word, time in results:
        sleep(0.1)  # 防止粘包
        connfd.send(("%s - %s - %s" % (name, word, time)).encode())

    sleep(0.1)
    connfd.send('over'.encode())  # 历史记录发送完了
    return


def do_child(connfd, db):
    '''子进程，用来处理具体事情'''
    while True:
        msg = connfd.recv(1024).decode()  # msg = 'xx xx xx'
        print('msg:', msg)

        if msg[0] == 'R':
            # 注册
            do_register(connfd, msg, db)
        if msg[0] == 'L':
            # 登录
            do_login(connfd, msg, db)
        if msg[0] == 'Q':
            # 查询
            do_query(connfd, msg, db)
        if msg[0] == 'H':
            # 查看历史记录
            do_history(connfd, msg, db)
        if msg[0] == 'E':
            # 关闭套接字，退出
            connfd.close()
            sys.exit(0)


def main():
    # 防止僵尸进程
    signal(SIGCHLD, SIG_IGN)
    # 主进程中连接数据库，生成数据库对象
    db = mysql_python("localhost", 3306, "Dict", "root", "mnc03141212")

    HOST = sys.argv[1]
    PORT = int(sys.argv[2])

    sockfd = socket()  # 创建流式套接字
    sockfd.bind((HOST, PORT))
    sockfd.listen(5)

    while True:
        try:
            # 阻塞等待客户端连接
            connfd, addr = sockfd.accept()
            print('connect addr:', addr)
        except KeyboardInterrupt:
            raise
        except:
            continue

        # 多进程并发
        pid = os.fork()
        if pid < 0:
            print('create child process failed')
            connfd.close()  # 关闭连接套接字
            continue
        elif pid == 0:
            sockfd.close()  # 关闭监听套接字
            do_child(connfd, db)
        else:
            connfd.close()  # 关闭连接套接字
            continue

    db.close()  # 关闭数据库连接
    sockfd.close()  # 关闭监听套接字
    sys.exit(0)  # 安全退出


if __name__ == '__main__':
    main()
