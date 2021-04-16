import argparse
import socket
import random


class KVBroker:

    def __init__(self, server_file, replication_factor):
        self.replication_factor = replication_factor
        self.servers = []
        with open(server_file) as f:
            text = f.read()
            for line in text.splitlines():
                ip_address, port = line.split()
                self.servers.append({'ip_address': ip_address, 'port': int(port)})
        self.connections = []

    def connect(self):
        for server in self.servers:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                s.connect((server['ip_address'], server['port']))
                self.connections.append(s)
            except ConnectionRefusedError:
                print('Server {} is down'.format(server['ip_address']))

    def check(self):
        down = 0
        for conn in self.connections:
            try:
                conn.sendall(b'PING')
                conn.recv(1024)
            except:
                down += 1
        if down == len(self.servers):
            print('ERROR: All servers are down')
            exit(1)
        elif down >= self.replication_factor:
            print(
                'WARNING: more than {} server(s) are down and therefore the correct output cannot be guaranteed'.format(
                    args.replication_factor))
        return down

    def index_data(self, data_to_index):
        with open(data_to_index) as f:
            text = f.read()
            for line in text.splitlines():
                query = 'PUT {}'.format(line)
                for conn in random.sample(self.connections, self.replication_factor):
                    conn.sendall(query.encode())
                    data = conn.recv(1024)
                    print(data.decode())

    def query(self, query):
        down = self.check()
        try:
            command = query.split(' ', 1)[0].upper()
        except ValueError:
            command = query
        if down > 0 and command == 'DELETE':
            return 'ERROR: Delete cannot be reliably executed'
        result = 'NOT FOUND'
        for conn in self.connections:
            try:
                conn.sendall(query.encode())
                data = conn.recv(1024)
                result = data.decode()
                if result != 'NOT FOUND':
                    break
            except BrokenPipeError:
                continue
        return result

    def close(self):
        for conn in self.connections:
            conn.close()


def main(args):
    kv_broker = KVBroker(args.server_file, args.replication_factor)
    kv_broker.connect()
    kv_broker.check()
    kv_broker.index_data(args.data_to_index)

    while True:
        try:
            query = input()
            if query == 'exit':
                break
            result = kv_broker.query(query)
            print(result)
        except KeyboardInterrupt:
            break

    kv_broker.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', dest='server_file', default='serverFile.txt',
                        help='Separated list of server IPs and their respective ports', type=str)
    parser.add_argument('-i', dest='data_to_index', default='dataToIndex.txt',
                        help='Data to index', type=str)
    parser.add_argument('-k', dest='replication_factor', default='1',
                        help='Replication factor', type=int)

    args = parser.parse_args()

    main(args)
