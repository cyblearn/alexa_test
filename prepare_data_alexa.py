#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 2021.02.04

@author: chenyingbo


"""

import os
import sys
import numpy as np
import soundfile as sf
#from alignment import *
from utils import *

# ------------------------------------- defines ----------------------------------------- #
class PREPARE_DATA_ALEXA:
    # 初始化
    def __init__(self, dir_src, dir_dst, interval=2, dst_sr=20050):
        self.dir_p_src_ = dir_src
        self.dir_dst_ = dir_dst
        self.interval_ = interval
        self.locals_ = ['AU', 'BR_PT', 'CA_FR', 'DE', 'ES-ES', 'FR', 'IN', 'IN_HI', 'IT', 'JP', 'MX-ES', 'UK', 'US_CA', 'US-ES']
        self.dir_prefixs_ = ['FRR_RAR_utterances_', 'LatencyTest_utterances_', 'MobileTest_']
    
    # 测试dir_src完整性，检查dir_dst是否为空。成功返回1，否则0
    def check(self):
        # 原始文件完整性
        for i in range(len(self.locals_)):
            dir_tmp = os.path.join(self.dir_p_src_, self.locals_[i])
            if not os.path.exists(dir_tmp):
                LOG("path not exists: " + str(dir_tmp))
                return 0
        
        if os.path.exists(self.dir_dst_):
            rmdir(self.dir_dst_)
        else:
            os.mkdir(self.dir_dst_)
        return 1

    # 生成测试音频
    def run(self):
        for i in range(len(self.locals_)):
            os.mkdir(os.path.join(self.dir_dst_, self.locals_[i]))  # 新建目标文件夹中的地区文件夹

            dir_p_0 = os.path.join(self.dir_p_src_, self.locals_[i]) # local dir
            dir_n_1 = os.listdir(dir_p_0)
            for j in range(len(dir_n_1)):
                dir_p_1 = os.path.join(dir_p_0, dir_n_1[j])
                if not os.path.isfile(dir_p_1) and dir_n_1[j] != "__MACOSX":
                    wav_list = getFiles(dir_p_1)
                    for k in range(len(wav_list)):
                        wav_list[k] = os.path.join(dir_p_1, wav_list[k])

                    wav_data, sr, calib_list = self.generate_wav_and_calib(wav_list)
                    
                    dst_path = os.path.join(self.dir_dst_, self.locals_[i], dir_n_1[j])
                    dst_path_wav = dst_path + '.wav'
                    dst_path_clb = dst_path + '.clb'
                    
                    # 写文件
                    sf.write(dst_path_wav, wav_data, sr)
                    f = open(dst_path_clb, "w")
                    for line in calib_list:
                        f.write(line + '\n')
                    f.close()
    
    # 生成长音频和标注文本
    def generate_wav_and_calib(self, wav_lists):
        wav, sr = sf.read(wav_lists[0])
        wav_zeros = np.zeros((sr * self.interval_), dtype='float64')

        #ali = Alignment()
        #ali_data = ali.create(sr)

        wav_sum = wav_zeros.copy()
        #wav_sum = np.concatenate((wav_sum, ali_data, wav_zeros), axis=0)

        calib_list = []
        time_loc = 2
        
        for i in range(len(wav_lists)):
            wav_tmp, sr = sf.read(wav_lists[i])
            dur_tmp = wav_tmp.shape[0] / sr
            
            # 更新
            wav_sum = np.concatenate((wav_sum, wav_tmp, wav_zeros), axis=0)
            calib_list.append(str(wav_lists[i]) + '    ' + str(time_loc) + '     ' + str(time_loc + dur_tmp))
            time_loc = time_loc + dur_tmp + self.interval_
        
        return wav_sum, sr, calib_list

        
# ---------------------------------------------------  main  ---------------------------------------------------- #

if __name__ == "__main__":
    alexa = PREPARE_DATA_ALEXA(r"E:\anaconda projects\x20_auto_record\dataset", r"E:\anaconda projects\x20_auto_record\dataset_play", 2)
    alexa.check()
    alexa.run()
