from abstract_instrument import abstract_instrument
import socket

#==============================================================================

ALL_VAL_TYPE = ['FREQ']  #, 'PERIOD']
ALL_CHANNELS = ['1'] #, '2']

ADRESS = "192.168.0.52"
CONF_VAL_TYPE = ['CONF:FREQ'] #, 'CONF:PERIOD']

#==============================================================================

class HP53132A(abstract_instrument):
    def __init__(self, channels, vtypes, adress):
        self.adress = adress
        self.port = 1234
        self.gpib_addr = 12
        self.channels = channels
        self.vtypes = vtypes

    def model(self):
        #self.send("*IDN?")
        #return self.read()
        return "HP53132A"

    def connect(self):
        print('Connecting to device @%s:%s...' %(self.adress, self.port))
        self.sock = socket.socket(socket.AF_INET,
                             socket.SOCK_STREAM,
                             socket.IPPROTO_TCP)
        self.sock.settimeout(10.0)    # Don't hang around forever
        self.sock.connect((self.adress, self.port))
        self.init_prologix()
        print('  --> Ok')
        print(self.model())
        self.configure()

    def configure(self):
        self.strCh = ''
        for ch in self.channels:
            self.send('%s (@%s)'%(CONF_VAL_TYPE[ALL_VAL_TYPE.index(self.vtypes[self.channels.index(ch)])], ch))
            self.strCh = self.strCh + '(@%s),'%ch
        self.strCh = self.strCh[0:-1]
        self.send('FORMAT ASCII')

        #self.send('ROUT:SCAN (@%s)'%self.strCh)
        #self.send('TRIG:COUN 1')
        self.send('*RST')
        self.send(":FUNC 'FREQ 1'")
        self.send(":ROSC:SOUR INT")
        self.send(":INIT:CONT ON")

    def getValue(self):
        self.send('FETC?')
        return self.read()

    def read(self):
        self.send("++read eoi")
        ans = ''
        nb_data_list = []
        nb_data = ''
        try:
            while ans != '\n':
                ans = self.sock.recv(1)
                nb_data_list.append(ans) # Return the number of data
            list_size = len(nb_data_list)
            for j in range (0, list_size):
                nb_data = nb_data+nb_data_list[j]
            return nb_data
        except socket.timeout:
            print "Socket timeout error when reading."
            raise

    def disconnect(self):
        self.send('*RST')
        self.sock.close()

    def send(self, command):
        self.sock.send("%s\n"%command)

    def init_prologix(self):
        try:
            self.sock.send("++mode 1\n") # Set mode as CONTROLLER
            self.sock.send('++addr ' + str(self.gpib_addr) + '\n') # Set the GPIB address
            self.sock.send('++eos 3\n') # Set end-of-send character to nothing
            self.sock.send("++eoi 1\n") # Assert EOI with last byte to indicate end
            self.sock.send("++read_tmo_ms 2750\n") # Set read timeout
            self.sock.send("++auto 0\n") # Turn off read-after-write to avoid
                                # "Query Unterminated" errors

        except self.socket.timeout:
            print "Socket timeout"
            raise
        except self.socket.error as er:
            print "Socket error: " + str(er)
            raise
        except Exception as er:
            print "Unexpected error: " + str(er)
            raise