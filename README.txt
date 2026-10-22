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


Part 2: DNS over HTTPS (DoH) Wrapper

Requirements: Part 2 requires two libraries. Run the following command to download both:
```pip install requests dnslib```

How to run: Run the following command in this directory:
```python3 part2.py```

Test with:
```dig @127.0.0.1 -p 1053 google.com A```

Design:
`main`: creates UDP socket on 127.0.0.1:1053 and runs the event loop, starting a task for each query
`handle_client`: handles one query from start to finish (parse, ask Google, build reply, send back to client)
`parse_query`: reads the client's packet with dnslib to get question name and type
`query`: sends the question to Google's JSON DoH API over HTTPS with "requests"
`build_response`: uses dnslib to convert Google's JSON answer into a DNS response packet

- `main()` creates a UDP socket to 127.0.0.1:1053 and loops forever, waiting for queries
- `parse_query` extracts the name and type, while misformed packets are dropped
- `query` runs in the background thread so other clients aren't held up by slow HTTPS requests
    - HTTPS certificates are verified (requests default)
- `build_response` uses `request.reply()` to match the ID, flags, and question to the query
    - Includes A and CNAME answers; unknown names return "does not exist" error
- Every query is logged with its name, type, and response size
- If HTTPS request fails, client gets a server failure response

Testing (with dig):
- queried 10 domains for A records: all returned addresses
- queried www.github.com: got a CNAME to github.com and its A record

Extra Credit Part 3: Persistent DoH Session

How to run: Run the following command in this directory:
```python3 part3.py```

Design:
part3.py uses the same libraries as part2.py:
part3.py is part2.py with two changes:
- `query` sends every request through a shared `requests.Session()` created at the start instead of `requests.get` each time
    - session keeps the HTTPS connection to dns.google open between requests
- latency is measured from when the packet arrives to when the reply is sent

Measurements:
- query 1: example.com 161.6 ms
- query 2: google.com 14.9 ms
- query 3: github.com 51 ms 
- query 4: wikipedia.org 22.3 ms
- query 5: netflix.com 22 ms
- query 6: amazon.com 19.8 ms 
- query 7: reddit.com 18.5 ms 
- query 8: nytimes.com 35.3 ms 
- query 9: apple.com 18.6 ms 
- query 10: microsoft.com 17.5 ms 

Observations/Explanations:
- The first query is an outlier compared to the rest (161.6 ms compared to 14.9-51 ms)
    - the first query opens a new HTTPS connection to dns.google.
    - after the first query the session keeps the connection open, allowing later queries to reuse and skip the setup time