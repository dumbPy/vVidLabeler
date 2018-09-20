import skvideo.io
import numpy as np
import json
import os


class iVideo(object):
    def __init__(self, videoArray, videoName, labelPath, frameLabel=[], classLabel="", config={}):
        self.vid=videoArray
        self.len=len(self.vid)      #Number of Video Frames
        self.index=0                #Current Index. Starts at 0
        self.rollover=False         #tracks frame video rollover
        self.frameLabel=frameLabel  #Label for each frame
        self.classLabel=classLabel  #Label for whole Video
        self.forward=True           #Used to show Forward and Reverse sequence
        self.config=config          #Used to map the label chars to passed text before saving to json
        self.videoName=videoName    #Used for saving Labels
        self.labelPath=labelPath
    
    
    def get(self, i):   return self.vid[i]
    def reset(self):    self.index=0
    def nextFrame(self):
        if not self.forward:
            self.forward=True
            if self.index==0: self.index+=1
            else: self.index+=2
        if  self.index<self.len-1:    #Forward playback and index not at last frame
            self.index+=1
            return self.vid[self.index-1]
        else: return self.vid[self.index]
    
    def previousFrame(self): #reverse Video Playback
        if self.forward:
            self.forward=False
            if self.index==self.len-1: self.index-=1
            else: self.index-=2
        if self.index>0:     #index ahead of 0 so we can go backwards
            self.index-=1
            return self.vid[self.index+1]
        else: return self.vid[self.index]

    @classmethod        
    def load(cls, path, labelFolderPath): #load video using class method:  object=iVideo.load(path)
            #vid = skvideo.io.vread(path)  #This returns 500 frames and leads to segmentation fault in my videos. known issue with skvideo I read
            vid = np.asarray([frame for frame in skvideo.io.vreader(path)]) #vreader returns Generator that gives me 497-498 frames as opposed to faulty vread above
            #vid =np.asarray([frame for frame in  imageio.get_reader(path, "ffmpeg")]) #this uses imageio rather than skvideo
            vidName=extract_file_name(path)
            labelPath=os.path.join(labelFolderPath, vidName+".json")
            if os.path.isfile(labelPath):
                with open(labelPath) as f:
                    details=json.load(f)
                try:    frameLabels=details["frameLabels"]
                except: frameLabels=[]
                try:    classLabel =details["classLabel"]
                except: classLabel =""
                try:    config     =details["config"]
                except: config     ={}
                return cls(vid, vidName, labelPath, frameLabels, classLabel, config)
            else: return cls(vid, vidName, labelPath)

    def setFrameLabel(self, label, i=None): #Can be used for labeling a frame at index i
        try:    
            if i==None: i=self.index-1    
            if len(self.frameLabel)<i+1:
                self.frameLabel+=['None']*(i+1-len(self.frameLabel)) #pad with 'None' labels to preserve index
            self.frameLabel[i]=label
        except: print("Problem in SetFrameLabel")

    def setClassLabel(self, label):
        self.classLabel=label

    def writeMeta(self, path=None):
        if path==None: path=self.labelPath
        meta={"frameLabels":self.frameLabel,
              "classLabel":self.classLabel,
              "config": self.config}
        with open(path, 'w') as f:
            json.dump(meta, f)

    def getConfig(self): return self.config
    def writeConfig(self, config):  self.config=config

class iVideoDataset(object):
    def __init__(self, videoFolderPath, labelFolderPath):
        self.videoFolderPath,self.labelFolderPath = videoFolderPath,labelFolderPath
        self.index=0            #Start with 0th video
        self.updateDetails()    #Separated so that it can be called externally everytime we add new label file
        self.forward=True       

    def getVid(self, i): 
        if i<self.len:
            if extract_file_name(self.vids[i])+".json" in self.labels:
                return iVideo.load(path=os.path.join(self.videoFolderPath, self.vids[i]), labelFolderPath=self.labelFolderPath)
            else: return iVideo.load(path=os.path.join(self.videoFolderPath, self.vids[i]), labelFolderPath=self.labelFolderPath)
    
    def getNextVideo(self): 
        if not self.forward:
            self.forward=True
            if self.index==0: self.index+=1
            else: self.index+=2
        if  self.index<self.len-1:    #Forward playback and index not at last frame
            self.index+=1
            return self.getVid(self.index-1)
        else: return self.getVid(self.index)

    def getPreviousVideo(self):
        if self.forward:
            self.forward=False
            if self.index==self.len-1: self.index-=1
            else: self.index-=2
        if self.index>0:     #index ahead of 0 so we can go backwards
            self.index-=1
            return self.getVid(self.index+1)
        else: return self.getVid(self.index)


    def reset(self): self.index=0; self.updateDetails()

    def updateDetails(self):
        self.vids=[video for video in os.listdir(self.videoFolderPath) if os.path.isfile(os.path.join(self.videoFolderPath, video))]
        self.labels=[label for label in os.listdir(self.labelFolderPath) if os.path.isfile(os.path.join(self.labelFolderPath, label))]
        self.len = len(self.vids)



def extract_file_name(path):
    tail=os.path.split(path)[-1]
    return ''.join(tail.split(".")[:-1])
