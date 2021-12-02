#python pyvisa commands for controlling Multicomp Pro MP71025X series power supplies
#MP710256 - 30V 30A 300W
#MP710257 - 60V 15A 300W

import pyvisa
import time
import easygui as eg
import serial

# Power Supply
class MP71025X:
	# Initialize the MP71025X Power Supply (X is 6 or 7)
	
	baud_rate = 115200
	read_termination = '\n'
	query_delay = 0.05
	
	def __init__(self, resource_id = None):
		
		rm = pyvisa.ResourceManager('@py')
		
		if(resource_id == None):
			resources = rm.list_resources()

			################# IDN VERSION #################
			#Attempt to connect to each Visa Resource and get the IDN response
			title = "Power Supply Selection"
			if(len(resources) == 0):
				resource_id = 0
				print("No PyVisa Resources Available. Connection attempt will exit with errors")
			idns_dict = {}
			for resource in resources:
				try:
					instrument = rm.open_resource(resource)
					instrument.baud_rate = MP71025X.baud_rate
					instrument.read_termination = MP71025X.read_termination
					instrument.query_delay = MP71025X.query_delay
					instrument_idn = instrument.query("*IDN?")
					idns_dict[resource] = instrument_idn
					instrument.close()
				except (pyvisa.errors.VisaIOError, PermissionError, serial.serialutil.SerialException):
					pass
					
			#Now we have all the available resources that we can connect to, with their IDNs.
			resource_id = 0
			if(len(idns_dict.values()) == 0):
				print("No Equipment Available. Connection attempt will exit with errors")
			elif(len(idns_dict.values()) == 1):
				msg = "There is only 1 Visa Equipment available.\nWould you like to use it?\n{}".format(list(idns_dict.values())[0])
				if(eg.ynbox(msg, title)):
					idn = list(idns_dict.values())[0]
			else:
				msg = "Select the Power Supply Model:"
				idn = eg.choicebox(msg, title, idns_dict.values())
			#Now we know which IDN we want to connect to
			#swap keys and values and then connect
			resources_dict = dict((v,k) for k,v in idns_dict.items())
			resource_id = resources_dict[idn]
					
			
			
		self.inst = rm.open_resource(resource_id)
		
		self.inst.baud_rate = MP71025X.baud_rate
		self.inst.read_termination = MP71025X.read_termination
		self.inst.query_delay = MP71025X.query_delay
        
		self.inst_idn = self.inst.query("*IDN?")
		print("Connected to {}\n".format(self.inst_idn))
		
		split_string = self.inst_idn.split(" ")
		self.model_number = split_string[0]
		self.version_number = split_string[1]
		self.serial_number = split_string[2]
		
		#this unit does not have a reset command
		#self.inst.write("*RST")
		time.sleep(0.01)
		
		self.lock_commands(False)
		time.sleep(0.01)
		self.toggle_output(0)
		time.sleep(0.01)
		self.set_current(0)
		time.sleep(0.01)
		self.set_voltage(0)
		time.sleep(0.01)
		
	# To set power supply limit in Amps 
	def set_current(self, current_setpoint_A):		
		self.inst.write("ISET:{}".format(current_setpoint_A))

	def set_voltage(self, voltage_setpoint_V):
		self.inst.write("VSET:{}".format(voltage_setpoint_V))

	def toggle_output(self, state, ch = 1):
		if state:
			self.inst.write("OUT:1")
		else:
			self.inst.write("OUT:0")
	
	def remote_sense(self, state):
		if state:
			self.inst.write("COMP:1")
		else:
			self.inst.write("COMP:0")
	
	def lock_commands(self, state):
		if state:
			self.inst.write("LOCK:1")
		else:
			self.inst.write("LOCK:0")
	
	def measure_voltage(self):
		return float(self.inst.query("VOUT?"))

	def measure_current(self):
		return float(self.inst.query("IOUT?"))
		
	def measure_power(self):
		current = self.measure_current()
		voltage = self.measure_voltage()
		return float(current*voltage)
		
	def __del__(self):
		self.toggle_output(False)
		self.lock_commands(False)
		try:
			self.inst.close()
		except AttributeError:
			pass
