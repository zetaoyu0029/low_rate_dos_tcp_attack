#!/usr/bin/python

from mininet.cli import CLI
from mininet.topo import Topo
from mininet.node import CPULimitedHost
from mininet.link import TCLink
from mininet.net import Mininet
from mininet.log import lg
from mininet.util import dumpNodeConnections
from subprocess import Popen, PIPE
from time import sleep, time
from argparse import ArgumentParser
from collections import defaultdict 

import sys
import os
import math
import random
import termcolor as T
import subprocess
import threading
import json
import re
import csv

# Global var
hostBw = 15
netBw = 1.5
delay = 6
burst = 0.3
iperf = '/usr/bin/iperf'

# Parse arguments
parser = ArgumentParser(description="Program parameters")
# Number of TCP flows
parser.add_argument('--tcpNum', '-t',
                    dest="tcpNum",
                    type=int,
                    action="store",
                    default=1,
                    required=False)
# Attack length
parser.add_argument('--period',
                    dest="period",
                    type=float,
                    action="store",
                    required=True)
# Min RTO in s
parser.add_argument('--minRTO',
                    dest="minRTO",
                    type=float,
                    action="store",
                    required=True)
# Output directory
parser.add_argument('--output', '-d',
                    dest="output",
                    action="store",
                    default="results",
                    required=True)
# HTTP test
parser.add_argument('--http',
                    dest="http",
                    action='store_true',
                    default=False,
                    required=False)
args = parser.parse_args()

if not os.path.exists(args.output):
  os.makedirs(args.output)
  opt = open("%s/options" % (args.output, ), 'w')
  print >> opt, json.dumps(vars(args), sort_keys=True, indent=4, separators=(',', ': '))
  opt.close()

# Topology to be instantiated in Mininet
class MyTopo(Topo):
  def __init__(self, switch_bw, switch_delay, host_bw, queue_size):
    # Add default members to class.
    super(MyTopo, self).__init__()
    self.switch_bw = switch_bw
    self.host_bw = host_bw
    self.switch_delay = switch_delay
    self.queue_size = queue_size

    alice = self.addHost('alice')
    bob = self.addHost('bob')
    attacker = self.addHost('attacker')
    faker = self.addHost('faker')

    switch_1 = self.addSwitch('s0')
    switch_2 = self.addSwitch('s1')

    self.addLink(switch_1, switch_2, bw=self.switch_bw,
                         delay=self.switch_delay,
                         max_queue_size=math.ceil(self.queue_size / (1440.)))
    self.addLink(alice, switch_1, bw=self.host_bw)
    self.addLink(bob, switch_2, bw=self.host_bw)
    self.addLink(attacker, switch_1, bw=self.host_bw)
    self.addLink(faker, switch_2, bw=self.host_bw)


def get_all_bytes():
  f = open('/proc/net/dev', 'r')
  lines = f.readlines()[2:]
  data = defaultdict(list)
  i = 0
  for line in lines:
    info = line.split(':')
    info_2 = (float(info[1].split()[0]), float(info[1].split()[8]))
    data[info[0]] = info_2
  return data

def get_bytes(received=False):
  try:
    i = 's1-eth2'
    data = get_all_bytes()
    if received:
      return data[i][0]
    else:
      return data[i][1]
  except:
    print("No s1-eth2 record exists.")
    return -1

def run_receiver(host):
  if host.name is 'faker':
    host.popen('%s -u -s -p %s > %s/iperf_server-%s.txt' % (iperf, 5001, args.output, host.name), shell=True)
  else:
    host.popen('%s -s -p %s > %s/iperf_server-%s.txt' % (iperf, 5001, args.output, host.name), shell=True)

def calculate_throughput(interval):
  a = get_bytes()
  sleep(interval)
  b = get_bytes()
  return (8.0 * (b - a) / interval / 1024 / 1024)

