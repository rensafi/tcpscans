#!/usr/bin/env python
#
# Copyright 2013 by Philipp Winter <phw@nymity.ch>
#
# Reads the given .pcap file and determines the subsequent SYN/ACK
# retransmissions after a SYN segment was sent to a service.

from scapy.all import *
from scapy.utils import rdpcap

import sys

pkts=rdpcap(sys.argv[1])

SYN=2
SYNACK=18

class Connection( object ):

    def __init__( self, syn):
        self.syn = syn
        self.synAcks = []

    def addSynAck( self, synack ):
        self.synAcks.append(synack)

    def getISN( self ):
        return self.syn[TCP].seq

# Maps ISNs to network packets.
connections = {}

for pkt in pkts:

    flags = pkt[TCP].flags

    # Add a new SYN segment to our hash table.
    if flags == SYN:
        #connections.append(Connection(pkt))
        connections[pkt[TCP].seq] = Connection(pkt)
        continue

    # Add a SYN/ACK response to the respective SYN segment.
    elif flags == SYNACK:
        if connections.has_key(pkt[TCP].ack - 1):
            conn = connections[pkt[TCP].ack - 1]
            conn.addSynAck(pkt)

# Now sort the dictionary based on the timestamps.
final = sorted(connections.items(), key=lambda x: x[1].syn.time)
i=1
syns = synacks = 0
for (_, conn) in final:
    print "[%.4f] SYN segment #%d received %d SYN/ACKs." % \
          (conn.syn.time, i, len(conn.synAcks))
    synacks += len(conn.synAcks)
    syns += 1
    i += 1

# Finally, print the overall statistics.
print "Sent %d SYNs and received %d SYN/ACKs." % (syns, synacks)
print "On average, we received %.3f SYN/ACKs for every SYN." % \
      (0 if syns == 0 else float(synacks) / syns)
