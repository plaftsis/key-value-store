# Key-Value Store

This project is a prototype implementation of a distributed, fault-tolerant Key-Value database. It was created for the postgraduate course M111: Big Data Management, at the Department of Informatics and Telecommunications within the University of Athens.

## Data Creation

Our KV store is able to index data of arbitrary length and arbitrary nesting of the form:

```
key : value
```

In this case, ``​key`` ​represents the key of the data that we care to store and ``value`` is the payload (or value) of the data that we want to store for that key. The ``​value``​ can also contain a set of ​``key : value`` ​pairs. Here is an example of some data that we are interested in storing in our KV store:

```
"person1" : { "name" : "John" ; "age" : 22 }
"person2" : { "name" : "Mary" ; "address" : { "street" : "Panepistimiou" ; "number" : 12 } } "person3" : { "height" : 1.75 ; "profession" : "student" }
"person4" : {}
```

We have implemented a script for generating syntactically correct data that can be loaded to the key value store. The script operates as follows:

```bash
python create_data.py -k keyFile.txt -n 1000 -d 3 -l 4 -m 5 > dataToIndex.txt
```
where

-n​ indicates the number of lines (i.e. separate data) that we would like to generate.

-d ​is the maximum level of nesting. Zero means no nesting.

-m​ is the maximum number of keys inside each value.

-l ​is the maximum length of a string value whenever you need to generate a string. Strings can be only letters (upper and lowercase) and numbers. No symbols.

-k is a file containing a space-separated list of key names and their data types that we can potentially use for creating dummy data. For example:
```
name string
age int
height float
street string
level int
```

## Key-Value Broker

The Key-Value broker accepts queries and redirects requests to the Key-Value servers, collecting the results and presenting them to the user.

The KV broker starts with the following command:
```bash
python kv_broker.py -s serverFile.txt -i dataToIndex.txt -k 2
```

The ​``serverFile.txt``​ is a space separated list of server IPs and their respective ports that will be listening for queries and indexing commands. For example:
```
127.0.0.1 65432
127.0.0.1 65433
127.0.0.1 65434
```
Is an example of a ​server file​ indicating that this broker will be working with 3 servers with the IPs described and on the respective ports described.

The ​``dataToIndex.txt​`` is a file containing dummy data that was generated in the previous part of the project.

The ​``k​`` value is the replication factor, i.e. how many different servers will have the same replicated data.

Once the KV broker starts, it connects to all the servers, and for each line ​of ``dataToIndex.txt``​ it randomly picks ​``k`` ​servers where it sends a request of the form ``PUT data``. It then waits for user input.
 
The KV broker can be terminated by either typing ​``exit​`` and hitting ​``​Enter`` or pressing ​``Ctrl+C​``.

## Key-Value Server
The KV server starts at the specified IP address and port (which should be one from the server file that the broker is accepting as input) and is waiting for queries. In order to search the data internally (in-memory) efficiently the server maintains a Trie data structure where both top-level and nested keys are stored.

The KV server starts with the following command:
```bash
python kv_server.py -a 127.0.0.1 -p 65432
```

The KV server can be terminated by pressing ​``Ctrl+C​``.


## Usage
The KV store supports the following case-insensitive commands given in the broker:

### ``PUT data``

Both top-level and nested keys should be quoted. For example:
```bash
~ $ PUT "person1" : { "name" : "John" ; "age" : 22 }
OK
~ $ put "person1" : {}
ERROR: Key already exists
```

### ``GET key``

Quotes are not accepted here. If >= ``k`` servers are down the broker cannot guarantee the correct output and prints a warning message. For example:
```bash
~ $ GET person1
person1 : { name : John ; age : 22 }
~ $ GET name
NOT FOUND
~ $ get person2
WARNING: more than 2 server(s) are down and therefore the correct output cannot be guaranteed
NOT FOUND
```

### ``DELETE key``

This command needs to be forwarded to all servers. If there is even one server down, delete cannot be reliably executed and thus a message appears indicating that delete cannot happen. For example:
```bash
~ $ delete person1
OK
~ $ DELETE person2
WARNING: more than 1 server(s) are down and therefore the correct output cannot be guaranteed
ERROR: Delete cannot be reliably executed
```

### ``QUERY keypath``

This command is similar to GET above but is meant to return the value of a subkey. For example:
```bash
~ $ QUERY person2.name
person2.name : Mary
```

## License
[MIT](https://choosealicense.com/licenses/mit/)
