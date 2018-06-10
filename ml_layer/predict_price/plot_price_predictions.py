import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# preds = np.loadtxt('predictions.csv',delimiter=',')
df = pd.read_csv('predictions_till_16_midnight.csv', sep=',', header=0)
preds = df.as_matrix()[:,1:]

plt.title('low')
plt.subplot(3,2,1).plot(preds[:,0],color="blue")
plt.title('low')

plt.subplot(3,2,2).plot(preds[:,1],color="blue")
plt.title('high')

plt.subplot(3,2,3).plot(preds[:,2],color="blue")
plt.title('open')

plt.subplot(3,2,4).plot(preds[:,3],color="blue")
plt.title('close')

plt.subplot(3,2,5).plot(preds[:,4],color="blue")
plt.title('volume')

plt.subplot(3,2,6).plot(preds[:,5],color="blue")
plt.title('market cap')

plt.tight_layout()
plt.show()