import socket
import threading
import datetime
from queue import Queue
import random


# 서버에서 클라이언트로 보내는 스레드


def Send(users, send_queue, name, mentioned):
    print('Thread Send Start')
    while True:
        try:
            # 새롭게 추가된 클라이언트가 있을 경우 Send 쓰레드를 새롭게 만들기 위해 루프를 빠져나감

            recv = send_queue.get()

            if mentioned == True:
                mentioned = False
                continue

            if recv == '입장':
                print('입장')
                break

            now = datetime.datetime.now()
            newDate = now.strftime("%H시 %M분")

            if str(recv[0]) == '/nickname':
                continue

            if str(recv[0]) == '@':
                mentioned = True
                continue

            name = recv[3]
            if name.find('block:') != -1:
                # 차단한 사람의 인덱스 변수
                blockIdx = int(name[0])
                blockCnt = name.index('b')

                tmp = 0
                # 해당 인덱스 닉네임 찾기
                startName = blockCnt + 6
                name = name[int(startName):]
                for conn in users:
                    msg = '[' + str(newDate) + '] ' +  \
                        str(name) + ' : ' + str(recv[0])

                    if blockIdx == tmp:
                        tmp += 1
                        continue
                    elif recv[1] != conn:
                        tmp += 1
                        conn.send(bytes(msg.encode()))
                    else:
                        tmp += 1
                        pass

                continue

            for conn in users:
                msg = '[' + str(newDate) + '] ' +  \
                    str(recv[3]) + ' : ' + str(recv[0])
                # 본인 제외 모두에게 메시지 전달
                if recv[1] != conn:
                    conn.send(bytes(msg.encode()))
                else:
                    pass

            print(str(msg))
        except:
            pass


def sendExit(users, name):
    # 클라이언트 퇴장 알림 함수
    print(str(name) + '님이 퇴장하셨습니다.')
    for conn in users:
        msg = str(name) + '님이 퇴장하셨습니다.'
        conn.send(bytes(msg.encode()))


def sendEnt(users, name):
    # 클라이언트 입장 알림 함수
    for conn in users:
        msg = str(name) + "님이 입장하셨습니다. 현재 인원은 " + str(len(users)) + '명 입니다.'
        conn.send(bytes(msg.encode()))


def sendMention(users, name, num, content):
    # 언급 메시지 보내는 함수
    msg = str(name) + '님에게서 온 메시지:' + str(content)
    conn = users[num]
    conn.send(bytes(msg.encode()))


def sendNewNickname(users, name, msg):
    # 클라이언트 닉네임 변경 알림 함수

    msg += str(name) + '로 변경하셨습니다.'
    for conn in users:
        conn.send(bytes(msg.encode()))
    print(msg)


