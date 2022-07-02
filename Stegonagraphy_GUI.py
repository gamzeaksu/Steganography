
from tkinter import *
import tkinter.filedialog
from PIL import ImageTk
from PIL import Image
from tkinter import messagebox
from io import BytesIO
import  os

from PIL import Image
import numpy as np
import wave
from os.path import isfile,join

import time           
import cv2
import numpy as np
import math
import os
import shutil
from subprocess import call,STDOUT
#from playsound import playsound
import pygame
#from tkvideo import tkvideo
from tkVideoPlayer import TkinterVideo

class Steganography:
    def rsa_en(self, message):
        p = 17
        q = 13
        n = p * q
        e = 7
        numberofletter = ord(message)
        #print(numberofletter)
        encrypted = pow(numberofletter, e) % n
        #print(encrypted)
        return  encrypted
    
    def rsa_de(self, encrypted):
        p = 17
        q = 13
        n = p * q
        totient = (p - 1) * (q - 1)
        e = 7
        d = (2 * totient + 1) / e
        decrypted = pow(encrypted, int(d)) % n
        #print(decrypted)
        return chr(decrypted)
    
    
    def get_byte(self,message):
        #byte = bytes(message, "ascii")
        arr = []
        message += "$$cg"
        for i in message:
            encrypted = self.rsa_en(i)
            arr.append(format(encrypted, '08b'))
            newarr = ''.join(arr)
        return  newarr
        #ord unicode hali
        
    def print_message(self,message):
      if '$$cg' in message:
        message = message[:-4]
        
        return 'Decrypted Message: ' + message
      else:
        return 'There is no message!'
        
    def image_encode(self,src, message, dest):
        img = Image.open(src, 'r')
        img = img.convert('RGB')
        w, h = img.size
        
        array = np.array(list(img.getdata()))
     
        msg = self.get_byte(message)
        if len(msg)>len(array):
          print('ERROR: Need larger file size')
        else: 
          i = 0
          for p in range(len(array)):
              for q in range(3):
                  if i < len(msg):
                      binary = bin(array[p][q])[2:]
                      new = binary + msg[i]
                      new = int(new,2)
                      array[p][q] = new
                      i += 1
    
        array=array.reshape(h, w, 3)
        enc_img = Image.fromarray(array.astype('uint8'), img.mode)
        enc_img.save(dest)
        
    def image_decode(self, src):
        img = Image.open(src, 'r').convert('RGB')
        array = np.array(list(img.getdata()))
    
        hiddenb = ""
        for p in range(len(array)):
            for q in range(3):
                arr = bin(array[p][q])
                hiddenb += (arr[2:][-1])
    
        hiddenc = []
        for i in range(0,len(hiddenb),8):
            hiddenc.append(hiddenb[i:i+8])

        message = ''
    
        for i in range(len(hiddenc)):
          if message[-4:] == '$$cg':
            break
          else:
            msgbit = int(hiddenc[i],2)
            char = self.rsa_de(msgbit)
            message += char
    
        msg = self.print_message(message)
        return msg
        
    def audio_encode(self, music, message,dest):
      audio = wave.open(music,mode="rb")
      msg = self.get_byte(message)
      #This will give us the number of bytes of frames that we have
      frame_bytes = bytearray(list(audio.readframes(audio.getnframes()))) #convert to byte array
      msg=list(msg)
      if(len(frame_bytes) < len(msg)): # 24 for ending characters
            messagebox.showinfo('[INFO] Reduce the message size')
      else:
        for i in range(len(msg)):
            frame_bytes[i] = (frame_bytes[i]&254) | int(msg[i])
        frame_modified = bytes(frame_bytes)
        with wave.open(dest, 'wb') as fd:
          fd.setparams(audio.getparams())
          fd.writeframes(frame_modified)
        audio.close()
        
    def audio_decode(self, music):
    
        end_char = '$$cg'
        song = wave.open(music, 'rb')
    
        frame_bytes = bytearray(list(song.readframes(song.getnframes())))
        hiddenb=""
        for i in range(len(frame_bytes)):
          hiddenb += str(frame_bytes[i] & 1)
    
        hiddenc = []
        for i in range(0, len(hiddenb), 8):
            hiddenc.append(hiddenb[i:i+8])
        message = ''
        for i in range(len(hiddenc)):
          if message[-4:] == '$$cg':
            break
          else:
            msgbit = int(hiddenc[i],2)
            char = self.rsa_de(msgbit)
            message += char
        msg = self.print_message(message)
        return msg
        
    def frame_extraction(self, video = 'video.mp4',path='./encode'):
        if not os.path.exists(path): #dosya yolu var mı yok mu
            os.makedirs(path)          #pathi oluşturur
            #messagebox.showinfo("[INFO] encode directory is created")
        temp_folder=path
        
    
        vidcap = cv2.VideoCapture(video)
        count = 0
    
        while True:
            success,image = vidcap.read()
            if not success:
                break
            cv2.imwrite(os.path.join(temp_folder, "{:d}.png".format(count)), image)
            count += 1
    
    def clean_tmp(self, path="./encode"): #d
        if os.path.exists(path):
            shutil.rmtree(path)
            
    def video_encode(self, video, message, dest, root="./encode/"):
        self.frame_extraction(video)
        
        call(["ffmpeg", "-i",video, "-q:a", "0", "-map", "a", root+"audio.mp3", "-y"],
            stdout=open(os.devnull, "w"), stderr=STDOUT) #sesi ayırıyor
        
        
        msg=list(message +'$$cg')
        
        for i in range(len(msg)):
            image="{}{}.png".format(root,i+1) #videodan çıkarılan imageları tek tek alma
            
            self.image_encode(image, msg[i],image) #her bir imagea mesajın bir harfini gizliyor
            
            #print("[INFO] frame {} holds {}".format(image,msg[i]))
        
             
        call(["ffmpeg", "-i", root+"%d.png" , "-vcodec", "png", root+"video.mp4", "-y"],
             stdout=open(os.devnull, "w"), stderr=STDOUT)   #resimlerden video yapıyor
        
        call(["ffmpeg", "-i", root+"video.mp4", "-i", root+"audio.mp3", "-codec", "copy", dest, "-y"],
             stdout=open(os.devnull, "w"), stderr=STDOUT)      #videoya sesi geri ekliyor
        
        self.clean_tmp()
    
    def video_decode(self, video= 'video_enc.mp4',root ='./encode/'):
        #self.frame_extraction(video) # 
        if not os.path.exists(root): #dosya yolu var mı yok mu
            os.makedirs(root)          #pathi oluşturur
            #print("[INFO] encode directory is created")
        call(['ffmpeg','-i',video,root+'%d.png'])
        secret=[]
        
        #print(len(os.listdir(root)))
        video_msg = ''
        for i in range(len(os.listdir(root))):
            image="{}{}.png".format(root,i+1) #./tmp/0.png
            print(image)
            #image_decode(image)
    
            img = Image.open(image, 'r').convert('RGB')
            array = np.array(list(img.getdata()))
    
            hiddenb = ""
            for p in range(len(array)):
                for q in range(3):
                    arr = bin(array[p][q])
                    hiddenb += (arr[2:][-1])
    
            hiddenc = []
            for i in range(0,len(hiddenb),8):
                hiddenc.append(hiddenb[i:i+8])
    
            message = ''
    
            for i in range(len(hiddenc)):
              if message[-4:] == '$$cg':
                break
              else:
                msgbit = int(hiddenc[i],2)
                char = self.rsa_de(msgbit)
                message += char
            
            if '$$cg' in message:
              message = message[:-4]
              print('Decrypted Message:',message)
              video_msg = video_msg + message
              print(video_msg)
            else:
              print('There is no message!')
          
            if video_msg[-4:] == '$$cg':
                break
    
        self.clean_tmp()
        msg = self.print_message(video_msg)
        return msg
    
