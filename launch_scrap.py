import pandas as pd
import dateutil.parser as parser

from datetime import datetime , timedelta, date

FILENAME = 'launch.csv'
URL = 'https://en.wikipedia.org/wiki/2019_in_spaceflight#Orbital_launches'


def get_table(url):
    """
      Getting table as dataframe from the url input and output as df    
    """
    tables = pd.read_html(url)
    #for this page, we need table[3] for orbital launch
    df = tables[3] 
    df = df[3:]
    df.columns = ['Date and time (UTC)','Rocket','Flight number','1','Launch site','2','LS']
    
    return df

def isodateformat(dt):
    """
    Change input raw date into ISO format '2019-01-01T00:00:00+00:00'
    Output: ISO formatted date in UTC time zone +00:00 as per wiki for 2019 year
    """
    #remove those citations in date
    if '['in dt:
        id = dt.index('[')
        dt = dt[:id]
    d = dt.split()
    #print(d)
    cnt=0
    for x in d[1]:
        if x.isdigit():
            idx = d[1].index(x)
            cnt=1
            break
    #if no time then default to 00:00
    if cnt==0:
        idx=len(d[1])
        d[1]+='00:00'
    
    time = d[1][idx:]
    d[1] = d[1][:idx]
    d.insert(2,'2019')
    time = time.split(':')
    if len(time)!=3:
        time.append('00')
    
    #print(time)
    dat = ' '.join(d[:3])+'T'+':'.join(time)
    #print(date)
    
    dat = datetime.strptime(dat, '%d %B %YT%H:%M:%S')
    dat.isoformat()
    isodate = 'T'.join(str(dat).split(' '))+'+00:00'
    
    #returning isoformatted date as string
    
    return isodate

def generate_dict(unique_dates):
    """
    To generate dates in the year 2019 and assign values 0 default and if any launch then its value
    Input: Unique dates dict with (date,num_launches) pairs
    Output: Required dict with all 2019 days format
    """
    from datetime import date, timedelta

    sdate = date(2019, 1, 1)   # start date
    edate = date(2019, 12, 31)   # end date


    delta = edate - sdate       # as timedelta

    required_dict = {}
    
    for i in range(delta.days + 1):
        day = str(sdate + timedelta(days=i)).split(' ')[0]
        if day in unique_dates.keys():
            required_dict[day+'T00:00:00+00:00'] = unique_dates[day]
        else:
            required_dict[day+'T00:00:00+00:00'] = 0
            
    return required_dict

if __name__ == '__main__':
    
    #link for scrapping as above 
    url = URL
    
    #to table
    df = get_table(url)
    
    #cleaning data - remove garbage values
    indextoremove = df[df['Date and time (UTC)'].str.startswith('←')].index
    df.drop(indextoremove,inplace=True)
    
    #apply the function to all dates
    df['Date and time (UTC)'] = df['Date and time (UTC)'].apply(lambda dt : isodateformat(dt))
    df = df.reset_index(drop=True)
    
    #get unique dates from the table
    unique_dates = df['Date and time (UTC)'].unique().tolist()
    
    #get corresponding values of Launch status
    new_df = {}
    for date in unique_dates:
        new_df[date] = df.loc[df['Date and time (UTC)'] == date]['LS'].tolist()
    
    #get those successful dates 
    successdates = []
    for k,v in new_df.items():
        if 'Successful' in v or 'Operational' in v or 'En Route' in v: 
            successdates.append(k)
            
    #successdates gives all dates in ISO format that are successful
    
    unique_dates = {}
    for dt in successdates:
        date = dt.split('T')[0]
        if date not in unique_dates:
            unique_dates[date]=1
        else:
            unique_dates[date]+=1
            
    #unique dates has frequency for each date without iso format
    #print(unique_dates)
    
    #req_dict with required format with all dates of 2019
    req_dict = generate_dict(unique_dates)
    
    data = pd.DataFrame.from_dict(req_dict, orient='index',columns = None)
    #save as filename
    data.to_csv(FILENAME, header=False)