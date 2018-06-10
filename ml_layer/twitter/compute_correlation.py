import numpy as np
from scipy.stats.stats import pearsonr
import matplotlib.pyplot as plt

gip_data = np.loadtxt('gip.csv',delimiter=',')

x = gip_data[:,1]

y_low = gip_data[:,4]
y_high = gip_data[:,5]
y_open = gip_data[:,6]
y_close = gip_data[:,7]
y_volume = gip_data[:,8]

pr_low = pearsonr(x,y_low)
pr_high = pearsonr(x,y_high)
pr_open = pearsonr(x,y_open)
pr_close = pearsonr(x,y_close)
pr_volume = pearsonr(x,y_volume)

print(pr_low)
print(pr_high)
print(pr_open)
print(pr_close)
print(pr_volume)

plt.title('low')
plt.subplot(3,2,1).plot(x,y_low,color="blue")
plt.title('low')

plt.subplot(3,2,2).plot(x,y_high,color="blue")
plt.title('high')

plt.subplot(3,2,3).plot(x,y_open,color="blue")
plt.title('open')

plt.subplot(3,2,4).plot(x,y_close,color="blue")
plt.title('close')

plt.subplot(3,2,5).plot(x,y_volume,color="blue")
plt.title('volume')

plt.tight_layout()
plt.show()