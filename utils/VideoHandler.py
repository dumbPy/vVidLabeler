#import skvideo.io
import imageio #Moving to image io as it supports downloading ffmpeg in windows and linux without admin  permission
imageio.plugins.ffmpeg.download()
import numpy as np
import json
import os


class iVideo(object):
    def __init__(self, videoArray, vidName, labelFolderPath, frameLabel=[], classLabel="No Label", config={}, *args, **kwargs):
        self.vid=videoArray
        self.len=len(self.vid)      #Number of Video Frames
        self.index=0                #Current Index. Starts at 0
        self.rollover=False         #tracks frame video rollover
        self.frameLabel=frameLabel  #Label for each frame
        self.classLabel=classLabel  #Label for whole Video
        self.forward=True           #Used to show Forward and Reverse sequence
        self.config=config          #Used to map the label chars to passed text before saving to json
        self.vidName=vidName    #Used for saving Labels
        self.labelFolderPath=labelFolderPath
        self.kwargs=kwargs
        if "description" in kwargs.keys(): self.description=kwargs["description"] #Add description of video
    
    def get(self, i):   return self.vid[i]
    def reset(self):    self.index=0
    def nextFrame(self):
        if self.index!=self.len-1:self.index+=1  #Not at last Frame, send next frame, else same frame
        return self.vid[self.index]
    
    def previousFrame(self): #reverse Video Playback
        if self.index!=0: self.index-=1  #If not at 1st frame, return last frame, else same frame
        return self.vid[self.index]

    @classmethod        
    def load(cls, path, labelFolderPath): #load video using class method:  object=iVideo.load(path)
            #vid = skvideo.io.vread(path)  #This returns 500 frames and leads to segmentation fault in my videos. known issue with skvideo I read
            #vid = np.asarray([frame for frame in skvideo.io.vreader(path)]) #vreader returns Generator that gives me 497-498 frames as opposed to faulty vread above
            def getValidFrames(generator):
                while True:
                    try: frame=generator.get_next_data()
                    except imageio.core.CannotReadFrameError: break
                    else: yield frame

            vid =np.asarray([frame for frame in  getValidFrames(imageio.get_reader(path, "ffmpeg"))]) #this uses imageio rather than skvideo
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
                return cls(vid, vidName, labelFolderPath, frameLabels, classLabel, config)
            else: return cls(vid, vidName, labelFolderPath)

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
        if path==None: path=os.path.join(self.labelFolderPath, self.vidName+".json")
        meta={"frameLabels":self.frameLabel,
              "classLabel":self.classLabel,
              "config": self.config}
        with open(path, 'w') as f:
            json.dump(meta, f)
        
        config_path=os.path.join(self.labelFolderPath, ".config.json")
        if os.path.exists(config_path):
            with open(config_path) as f: #Read Universal Config File
                config=json.load(f)
                try: allVideoClasses=config["allVideoClasses"]    #Get all Video Classes
                except: allVideoClasses=[]
                if not (self.classLabel in allVideoClasses):      #If self.classLabel not in all classes, add it
                    allVideoClasses.append(self.classLabel)
                config["allVideoClasses"]=allVideoClasses
            with open(config_path, "w") as f:
                json.dump(config, f)
            
            
    def getConfig(self): return self.config
    def writeConfig(self, config):  self.config=config

class iVideoDataset(object):
    def __init__(self, videoFolderPath, labelFolderPath):
        self.videoFolderPath,self.labelFolderPath = videoFolderPath,labelFolderPath
        self.index=0            #Start with 0th video then update it in readDetails as per .config.json
        self.readDetails()    #Separated so that it can be called externally everytime we add new label file
        self.forward=True       

    def getVid(self, i): 
        if i<self.len:
            if extract_file_name(self.vids[i])+".json" in self.labels:
                return iVideo.load(path=os.path.join(self.videoFolderPath, self.vids[i]), labelFolderPath=self.labelFolderPath)
            else: return iVideo.load(path=os.path.join(self.videoFolderPath, self.vids[i]), labelFolderPath=self.labelFolderPath)
    
    def writeIndexToConfig(self):
        with open(self.config_path) as f:
            config=json.load(f)
        config["index"]=self.index
        print(f"Writing Index: {self.index}")
        with open(self.config_path, "w+") as f:
            json.dump(config, f)

    def getNextVideo(self, next=True):  #FirstTime flag is used to load current index while attaching
        if self.index!=self.len-1 and next:
            self.index+=1
            self.writeIndexToConfig()
        return self.getVid(self.index)

    def getPreviousVideo(self):
        if self.index!=0:
            self.index-=1
            self.writeIndexToConfig()
        return self.getVid(self.index)


    def reset(self): self.index=0; self.readDetails()

    def readDetails(self):
        videoFormat=[".mov", ".avi", ".mpg", ".mpeg", ".mp4", ".mkv", ".wmv"]
        
        self.vids=[]
        for (path, _, files) in os.walk(self.videoFolderPath):
            if len(files)>0:
                for file in files:
                    if '.'+file.split('.')[-1] in videoFormat: self.vids.append(os.path.join(path,file))
         
        self.labels=[label for label in os.listdir(self.labelFolderPath) if os.path.isfile(os.path.join(self.labelFolderPath, label))]
        self.len = len(self.vids)
        self.config_path=os.path.join(self.labelFolderPath, ".config.json") #If there is a .config.json file, load all class names to create buttons
        if os.path.exists(self.config_path):
            with open(self.config_path) as f:
                config=json.load(f)
                try:    self.allVideoClasses=config["allVideoClasses"]
                except: self.allVideoClasses=[]
                try:    self.index=config["index"]
                except: self.index=0
        else:
            self.allVideoClasses=[]
            self.index=0
            config={"allVideoClasses":self.allVideoClasses,
                    "index"      :self.index} 
            with open(self.config_path, 'w+') as f: json.dump(config, f) #Dump a blank file
            
            



def extract_file_name(path):
    tail=os.path.split(path)[-1]
    return ''.join(tail.split(".")[:-1])
