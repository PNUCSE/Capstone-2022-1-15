import numpy as np
from tensorflow.keras.models import Sequential, model_from_json
from tensorflow.keras import backend as K
from tensorflow.keras import models
import datetime

class Inference():
    def __init__(self, model_json, model_weight):

        model_graph = open(model_json, 'r')
        model_loaded = model_graph.read()
        model_graph.close()

        model = model_from_json(model_loaded)
        model.load_weights(model_weight)
        model.compile(loss = self.euc_dist_keras, optimizer = 'adam')
        self.model = model


    def preprocess_skeletons(self, keypoints):
        for i in range(len(keypoints)):
            if np.isnan(keypoints[i]):
                keypoints[i] = 0


    def replace_missing_values(self,skeletons):
        def put_mid(arr):
            i = 0
            while (i < len(arr) and arr[i] == 0):
                i += 1
            if (i >= len(arr)):
                return
            for k in range(i):
                arr[k] = arr[i]

            while (i < len(arr)):
                if (arr[i] == 0):
                    left = i - 1
                    while (arr[i] == 0):
                        i += 1
                        if (i >= len(arr)):
                            for k in range(left, i):
                                arr[k] = arr[left]
                            break
                    if (i >= len(arr)):
                        break
                    for k in range(left + 1, i):
                        arr[k] = (arr[k - 1] + arr[i]) / 2

                if (i >= len(arr)):
                    break
                i += 1

        x_values = []
        y_values = []
        for i in range(15):
            x_values.append([])
            y_values.append([])

        for skeleton in skeletons:
            self.preprocess_skeletons(skeleton)
            for i in range(15):
                x_values[i].append(skeleton[i*2])
                y_values[i].append(skeleton[i*2+1])

        for i in range(15):
            put_mid(x_values[i])
            put_mid(y_values[i])

        for i in range(len(skeletons)):
            for j in range(15):
                skeletons[i][j*2] = x_values[j][i]
                skeletons[i][j*2+1] = y_values[j][i]


    def make3D(self,skeletons):
        skeleton_3d = []

        self.replace_missing_values(skeletons)

        for key_points in skeletons:
            model = self.model
            key2d=[]

            for i in range(0,len(key_points),2):
                key2d.append((key_points[i],key_points[i+1]))
            key_points = key2d
            x_std, y_std = [], []
            key_points = np.array(key_points)
            x1 = key_points[..., 0]
            y1 = key_points[..., 1]

            try:
                x = [x1[8], x1[1], x1[0],
                     x1[2], x1[3], x1[4],
                     x1[5], x1[6], x1[7],
                     x1[9], x1[10], x1[11],
                     x1[12], x1[13], x1[14]]

                y = [y1[8], y1[1], y1[0],
                     y1[2], y1[3], y1[4],
                     y1[5], y1[6], y1[7],
                     y1[9], y1[10], y1[11],
                     y1[12], y1[13], y1[14]]

                xm = np.mean(x)
                ym = np.mean(y)
                sigma_x = np.std(x)
                sigma_y = np.std(y)

                for l in range(len(key_points)):
                    xs = (x[l] - xm) / ((sigma_x + sigma_y) / 2)
                    ys = (y[l] - ym) / ((sigma_x + sigma_y) / 2)
                    x_std.append(xs)
                    y_std.append(ys)

                inpt = np.concatenate((x_std, y_std))
                inpt = inpt.reshape(1, len(inpt))
                # print("start_predict")
                output = model.predict(inpt)

                # print("end_predicts")
                # print(output)
                z = output[0]
                """
                inpt_=np.append(inpt_,inpt,axis=0)
                if num > 2:
                    # print("inpt_")
                    # print(inpt_)
                    output = model.predict(inpt_)
                    # print(output)
                    # return
                    z = output[0]
                continue
                """
                for k in range(len(z)):
                    z[k] = abs((z[k] * ((sigma_x + sigma_y) / 2)))

                key_points_3d = []

                for i in range(9):
                    key_points_3d.append([x[i], y[i], z[i]])

                skeleton_3d.append(key_points_3d)

            except Exception as e:
                print("except: ", e)
                continue

        return skeleton_3d


    def euc_dist_keras(self, y_true, y_pred):
        return K.sqrt(K.sum(K.square(y_true - y_pred), axis=-1, keepdims=True))

