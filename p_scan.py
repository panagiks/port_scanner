#!/usr/bin/python

#@syntax
# network/mask port_range (timeout)
# ex. p_scan.py 192.168.1.0/24 20-1024 (20)

import socket
import sys
from math import floor, ceil
from multiprocessing import Process, Queue

def find_next_host(last_host_ip):
    s = 3
    tmp_host_func = last_host_ip
    while(True):
        if (last_host_ip[s] == 255):
            s -= 1
        else:
            tmp_host_func[s] = tmp_host_func[s] + 1
            return tmp_host_func

def port_check(host,port_start,port_end,timeout,return_queue):
    s = socket.socket()
    s.settimeout(timeout)
    for port in range(port_start,port_end+1):
        try:
            s.connect((host,port))
            s.send(bytes(('.', 'UTF-8')))
            banner = s.recv(1024)
            s.close()
            if banner:
                return_queue.put((host,port))
                #Want a nice print, uncomment 
                #print ('[+] Port '+str(port)+' open at '+host+' '+str(banner))
        except Exception as e:
            pass
            
def main():
    try:
        ip_range = sys.argv[1]
        port_range = sys.argv[2]
    except:
        print ("Syntax Error")
        print ("Correct syntax : ip_range port_range")
        print ("ex. p_scan.py 192.168.1.0/24 20-1024")
        sys.exit()

    try:
        timeout = int(sys.argv[3])
    except:
        timeout = 20
            
    ip_split = ip_range.split('/')
    if (ip_split == ip_range):
        print ("Syntax Error \n")
        print ("Correct syntax : network/mask port_range \n")
        print ("ex. p_scan.py 192.168.1.0/24 20-1024")
        sys.exit()
    
    port_split = port_range.split('-')
    if (port_split == port_range):
        print ("Syntax Error \n")
        print ("Correct syntax : network/mask port_range \n")
        print ("ex. p_scan.py 192.168.1.0/24 20-1024")
        sys.exit()
    port_start = port_split[0]
    port_end = port_split[1]
    try:
        port_start = int(port_start)
        port_end = int(port_end)
        if (port_start > port_end):
            raise
    except:
        print("Port not an integer or wrong port syntax")
        sys.exit()
    
    network = ip_split[0]
    try:
        mask = int(ip_split[1])
        if (mask > 32):
            raise
    except:
        print("Network mask is not an Integer or is greater than 32")
        sys.exit()

    network_dotted = network.split('.')
    if (network_dotted == network or len(network_dotted) != 4 ):
        print("Wrong IP formating")
        sys.exit()

    i = 0
    try:
        for ip_part in network_dotted:
            network_dotted[i] = int(ip_part)
            if (network_dotted[i] > 255):
                raise
            network_dotted[i] = bin(network_dotted[i])
            network_dotted[i] = list(network_dotted[i][2:])
            i += 1
    except:
        print ("Wrond IP formating")

    network_base = []
    for ip_part in network_dotted:
        for k in range(len(ip_part),8):
            ip_part[0:0] = ['0']
    for j in range(0,int(floor(mask/8))):
        network_base.append(network_dotted[j])
    if (mask%8 != 0):
        network_base.append(network_dotted[j+1][:(mask%8)] + ['0'] *(8-(mask%8)))
    for j in range(int(ceil(mask/8)),4):
        network_base.append((['0']*8))
    network_base[3][7] = '1'

    ip_base_parts = []
    for ip_part in network_base:
        ip_part[0:0] = ['0','b']
        ip_base_parts.append(''.join(ip_part))
    for j in range(0,4):
        ip_base_parts[j] = int(ip_base_parts[j],2)
        
    hosts = (2**(32 - mask)) - 2
    hosts_to_scan = []
    
    last_host_ip = ip_base_parts
    host_tmp = []
    for j in range(0,4):
        host_tmp.append(str(ip_base_parts[j]))
    hosts_to_scan.append('.'.join(host_tmp))
    
    for j in range(0,hosts-1):
        host_tmp = []
        last_host = find_next_host(last_host_ip)
        for j in range(0,4):
            host_tmp.append(str(last_host[j]))
        hosts_to_scan.append('.'.join(host_tmp))

    jobs = []
    q = Queue()
    for host_ip in hosts_to_scan:
        proc = Process(target=port_check,args=(host_ip,port_start,port_end,timeout,q))
        jobs.append(proc)
    for j in jobs:
        j.start()
    for j in jobs:
        j.join()
    for i in range(0,q.qsize()):
        pr = q.get()
        #You can do more stuff with pr
        print (pr)

#Start Here!
if __name__ == "__main__":
    main()
