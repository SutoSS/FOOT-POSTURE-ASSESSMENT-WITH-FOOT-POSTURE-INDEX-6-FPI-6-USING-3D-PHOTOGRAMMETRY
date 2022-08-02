import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter.font import Font
import cv2
import PIL.Image, PIL.ImageTk
import time
import datetime as dt
import argparse
import serial

class Hardware(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        self.root=root
        self.main_menu = kwargs['main_menu']
        self.main_title = kwargs['main_title']
        self.processMenu = kwargs['processMenu']
        self.quitBtn = tk.Button(master=root, text="Back", command=self.quit)
        self.quitBtn.pack(side="top", fill="x")
        self.ok=False


        root.title("Hardware Window")

        self.header = tk.Frame(root)
        self.header.pack(side="top", fill="x")

        #timer
        self.timer=ElapsedTimeClock(self.header)

        # open video source (by default this will try to open the computer webcam)
        self.vid = VideoCapture(save_dir=kwargs['directory'], video_source=1)

        self.left = tk.Frame(root)
        self.left.pack(side="left")

        self.right = tk.Frame(root)
        self.right.pack(side="right",fill = 'both', expand = True, padx = 50)

        video = tk.Frame(self.left)
        video.pack()

        menu = tk.Frame(self.right)
        menu.pack()

        
        arduinoData = serial.Serial(port='COM4', baudrate=9600, timeout=.1)
        def run():
            print("Run")
            arduinoData.write('1'.encode())

        def back():
            print("Back")
            arduinoData.write('0'.encode())
    
        def on():
            print("On")
            arduinoData.write('2'.encode())
        
        def off():
            print("Off")
            arduinoData.write('3'.encode())

        #detailed components in video frame
        self.videoCanvas = tk.Canvas(video, width = self.vid.width, height = self.vid.height)
        self.videoCanvas.pack()
        videoCommand = tk.Frame(video)
        videoCommand.pack(fill="x")
        startStop = tk.Frame(videoCommand)
        startStop.pack(side="left")

        separator = ttk.Separator(self.right, orient='horizontal')
        separator.pack(fill='x', pady=15)

        recordlabel = tk.Label(self.right, text="RECORD", font="Verdana 10")
        recordlabel.pack(pady=5)
        recordsetting = tk.Frame(self.right)
        recordsetting.pack(fill="x")
        stopVideo = tk.Button(recordsetting, text="Stop", width=7, command=self.close_camera)
        stopVideo.pack(side="right")
        startVideo = tk.Button(recordsetting, text="Start", width=7, command=self.open_camera)
        startVideo.pack(side="left")

        separator = ttk.Separator(self.right, orient='horizontal')
        separator.pack(fill='x', pady=15)
        motorLabel = tk.Label(self.right, text="MOTOR", font="Verdana 10")
        motorLabel.pack(pady=5)
        motorSetting = tk.Frame(self.right)
        motorSetting.pack(fill="x")
        runMotor = tk.Button(motorSetting, width=7, text="RUN", command=run)
        runMotor.pack(side="left")
        backMotor = tk.Button(motorSetting, width=7, text="BACK", command=back)
        backMotor.pack(side="right")

        separator = ttk.Separator(self.right, orient='horizontal')
        separator.pack(fill='x', pady=15)

        lampLabel = tk.Label(self.right, text="LAMP", font="Verdana 10")
        lampLabel.pack(pady=5)
        lampSetting = tk.Frame(self.right)
        lampSetting.pack(fill="x")
        onLamp = tk.Button(lampSetting, width=7, text="TURN ON", command=on)
        onLamp.pack(side="left")
        backMotor = tk.Button(lampSetting, width=7, text="TURN OFF", command=off)
        backMotor.pack(side="right")

        separator = ttk.Separator(self.right, orient='horizontal')
        separator.pack(fill='x', pady=15)


        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay=10
        self.update()

    def open_camera(self):
        self.ok = True
        self.timer.start()
        print("camera opened => Recording")

    def close_camera(self):
        self.ok = False
        self.timer.stop()
        print("camera closed => Not Recording")

    def update(self):

        # Get a frame from the video source
        try:
            ret, frame = self.vid.get_frame()
            if self.ok:
                self.vid.out.write(cv2.cvtColor(frame,cv2.COLOR_RGB2BGR))

            if ret:
                self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
                self.videoCanvas.create_image(0, 0, image = self.photo, anchor = tk.NW)
            self.root.after(self.delay,self.update)
        except:
            pass


    def quit(self):
        self.header.pack_forget()
        self.left.pack_forget()
        self.right.pack_forget()
        self.quitBtn.pack_forget()
        self.main_title.pack()
        self.main_menu.pack(fill = 'both', expand = True, padx = 50, pady = 100)
        self.processMenu.pack()
        del self.vid

        return False

class VideoCapture:
    def __init__(self, save_dir, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Command Line Parser
        args=CommandLineParser().args

        
        #create videowriter

        # 1. Video Type
        VIDEO_TYPE = {
            'avi': cv2.VideoWriter_fourcc(*'XVID'),
            #'mp4': cv2.VideoWriter_fourcc(*'H264'),
            'mp4': cv2.VideoWriter_fourcc(*'XVID'),
        }

        self.fourcc=VIDEO_TYPE[args.type[0]]

        # 2. Video Dimension
        STD_DIMENSIONS =  {
            '480p': (640, 480),
            '720p': (1280, 720),
            '1080p': (1920, 1080),
            '4k': (3840, 2160),
        }
        res=STD_DIMENSIONS[args.res[0]]
        self.filename = save_dir+'/'+args.name[0]+'.'+args.type[0]
        self.out = cv2.VideoWriter(self.filename,self.fourcc,10,res)

        #set video sourec width and height
        self.vid.set(3,res[0])
        self.vid.set(4,res[1])

        # Get video source width and height
        self.width,self.height=res


    # To get frames
    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                frame = cv2.flip(frame,1)
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            else:
                return (ret, None)
        else:
            return (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
            self.out.release()
            cv2.destroyAllWindows()

class ElapsedTimeClock:
    def __init__(self,window):
        self.T=tk.Label(window,text='00:00:00',font=('times', 20, 'bold'), bg='green')
        self.T.pack(fill=tk.BOTH, expand=1)
        self.elapsedTime=dt.datetime(1,1,1)
        self.running=0
        self.lastTime=''
        t = time.localtime()
        self.zeroTime = dt.timedelta(hours=t[3], minutes=t[4], seconds=t[5])

 
    def tick(self):
        # get the current local time from the PC
        self.now = dt.datetime(1, 1, 1).now()
        self.elapsedTime = self.now - self.zeroTime
        self.time2 = self.elapsedTime.strftime('%H:%M:%S')
        # if time string has changed, update it
        if self.time2 != self.lastTime:
            self.lastTime = self.time2
            self.T.config(text=self.time2)
        # calls itself every 200 milliseconds
        # to update the time display as needed
        # could use >200 ms, but display gets jerky
        self.updwin=self.T.after(1000, self.tick)

    def start(self):
            if not self.running:
                self.zeroTime=dt.datetime(1, 1, 1).now()-self.elapsedTime
                self.tick()
                self.running=1

    def stop(self):
            if self.running:
                self.T.after_cancel(self.updwin)
                self.elapsedTime=dt.datetime(1, 1, 1).now()-self.zeroTime
                self.time2=self.elapsedTime
                self.running=0



class CommandLineParser:
    
    def __init__(self):

        # Create object of the Argument Parser
        parser=argparse.ArgumentParser(description='Script to record videos')

        # Create a group for requirement 
        # for now no required arguments 
        # required_arguments=parser.add_argument_group('Required command line arguments')

        # Only values is supporting for the tag --type. So nargs will be '1' to get
        parser.add_argument('--type', nargs=1, default=['avi'], type=str, help='Type of the video output: for now we have only AVI & MP4')

        # Only one values are going to accept for the tag --res. So nargs will be '1'
        parser.add_argument('--res', nargs=1, default=['720p'], type=str, help='Resolution of the video output: for now we have 480p, 720p, 1080p & 4k')

        # Only one values are going to accept for the tag --name. So nargs will be '1'
        parser.add_argument('--name', nargs=1, default=['output'], type=str, help='Enter Output video title/name')

        # Parse the arguments and get all the values in the form of namespace.
        # Here args is of namespace and values will be accessed through tag names
        self.args = parser.parse_args()