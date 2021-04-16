import argparse
import socket
import json
import re

from trie import Trie


def parse(obj):
    key, value = obj.split(':', 1)
    key = re.search(r'"([A-Za-z0-9_\./\\-]*)"', key).group(1)
    value = json.loads(value.strip().replace(';', ','))
    return key, value


def beautify(value):
    return json.dumps(value).replace('"', '').replace(',', ' ;').replace('{', '{ ').replace('}', ' }')


def put(trie, payload):
    try:
        key, value = parse(payload)
        if trie.insert(trie.root, key, value):
            return 'OK'
        else:
            return 'ERROR: Key already exists'
    except Exception:
        return 'ERROR: Wrong format'


def get(trie, payload):
    if payload:
        key = payload.strip()
        if re.match("^[A-Za-z0-9]*$", key):
            value = trie.find(key)
            if value is not None:
                return '{} : {}'.format(key, beautify(value))
            else:
                return 'NOT FOUND'
        else:
            return 'ERROR: Key can contain only letters and numbers'
    else:
        return 'ERROR: Key missing'


def delete(trie, payload):
    if payload:
        key = payload.strip()
        if re.match("^[A-Za-z0-9]*$", key):
            if trie.delete(key):
                return 'OK'
            else:
                return 'NOT FOUND'
        else:
            return 'ERROR: Key can contain only letters and numbers'
    else:
        return 'ERROR: Key missing'


def query(trie, payload):
    if payload:
        keypath = payload.strip()
        value = trie.find(keypath)
        if value is not None:
            return '{} : {}'.format(keypath, beautify(value))
        else:
            return 'NOT FOUND'
    else:
        return 'ERROR: Keypath missing'


def main(args):

    host = args.ip_address
    port = args.port

    trie = Trie()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()

        while True:
            try:
                conn, addr = s.accept()
                with conn:
                    print('Connected by', addr)
                    while True:
                        data = conn.recv(1024)
                        input = data.decode()

                        try:
                            command, payload = input.split(' ', 1)
                            command = command.upper()
                        except ValueError:
                            command = input
                            payload = None

                        if command == 'PUT':
                            result = put(trie, payload)
                        elif command == 'GET':
                            result = get(trie, payload)
                        elif command == 'DELETE':
                            result = delete(trie, payload)
                        elif command == 'QUERY':
                            result = query(trie, payload)
                        elif command == 'PING':
                            result = 'PONG'
                        else:
                            result = 'ERROR: Command not found'

                        conn.sendall(result.encode())
            except (ConnectionResetError, BrokenPipeError):
                continue
            except KeyboardInterrupt:
                if conn:
                    conn.close()
                break


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-a', dest='ip_address', default='127.0.0.1',
                        help='IP address', type=str)
    parser.add_argument('-p', dest='port', default='65432',
                        help='Port', type=int)

    args = parser.parse_args()

    main(args)
