from time import sleep
import time
from threading import Thread
import threading
from dynio import *
import numpy
import logging

action = "slither"
quit = False
past_pos = [2500, 2500, 2000, 2500, 2000, 1000]
additional_offset = [0, 0, 0, 0, 0, 0]
    
def Wait_Char():
	global action, quit
	past_action = action
	while(not quit):
		past_action = action
		action = input("Enter action")
		if (not(action == "slither" or action == "climb" or action == "lift" or action == "neutral" or action == "left" or action == "right" or action == "quit")):
			action = past_action
    
def slither(time, offset, mod_num, id, direction):
	global past_pos, additional_offset
	lat_angle_offset = 0
	lat_amplitude = 1
	lat_spatial_frequency = 12
	lat_frequency = 1 / 2

	dor_angle_offset = 0
	dor_amplitude = 1
	dor_spatial_frequency = 12
	dor_frequency = 1 / 2

	target_angle = 0
	if (id % 2 == 0):
		temp = dor_spatial_frequency * time / 20 + dor_frequency * mod_num
		target_angle = dor_angle_offset + dor_amplitude * numpy.sin(temp + numpy.pi / 2)
	else:
		temp = lat_spatial_frequency * time / 20 + lat_frequency * mod_num
		target_angle = lat_angle_offset + lat_amplitude * numpy.sin(temp)
	target_angle = target_angle * 180 / numpy.pi
	if (direction == "right"):
		target_angle *= -1
	pos = ((target_angle * 4096 / 360 + offset)) % 4096
	if (pos < 0):
		pos += 4096
	past_pos[id - 1] = pos
	return pos

def climb(time, offset, mod_num, id):
	global past_pos
	lat_amplitude = 1
	lat_frequency = 1 / 2

	dor_amplitude = 1
	dor_frequency = 1 / 2

	target_angle = 0
	if (id % 2 == 0):
		temp = (time) % (2 * numpy.pi) + dor_frequency * mod_num
		target_angle = dor_amplitude * numpy.sin(temp + numpy.pi / 2)
	else:
		temp = (time) % (2 * numpy.pi) + lat_frequency * mod_num
		target_angle = lat_amplitude * numpy.sin(temp)
	target_angle = target_angle * 180 / numpy.pi
	pos = ((target_angle * 4096 / 360 + offset)) % 4096
	if (pos < 0):
		pos += 4096
	past_pos[id - 1] = pos
	return pos

def move_gradual(target_pos, id):
	global past_pos
	current_pos = past_pos[id - 1]
	if (target_pos - current_pos < -50):
		past_pos[id - 1] -= 50
		return current_pos - 50
	elif (target_pos - current_pos > 50):
		past_pos[id - 1] += 50
		return current_pos + 50
	else:
		past_pos[id - 1] = target_pos
		return target_pos

def h():
	global action, quit, additional_offset
	
	file = open("/home/exagora/log/c.txt", "a")
	file.write("Time,Motor5Pos,Motor5Temp\n")

	dxl_io = dxl.DynamixelIO('/dev/ttyUSB0', 115200)

	log = ""
	t0 = time.time()

	while(not quit):
		
		t = time.time()
		time_past = t - t0

		if(action == "slither"):
			dxl_io.write_control_table(1, 1, round(slither(time_past, 2500, 1, 1, "left")), 42, 2)
			dxl_io.write_control_table(1, 2, round(slither(time_past, 2500, 1, 2, "left")), 42, 2)
			dxl_io.write_control_table(1, 3, round(slither(time_past, 2000, 2, 3, "left")), 42, 2)
			dxl_io.write_control_table(1, 4, round(slither(time_past, 2500, 2, 4, "left")), 42, 2)
			dxl_io.write_control_table(1, 5, round(slither(time_past, 2000, 3, 5, "left")), 42, 2)
			dxl_io.write_control_table(1, 6, round(slither(time_past, 1000, 3, 6, "left")), 42, 2)

		elif(action == "climb"):
			dxl_io.write_control_table(1, 1, round(climb(time_past, 2500, 1, 1)), 42, 2)
			dxl_io.write_control_table(1, 2, round(climb(time_past, 2500, 1, 2)), 42, 2)
			dxl_io.write_control_table(1, 3, round(climb(time_past, 2000, 2, 3)), 42, 2)
			dxl_io.write_control_table(1, 4, round(climb(time_past, 2500, 2, 4)), 42, 2)
			dxl_io.write_control_table(1, 5, round(climb(time_past, 2000, 3, 5)), 42, 2)
			dxl_io.write_control_table(1, 6, round(climb(time_past, 1000, 3, 6)), 42, 2)
			
		elif(action == "lift"):
			dxl_io.write_control_table(1, 2, round(move_gradual(1988, 2)), 42, 2)
			
		elif(action == "neutral"):
			dxl_io.write_control_table(1, 1, round(move_gradual(2500, 1)), 42, 2)
			dxl_io.write_control_table(1, 2, round(move_gradual(2500, 2)), 42, 2)
			dxl_io.write_control_table(1, 3, round(move_gradual(2000, 3)), 42, 2)
			dxl_io.write_control_table(1, 4, round(move_gradual(2500, 4)), 42, 2)
			dxl_io.write_control_table(1, 5, round(move_gradual(2000, 5)), 42, 2)
			dxl_io.write_control_table(1, 6, round(move_gradual(1000, 6)), 42, 2)

		elif(action == "left"):
			if(past_pos[2] < 2512):
				dxl_io.write_control_table(1, 3, round(move_gradual(past_pos[2] + 512, 3)), 42, 2)
				additional_offset[2] += 512

		elif(action == "right"):
			dxl_io.write_control_table(1, 1, round(slither(time_past, 2500, 1, 1, "right")), 42, 2)
			dxl_io.write_control_table(1, 2, round(slither(time_past, 2500, 1, 2, "right")), 42, 2)
			dxl_io.write_control_table(1, 3, round(slither(time_past, 2000, 2, 3, "right")), 42, 2)
			dxl_io.write_control_table(1, 4, round(slither(time_past, 2500, 2, 4, "right")), 42, 2)
			dxl_io.write_control_table(1, 5, round(slither(time_past, 2000, 3, 5, "right")), 42, 2)
			dxl_io.write_control_table(1, 6, round(slither(time_past, 1000, 3, 6, "right")), 42, 2)

		elif(action == "quit"):
			print("done!")
			quit = True
	
		currentPos5 = dxl_io.read_control_table(1, 5, 56, 2)
		currentTemp5 = dxl_io.read_control_table(1, 5, 63, 1)
		log += str(currentPos5) + "," + str(currentTemp5) + "\n"

	file.write(log)
	file.close()
	print("ended")
    
    
thread1 = Thread(target=Wait_Char)
thread2 = Thread(target=h)
thread1.start()
thread2.start()
print("threads finished...exiting")