def Recv(conn, send_queue, nicknames, mentioned, blocked, quized):
    # 클라이언트에서 오는 메시지 받는 스레드
    print('Thread Recv' + str(len(users)) + ' Start')

    # 처음 입장할 때 닉네임 설정하는 while문
    while True:
        name = conn.recv(1024).decode()

        # 이미 존재하는 닉네임이면 다시 입력하도록 함
        if (str(name) in nicknames) == True:
            msg = '이미 존재하는 닉네임입니다. 다시 입력하세요.'
            conn.send(bytes(msg.encode()))
            continue

        # 명령어를 입력하면 다시 입력하도록 함
        elif str(name) == '/exit' or str(name) == '/' or str(name) == '/time' or str(name) == '/all' or str(name) == '/nickname' or str(name) == '/blockOn' or str(name) == '/blockOff' or str(name) == '/game' or str(name) == '@':
            msg = '불가능한 닉네입입니다. 다시 입력하세요.'
            conn.send(bytes(msg.encode()))
            continue

        else:
            nicknames.append(str(name))
            answer = random.randint(1, 100)
            quiz_answer[name] = answer
            print(quiz_answer)
            break
    data = str(name) + "님이 입장하셨습니다. 현재 인원은 " + str(len(users)) + '명 입니다.'
    print(data)
    sendEnt(users, name)

    chance = 5
    while True:
        data = conn.recv(1024).decode('utf-8')

        if quized == True:
            chance -= 1
            print(chance)
            if str(quiz_answer[name]) == data:
                msg = '정답입니다. 게임을 종료합니다.'
                conn.send(bytes(msg.encode()))
                quized = False
                chance = 5
                continue

            if chance == 0 and str(quiz_answer[name]) != data:
                msg = '실패하셨습니다. 게임을 종료합니다.'
                conn.send(bytes(msg.encode()))
                quized = False
                chance = 5
                continue

            elif str(quiz_answer[name]) < data:
                msg = '더 작습니다.'
                conn.send(bytes(msg.encode()))
                continue
            else:
                msg = '더 큽니다.'
                conn.send(bytes(msg.encode()))
                continue

        # 언급
        if mentioned == True:
            menNum = data.index(' ')
            menNick = data[0:menNum]

            # 받는 사람 인덱스 찾기
            recvIndex = 0
            recvNum = 0
            for tmpUser in nicknames:
                if tmpUser == str(menNick):
                    recvNum = recvIndex
                    break
                else:
                    recvIndex += 1

            content = data[menNum:]

            sendMention(users, name, recvNum, content)
            mentioned = False

        # 차단
        if blocked == True:

            # 닉네임 받기
            blockNick = data
            blockIndex = 0

            # 차단할 사람 인덱스 찾기
            tmpindex = 0
            for tmpUser in nicknames:
                if tmpUser == blockNick:
                    blockIndex = tmpindex
                else:
                    tmpindex += 1

            # 이미 차단한 사람이 존재한다면
            if name.find('block:') != -1:
                name = str(blockIndex) + name

            else:
                name = str(blockIndex) + 'block:' + str(name)

            msg = blockNick + '님을 차단하셨습니다.'
            conn.send(bytes(msg.encode()))
            blocked = False
            continue

        # 퇴장
        if data == '/exit':
            sendExit(users, name)
            users.remove(conn)
            conn.close()
            break

        # 명령어 도움말
        if str(data) == '/?':
            msg = '\n명령어 도움말\n\n'
            msg += '"/?" 는 모든 명령어에 대한 정보를 알려주는 명령어입니다.\n\n'
            msg += '"/exit" 는 퇴장 명령어입니다.\n\n'
            msg += '"/time" 는 현재 날짜와 시간을 출력하는 명령어입니다.\n\n'
            msg += '"/all" 은 현재 채팅방에 있는 모든 사람의 닉네임을 보여주는 명령어입니다.\n\n'
            msg += '"/nickname" 은 닉네임을 변경하는 명령어입니다.\n\n'
            msg += '"/blockOn" 은 유저를 차단하는 명령어입니다.\n\n'
            msg += '"/blockOff" 는 차단을 해제하는 명령어입니다.\n\n'
            msg += '"/game" 는 게임을 실행하는 명령어입니다.\n\n'
            msg += '"@" 은 언급 명령어입니다.\n'
            conn.send(bytes(msg.encode()))
            continue

        # 닉네임 모두 보여주기
        if str(data) == '/all':
            number = 1
            msg = '\n닉네임 목록\n'
            for user in nicknames:
                msg += str(number) + '번: ' + str(user) + '\n'
                number += 1
            conn.send(bytes(msg.encode()))
            continue

        # 닉네임 바꾸기
        if data == '/nickname':
            oldName = str(name)

            # 새로운 닉네임 지정
            while True:
                newName = conn.recv(1024).decode()
                if (str(newName) in nicknames) == True:
                    msg = '이미 존재하는 닉네임입니다. 다시 입력하세요.'
                    conn.send(bytes(msg.encode()))
                    continue

                elif str(newName) == '/exit' or str(newName) == '/' or str(newName) == '/time' or str(newName) == '/all' or str(newName) == '/nickname' or str(newName) == '/blockOn' or str(newName) == '/blockOff' or str(newName) == '/game' or str(newName) == '@':

                    msg = '불가능한 닉네입입니다. 다시 입력하세요.'
                    conn.send(bytes(msg.encode()))
                    continue

                else:
                    msg = str(oldName) + '님이 닉네임을 '

                    # 변경 전 닉네임의 인덱스 위치 찾기
                    tmpNum = 0
                    for tmpNick in nicknames:
                        if tmpNick == str(oldName):
                            nickIndex = tmpNum
                        else:
                            tmpNum += 1

                    # nicknames 리스트에서 변경 전 닉네임 삭제
                    nicknames.remove(str(oldName))

                    # 변경 전 닉네임이 존재한 인덱스로 변경 후 닉네임 삽입
                    nicknames.insert(nickIndex, str(newName))

                    # 변경 완료 메시지 보내는 함수 호출
                    sendNewNickname(users, newName, msg)

                    # 변경 후 닉네임을 클라이언트 닉네임으로 설정
                    name = newName
                break

        # 언급
        if data == '@':
            msg = '언급할 사람의 닉네임과 보낼 메시지를 입력해주세요.("닉네임 메시지")\n'

            # 유저 목록 보여주기
            number = 1
            for user in nicknames:
                if str(name) != user:
                    msg = msg + str(number) + '번 사용자: ' + str(user) + '\n'
                else:
                    number -= 1
                number += 1

            conn.send(bytes(msg.encode()))
            mentioned = True

        # 차단
        if data == '/blockOn':
            if name.find('block:') != -1:
                msg = '두 명 이상의 차단은 불가능합니다.\n'
                conn.send(bytes(msg.encode()))
                continue

            msg = '차단할 사람의 닉네임을 입력해주세요.\n'

            number = 1
            # 닉네임 목록 출력
            for user in nicknames:
                if str(name) != user:
                    msg = msg + str(number) + '번 사용자: ' + str(user) + '\n'
                else:
                    number -= 1
                number += 1

            conn.send(bytes(msg.encode()))
            blocked = True
            continue

        # 차단 해제
        if data == '/blockOff':
            if name.find('block:') == -1:
                msg = '차단한 유저가 존재하지 않습니다.\n'
                conn.send(bytes(msg.encode()))
                continue

            name = name[7:]
            msg = '차단 해제가 완료되었습니다.'
            conn.send(bytes(msg.encode()))
            continue

        # 게임
        if data == '/game':
            msg = '게임을 시작합니다. 1 ~ 100 중 숫자를 맞춰주세요. 기회는 5번입니다.'
            conn.send(bytes(msg.encode()))
            quized = True
            continue

        # 현재 날짜, 시간 표시
        if data == '/time':
            now = datetime.datetime.now()
            newDate = now.strftime("%Y년 %m월 %d일, %H시 %M분")

            msg = "현재 " + str(newDate) + '입니다.'
            conn.send(bytes(msg.encode()))
            continue

        send_queue.put([data, conn, len(users), name])


