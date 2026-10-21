Names: Annie Liu (agb2275), Ken Zheng (ktz9099)
How to run: run the following command inside this directory:
```python3 part1.py```

Design description:
`main`: handles event loop, waiting for response
`handle_client`: handles receiving/parsing user query and sending DNS response back to client 
`forward`: forwards a DNS query to google's dns resolver
`parse_question`: parses a user query to get the question type and name 

- Primary script at `main()` starts by creating a UDP socket listening on 127.0.0.1:1053
- The event loop loops forever waiting for a user query from the socket
    - Upon receiving a user query, it asynchronously runs `handle_client` for this query
- `handle_client` parses the user query with `parse_question` to get the name and type
- `handle_client` also calls `forward` 
- `forward` attempts to forward the query data to `8.8.8.8:53`
    - This will retry 3 times and has a timeout of 5 seconds.
- If it gets a response it prints the name, type, and length of the response and returns the response
- `handle_client` gets the return from `forward` and sends it back to the client
