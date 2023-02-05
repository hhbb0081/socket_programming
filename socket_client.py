import socket
import threading


def Send(client_sock, mentioned, quized):
    while True:
        if quized == True:
            quized = False
            continue

        # 사용자 입력
        send_data = bytes(input().encode())

        client_sock.send(send_data)  # Client -> Server 데이터 송신


def Recv(client_sock, nameChange, quized):
    chance = 6
    while True:
        recv_data = client_sock.recv(
            1024).decode()
        if str(recv_data) == '접속자 수가 최대 입니다. 들어오실 수 없습니다.':
            print('접속자 수가 이미 최대입니다. 입장하실 수 없습니다.')
            break

        elif str(recv_data) == '이미 존재하는 닉네임입니다. 다시 입력하세요.':
            print('이미 존재하는 닉네임입니다. 다시 입력하세요.')

        elif str(recv_data) == '불가능한 닉네입입니다. 다시 입력하세요.':
            print('불가능한 닉네입입니다. 다시 입력하세요.')

        else:
            print('채팅방에 입장하셨습니다.\n')
            print('\n명령어 도움말\n')
            print('"/?" 는 모든 명령어에 대한 정보를 알려주는 명령어입니다.\n')
            print('"/exit" 는 퇴장 명령어입니다.\n')
            print('"/time" 는 현재 날짜와 시간을 출력하는 명령어입니다.\n')
            print('"/all" 은 현재 채팅방에 있는 모든 유저의 닉네임을 보여주는 명령어입니다.\n')
            print('"/nickname" 은 닉네임을 변경하는 명령어입니다.\n')
            print('"/blockOn" 은 유저를 차단하는 명령어입니다.\n')
            print('"/blockOff" 는 차단을 해제하는 명령어입니다.\n')
            print('"/game" 는 게임을 실행하는 명령어입니다.\n')
            print('"@" 은 언급 명령어입니다. 원하는 유저에게 메시지를 보낼 수 있습니다.\n')
            break

    while True:
        try:
            # 닉네임을 변경하고 있는 중이 아니라면
            if nameChange == False:
                recv_data = client_sock.recv(
                    1024).decode()  # Server -> Client 데이터 수신

                if not recv_data:
                    break

                if recv_data == '존재하지 않는 닉네임입니다. 다시 입력해주세요.\n':
                    print('존재하지 않는 닉네임입니다. 다시 입력해주세요.\n')
                    msg = bytes(input().encode())
                    client_sock.send(msg)

                if recv_data == '차단할 사람의 닉네임을 입력해주세요.\n':
                    msg = bytes(input().encode())
                    client_sock.send(msg)

                if recv_data == '게임을 시작합니다. 1 ~ 100 중 숫자를 맞춰주세요. 기회는 5번입니다.':
                    quized = True

                if quized == True:
                    chance -= 1
                    if recv_data == '정답입니다. 게임을 종료합니다.':
                        print('정답입니다. 게임을 종료합니다.')
                        quized = False
                        continue

                    if recv_data == '실패하셨습니다. 게임을 종료합니다.':
                        print('실패하셨습니다. 게임을 종료합니다.')
                        quized = False
                        continue

                print(recv_data)

            # 닉네임을 변경 중이라면
            else:
                while True:
                    recv_data = client_sock.recv(
                        1024).decode()
                    print(recv_data)
                    # print(recv_data)
                    if str(recv_data) == '이미 존재하는 닉네임입니다. 다시 입력하세요.':
                        print('새로운 닉네임을 입력하세요: ')
                        name = bytes(name.encode())
                        # print(name) //b'333' 출력
                        client_sock.send(name)

                    elif str(recv_data) == '불가능한 닉네입입니다. 다시 입력하세요.':
                        name = input('새로운 닉네임을 입력하세요: ')
                        name = bytes(name.encode())
                        # print(name)
                        client_sock.send(name)

                    else:
                        nameChange = True
                        break

        except:
            pass


# TCP Client
if __name__ == '__main__':
    while True:
        name = input("닉네임을 입력하세요: ")
        break
    client_sock = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM)  # TCP Socket
    Host = 'localhost'  # 통신할 대상의 IP 주소
    Port = 7777  # 통신할 대상의 Port 주소
    nameChange = False
    quized = False
    mentioned = False
    client_sock.connect((Host, Port))  # 서버로 연결시도

    name = bytes(name.encode())
    client_sock.send(name)

    # Client의 메시지를 보낼 쓰레드
    thread1 = threading.Thread(
        target=Send, args=(client_sock, mentioned, quized,))
    thread1.start()

    # Server로 부터 다른 클라이언트의 메시지를 받을 쓰레드
    thread2 = threading.Thread(
        target=Recv, args=(client_sock, nameChange, quized,))
    thread2.start()
