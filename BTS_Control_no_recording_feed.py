import os
import cv2
import time
import threading
import subprocess
import numpy as np
import PySimpleGUI as sg
from time import strftime
import moviepy.editor as mp
from pyfirmata import Arduino, util
from multiprocessing import Process, Barrier

os.chdir('C://BTS/Videos')

with open('c://BTS/file.txt') as f:
    content = f.readlines()
content = [x.strip() for x in content]

def GUI():
        global globPar
        layout = [
            [sg.Text('Recording Parameters', size=(25, 1), font=('Helvetica', 20), text_color='black')],
            [sg.Text('Resolution:', size=(15,1), font=('Helvetica', 10), text_color='black'),
             sg.InputCombo(('640x360', '864x480', '1280x720', '1920x1080'), size=(10, 4), key='res')],
            [sg.Text('_'  * 100, size=(50, 1))],
            [sg.Text('Framerate:', size=(15,1), font=('Helvetica', 10), text_color='black'),
             sg.Slider(range=(1, 30), orientation='h', size=(31, 15), default_value=20, key='fps')],
            [sg.Text('_'  * 100, size=(50, 1))],
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
            [sg.Text('Illumination Intensity:', size=(15,1), font=('Helvetica', 10), text_color='black'),
             sg.InputCombo(('Off', 'Low', 'Medium', 'High', 'Manual Control'), size=(10, 4), key='__illum')],
            [sg.Text('_'  * 100, size=(50, 1))],
            [sg.Text('Notes:')],
            [sg.Multiline('', size=(50,1), key='notes')],
            [sg.Text('_'  * 100, size=(50, 1))],
            [sg.Submit('Record'), sg.Cancel(), sg.Button('Display Live Feed', size=(17,1))]
            ]

        sg.SetOptions(slider_relief='groove')

        window = sg.Window('Behavioral Tracking System', auto_size_text=True, default_element_size=(40, 1)).Layout(layout)

        button, values = window.Read()

        globPar = [values['res'], values['fps'], values['hrs'],
                      values['mins'], values['clipMins'], values['filename'], values['clipFilename'], values['__illum']]

        f = open('c://BTS/file.txt', 'w+') 
        for s in globPar:
                f.write(str(s))
                f.write('\n')
        f.close()

      #### Add save function for notes

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


def record(res, fps, in_File, _time):
        subprocess.call(['ffmpeg', '-f', 'dshow', '-video_size', res,
                         '-framerate', fps, '-vcodec', 'mjpeg', '-i',
                         'video=Logitech HD Pro Webcam C920', '-t', _time, in_File])


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


def saveNotes(test_file):
        n = open(str('c://BTS/'+test_file+'_Notes.txt'), 'w+') 
        n.write(str(content[6]))
        n.write('\n')
        n.close()


def illumOn(pinOn):
        board.digital[pinOn].write(1)


def illumOff(pinOff):
        board.digital[pinOff].write(0)


########################################################################################################################################

GUI()

with open('c://BTS/file.txt') as f:
    content = f.readlines()
    
content = [x.strip() for x in content]

resCheck = ['640x360', '864x480', '1280x720', '1920x1080']
a = str(content[5])
timestamp = str(strftime("%a_%d_%b_%Y_%H_%M"))
inFile = str(a + '_' + timestamp + ".mp4")

tMins = float(content[3])
tMins1 = tMins*60
tHrs = float(content[2])
tHrs1 = tHrs*3600
time1 = tMins1 + tHrs1
totTime = str(time1)

b = str(content[6])
startTime = str(0)
intStartTime = float(startTime)

outLengthMins = float(content[4])
strOutLength = str(outLengthMins*60)
intOutLength = float(strOutLength)

saveNotes(a)


########################################################################################################################################

#\\\\\ Video Settings

res = str(content[0])
fps = str(content[1])


########################################################################################################################################

#\\\\\ Illumination Settings

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
        
        
########################################################################################################################################

#\\\\\ Incorrect Selections Check

if any(x in content[0] for x in resCheck) == 0:
        sg.Popup("Please enter resolution value from dropbox.")
        GUI()
        
if int(content[2]) > 48:
        sg.Popup("Please select a time less than 48:00.")
        GUI()
        
if int(content[3]) > 59:
        sg.Popup("Please select a time less than 48:00.")
        GUI()
        
if int(content[2]) == 0:
        if int(content[3]) == 0:
                sg.Popup("Please enter time greater than 00:00")
                GUI()
        
if ' ' in str(content[5]):
        sg.Popup("Please enter filenames without spaces.")
        GUI()

if os.path.isfile(str('/' + a + '.mp4')) == 1:
        sg.Popup("A file with this name already exists. Please select a different name.")
        GUI()

        
#########################################################################################

record(res, fps, inFile, totTime) 

duration(inFile)
durationMins = float(format(globDur/60, '.3f'))
strMins = str(durationMins)
numClips = float(format(durationMins/outLengthMins, '.3f'))

i = 1
j = intStartTime
stri = str(i)
strj = str(j)

while i <= numClips:
        outFile = str(stri + '_' + b + "_" + timestamp + ".mp4")
        cut(inFile, outFile, strj, strOutLength)
        j += intOutLength
        strj = str(j)
        i += 1
        stri = str(i)

illumOff(illum)

