#!/usr/bin/env python
# coding: utf-8

# In[133]:


from googleapiclient.discovery import build
import pandas as pd
import seaborn as sns


# In[10]:


api_key ='AIzaSyB5aO88Yqmt9ivS27yHOPCDgaR4GoHCFCw'
channel_ids = ['UCnz-ZXXER4jOvuED5trXfEA',
              'UCLLw7jmFsvfIVaUFsLs8mlQ', #luke Barouse
              'UCiT9RITQ9PW6BhXK0y2jaeg', #ken Jee
              'UC7cs8q-gJRlGwj4A8OmCmXg', #Alex the analyst
              'UC2UXDak6o7rBm23k3Vv5dww' #Tina Huang
             ]


youtube = build('youtube','v3',developerKey = api_key)


# # function to get channel statistics

# In[58]:


def get_channel_stats(youtube, channel_ids):
    all_data = []
    request = youtube.channels().list(
            part ='snippet,contentDetails,statistics',
            id = ','.join(channel_ids))
    response = request.execute()
    
    for i in range (len(response['items'])):
        data = dict(Channel_name = response['items'][i]['snippet'] ['title'],
                    Subscriber = response['items'][i]['statistics'] ['subscriberCount'],
                    Views = response['items'][i]['statistics'] ['viewCount'],
                    Total_videos = response['items'][i]['statistics'] ['videoCount'],
                    playlist_id = response['items'][i]['contentDetails']['relatedPlaylists']['uploads']
                    )
        all_data.append(data)
    return all_data


# In[59]:


channel_stats =  get_channel_stats(youtube, channel_ids)


# **Load the data using pandas library** 

# In[60]:


channel_data = pd.DataFrame(channel_stats)


# In[61]:


channel_data


# In[62]:


channel_data.dtypes


# In[63]:


channel_data['Subscriber'] = pd.to_numeric(channel_data['Subscriber'])
channel_data['Views'] = pd.to_numeric(channel_data['Views'])
channel_data['Total_videos'] = pd.to_numeric(channel_data['Total_videos'])
channel_data.dtypes


# **using seaborn library i will analyze the data**

# In[40]:


sns.set(rc={'figure.figsize':(10,9)})
ax= sns.barplot(x='Channel_name',y='Subscriber',data = channel_data)


# In[41]:


ax= sns.barplot(x='Channel_name',y='Views',data = channel_data)


# In[42]:


ax= sns.barplot(x='Channel_name',y='Total_videos',data = channel_data)


# ## Function to get video ids

# In[67]:


channel_data


# In[187]:


playlist_id  = channel_data.loc[channel_data['Channel_name'] == 'techTFQ','playlist_id'].iloc[0]


# In[188]:


playlist_id


# In[189]:


def get_video_ids(youtube,playlist_id):
    request = youtube.playlistItems().list(
               part = 'contentDetails',
               playlistId = playlist_id,
               maxResults = 50)
    response = request.execute()
    
    video_ids=[]
    for i in range(len(response['items'])):
        video_ids.append(response['items'][i]["contentDetails"]["videoId"])
        
    next_page_token = response.get("nextPageToken")
    more_pages = True
    
    while more_pages:
        if next_page_token is None:
            more_pages = False
        else:
            request = youtube.playlistItems().list(
               part = 'contentDetails',
               playlistId = playlist_id,
               maxResults = 50,
               pageToken = next_page_token )
            response = request.execute()
            
            for i in range(len(response['items'])):
                video_ids.append(response['items'][0]["contentDetails"]["videoId"])

            next_page_token = response.get('nextPageToken')
                
    return video_ids


# In[190]:


video_ids = get_video_ids(youtube, playlist_id)


# In[191]:


video_ids


# ## Function to get video details

# In[192]:


def get_video_details(youtube, video_ids):
    all_video_stats = []
    for i in range(0,len(video_ids),50):

        request = youtube.videos().list(
                part = 'snippet,contentDetails,statistics',
                id = ','.join(video_ids[i:i+50]))
        response = request.execute() 

        for video in response['items']:
            video_stats = dict(Title = video['snippet']['title'],
                               Published_date = video['snippet']["publishedAt"],
                               Views = video["statistics"]['viewCount'],
                               likes=  video["statistics"]["likeCount"],
                               comments = video["statistics"]['commentCount']
                               )
            all_video_stats.append(video_stats)

    return all_video_stats


# In[193]:


video_details = get_video_details(youtube, video_ids)


# In[194]:


video_data = pd.DataFrame(video_details)
video_data


# In[195]:


video_data['Published_date'] = pd.to_datetime(video_data['Published_date']).dt.date
video_data['Views'] =pd.to_numeric(video_data['Views'])
video_data['likes'] =pd.to_numeric(video_data['likes'])
video_data['comments'] =pd.to_numeric(video_data['comments'])
video_data


# In[196]:


top10_video = video_data.sort_values(by='Views',ascending = False).head(10)


# In[197]:


top10_video


# In[198]:


ax1= sns.barplot(x='Views', y='Title', data=top10_video)


# In[200]:


video_data['Month'] =pd.to_datetime(video_data['Published_date']).dt.strftime('%b')


# In[201]:


video_data


# In[223]:


videos_per_month = video_data.groupby('Month',as_index=False).size()


# In[224]:


videos_per_month


# In[225]:


sort_order =["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


# In[226]:


videos_per_month.index = pd.CategoricalIndex(videos_per_month['Month'], categories= sort_order, ordered = True)


# In[227]:


videos_per_month = videos_per_month.sort_index()


# In[228]:


ax2 = sns.barplot(x='Month',y='size', data = videos_per_month)


# In[ ]:




