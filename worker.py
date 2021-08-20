#!/usr/bin/env python3
"""
This file contains the script that will be run on provider nodes executing our task.
It is included in the image built from this project's Dockerfile.
"""

import json
from pathlib import Path
from typing import List
from hashlib import sha256

import operator
import numpy as np
import matplotlib.pyplot as plt
from influxdb import InfluxDBClient
import pandas as pd
from sklearn.cluster import KMeans
from datetime import datetime
from matplotlib.colors import ListedColormap
from sklearn import neighbors, datasets

ENCODING = "utf-8"

HASH_PATH = Path("golem/input/hash.json")
WORDS_PATH = Path("golem/input/words.txt")
RESULT_PATH = Path("golem/output/result.json")

if __name__ == "__main__":
    result = ""

    ip_addr = "sensorweb.us"
    user_name = "test"
    user_pwd = "sensorweb"
    db_name = "waveform"

    client = InfluxDBClient(host=ip_addr, port=8086, username=user_name, password=user_pwd, database=db_name, ssl=True)

    tag_list = ["attack_01", "attack_07", "attack_08"]

    # influxdb query data command
    measurement = "sensor_04"
    field_key = "Ib"
    tag_key = "case"
    tag_value = "attack_05"
    start_time = "" 
    end_time = ""

    #query_command = 'SELECT * FROM "' + measurement + \
    #         '"'
    #for tag_value in tag_list:
    query_command = 'SELECT "'+ field_key + '"::field,"' + tag_key +'"::tag FROM "' + measurement + \
              '"'# WHERE ("'+ tag_key +'" = \''+tag_value+'\') '


    query_result = client.query(query_command)


    # points is a list of dictionary
    points = list(query_result.get_points())

    values =  map(operator.itemgetter(field_key), points)
    data1 = list(values)
    test =  map(operator.itemgetter(tag_key), points)
    labels = list(test)
    #print(np.unique(labels))
    #print(data.shape)

    if(len(data1) == 0):
      print("No data in the chosen time range!")
      quit()
    else:
      print("len:", len(data1))

    times  =  map(operator.itemgetter('time'),  points)
    time = list(times)
    time1=[]
    cases=[]
    for t in time:
        time1.append(str(t))
    for l in labels:
        cases.append(l)

    #print(time1[0:5])

    length = int(len(data1)) # print(np.unique(y))


    timet = []
    i=0
    while i < length:
          #print (t)
          if len(time[i])==27:
            temp = datetime.strptime(time[i], "%Y-%m-%dT%H:%M:%S.%fZ")
          elif len(time[i])==20:
            temp = datetime.strptime(time[i], "%Y-%m-%dT%H:%M:%SZ")
          timet.append(temp)
          i+=1


    datatemp={'time':[x for x in time1],
          'data':[d for d in data1],
          'case':[c for c in cases]}
    dataset=pd.DataFrame(datatemp,columns=['time','data','case'])
    fs = 20000 # for electric waveform data, 20KHz
    dataset.case = pd.Categorical(dataset.case)
    dataset['label'] = dataset.case.cat.codes
    #dataset.drop(['case'], axis=1)
    del dataset['case']

    #print(dataset[90000:90005])


    X=np.zeros((length,2),dtype=np.float64)

    y=[] #np.zeros((length,1),dtype=np.float64)

    i=0
    while i<length:
      X[i][0]= int(timet[i].timestamp())
      X[i][1]= dataset['data'][i]
      y.append(dataset['label'][i])
      i+=1

    del dataset

    # Specify the number of clusters and fit the data X
    #print(len(np.unique(y)))
    ks = KMeans(n_clusters=len(np.unique(y)), random_state=0)
    kmeans = ks.fit(X) #KMeans(n_clusters=2, random_state=0).fit(X)
    # Get the cluster centroids
    print("CLuster centers")
    print(ks.cluster_centers_)
    result = ks.cluster_centers_.tolist()

    # Plotting the cluster centers and the data points on a 2D plane
    plt.scatter(X[:, 0], X[:, -1])
        
    plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], c='red', marker='x')
        
    plt.title('Data points and cluster centroids')
    plt.show()
    for yi in range(2):
            plt.subplot(2, 1, 1 + yi)
            for xx in X[kmeans == yi]:
                plt.plot(xx.ravel(), "k-", alpha=.2)
            plt.plot(X, color='red')
            plt.plot(ks.cluster_centers_[yi].ravel(), "r-", color='green')
            #plt.xlim(0, sz)
            #plt.ylim(-4, 4)
            plt.title("Cluster %d" % (yi + 1))
    #a=[[-1.0, -4.6],[12.2, 80.0],[5.5,7.0]]
    #print([[1.0, 4.6]])
    #print("Predictions:")
    #kmeans.predict(a)

    with RESULT_PATH.open(mode="w", encoding=ENCODING) as f:
        json.dump(result, f)
