#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from scipy.stats import probplot

from stats import d2, D3, D4
from stats import XMR

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()


# # Guess the Process, Moving Range Charts
# 
# One of the easiest ways to start monitor a process is a moving range chart, especially if you have no prior data or knowledge of a process. Besides that, many processes do not allow for grouping up results for samples, so single measurements are the natural way to track it. Moving range charts are also used in many complicated processes as one part of their process control. It is also an introduction to more complicated charting like EWMA, or feedback in engineering control.
# 
# Even though there are lots of software packages that can be used to do calculations for control charting, it is very straight forward to implement yourself. See this small repository I made with some code to create moving range charts. The repository also goes into some more details about the charting and the data.
# 
# The control limits for the $X$ chart are calculated as followed:
# $$ \overline{X} = \frac{\sum_{i=1}^n{x_i}}{n} $$
# $$ UCL = \overline{X} + 3 \frac{\overline{MR}}{d_2} $$
# $$ LCL = \overline{X} - 3 \frac{\overline{MR}}{d_2} $$
# 
# Here $x_i$ are the measurement values, $d_2=1.128$ is a statistical constant, the center line is given by $\overline{X}$, the upper control limit line has value $UCL$ and lower control limit line has value $LCL$. Below it shows how to calculate $\overline{MR}$ and the control limits for the $MR$ chart. 
# $$ \overline{MR} = \frac{\sum_{i=2}^n{MR_i}}{n-1} $$
# $$ MR_i=|x_i-x_{i-1}| $$
# $$ UCL = D_4 \overline{MR} $$
# $$ LCL = D_3 \overline{MR} $$
# 
# $D_3=0$, and $D_4=3.267$ are statistical constants.

# In[2]:


df = pd.read_csv('data.csv')
df['date'] = pd.to_datetime(df['date'], format='%d-%b-%y')


# In[3]:


xmr_A = XMR(df['A'].values, index=df['date'].values)
xmr_B = XMR(df['B'].values, index=df['date'].values)


# In[4]:


fig, axes = plt.subplots(nrows=2, ncols=2, sharex=True, sharey='row', tight_layout=True)
ax = axes.flatten()

xmr_A.xchart(ax[0])
xmr_A.mrchart(ax[2])
xmr_B.xchart(ax[1], color='orange')
xmr_B.mrchart(ax[3], color='orange')

ax[0].xaxis.set_major_locator(mdates.WeekdayLocator()) # major ticks every start of week
ax[0].xaxis.set_minor_locator(mdates.DayLocator()) # minor ticks every day
ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
plt.setp(ax[2].get_xticklabels(), rotation=45)
plt.setp(ax[3].get_xticklabels(), rotation=45)
ax[0].set_ylabel('X')
ax[2].set_ylabel('MR')
ax[0].set_title('A')
ax[1].set_title('B')

plt.show()


# The charts above are two control charts, named A and B, that follow the same process, with measurements done almost daily. I've set up the control charts next to each other and used the same ranges for the vertical and horizontal axes so it is easier to compare. Both charts behave the same, this is more clear by plotting them in the same figure.

# In[5]:


axes = df.plot(x='date', y='A', marker='o', )
df.plot(x='date', y='B', marker='o', ax=axes, color='orange')

axes.legend()
axes.xaxis.set_major_locator(mdates.WeekdayLocator()) # major ticks every start of week
axes.xaxis.set_minor_locator(mdates.DayLocator()) # minor ticks every day
axes.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
plt.setp(axes.get_xticklabels(), rotation=45)
axes.set_ylabel('X')

plt.show()


# At the moment the amount of data is still quite limited, so I won't discuss in or out of control conditions until I get to update the figures with some more data. 
# 
# Here is the main question though:
#  - What process do you think these charts are tracking?
# 
# Post your answer in the comment, or ask questions for hints.
# 
# Lastly, another way to use the moving range chart is to monitor the measurement system for consistency. In about 2 weeks I should have enough data to show the results for the measurement sysem used to monitor the process above.

# In[6]:


df.loc[1:, 'MR A'] = xmr_A.data_mr
df.loc[1:, 'MR B'] = xmr_B.data_mr

df


# Most standard control charting depend on the data being normally distributed. Even with this quite limited data set we can get a good idea with a quantile plot. 
# 
# To create the quantile plots for A and B above I used the scipy.stats packages. The probplot function by default compares it to quantiles from the standard normal distribution. If the data is has a normal distribution it should show up as a straight line. Both follow a straight line, so there doesn't seem to be any issue assuming normally distributed data at this moment. 
# 
# You can get an estimate for the average value from the point where the theoretical quantile is equal to 0. From the slope you can get an estimate of the standard deviation. You can compare these values with those calculated from the data directly.

# In[7]:


fig, axes = plt.subplots(nrows=1, ncols=2, sharey=True, tight_layout=True)
axes = axes.flatten()

probplot(df['A'], plot=axes[0])
axes[0].set_title('A')
probplot(df['B'], plot=axes[1])
axes[1].set_title('B')

df.describe()


# ## Difference Chart
# 
# measurements A and B are taken before and after the process. This shows the loss during the process is predictable and stable. 
# 
# An issue that does come up is the granularity of the measurements, there are only 5 different values for the values of A-B. This is a limitation of the mmeasurement system that only has a resolution of 0.2. Nevertheless there are at least 5 values between the limits on the range chart, so the granularity shouldn't be effecting the ability to get an estimate of the average range. For a detailed discussion see the chapter on Chunky Data in EMP III, by D. Wheeler.
# 
# Unfortunately I do not have the ability to increase the number of digits displayed on the measurement system to reduce the granularity. Neither would try to increase the difference between A and B work out. So that would mean investing in a better measurement system. 

# In[18]:


df['A-B'] = df['A'] - df['B']
xmr_diff = XMR(df['A-B'].values, index=df['date'].values)


# In[19]:


fig, axes = plt.subplots(nrows=2, ncols=1, sharex=True, tight_layout=True)
ax = axes.flatten()

xmr_diff.xchart(ax[0])
xmr_diff.mrchart(ax[1])

ax[0].xaxis.set_major_locator(mdates.WeekdayLocator()) # major ticks every start of week
ax[0].xaxis.set_minor_locator(mdates.DayLocator()) # minor ticks every day
ax[0].xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
plt.setp(ax[1].get_xticklabels(), rotation=45)
ax[0].set_ylabel('X')
ax[1].set_ylabel('MR')
ax[0].set_title('A - B')

plt.show()

