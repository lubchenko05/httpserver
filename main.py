import os
import sys
import socket


# Стандартные константы
HOST = '127.0.0.1'
PORT = 8000


def connect(host, port):
    """Метод, который развертывает сервер на указанном адресе и порту"""
    try:
        con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        con.bind((host, port))
        con.listen(5)
        return con
    except OSError as e:
        print(e)
        exit()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Таким образом проверяю являеться ли порт интом и больше ли он 0
        try:
            PORT = int(sys.argv[1])
            if PORT < 0:
                raise ValueError
        except ValueError:
            print("Введите корректное значение порта!")
            exit()
    s = connect(HOST, PORT)
    while True:
        # Поток блокируеться, ожидая подключения
        # (можно было сделать и многопоточный сервер, но в задании такого небыло ;P)
        # Как только получил соеденение, он разблокируеться и выводит адрес клиента в консоль
        (client, address) = s.accept()
        print("%s was connected" % str(address))
        # Получаю, декодю байты в строку
        data = client.recv(16384)
        data = data.decode("utf-8")
        # Беру ссылку с запроса
        link = ''
        target = ''
        try:
            link = data.split('\r')[0].split(' ')[1].split('/')[1:]
        except IndexError:
            print("Ошибка запроса")
            continue
        print(link)
        if link[0] == 'favicon.ico':
            client.send('HTTP/1.1 404 NotFound\r\n\n'.encode('UTF-8'))
            client.close()
            continue
        else:
            html = '<html><head></head><body>{content}</body></html>'
            target = link[-1]
            if '.' in target:
                try:
                    RESPONSE = 'HTTP/1.1 200 OK\r\n\n '+open('/'.join(link)).read()
                    client.send(RESPONSE.encode('UTF-8'))
                    client.close()
                except FileNotFoundError:
                    client.send('HTTP/1.1 404 NotFound\r\n\n'.encode('UTF-8'))
                    client.close()
                    continue
            else:
                content = ''
                file = ''
                try:
                    file = os.listdir('./'+'/'.join(link))
                except FileNotFoundError:
                    client.send('HTTP/1.1 404 NotFound\r\n\n'.encode('UTF-8'))
                    client.close()
                    continue
                if 'index.html' in file:
                    RESPONSE = 'HTTP/1.1 200 OK\r\n\n ' + open('./'+'/'.join(link) + '/' + 'index.html').read()
                    client.send(RESPONSE.encode('UTF-8'))
                    continue
                for item in file:
                    content += '<a href="'+target+'/'+item+'">'+item+'</a></br>'
                client.send(('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\n'
                             '<html><head></head><body>{body}</body></html>').format(body=content).encode('UTF-8'))
                client.close()
