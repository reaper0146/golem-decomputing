#!/usr/bin/env python3
"""
This file contains the script that will be run on provider nodes executing our task.
It is included in the image built from this project's Dockerfile.
"""

import json
from hashlib import sha256
from pathlib import Path
from typing import List

import pandas as pd
import numpy as np
import pywt
import matplotlib.pyplot as plt

ENCODING = "utf-8"

#HASH_PATH = Path("golem/input/hash.json")
WORDS_PATH = Path("golem/input/SCG_data.csv")
RESULT_PATH = Path("golem/output/result.json")

def wdenoise(data, method, threshold):
    # Create wavelet object and define parameters
    w = pywt.Wavelet(method)
    maxlev = pywt.dwt_max_level(len(data), w.dec_len)
    # maxlev = 2 # Override if desired
    print("maximum level is " + str(maxlev))
    # Decompose into wavelet components, to the level selected:
    coeffs = pywt.wavedec(data, method, level=maxlev)  
    #cA = 0.0
    #cA = pywt.threshold(cA, threshold*max(cA))
    # plt.figure()
    for i in range(1, len(coeffs)):
        # plt.subplot(maxlev, 1, i)
        # plt.plot(coeffs[i])
        coeffs[i] = pywt.threshold(coeffs[i], threshold*max(coeffs[i]))
        # plt.plot(coeffs[i])
    datarec = pywt.waverec(coeffs, method)
    return datarec

if __name__ == "__main__":
    result = ""

    ## example data importing
    data = pd.read_csv(WORDS_PATH).drop('Unnamed: 0',1).to_numpy()[0:20,:1000]
    data_rec = wdenoise(data[10,:], 'sym4',0.5)
    result = data_rec.tolist()
    print(type(data_rec))


    with open(RESULT_PATH, mode="w", encoding=ENCODING) as f:
        json.dump(result, f)
