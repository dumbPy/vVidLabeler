import skvideo.io
import numpy as np
import json
import os
from pathlib import Path
import matplotlib.pyplot as plt
import cv2


class iVideo(object):
    def __init__(self, videoArray, videoName, labelPath, frameLabel=[], classLabel="", labelMap=None):
        self.vid=videoArray
        if isinstance(self.vid, str): self.vid=skvideo.io.vread(self.vid) #Handeling Paths Directly to save memory
        self.len=len(self.vid)      #Number of Video Frames
        self.index=450                #Current Index. Starts at 0
        self.rollover=False         #tracks frame video rollover
        self.frameLabel=frameLabel  #Label for each frame
        self.classLabel=classLabel  #Label for whole Video
        self.forward=True           #Used to show Forward and Reverse sequence
        self.labelMap=labelMap      #Used to map the label chars to passed text before saving to json
        self.videoName=videoName    #Used for saving Labels
        self.labelPath=labelPath
    
    
    def get(self, i):   return self.vid[i]
    def reset(self):    self.rollover=False; self.index=0
    def nextFrame(self):
        print(f"Index: {self.index}")
        if self.forward and self.index<self.len:    #Forward playback and index not at last frame
            self.index+=1
            self.rollover=False                     #Flag to represent that we can save the returned frameLabel
            print(f"Loop1: {type(self.vid[self.index-1])}")
            return self.vid[self.index-1]
        elif self.index>0 and self.forward==False:  #reverse Video Playback and index ahead of 0
            self.index-=1
            self.rollover=False
            print(f"Loop2: {type(self.vid[self.index+1])}")
            # return self.vid[self.index+1]
        else:
            self.rollover=True                      #If key is still pressed, ignore the returned frameLabels by checking this flag
            print(f"Loop3: {type(self.vid[self.index-1])}")
            return self.vid[self.index-1]             #video stuck in last frame and no more frameLabels are saved
    
    @classmethod        
    def load(cls, path, labelFolderPath): #load video using class method:  object=iVideo.load(path)
            #vid =skvideo.io.vread(path)  #This returns 500 frames and leads to segmentation fault in my code. known issue with skvideo I read
            # vid=np.asarray([frame for frame in skvideo.io.vreader(path)]) #vreader returns Generator that gives me 497-498 frames as opposed to faulty vread above
            vid=loadVideoWithCV2(path)  #This uses cv2 to load video into np array as opposed to skvideo.io above.
            vidName=extract_file_name(path)
            labelPath=os.path.join(labelFolderPath, vidName+".json")
            if os.path.isfile(labelPath):
                with open(labelPath) as f:
                    label=json.load(f)["frameLabels"]
                return cls(vid, vidName, labelPath, label)
            else: return cls(vid, vidName, labelPath)

    def setFrameLabel(self, label, i=None): #Can be used for labeling a frame at index i
        try:    
            if i==None: i=self.index-1    
            if len(self.frameLabel)<i+1:
                self.frameLabel+=['None']*(i+1-len(self.frameLabel)) #pad with 'None' labels to preserve index
            self.frameLabel[i]=label
        except: print("Problem in SetFrameLabel")

    def writeLabels(self, path=None):
        if path==None: path=self.labelPath
        labels={"frameLabels":self.frameLabel,
                "classLabel":self.classLabel}
        with open(path, 'w') as f:
            json.dump(labels, f)


class iVideoDataset(object):
    def __init__(self, videoFolderPath, labelFolderPath):
        self.videoFolderPath,self.labelFolderPath = videoFolderPath,labelFolderPath
        self.index=0            #Start with 0th video
        self.updateDetails()   #Separated so that it can be called externally everytime we add new label file

    def getVid(self, i): 
        if i<self.len:
            if extract_file_name(self.vids[i])+".json" in self.labels:
                return iVideo.load(path=os.path.join(self.videoFolderPath, self.vids[i]), labelFolderPath=self.labelFolderPath)
            else: return iVideo.load(path=os.path.join(self.videoFolderPath, self.vids[i]), labelFolderPath=self.labelFolderPath)
    
    def getNext(self): 
        if self.index<self.len:
            self.index+=1
            return self.getVid(self.index-1)

    def reset(self): self.index=0; self.updateDetails()

    def updateDetails(self):
        self.vids=[video for video in os.listdir(self.videoFolderPath) if os.path.isfile(os.path.join(self.videoFolderPath, video))]
        self.labels=[label for label in os.listdir(self.labelFolderPath) if os.path.isfile(os.path.join(self.labelFolderPath, label))]
        self.len = len(self.vids)


def extract_file_name(path):
    tail=os.path.split(path)[-1]
    return ''.join(tail.split(".")[:-1])

def loadVideoWithCV2(path):
    cap = cv2.VideoCapture(path)
    frameCount = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frameWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frameHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(frameCount)
    buf=[]
    
    fc = 0
    ret = True

    noneEncountered=False
    while (fc < frameCount  and ret and noneEncountered==False):
        try: 
            ret, temp = cap.read()
            if isinstance(temp, np.ndarray): buf+=[temp]
        except: noneEncountered=True
        fc += 1
    cap.release()
    return np.asarray(buf)
