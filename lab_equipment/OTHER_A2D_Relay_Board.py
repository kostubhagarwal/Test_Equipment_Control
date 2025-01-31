#python library for controlling the A2D DAQ

import pyvisa
from .PyVisaDeviceTemplate import PyVisaDevice

#Data Acquisition Unit
class A2D_Relay_Board(PyVisaDevice):
    connection_settings = {
        'read_termination':         '\r\n',
        'write_termination':        '\n',
        'baud_rate':                57600,
        'query_delay':              0.02,
        'chunk_size':               102400,
        'pyvisa_backend':           '@py',
        'time_wait_after_open':     2,
        'idn_available':            True
    }
    
    def initialize(self):
        self.equipment_type_connected = None
        self.i2c_expander_addr = None
        self._eload_connected = False
        self._psu_connected = False
        self._num_channels = self._get_num_channels()
        
    def __del__(self):
        try:
            self.inst.close()
        except AttributeError:
            pass
    
    def connect_psu(self, state):
        value = 0
        if state:
            value = 1
        
        if self.equipment_type_connected[0] == 'psu':
            psu_channel = 0
        elif self.equipment_type_connected[1] == 'psu':
            psu_channel = 1
        
        self.inst.write('INSTR:DAQ:SET:OUTP (@{ch}),{val}'.format(ch = psu_channel, val = value))
        
        self._psu_connected = state
    
    def psu_connected(self):
        return self._psu_connected
        
    def connect_eload(self, state):
        value = 0
        if state:
            value = 1
        
        if self.equipment_type_connected[0] == 'eload':
            eload_channel = 0
        elif self.equipment_type_connected[1] == 'eload':
            eload_channel = 1
        
        self.inst.write('INSTR:DAQ:SET:OUTP (@{ch}),{val}'.format(ch = eload_channel, val = value))
    
        self._eload_connected = state
    
    def eload_connected(self):
        return self._eload_connected
    
    def reset(self):
        self.inst.write('*RST')

    def set_led(self, value = 0):
        if(value > 1):
            value = 1
        #x is a character that we parse but do nothing with (channel must be first)
        self.inst.write('INSTR:DAQ:SET:LED x {val}'.format(val = value))
        
    def _get_num_channels(self):
        return int(self.inst.query('INSTR:DAQ:GET:NCHS?'))
        
    def get_num_channels(self):
        return self._num_channels
        
    def set_i2c_expander_addr(self, addr):
        self.i2c_expander_addr = addr
        self.inst.write('INSTR:DAQ:SET:ADDR x {address}'.format(address = self.i2c_expander_addr))
    
if __name__ == "__main__":
    #connect to the daq
    relay_board = A2D_Relay_Board()