class Steganography_GUI:
    
    myfile =''
    message =''
    selected_audio = ''
    encoded_audio = ''
    text1 = ''
    text2=''
    def main(self,root):
        root.title('Steganography')
        root.geometry('550x600')
        root["background"]="#E9EC86"
        root.resizable(width =False, height=False)
        f = Frame(root)
        f["background"]="#E9EC86"
        
        title = Label(f,text='Steganography',pady =10,padx=10,bg='#E9EC86')
        title.config(font=('Lucida Calligraphy',33))
        title.place()

        load = Image.open("lisa.JPEG")
        resize_image = load.resize((400,200))
        img = ImageTk.PhotoImage(resize_image)
        panel = Label(f, image=img,bg='#E9EC86')
        panel.image = img
        
        panel.place(relx=0.5, rely=0.12, anchor=CENTER)
        
        
        l2 = Label(f, text='Enter the text to hide:',pady =10,padx=10,bg='#E9EC86')
        l2.config(font=('Lucida Calligraphy',18))
        l2.place(relx=0.5, rely=0.45, anchor=CENTER)
        
        entry = Text(f,  width = 50,
                            height=5,
                            padx=15,
                            pady=15,
                            font =12)
        
        entry.place()   
        self.entry = entry
        b_image = Button(f,text="Image",command= lambda :self.f_image(f,entry),bg='#F2F5A2')
        b_image.config(font=('Lucida Calligraphy',14, 'bold'))
     
        
        b_audio = Button(f, text="Audio",command=lambda :self.f_audio(f,entry),bg='#F2F5A2')
        b_audio.config(font=('Lucida Calligraphy',14, 'bold'))
     

        b_video = Button(f, text="Video",command=lambda :self.f_video(f,entry),bg='#F2F5A2')
        b_video.config(font=('Lucida Calligraphy',14, 'bold'))
        
        b_image.place()
        b_audio.place()
        b_video.place()
        
        f.pack()
        title.pack()
        panel.pack()
        
        l2.pack()
        entry.pack()
        b_image.pack(side=LEFT, padx=50, pady=20)
        b_audio.pack(side=LEFT, padx=20, pady=20)
        b_video.pack(side=LEFT, padx=50, pady=20)
        
    def f_video(self,f,entry):
        self.message = entry.get("1.0", END)
        
        f.destroy()
        root.geometry('550x400')
        f_v = Frame(root)
        root["background"]="#E9EC86"
        f_v["background"]="#E9EC86"        

        title = Label(f_v, text='Video Steganography', bg='#E9EC86',padx = 10,pady=10)
        title.config(font=('Lucida Calligraphy',25))
        title.place()

        myimg = Image.open('lisa.JPEG', 'r')
        myimage = myimg.resize((300, 200))
        img = ImageTk.PhotoImage(myimage)
        
        panel = Label(f_v, image=img,padx = 10,pady=10)
        panel.image = img
        panel.place() 

        b_encode = Button(f_v, text="Encode", command= lambda : self.encode_video(f_v), bg='#F2F5A2',padx = 10,pady=10)
        b_encode.config(font=('Lucida Calligraphy', 14, 'bold'))
        b_encode.place()
    
        b_decode = Button(f_v, text="Decode", command= lambda : self.decode_video(f_v), bg='#F2F5A2',padx = 10,pady=10)
        b_decode.config(font=('Lucida Calligraphy', 14, 'bold'))
        b_decode.place()      
        
        
        f_v.pack()
        title.pack()
        panel.pack()
        b_encode.pack(side=LEFT, padx=50, pady=20)
        b_decode.pack(side=LEFT, padx=50, pady=20)    
        
    def f_audio(self,f,entry):
        self.message = entry.get("1.0", END)
        
        f.destroy()
        root.geometry('550x400')
        f_a = Frame(root)
        root["background"]="#E9EC86"
        f_a["background"]="#E9EC86"        

        title = Label(f_a, text='Audio Steganography', bg='#E9EC86',padx = 10,pady=10)
        title.config(font=('Lucida Calligraphy',25))
        title.place()

        myimg = Image.open('lisa.JPEG', 'r')
        myimage = myimg.resize((300, 200))
        img = ImageTk.PhotoImage(myimage)
        panel = Label(f_a, image=img,padx = 10,pady=10)
        panel.image = img
        panel.place() 

        b_encode = Button(f_a, text="Encode", command= lambda : self.encode_audio(f_a), bg='#F2F5A2',padx = 10,pady=10)
        b_encode.config(font=('Lucida Calligraphy', 14, 'bold'))
        b_encode.place()
    
        b_decode = Button(f_a, text="Decode", command= lambda : self.decode_audio(f_a), bg='#F2F5A2',padx = 10,pady=10)
        b_decode.config(font=('Lucida Calligraphy', 14, 'bold'))
        b_decode.place()      
        
        f_a.pack()
        title.pack()
        panel.pack()
        b_encode.pack(side=LEFT, padx=50, pady=20)
        b_decode.pack(side=LEFT, padx=50, pady=20)
        
    def f_image(self,f,entry):
        self.message = entry.get("1.0", END)
        print(self.message) 
        
        
        f.destroy()
        root.geometry('550x400')
        f_img = Frame(root)
        root["background"]="#E9EC86"
        f_img["background"]="#E9EC86"
        
        title = Label(f_img, text='Image Steganography', bg='#E9EC86',padx = 10,pady=10)
        title.config(font=('Lucida Calligraphy',25))
        title.place()

        myimg = Image.open('lisa.JPEG', 'r')
        myimage = myimg.resize((300, 200))
        img = ImageTk.PhotoImage(myimage)
        panel = Label(f_img, image=img,padx = 10,pady=10)
        panel.image = img
        panel.place() 
        
        b_encode = Button(f_img, text="Encode", command= lambda : self.encode_image(f_img), bg='#F2F5A2',padx = 10,pady=10)
        b_encode.config(font=('Lucida Calligraphy', 14, 'bold'))
        b_encode.place()
    
        b_decode = Button(f_img, text="Decode", command= lambda : self.decode_image(f_img), bg='#F2F5A2',padx = 10,pady=10)
        b_decode.config(font=('Lucida Calligraphy', 14, 'bold'))
        b_decode.place()      
        
        
        f_img.pack()
        title.pack()
        panel.pack()
        b_encode.pack(side=LEFT, padx=50, pady=20)
        b_decode.pack(side=LEFT, padx=50, pady=20)
        
    def back(self,frame):
            frame.destroy()
            self.main(root)
            
    def encode_audio(self,f_a):
        
        root.geometry('550x600')
        f_a.destroy()
        f_en = Frame(root)
        root["background"]="#E9EC86"
        f_en["background"]="#E9EC86"
        
        self.text1 = tkinter.StringVar()
        self.text1.set('Selected Audio: ')
        l1 = Label(f_en, textvariable=self.text1, bg='#E9EC86')
        l1.config(font=('Lucida Calligraphy',25))
        l1.place()
        self.text2 = tkinter.StringVar()
        self.text2.set('Encoded Audio: ')
        l2 = Label(f_en, textvariable=self.text2, bg='#E9EC86')
        l2.config(font=('Lucida Calligraphy',25))
        l2.place()
        
        b_choose = Button(f_en, text="Choose Audio", command= lambda : self.choose_audio(f_en,'encode',l1,l2), bg='#F2F5A2')
        b_choose.config(font=('Lucida Calligraphy', 14, 'bold'))
        b_choose.place()
        
        b_back= Button(f_en, text="Back", command= lambda : self.back(f_en), bg='#F2F5A2')
        b_back.config(font=('Lucida Calligraphy', 14, 'bold'))
        b_back.place()  
        
        b_play1 = Button(f_en, text="▶",width=2, height=1,command= lambda : self.play_audio(self.selected_audio), bg='#F2F5A2',padx = 10,pady=10)
        b_play1.config(font=('Lucida Calligraphy', 14, 'bold'))
        b_play1.place()
        
        b_play2= Button(f_en, text="▶",width=2, height=1, command= lambda : self.play_audio(self.encoded_audio), bg='#F2F5A2',padx = 10,pady=10)
        b_play2.config(font=('Lucida Calligraphy', 14, 'bold'))
        b_play2.place()
        
        b_pause1 = Button(f_en, text="⏸️",width=2, height=1, command= lambda : self.stop_audio(), bg='#F2F5A2',padx = 10,pady=10)
        b_pause1.config(font=('Lucida Calligraphy', 14, 'bold'))
        b_pause1.place()
        
        b_pause2= Button(f_en, text="⏸️",width=2, height=1, command= lambda : self.stop_audio(), bg='#F2F5A2',padx = 10,pady=10)
        b_pause2.config(font=('Lucida Calligraphy', 14, 'bold'))
        b_pause2.place()


        l1 = Label(f_en, text='Selected Audio: ', bg='#E9EC86')
        l1.config(font=('Lucida Calligraphy',14))
        l1.place()
      
        l2 = Label(f_en, text='Encoded Audio', bg='#E9EC86')
        l2.config(font=('Lucida Calligraphy',14))
        l2.place()
        
        f_en.pack()
        b_choose.pack( padx=50, pady=20)
        l1.pack()
        b_play1.place(x=130,y=170)
        b_pause1.place(x=250,y=170)
        l2.pack(padx=50, pady=120)
        b_play2.place(x=130,y=350)
        b_pause2.place(x=250,y=350)
        b_back.pack( padx=150, pady=50)  
        
    def play_audio(self,audio):
        pygame.mixer.init()
        pygame.mixer.music.load(audio)
        pygame.mixer.music.play(loops=0)   
        
    def stop_audio(self):
        pygame.mixer.music.stop()  
        
    def play_video(self,video):
        player = tkvideo(video, video_label,
                 loop = 1, size = (700, 500))
        player.play()
        
    def encode_image(self,f_img):
        root.geometry('550x800')
        f_img.destroy()
        f_en = Frame(root)
        root["background"]="#E9EC86"
        f_en["background"]="#E9EC86"
        
        myimg = Image.open('transparent.png')
        myimage = myimg.resize((300, 200))
        img = ImageTk.PhotoImage(myimage)
        
        panel1 = Label(f_en, image=img, bg ='#E9EC86')
        panel1.image = img
        panel1.place()   
        
        myimg = Image.open('transparent.png')
        myimage = myimg.resize((300, 200))
        img = ImageTk.PhotoImage(myimage)
        panel2 = Label(f_en, image=img, bg ='#E9EC86')
        panel2.image = img
        panel2.place()
            
        b_choose = Button(f_en, text="Choose Image", command= lambda : self.choose_image(f_en, panel1,'encode', panel2), bg='#F2F5A2',padx = 10,pady=10)
        b_choose.config(font=('Lucida Calligraphy', 14, 'bold'))
        b_choose.place()
        
        b_back= Button(f_en, text="Back", command= lambda : self.back(f_en), bg='#F2F5A2',padx = 10,pady=10)
        b_back.config(font=('Lucida Calligraphy', 14, 'bold'))
        b_back.place()
        
   
        l1 = Label(f_en, text='Selected Image', bg='#E9EC86')
        l1.config(font=('Lucida Calligraphy',25))
        l1.place()

      
        l2 = Label(f_en, text='Encoded Image', bg='#E9EC86')
        l2.config(font=('Lucida Calligraphy',25))
        l2.place()

        f_en.pack()
        b_choose.pack( padx=50, pady=20)
        
        l1.pack()
        panel1.pack()
        l2.pack()
        panel2.pack()
        b_back.pack( padx=50, pady=20)
 
    def encode_video(self,f_v):
        root.geometry('550x600')
        f_v.destroy()
        f_en = Frame(root)
        root["background"]="#E9EC86"
        f_en["background"]="#E9EC86"
        

        b_choose = Button(f_en, text="Choose Video", command= lambda : self.choose_video(f_en,'encode'), bg='#F2F5A2',padx = 10,pady=10)
        b_choose.config(font=('Lucida Calligraphy', 14, 'bold'))
        b_choose.place()
        
        b_back= Button(f_en, text="Back", command= lambda : self.back(f_en), bg='#F2F5A2',padx = 10,pady=10)
        b_back.config(font=('Lucida Calligraphy', 14, 'bold'))
        b_back.place()

        f_en.pack()
        b_choose.pack( padx=50, pady=20)

        b_back.pack( padx=50, pady=20)
    
        
    def choose_video(self, f_en, ste):

        self.myfile = tkinter.filedialog.askopenfilename(filetypes = ([('mp4', '*.mp4'),('All Files', '*.*')]))
        if not self.myfile:
            messagebox.showerror("Error","You have selected nothing !")
        else:    
            file = self.myfile
  
            l1 = Label(f_en, text='Selected Video:'+file.split('/')[-1], bg='#E9EC86')
            l1.config(font=('Lucida Calligraphy',14))
            l1.pack()
            videoplayer = TkinterVideo(master=f_en, scaled=True)
            videoplayer.load(r"{}".format(file))
            videoplayer.pack()
            videoplayer.play()

            
            if ste == 'encode':
                stg = Steganography()
                dest = self.myfile.split('.')[-2]+'_enc.mp4'
                print(dest)
                stg.video_encode(self.myfile, self.message, dest)
                
                l2 = Label(f_en, text='Encoded Video:'+dest.split('/')[-1], bg='#E9EC86')
                l2.config(font=('Lucida Calligraphy',14))
                l2.pack()
                videoplayer = TkinterVideo(master=f_en, scaled=True)
                videoplayer.load(r"{}".format(dest))
                videoplayer.pack()
                videoplayer.play()
            
            else:
                stg = Steganography()
                msg = stg.video_decode(self.myfile)
                messagebox.showinfo("Info",msg) 
        
    def choose_image(self, f_en, panel1,ste, panel2 = None ):

        self.myfile = tkinter.filedialog.askopenfilename(filetypes = ([('png', '*.png'),('jpeg', '*.jpeg'),('jpg', '*.jpg'),('All Files', '*.*')]))
        if not self.myfile:
            messagebox.showerror("Error","You have selected nothing !")
        else:    
            file = self.myfile
           
            
            myimg = Image.open(file)
            myimage = myimg.resize((300, 200))
            img = ImageTk.PhotoImage(myimage)
            
            #panel1 = Label(f_en, image=img)
            panel1.configure(image=img)
            panel1.image = img
            panel1.pack()   
            
            if ste == 'encode':
                stg = Steganography()
                dest = self.myfile.split('.')[-2]+'_enc.png'
                stg.image_encode(self.myfile, self.message, dest)  
                myimg = Image.open(dest)
                myimage = myimg.resize((300, 200))
                img = ImageTk.PhotoImage(myimage)
                #panel2 = Label(f_en, image=img)
                panel2.configure(image=img)
                panel2.image = img
                panel2.pack() 
            else:
                stg = Steganography()
                msg = stg.image_decode(self.myfile)
                messagebox.showinfo("Info",msg) 
                
    def choose_audio(self,f_en,ste,l1,l2=None):
        self.myfile = tkinter.filedialog.askopenfilename(filetypes = ([('wav', '*.wav'),('All Files', '*.*')]))
        self.selected_audio = self.myfile
        print(self.myfile)
        if not self.myfile:
            messagebox.showerror("Error","You have selected nothing !")
        else:    
            file = self.myfile
            l1['text'] = ('Selected Audio:\n '+ file.split('/')[-1])

            if ste == 'encode':
                dest = file.split('.')[-2]+'_enc.wav'
                print(dest)
                stg = Steganography()
                stg.audio_encode(self.myfile, self.message, dest)      
                #text = tkinter.StringVar()
                l2['text']=('Encoded Audio:\n '+dest.split('/')[-1]) 
                self.encoded_audio = dest

            else:
                stg = Steganography()
                msg = stg.audio_decode(self.myfile) 
                messagebox.showinfo("Info",msg) 
                
    def decode_audio(self,f_a):
        root.geometry('550x500')
        f_a.destroy()
        f_de = Frame(root)
        root["background"]="#E9EC86"
        f_de["background"]="#E9EC86"
        
        l1 = Label(f_de, text='Selected Audio', bg='#E9EC86')
        l1.config(font=('Lucida Calligraphy',14))
        l1.place()
      
        b_choose = Button(f_de, text="Choose Audio", command= lambda : self.choose_audio(f_de,'decode',l1), bg='#F2F5A2',padx = 10,pady=10)
        b_choose.config(font=('Lucida Calligraphy', 14, 'bold'))
        b_choose.place()
        
        b_back= Button(f_de, text="Back", command= lambda : self.back(f_de), bg='#F2F5A2',padx = 10,pady=10)
        b_back.config(font=('Lucida Calligraphy', 14, 'bold'))
        b_back.place()

        b_play1 = Button(f_de, text="▶",width =2,height=1, command= lambda : self.play_audio(self.selected_audio), bg='#F2F5A2',padx = 10,pady=10)
        b_play1.config(font=('Lucida Calligraphy', 14, 'bold'))
        b_play1.place()
        
        b_pause1 = Button(f_de, text="⏸️",width =2,height=1,  command= lambda : self.stop_audio(), bg='#F2F5A2',padx = 10,pady=10)
        b_pause1.config(font=('Lucida Calligraphy', 14, 'bold'))
        b_pause1.place()
    
        f_de.pack()
        b_choose.pack( padx=50, pady=20)
        
        l1.pack()
        b_play1.pack()
        b_pause1.pack()

        b_back.pack( padx=50, pady=20)

        
    def decode_image(self,f_img):
        root.geometry('550x500')
        f_img.destroy()
        f_de = Frame(root)
        root["background"]="#E9EC86"
        f_de["background"]="#E9EC86"
        
        myimg = Image.open('transparent.png')
        myimage = myimg.resize((300, 200))
        img = ImageTk.PhotoImage(myimage)
        panel1 = Label(f_de, image=img, bg ='#E9EC86')
        panel1.image = img
        panel1.place()      
            
        b_choose = Button(f_de, text="Choose Image", command= lambda : self.choose_image(f_de, panel1,'decode'), bg='#F2F5A2',padx = 10,pady=10)
        b_choose.config(font=('Lucida Calligraphy', 14, 'bold'))
        b_choose.place()
        
        b_back= Button(f_de, text="Back", command= lambda : self.back(f_de), bg='#F2F5A2',padx = 10,pady=10)
        b_back.config(font=('Lucida Calligraphy', 14, 'bold'))
        b_back.place()

        l1 = Label(f_de, text='Selected Image', bg='#E9EC86')
        l1.config(font=('Lucida Calligraphy',25))
        l1.place()
      

        f_de.pack()
        b_choose.pack( padx=50, pady=20)
        
        l1.pack()
        panel1.pack()

        b_back.pack( padx=50, pady=20)
        
    def decode_video(self,f_v):
        root.geometry('550x500')
        f_v.destroy()
        f_de = Frame(root)
        root["background"]="#E9EC86"
        f_de["background"]="#E9EC86"
            
            
        b_choose = Button(f_de, text="Choose Video", command= lambda : self.choose_video(f_de,'decode'), bg='#F2F5A2',padx = 10,pady=10)
        b_choose.config(font=('Lucida Calligraphy', 14, 'bold'))
        b_choose.place()
        
        b_back= Button(f_de, text="Back", command= lambda : self.back(f_de), bg='#F2F5A2',padx = 10,pady=10)
        b_back.config(font=('Lucida Calligraphy', 14, 'bold'))
        b_back.place()     

        f_de.pack()
        b_choose.pack( padx=50, pady=20)
        b_back.pack( padx=50, pady=20)
                    
            
root = Tk()

o = Steganography_GUI()
o.main(root)

root.mainloop()