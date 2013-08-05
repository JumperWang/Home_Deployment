'''This script finds the total number of entries in a day for smart meter'''


import pandas as pd
import numpy as np
import MySQLdb
import pandas.io.sql as psql
mysql_conn=MySQLdb.connect(user='root',passwd='password',db='smart_meter');
import datetime
import time
import pytz
import time
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
start_date=datetime.datetime(2013,5,25,0,0,0,tzinfo=pytz.timezone('Asia/Kolkata'))
import matplotlib
matplotlib.rcParams.update({'font.size': 32})
v=[]
f=[]
num_days=61
stats={}
stats['X']=[]
stats['count']=[]
stats['electricity']=[]

hours=[None]*24
for i in range(24):
	hours[i]=0
	
prev=None
dur=[]
c=0
	
for i in range(num_days):
   	start=start_date+datetime.timedelta(i)
   	end=start_date+datetime.timedelta(i+1)
   	print "*"*80
   	print start
   	start_timestamp=int(time.mktime(start.timetuple()))
   	end_timestamp=int(time.mktime(end.timetuple()))
	query='select count(*) from smart_meter_data where timestamp between %d and %d;' %(start_timestamp,end_timestamp)
 	result=psql.frame_query(query,mysql_conn)
	stats['count'].append(result.values[0][0])
	stats['X'].append(start)
	query='select timestamp from smart_meter_data where timestamp between %d and %d;' %(start_timestamp,end_timestamp)
	result=psql.frame_query(query,mysql_conn)
	times=result.values.flatten()
	delta_times=np.diff(times)
	idx=delta_times>100
	fails=delta_times[delta_times>100]
	start_fail_times=times[idx]
	if times[0]-start_timestamp>100:
		'''Find if there was electricity failure from last night'''
		if prev is not None:
			#print prev
			#print datetime.datetime.fromtimestamp(prev)
			prev_day=datetime.datetime.fromtimestamp(prev).day
			prev_month=datetime.datetime.fromtimestamp(prev).month
			
			prev_datetime=datetime.datetime(2013,prev_month,prev_day,tzinfo=pytz.timezone('Asia/Kolkata'))
			if prev_datetime+datetime.timedelta(1)==start:
				'''Electricity failure started last night'''
				#print "Failure started last night at",datetime.datetime.fromtimestamp(prev),"ended at ",datetime.datetime.fromtimestamp(times[0])
				fails=np.insert(fails,0,times[0]-prev)
		
	if end_timestamp-times[-1]>600:
		prev=times[-1]
		start_fail_times=np.insert(start_fail_times,0,prev)
		print "Failure in night"
		query='select F,VLN from smart_meter_data where timestamp = %d;' %(prev)
		result=psql.frame_query(query,mysql_conn)
		print result
		if len(result['F'].flatten().values)>0:
			f.append(result['F'].flatten().values[0])
			v.append(result['VLN'].flatten().values[0])
		
	print start_fail_times
	
	c+=len(start_fail_times)
	#print datetime.datetime.fromtimestamp(start_fail_time)
	
		
print v
print f

plt.plot(v)
plt.show()
plt.plot(f)
plt.show()
plt.boxplot([f,v])
#plt.xticks('Frequency','Voltage')
plt.show()
'''	
print dur,np.mean(dur),len(dur)

plt.hist(dur,cumulative=False,bins=range(0,550,10))
plt.xlabel('Minutes')
plt.ylabel('# instances')
plt.title('Power outage duration distribution in minutes')
fig=plt.gcf()
fig.set_size_inches(16,9)	
plt.savefig('failure_durations.png',dpi=100,bbox_inches='tight')
'''
