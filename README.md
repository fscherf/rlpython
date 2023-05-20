# rlpython

rlpython is a GNU Readline based Python REPL without any external dependencies


## Installation

```shell
$ pip install rlpython
```


## Starting rlpython from the command line

```shell
$ rlpython
```


## Starting rlpython from Python code

```python
import rlpython

rlpython.embed()
```


## Attach a rlpython shell over network

```python
import rlpython

rlpython.embed(bind='localhost:5000')
```


```shell
$ rlpython localhost:5000
```


## Start a multisession shell server

### Server

```python
import asyncio

import rlpython

loop = asyncio.get_event_loop()

with rlpython.embed(bind='localhost:5000', multi_session=True):
    loop.run_forever()
```


```shell
$ rlpython localhost:5000
```
