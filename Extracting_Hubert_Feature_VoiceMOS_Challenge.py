"""
@author: Ryandhimas Zezario
ryandhimas@citi.sinica.edu.tw
"""

import sys
import scipy.io
import librosa
import os
import time  
import numpy as np
import numpy.matlib
import random
import pdb
import torch
import fairseq

def ListRead(filelist):
    f = open(filelist, 'r')
    Path=[]
    for line in f:
        Path=Path+[line[0:-1]]
    return Path
    
def shuffle_list(x_old,index):
    x_new=[x_old[i] for i in index]
    return x_new    
         
def Extract_SSL_Feat(filepath, model, list_new,dirname):
    name = filepath [0]
    name_without_ext = name[:-4] 
    new_name =  name_without_ext +'.npy'
    path = './data/phase1-main/DATA/wav/'+name  

    cached_path = dirname+str(new_name)
    audio_data, _ = librosa.load(path, sr=16000) 

    end2end_channel_1 = np.reshape(audio_data,(1,audio_data.shape[0]))   
    end2end_channel_1 = torch.from_numpy(end2end_channel_1).to("cuda:0")
    features_1 = model(end2end_channel_1, features_only=True, mask=False)['x']  
    causal_1 = features_1.detach().to("cpu").numpy()
    
    np.save(cached_path,causal_1)
        
    info = filepath[1]+','+str(cached_path)
    list_new.append(info)
    
    return list_new
    
def train_data_generator(file_list,model):
    dirname='./data/phase1-main/Hubert/train/'
    list_new=[]
    for index in range(len(file_list)):
        pesq_filepath = file_list[index].split(',')
        list_new=Extract_SSL_Feat(pesq_filepath, model, list_new,dirname)    
   
    with open('./data/phase1-main/DATA/sets/List_Npy_Train_hubert_MOS_Challenge_phase1_main.txt','w') as g:
        for item in list_new:
          g.write("%s\n" % item)

def val_data_generator(file_list,model):
    dirname='./data/phase1-main/Hubert/val/'
    list_new=[]
    
    for index in range(len(file_list)):   
        pesq_filepath = file_list[index].split(',')
        list_new=Extract_SSL_Feat(pesq_filepath, model, list_new,dirname)    

    with open('./data/phase1-main/DATA/sets/List_Npy_Val_hubert_MOS_Challenge_phase1_main.txt','w') as g:
        for item in list_new:
          g.write("%s\n" % item)
                    
def Save_NPY(Train_data, Val_data):
    cp_path = './fairseq/hubert_large_ll60k.pt'
    model, cfg, task = fairseq.checkpoint_utils.load_model_ensemble_and_task([cp_path], arg_overrides={"data": "./fairseq/data/dict"})
    model = model[0]
    model.eval()
    device = torch.device("cuda:0")
    model = model.to(device)
    train_data_generator(Train_data,model)
    val_data_generator(Val_data,model)

if __name__ == '__main__':	
    Train_list= ListRead('./data/phase1-main/DATA/sets/train_mos_list.txt')
    Val_list= ListRead('./data/phase1-main/DATA/sets/val_mos_list.txt')
    Save_NPY(Train_list, Val_list)
	
