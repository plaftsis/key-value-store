import argparse
import random
import string


def random_value(type):
    if type == 'int':
        return random.randint(0, 100)
    elif type == 'float':
        return round(random.uniform(0, 100), 2)
    elif type == 'string':
        return''.join(random.choice(string.ascii_letters) for i in range(args.max_string_length))
    else:
        return None


def generate_value(type, level, max_keys_number, keys):
    nesting_level = random.randint(0, level)
    if nesting_level == 0:
        return random_value(type)
    else:
        dict = {}
        for i in range(random.randint(0, max_keys_number)):
            key = random.choice(keys)
            dict[key['name']] = generate_value(key['type'], level-1, max_keys_number, keys)
        return dict


def main(args):

    keys = []
    with open(args.key_file) as f:
        text = f.read()
        for line in text.splitlines():
            name, type = line.split()
            keys.append({'name': name, 'type': type})

    for i in range(args.number_of_lines):
        dict = {}
        if args.max_nesting_level > 0:
            for j in range(random.randint(0, args.max_keys_number)):
                key = random.choice(keys)
                dict[key['name']] = generate_value(key['type'],
                                                   random.randint(0, args.max_nesting_level-1),
                                                   args.max_keys_number,
                                                   keys)
        print('"key{}" : {}'.format(i + 1, str(dict).replace('\'', '\"').replace(',', ' ;')))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-k', dest='key_file', default='keyFile.txt',
                        help='File containing a space-separated list of key names and their data types', type=str)
    parser.add_argument('-n', dest='number_of_lines', default='1000',
                        help='Number of lines to generate', type=int)
    parser.add_argument('-d', dest='max_nesting_level', default='3',
                        help='=Maximum level of nesting', type=int)
    parser.add_argument('-l', dest='max_string_length', default='4',
                        help='Maximum length of a string value whenever generating a string', type=int)
    parser.add_argument('-m', dest='max_keys_number', default='5',
                        help='Maximum number of keys inside each value', type=int)

    args = parser.parse_args()

    main(args)
