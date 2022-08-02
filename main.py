import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image
from tkinter import ttk
import cv2
import requests

from HardwareWindow import Hardware
from FPIAnalysisWindow import FPIAnalysis

class MainWindow(tk.Frame):
    def __init__(self, root, *args, **kwargs):
        global hardwareImg, classifyImg
        self.root = root
        self.title = tk.Label(root, text="FPI-6", font="Verdana 20")
        self.title.pack()
        
        self.menu = tk.Frame(root)
        self.menu.pack(fill = 'both', expand = True, padx = 50, pady = 100)

        hardwareImg = Image.open("assets/hardware.png").resize((150, 150), Image.ANTIALIAS)
        hardwareImg = ImageTk.PhotoImage(hardwareImg)
        hardware = tk.Button(self.menu, image=hardwareImg, text='Hardware', compound="bottom", command=self.openHardware)
        hardware.pack(side="left", padx = 50)

        classifyImg = Image.open("assets/classify.png").resize((150, 150), Image.ANTIALIAS)
        classifyImg = ImageTk.PhotoImage(classifyImg)
        classify = tk.Button(self.menu, image=classifyImg, text='Classification', compound="bottom", command=self.openClassify)
        classify.pack(side="right", padx = 50)


        def convertVtI(status_label):
            status_label.config(text="RUNNING")
            directory = filedialog.askdirectory()
            filename=directory+"/output.avi"
            vidcap = cv2.VideoCapture(filename)
            def getFrame(sec):
                vidcap.set(cv2.CAP_PROP_POS_MSEC,sec*500)
                hasFrames,image = vidcap.read()
                if hasFrames:
                    cv2.imwrite(directory+"/image"+str(count)+".jpg", image)     # save frame as JPG file
                return hasFrames
            sec = 0
            frameRate = 0.5 #//it will capture image in each 0.5 second
            count=1
            success = getFrame(sec)
            while success:
                count = count + 1
                sec = sec + frameRate
                sec = round(sec, 2)
                success = getFrame(sec)

            status_label.config(text="NOT RUNNING")
            print("Video Converted!!")

        def removebg(status_label):
            status_label.config(text="RUNNING")
            imgFile = filedialog.askopenfilename()
            response = requests.post(
                'https://api.remove.bg/v1.0/removebg',
                files={'image_file': open(imgFile, 'rb')},
                data={'size': 'auto'},
                headers={'X-Api-Key': 'AMU3yeXwoJ7zBtBK3V49erPx'},
            )
            if response.status_code == requests.codes.ok:
                files = [
                    ('Image', '*.png'),
                    ('Image', '*.jpg'),
                    ('Image', '*.jpeg'),
                ]
                resultFilename = filedialog.asksaveasfile(mode="wb", filetypes=files, defaultextension=files)
                resultFilename.write(response.content)
            else:
                print("Error:", response.status_code, response.text)
            
            status_label.config(text="NOT RUNNING")
            print("Removed Successfully!!")


        self.processMenu = tk.Frame(root)
        self.processMenu.pack(side="bottom")
        vidImgLabel = tk.Label(self.processMenu, text="CONVERT VIDEO TO IMAGES", font="Verdana 10")
        vidImgLabel.pack(pady=5)
        vidImgSetting = tk.Frame(self.processMenu)
        vidImgSetting.pack()
        status1 = tk.Label(vidImgSetting, text="NOT RUNNING")
        status1.pack(side="right")
        process = tk.Button(vidImgSetting, text="PROCESS", width=7, command=lambda: convertVtI(status1))
        process.pack(side="left")

        separator = ttk.Separator(self.processMenu, orient='horizontal')
        separator.pack(fill='x', pady=15)

        removeLabel = tk.Label(self.processMenu, text="REMOVE BACKGROUND", font="Verdana 10")
        removeLabel.pack(pady=5)
        removeSetting = tk.Frame(self.processMenu)
        removeSetting.pack()
        status2 = tk.Label(removeSetting, text="NOT RUNNING")
        status2.pack(side="right")
        process = tk.Button(removeSetting, text="PROCESS", width=7, command=lambda: removebg(status2))
        process.pack(side="left")

        separator = ttk.Separator(self.processMenu, orient='horizontal')
        separator.pack(fill='x', pady=15)

    def openClassify(self):
        self.title.pack_forget()
        self.menu.pack_forget()
        self.processMenu.pack_forget()
        directory = filedialog.askdirectory()
        FPIAnalysis(self.root, main_title=self.title, main_menu = self.menu, directory=directory, processMenu=self.processMenu)

    def openHardware(self):
        self.title.pack_forget()
        self.menu.pack_forget()
        self.processMenu.pack_forget()
        directory = filedialog.askdirectory(title='Select folder to save results')
        Hardware(self.root, main_title=self.title, main_menu = self.menu, directory=directory, processMenu=self.processMenu)


if __name__=="__main__":
    root = tk.Tk()
    MainWindow(root)
    #FPIAnalysis(root)
    root.mainloop()