import os
import cv2
import time
import threading
import subprocess
import numpy as np
import PySimpleGUI as sg
import moviepy.editor as mp

from time import strftime
from pyfirmata import Arduino, util
from multiprocessing import Process, Barrier

os.chdir('C://BTS/Videos')

with open('c://BTS/file.txt', 'w+') as f:
    content = f.readlines()
content = [x.strip() for x in content]

def GUI():
        global globPar
        global globFPS
        layout = [
            [sg.Text('Recording Parameters', size=(25, 1), font=('Helvetica', 20), text_color='black')],
            [sg.Text('Recording Time:', size=(15,1), font=('Helvetica', 10), text_color='black')],
            [sg.Spin([i for i in range(0,49)], size = (2,1), initial_value=0, key='hrs'), sg.Text('Hours'), sg.Text(':'),
             sg.Spin([i for i in range(0,60)], size = (2,1), initial_value=0, key='mins'), sg.Text('Minutes')],
            [sg.Text('_'  * 100, size=(50, 1))],
            [sg.Text('Video File Name')],
            [sg.InputText('', key='filename')],
            [sg.Text('_'  * 100, size=(50, 1))],
            [sg.Text('(OPTIONAL) Please select the length of each edited video clip:', size=(75,1),font=('Helvetica', 10), text_color='black')],
            [sg.Text('Clip Length', size=(50,1),font=('Helvetica', 10), text_color='black')],
            [sg.Spin([i for i in range(0,60)], size = (2,1), initial_value=0, key='clipMins'), sg.Text('Minutes')],
            [sg.Text('Video Clip File Name')],
            [sg.InputText('', key='clipFilename')],
            [sg.Text('_'  * 100, size=(50, 1))],
            [sg.Text('Illumination Intensity:', size=(15,1), font=('Helvetica', 10), text_color='black')],
            [sg.InputCombo(('Off', 'Low', 'Medium', 'High', 'Manual Control'), size=(10, 4), key='__illum')],
            [sg.Text('_'  * 100, size=(50, 1))],
            [sg.Text('Notes:')],
            [sg.Multiline('', size=(50,1), key='notes')],
            [sg.Text('_'  * 100, size=(50, 1))],
            [sg.Submit('Record'), sg.Cancel(), sg.Button('Display Live Feed', size=(17,1))]
            ]

        sg.SetOptions(slider_relief='groove')

        window = sg.Window('Behavioral Tracking System', auto_size_text=True).Layout(layout)
        
        button, values = window.Read()

        globPar = [values['hrs'],
                      values['mins'], values['clipMins'], values['filename'], values['clipFilename'], values['__illum'], values['notes']]
        

        f = open('c://BTS/file.txt', 'w+') 
        for s in globPar:
                f.write(str(s))
                f.write('\n')
        f.close()

        if button == 'Display Live Feed':
                        feed()
                        GUI()
        
        
def cut(in_File, out_File, start_Time, out_Length):
	subprocess.call(['ffmpeg', '-ss', start_Time, '-i', in_File, '-c',
                         'copy', '-t', out_Length, out_File])


def duration(length):
        global globDur
        dur =  mp.VideoFileClip(length).duration
        globDur = float(format(dur, '.3f'))
        

def feed():

        if content[7] == 'Off':
                board = Arduino("COM4")
                illum = 5
                illumOn(illum)
        
        if content[7] == 'Low':
                board = Arduino("COM4")
                illum = 9
                illumOn(illum)
        
        if content[7] == 'Medium':
                board = Arduino("COM4")
                illum = 10
                illumOn(illum)
        
        if content[7] == 'High':
                board = Arduino("COM4")
                illum = 11
                illumOn(illum)
        
        if content[7] == 'Manual Control':
                board = Arduino("COM4")
                illum = 3
                illumOn(illum)
                
        cap = cv2.VideoCapture(1)
        #cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        #cap.set(cv2.CAP_PROP_FPS, 5)

        if (cap.isOpened()== False): 
          print("Error opening video stream or file")
 
        while(cap.isOpened()):
          ret, frame = cap.read()
    
          if ret == True:
            cv2.imshow('Live Video Feed (Press "q" to return to Recording Parameters)', frame)
            if cv2.waitKey(25) & 0xFF == ord('q'):
                  break
                
          else: 
            break
 
        cap.release()
        cv2.destroyAllWindows()


class VideoRecorder():
	
	# Video class based on openCV 
	def __init__(self):

		
		self.open = True
		self.device_index = 1
		self.fps = 24             # fps should be the minimum constant rate at which the camera can
		self.fourcc = "MJPG"       # capture images (with no decrease in speed over time; testing is required)
		self.frameSize = (640, 480) # video formats and sizes also depend and vary according to the camera used
		self.video_filename = inFile
		self.video_cap = cv2.VideoCapture(self.device_index)
		self.video_writer = cv2.VideoWriter_fourcc(*self.fourcc)
		self.video_out = cv2.VideoWriter(self.video_filename, self.video_writer, self.fps, self.frameSize)
		self.frame_counts = 1
		self.start_time = time.time()

	
	def record(self):
		