# TCP Echo Server
if __name__ == '__main__':
    send_queue = Queue()
    HOST = ''  # 수신 받을 모든 IP를 의미
    PORT = 7777  # 수신받을 Port
    lock = threading.Lock()
    server_sock = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM)  # TCP Socket
    server_sock.bind((HOST, PORT))  # 소켓에 수신받을 IP주소와 PORT를 설정
    server_sock.listen(4)  # 소켓 연결, 여기서 파라미터는 접속수를 의미

    MaxUser = 5
    users = []  # 연결된 클라이언트의 소켓정보를 리스트로 묶기 위함
    nicknames = []
    quiz_answer = {}
    mentioned = False
    blocked = False
    quized = False
    name = ''
    while True:
        conn, addr = server_sock.accept()  # 해당 소켓을 열고 대기

        users.append(conn)  # 연결된 클라이언트의 소켓정보

        if len(users) >= MaxUser:
            msg = '접속자 수가 최대 입니다. 들어오실 수 없습니다.'
            conn.send(bytes(msg.encode()))
            users.remove(conn)
            break
        print('Connected ' + str(addr) + '\n' +
              '현재 접속자 수는 ' + str(len(users)) + '명 입니다.')

        # 소켓에 연결된 모든 클라이언트에게 동일한 메시지를 보내기 위한 쓰레드(브로드캐스트)
        # 연결된 클라이언트가 1명 이상일 경우 변경된 users 리스트로 반영
        name = ''
        if len(users) > 1:
            send_queue.put('입장')
            thread1 = threading.Thread(
                target=Send, args=(users, send_queue, name,  mentioned,))
            thread1.start()
            pass
        else:
            thread1 = threading.Thread(
                target=Send, args=(users, send_queue, name,  mentioned,))
            thread1.start()

        # 소켓에 연결된 각각의 클라이언트의 메시지를 받을 쓰레드
        thread2 = threading.Thread(
            target=Recv, args=(conn,  send_queue, nicknames, mentioned, blocked, quized))
        thread2.start()
