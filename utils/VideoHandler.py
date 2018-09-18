import skvideo.io
import numpy as np
import json
import os
from pathlib import Path

class iVideo(object):
    def __init__(self, videoArray, frameLabel=[], classLabel="", labelMap=None):
        self.vid=videoArray
        if isinstance(self.vid, str): self.vid=skvideo.io.vread(self.vid) #Handeling Paths Directly to save memory
        self.len=len(self.vid)      #Number of Video Frames
        self.index=0                #Current Index. Starts at 0
        self.rollover=False         #tracks frame video rollover
        self.frameLabel=frameLabel  #Label for each frame
        self.classLabel=classLabel  #Label for whole Video
        self.forward=True           #Used to show Forward and Reverse sequence
        self.labelMap=labelMap      #Used to map the label chars to passed text before saving to json

    def get(self, i):   return self.vid[i]
    def reset(self):    self.rollover=False; self.index=0
    def nextFrame(self):
        if self.forward and self.index<self.len:    #Forward playback and index not at last frame
            self.index+=1
            return self.vid[self.index-1]
        elif self.index>0:                          #reverse Video Playback and index ahead of 0
            self.index-=1
            return self.vid[self.index+1]

    
    @classmethod        
    def load(cls, path, labelPath=None): #load video using class method:  object=iVideo.load(path)
            vid =skvideo.io.vread(path)
            if labelPath:
                with open(labelPath) as f:
                    label=json.load(f)["frame_labels"]
                return cls(vid, label)
            else: return cls(vid)

    def setFrameLabel(self, label, i=None): #Can be used for labeling a frame at index i
        if i==None: i=self.index-1    
        if len(self.frameLabel)<i+1:
            self.frameLabel+=['None']*(i+1-len(self.frameLabel)) #pad with 'None' labels to preserve index
        self.frameLabel[i]=label

    def writeLabels(self, path):
        labels={"framelabel":self.frameLabel,
                "classLabel":self.classLabel}
        with open(path, 'w') as f:
            json.dump(labels, f)


class iVideoDataset(object):
    def __init__(self, videoFolderPath, labelFolderPath):
        self.updateDetails()   #Separated so that it can be called externally everytime we add new label file
        self.videoFolderPath,self.labelFolderPath = videoFolderPath,labelFolderPath
        self.index=0            #Start with 0th video

    def getVid(self, i): 
        if i<self.len:
            if extract_file_name(self.vids[i])+".json" in self.labels:
                return iVideo.load(path=self.vids[i], labelPath=os.path.join(self.labelFolderPath, extract_file_name(self.vids[i])+".json"))
            else: return iVideo.load(path=self.vids[i])
    
    def getNext(self): 
        if self.index<self.len:
            self.index+=1
            return self.getVid(self.index-1)

    def reset(self): self.index=0; self.updateDetails()

    def updateDetails(self):
        self.vids=[video for video in os.listdir(self.videoFolderPath) if os.path.isfile(video)]
        self.labels=[label for label in os.listdir(self.labelFolderPath) if os.path.isfile(label)]
        self.len = len(self.vids)


def extract_file_name(path):
    tail=os.path.split(path)[-1]
    return ''.join(tail.split(".")[:-1])