#		counter = 1
		timer_start = time.time()
		timer_current = 0
		
		
		while(self.open==True):
			ret, video_frame = self.video_cap.read()
			if (ret==True):
				
					self.video_out.write(video_frame)
#					print str(counter) + " " + str(self.frame_counts) + " frames written " + str(timer_current)
					self.frame_counts += 1
#					counter += 1
#					timer_current = time.time() - timer_start
					time.sleep(0.02)
					
					# Uncomment the following three lines to make the video to be
					# displayed to screen while recording
					
					color = cv2.cvtColor(video_frame, cv2.IMREAD_COLOR)
					cv2.imshow('video_frame', color)
					cv2.waitKey(1)
			else:
				break
							
				# 0.16 delay -> 6 fps
				# 
				

	# Finishes the video recording therefore the thread too
	def stop(self):
		
		if self.open==True:
			
			self.open=False
			self.video_out.release()
			self.video_cap.release()
			cv2.destroyAllWindows()
			
		else: 
			pass

	# Launches the video recording function using a thread			
	def start(self):
		video_thread = threading.Thread(target=self.record)
		video_thread.start()


def start_AVrecording(filename):
				
	global video_thread

	video_thread = VideoRecorder()
	video_thread.start()

	return filename


def start_video_recording(filename):
				
	global video_thread
	
	video_thread = VideoRecorder()
	video_thread.start()

	return filename

	
def stop_AVrecording(filename):
	

	frame_counts = video_thread.frame_counts
	elapsed_time = time.time() - video_thread.start_time
	recorded_fps = frame_counts / elapsed_time
	print("total frames " + str(frame_counts))
	print("elapsed time " + str(elapsed_time))
	print("recorded fps " + str(recorded_fps))
	video_thread.stop()


def saveNotes(test_file):
        n = open(str('c://BTS/'+test_file+'_Notes.txt'), 'w+') 
        n.write(str(content[6]))
        n.write('\n')
        n.close()


def illumOn(pinOn):
        board.digital[pinOn].write(1)


def illumOff(pinOff):
        board.digital[pinOff].write(0)
 
          
#########################################################################################
        
GUI()

with open('c://BTS/file.txt') as f:
    content = f.readlines()
    
content = [x.strip() for x in content]

resCheck = ['640x360', '864x480', '1280x720', '1920x1080']
a = str(content[3])
timestamp = str(strftime("%a_%d_%b_%Y_%H_%M"))
inFile = str(a + '_' + timestamp + ".avi")

tMins = float(content[1])
tMins1 = tMins*60
tHrs = float(content[0])
tHrs1 = tHrs*3600
time1 = tMins1 + tHrs1
totTime = str(time1)
floatTotTime = float(totTime)

b = str(content[4])
startTime = str(0)
intStartTime = float(startTime)

outLengthMins = float(content[2])
strOutLength = str(outLengthMins*60)
intOutLength = float(strOutLength)

saveNotes(a)


#########################################################################################

#\\\\\ Illumination Settings

if content[5] == 'Off':
        board = Arduino("COM4")
        illum = 5
        illumOn(illum)
        
if content[5] == 'Low':
        board = Arduino("COM4")
        illum = 9
        illumOn(illum)
        
if content[5] == 'Medium':
        board = Arduino("COM4")
        illum = 10
        illumOn(illum)
        
if content[5] == 'High':
        board = Arduino("COM4")
        illum = 11
        illumOn(illum)
        
if content[5] == 'Manual Control':
        board = Arduino("COM4")
        illum = 3
        illumOn(illum)


#########################################################################################

#\\\\\ Incorrect Selections Check
        
if int(content[0]) > 48:
        sg.Popup("Please select a time less than 48:00.")
        GUI()
        
if int(content[1]) > 59:
        sg.Popup("Please select a time less than 48:00.")
        GUI()
        
if int(content[0]) == 0:
        if int(content[1]) == 0:
                sg.Popup("Please enter time greater than 00:00")
                GUI()
        
if ' ' in str(content[3]):
        sg.Popup("Please enter filenames without spaces.")
        GUI()

if os.path.isfile(str('/' + a + '.avi')) == 1:
        sg.Popup("A file with this name already exists. Please select a different name.")
        GUI()

        
#########################################################################################

if __name__== "__main__":
	
	filename = "Default_user"	
	
	start_AVrecording(inFile)  
	
	time.sleep(floatTotTime)
	
	stop_AVrecording(inFile)
	print("Done") #===========#
    
duration(inFile)
durationMins = float(format(globDur/60, '.3f'))
strMins = str(durationMins)
numClips = float(format(durationMins/outLengthMins, '.3f'))

i = 1
j = intStartTime
stri = str(i)
strj = str(j)

while i <= numClips:
        outFile = str(stri + '_' + b + "_" + timestamp + ".avi")
        cut(inFile, outFile, strj, strOutLength)
        j += intOutLength
        strj = str(j)
        i += 1
        stri = str(i)

illumOff(illum)
