import subprocess
import time
from plot import *
from datetime import datetime

time_str = datetime.now().strftime("%y-%m-%d--%H:%M")
root_dir = './Expr-%s/' % time_str

for n_connections in {1}:
    for minRTO in range(1000, 1300, 100):

        normalized_throughput_data = []
        period_data = []

        for period in [x * 0.1 for x in range(3, 31)]:

            output_name = str(minRTO) + '-' + str(period)
            output_dir = root_dir + '/rto-min-%f-tcp_n-%d/interval-%f/' % (minRTO, n_connections, period)

            p = subprocess.Popen('''python dos.py \
                                --output %s \
                                --period %f \
                                --minRTO %d \
                                --tcpNum %d'''
                                 % (output_dir,
                                    period,
                                    minRTO,
                                    n_connections
                                    ), shell=True)
            p.communicate()
            time.sleep(5)
            normalized_throughput_data.append(read_throughput(output_dir))
            period_data.append(period)
        output_dir = root_dir + '/rto-min-%f-tcp_n-%d/' % (minRTO, n_connections)
        plot_throughput(xdata=period_data, ydata=normalized_throughput_data, output_path=output_dir + 'res_all.png')
