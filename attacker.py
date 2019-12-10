#!/usr/bin/env python

import sys
import socket
from time import time, sleep

FAKER_IP = sys.argv[1]
FAKER_PORT = int(sys.argv[2])
BURST = float(sys.argv[3])
INTERVAL = float(sys.argv[4])
RATE = 15 * 1024 * 1024.
INITIAL_SLEEP_TIME = 0.9
MESSAGE = '0' * 1440 * 8

faker_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sleep(INITIAL_SLEEP_TIME)

bits = len(MESSAGE)
pass_time = time()
avg_rate = bits / pass_time
start_time = time()
next_start_time = time()

while True:

  bits = 0
  start_time = time()

  while time() - start_time < BURST:
    faker_socket.sendto(MESSAGE, (FAKER_IP, FAKER_PORT))
    bits = bits + len(MESSAGE)
    pass_time = time() - start_time
    avg_rate = bits / pass_time
    if avg_rate > RATE:
      sleep(bits / RATE - pass_time)

  next_start_time = next_start_time + INTERVAL
  if next_start_time > time():
    sleep(next_start_time - time())