def run_udp(net):
  attacker = net.getNodeByName('attacker')
  faker = net.getNodeByName('faker')
  run_receiver(faker)
  return attacker.popen(['python', 'udp_send.py', faker.IP(), '5001', str(burst), str(args.period)])
  
def run_tcp(net, n):


  t = 0.0
  while t < float(netBw):
    receiver = net.getNodeByName('bob')
    run_receiver(receiver)
    for i in range(n):
      sender = net.getNodeByName('alice')
      sender.popen('%s -c %s -p %s -t %f -i 1 -yc -Z %s > /dev/null' %
          (iperf, receiver.IP(), 5001, 3600, 'bic'), shell=True)
    sleep(10)
    t = calculate_throughput(3)
    print("Regular TCP Throughput: %f Mbits\n" % (t, ))
    t = float(t/0.9)
    if t >= float(netBw):
      break
    os.system('killall ' + iperf)

def execution(net, n):
  print("Start attack with period %s, burst %s under %s simultaneous TCP(s)\n" % (args.period, burst, args.tcpNum))
  alice = net.getNodeByName('alice')
  alice.popen("ip route change 10.0.0.0/8 dev %s rto_min %s scope link src %s proto kernel" %
              ('alice-eth0', args.minRTO, alice.IP()), shell=True).communicate()

  run_tcp(net, n)
  attack = run_udp(net)
  throughput = calculate_throughput(30)
  with open('%s/output.txt' % args.output, 'w') as f:
    f.write(str(throughput))
  print("TCP Throughput: %f Mbits\n" % (throughput, ))

  attack.kill()

# def download(net, objs):
#     bob = net.getNodeByName('bob')
#     alice = net.getNodeByName('alice')

#     # Start download
#     processes = []
#     for obj in objs:
#       cmd = "curl -o /dev/null -s -w %%{time_total} %s/http/Random_objects/%sPackages" % (alice.IP(), obj)
#       processes += [bob.popen(cmd, shell=True)]

#     # Waiting for each to stop
#     output = []
#     for p in processes:
#       output += [float(p.communicate()[0])]

#     return (output)

# def measure(net, objs, flag):
#   lengths = []
#   for i in range(10):
#     lengths += [download(net, objs)]
#     sleep(3)
#   res = []
#   if flag is True:
#     res = [avg(x) for x in zip(*lengths)]
#   else:
#     res = [x for x in zip(*lengths)]
#   return res

# # calculate basic communication
# def test_http(net):
#     # Obtain Test data
#     sizes = range (100, 1000, 5)
#     test_set = []
#     for i in xrange(30):
#       test_set += [random.choice(sizes)]

#     # Get base and attacked throughput to calculate normalization
#     print("Calculate baseline\n")
#     baseline = measure(net, test_set, True)
#     print("Attack HTTP flow\n")
#     attacker = net.getNodeByName('attacker')
#     faker = net.getNodeByName('faker')
#     p = attacker.popen(['python', 'udp_send.py', faker.IP(), '5001', str(args.burst), str(period)])
#     attack = measure(net, test_set, False)
#     p.kill()

def main():

  # start run and attack
  start = time()

  topo = MyTopo(switch_bw=netBw, host_bw=hostBw, switch_delay='%sms' %(delay, ), queue_size=23593)
  net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink)
  net.start()
  dumpNodeConnections(net.hosts)
  net.pingAll()

  # if args.http:
  #   test_http(net)  # for test only
  # else:
  execution(net, args.tcpNum)

  os.system('killall ' + iperf)
  net.stop()
  Popen("killall -9 top bwm-ng tcpdump cat mnexec; mn -c", shell=True, stderr=PIPE)
  # Popen("pgrep -f webserver.py | xargs kill -9", shell=True).wait()
  end = time()
  print("Experiment took %s seconds\n" % (end - start))

if __name__ == '__main__':
  lg.setLogLevel('warning')
  main()

