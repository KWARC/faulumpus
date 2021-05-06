# FAULumpus


### Requirements
You need to have a recent Python version.
Furthermore, you will need the `requests` library.
You should be able to install it with `pip`:
```
pip3 install requests
```


### Creating an agent
You can create a new agent by modifying `agent.py`.
The file contains the relevant instructions.
Don't forget to set appropriate values for `AGENT_NAME`, `AGENT_PASSWORD` and `AGENT` at the end of the file!

### Testing your agent locally
You should be able to test your agent locally.
You can start a server on localhost using
```
python3 server.py
```
To test your agent, you can then start the client with
```
python3 client.py
```

To see how your agent performs, the server can visualize the games.
Simply start the server with the `-visualize` option:
```
python3 server.py -visualize
```
You can run the client with the `-step` option to wait for your input before each move:
```
python3 client.py -step
```

If you press the left control key in the server's GUI, you can see the undiscovered squares.


### Competing on `faulumpus.kwarc.info`
To compete with your agent on `faulumpus.kwarc.info`, you have to pass the `-compete` option to the client:
```
python3 client.py -compete
```


### The world generator
If you want to get a feeling for what the FAULumpus world looks like,
you can run
```
python3 generate.py
```
It displays randomly generated worlds.
Press `Return` to show generate a new world.
