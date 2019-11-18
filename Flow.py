from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel

class ExperimentTopo(Topo):
    "Single switch connected to n hosts."
    def build(self):
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')

        sender   = self.addHost('sender')
        attacker = self.addHost('attacker')
        receiver = self.addHost('receiver')

        self.addLink(sender  , s1, bw=100, delay='1ms',  max_queue_size=10)
        self.addLink(attacker, s1, bw=100, delay='1ms',  max_queue_size=10)
        self.addLink(receiver, s2, bw=100, delay='1ms',  max_queue_size=10)
        self.addLink(s1      , s2, bw=1.5, delay='20ms', max_queue_size=1000)
        

def simpleTest():
    "Create and test a simple network"
    topo = ExperimentTopo()
    net = Mininet(topo)
    net.start()
    print "Dumping host connections"
    dumpNodeConnections(net.hosts)
    print "Testing network connectivity"
    net.pingAll()
    net.stop()

if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    simpleTest()
