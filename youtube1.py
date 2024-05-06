from googleapiclient.discovery import build
import pymongo
import psycopg2
import pandas as pd
import streamlit as st

#API Key Connection

def Api_connect():
    Api_Id= "AIzaSyD4DxclgbUCxTlbvpka94GK4meTKSUduDY"

    api_service_name= "youtube"
    api_version="v3"

    youtube=build(api_service_name,api_version,developerKey=Api_Id)

    return youtube

youtube=Api_connect()


#get channel information

def get_channel_info(channel_id):
    request=youtube.channels().list(
                    part= "snippet,ContentDetails,statistics",
                    id=channel_id
    )
    response=request.execute()
    print("Response from YouTube API:", response)  # Add this line to print the response


    for i in response.get['items',[]]:
        data=dict(Channel_Name=i["snippet"]["title"],
                Channel_id=i["id"],
                Subscribers=i['statistics']['subscriberCount'],
                Views=i["statistics"]["viewCount"],
                Total_Videos=i["statistics"]["videoCount"],
                Channel_Description=i["snippet"]["description"],
                Playlist_Id=i["contentDetails"]["relatedPlaylists"]["uploads"])
    return data
def channel_details(channel_id, coll1):
    ch_details = get_channel_info(channel_id, coll1)


#get video ids

def get_videos_ids(channel_id):
    video_ids=[]
    response=youtube.channels().list(id=channel_id,part='contentDetails').execute()

    Playlist_Id=response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    next_page_token=None

    while True:
        response1=youtube.playlistItems().list(part='snippet',playlistId=Playlist_Id,maxResults=50,pageToken=next_page_token).execute()
        for i in range(len(response1['items'])):
            video_ids.append(response1['items'][i]['snippet']['resourceId']['videoId'])
        next_page_token=response1.get('nextPageToken')  # Corrected accessing 'nextPageToken' using .get() method

        if next_page_token is None:
            break
    return video_ids

#Video_Ids = get_videos_ids("UChGd9JY4yMegY6PxqpBjpRA")


#get video information

def get_video_info(video_ids):
    video_data=[]
    for video_id in video_ids:
        request=youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_id
        )
        response=request.execute()

        for item in response["items"]:
            data=dict(Channel_Name=item['snippet']['channelTitle'],
                    Channel_Id=item['snippet']['channelId'],
                    Video_Id=item['id'],
                    Title=item['snippet']['title'],
                    Tags=item['snippet'].get('tags'),
                    Thumbnail=item['snippet']['thumbnails']['default']['url'],
                    Description=item['snippet'].get('description'),
                    Published_Date=item['snippet']['publishedAt'],
                    Duration=item['contentDetails']['duration'],
                    Views=item['statistics'].get('viewCount') ,
                    Likes=item['statistics'].get('likeCount'),
                    Comments=item['statistics'].get('commentCount'),
                    Favorite_Count=item['statistics']['favoriteCount'],
                    Definition=item['contentDetails']['definition'],
                    Caption_Status=item['contentDetails']['caption']
                    )
            video_data.append(data)
    return video_data    


#get comment information

def get_comment_info(video_ids):
    Comment_data=[]
    try:
        for video_id in video_ids:
            request=youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=50
            )
            response=request.execute()

            for item in response['items']:
                data=dict(Comment_Id=item['snippet']['topLevelComment']['id'],
                        Video_Id=item['snippet']['topLevelComment']['snippet']['videoId'],
                        Comment_Text=item['snippet']['topLevelComment']['snippet']['textDisplay'],
                        Comment_Author=item['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                        Comment_Published=item['snippet']['topLevelComment']['snippet']['publishedAt'])
                
                Comment_data.append(data)

    except:
        pass
    return Comment_data

#get_playlist_details

def get_playlist_details(channel_id):
        next_page_token=None
        All_data=[]
        while True:
                request=youtube.playlists().list(
                        part='snippet,contentDetails',
                        channelId=channel_id,
                        maxResults=50,
                        pageToken=next_page_token
                )
                response=request.execute()

                for item in response['items']:
                        data=dict(Playlist_Id=item['id'],
                                Title=item['snippet']['title'],
                                Channel_Id=item['snippet']['channelId'],
                                Channel_Name=item['snippet']['channelTitle'],
                                PublishedAt=item['snippet']['publishedAt'],
                                Video_count=item['contentDetails']['itemCount'])
                        All_data.append(data)

                next_page_token=response.get('nextPagetoken')
                if next_page_token is None:
                        break
        return All_data
        
        

#upload to mongoDB

client=pymongo.MongoClient("mongodb+srv://achantatejanjani14:Tejanjani1406@tejanjani.xiyuhwu.mongodb.net/?retryWrites=true&w=majority&appName=Tejanjani")
db=client["Youtube_data"]

def channel_details(channel_id):
    ch_details=get_channel_info(channel_id)
    pl_details=get_playlist_details(channel_id)
    vi_ids=get_videos_ids(channel_id)
    vi_details=get_video_info(vi_ids)
    com_details=get_comment_info(vi_ids)

    coll1=db["channel_details"]
    coll1.insert_one({"channel_information":ch_details,"Playlist_information":pl_details,
                      "video_information":vi_details,"comment_information":com_details})
    
    return "upload completed successfully"


#Table creation for channels,playlists,videos,comments

def channels_table(channel_name_s): 
    mydb=psycopg2.connect(host="localhost",
                        user="postgres",
                        password="123456",
                        database="youtube_data",
                        port="5432")
    cursor=mydb.cursor()

    #drop_query='''drop table if exists channels'''
    #cursor.execute(drop_query)
    #mydb.commit()

    try:
        create_query='''create table if not exists channels(Channel_Name varchar(100),
                                                            Channel_Id varchar(80) primary key,
                                                            Subscribers bigint,
                                                            Views bigint,
                                                            Total_Videos int,
                                                            Channel_Description text,
                                                            Playlist_Id varchar(80))'''
        cursor.execute(create_query)
        mydb.commit()

    except:
        print("Channel table already created")
    
    #fetching all datas
    query_1="SELECT * FROM channels"
    cursor.execute(query_1)
    table=cursor.fetchall()
    mydb.commit()

    chann_list=[]
    chann_list2=[]
    df_all_channels=pd.DataFrame(table)

    chann_list.append(df_all_channels[0])
    for i in chann_list[0]:
        chann_list2.append(i)
    
    if channel_name_s in chann_list2:
        news= f"Your Provided channel {channel_name_s} is already exists"
        return news
    
    else:
        single_channel_details=[]
        coll1=db["channel_details"]
        for ch_data in coll1.find({"channel_information.Channel_Name":channel_name_s},{"_id":0}):
            single_channel_details.append(ch_data["channel_information"])
        
        df_single_channel=pd.DataFrame(single_channel_details)

    for index,row in df_single_channel.iterrows():
        insert_query='''insert into channels(Channel_Name,Channel_id,Subscribers,Views,Total_Videos,Channel_Description,Playlist_Id)
                                            values(%s,%s,%s,%s,%s,%s,%s)'''
        values=(row['Channel_Name'],
                row['Channel_id'],
                row['Subscribers'],
                row['Views'],
                row['Total_Videos'],
                row['Channel_Description'],
                row['Playlist_Id'])
        
        try:
            cursor.execute(insert_query,values)
            mydb.commit()

        except:
            print("channel values are already inserted")



def playlist_table(channel_name_s):
    mydb=psycopg2.connect(host="localhost",
                        user="postgres",
                        password="123456",
                        database="youtube_data",
                        port="5432")
    cursor=mydb.cursor()

    #drop_query='''drop table if exists playlists'''
    #cursor.execute(drop_query)
    #mydb.commit()

    create_query='''create table if not exists playlists(Playlist_Id varchar(100) primary key,
                                                        Title varchar(100),
                                                        Channel_Id varchar(100),
                                                        Channel_Name varchar(100),
                                                        PublishedAt timestamp,
                                                        Video_Count int
                                                        )'''

    cursor.execute(create_query)
    mydb.commit()

    single_channel_details= []
    coll1=db["channel_details"]
    for ch_data in coll1.find({"channel_information.Channel_Name":channel_name_s},{"_id":0}):
        single_channel_details.append(ch_data["Playlist_information"])

    df_single_channel= pd.DataFrame(single_channel_details[0])

    #pl_list=[]
    #db=client["Youtube_data"]
    #coll1=db["channel_details"]
    #for pl_data in coll1.find({},{"_id":0,"Playlist_information":1}):
       # for i in range(len(pl_data["Playlist_information"])):
           # pl_list.append(pl_data["Playlist_information"][i])
    #df1=pd.DataFrame(pl_list)

    for index,row in df_single_channel.iterrows():
        insert_query='''insert into playlists(Playlist_Id,Title,Channel_Id,Channel_Name,PublishedAt,Video_count)values(%s,%s,%s,%s,%s,%s)'''
        values=(row['Playlist_Id'],
            row['Title'],
            row['Channel_Id'],
            row['Channel_Name'],
            row['PublishedAt'],
            row['Video_count'])

    cursor.execute(insert_query,values)
    mydb.commit()


def videos_table(channel_name_s):

    mydb=psycopg2.connect(host="localhost",
                        user="postgres",
                        password="123456",
                        database="youtube_data",
                        port="5432")
    cursor=mydb.cursor()

    #drop_query='''drop table if exists videos'''
    #cursor.execute(drop_query)
    #mydb.commit()

    create_query='''create table if not exists videos(Channel_Name varchar(100),
                                                    Channel_Id varchar(100),
                                                    Video_Id varchar(30) primary key,
                                                    Title varchar(150),
                                                    Tags text,
                                                    Thumbnail varchar(200),
                                                    Description text,
                                                    Published_Date timestamp,
                                                    Duration interval,
                                                    Views bigint ,
                                                    Likes bigint,
                                                    Comments int,
                                                    Favorite_Count int,
                                                    Definition varchar(10),
                                                    Caption_Status varchar(50))'''

    cursor.execute(create_query)
    mydb.commit()

    single_channel_details= []
    coll1=db["channel_details"]
    for ch_data in coll1.find({"channel_information.Channel_Name":channel_name_s},{"_id":0}):
        single_channel_details.append(ch_data["video_information"])

    df_single_channel= pd.DataFrame(single_channel_details[0])


    #vi_list=[]
    #db=client["Youtube_data"]
    #coll1=db["channel_details"]
    #for vi_data in coll1.find({},{"_id":0,"video_information":1}):
        #for i in range(len(vi_data["video_information"])):
            #vi_list.append(vi_data["video_information"][i])
    #df2=pd.DataFrame(vi_list)


    for index,row in df_single_channel.iterrows():
            insert_query='''insert into videos(Channel_Name,
                                            Channel_Id,
                                            Video_Id,
                                            Title,
                                            Tags,
                                            Thumbnail,
                                            Description,
                                            Published_Date,
                                            Duration,
                                            Views,
                                            Likes,
                                            Comments,
                                            Favorite_Count,
                                            Definition,
                                            Caption_Status)values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
            
            values=(row['Channel_Name'],
                row['Channel_Id'],
                row['Video_Id'],
                row['Title'],
                row['Tags'],
                row['Thumbnail'],
                row['Description'],
                row['Published_Date'],
                row['Duration'],
                row['Views'],
                row['Likes'],
                row['Comments'],
                row['Favorite_Count'],
                row['Definition'],
                row['Caption_Status'])

            cursor.execute(insert_query,values)
            mydb.commit()

def comments_table(channel_name_s):
    mydb=psycopg2.connect(host="localhost",
                        user="postgres",
                        password="123456",
                        database="youtube_data",
                        port="5432")
    cursor=mydb.cursor()

    #drop_query='''drop table if exists comments'''
    #cursor.execute(drop_query)
    #mydb.commit()

    create_query='''create table if not exists comments(Comment_Id varchar(100) primary key,
                                                        Video_Id varchar(50),
                                                        Comment_Text text,
                                                        Comment_Author varchar(150),
                                                        Comment_Published timestamp)'''

    cursor.execute(create_query)
    mydb.commit()

    single_channel_details= []
    coll1=db["channel_details"]
    for ch_data in coll1.find({"channel_information.Channel_Name":channel_name_s},{"_id":0}):
        single_channel_details.append(ch_data["comment_information"])

    df_single_channel= pd.DataFrame(single_channel_details[0])


    #com_list=[]
    #db=client["Youtube_data"]
    #coll1=db["channel_details"]
    #for com_data in coll1.find({},{"_id":0,"comment_information":1}):
     #   for i in range(len(com_data["comment_information"])):
    #        com_list.append(com_data["comment_information"][i])
    #df3=pd.DataFrame(com_list)

    for index,row in df_single_channel.iterrows():
            insert_query='''insert into comments(Comment_Id,
                                            Video_Id,
                                            Comment_Text,
                                            Comment_Author,
                                            Comment_Published
                                            )
                                            values(%s,%s,%s,%s,%s)'''

            values=(row['Comment_Id'],
                row['Video_Id'],
                row['Comment_Text'],
                row['Comment_Author'],
                row['Comment_Published'])
        
            cursor.execute(insert_query,values)
            mydb.commit()


def tables(channel_name):

    news= channels_table(channel_name)
    if news:
        st.write(news)
    else:
        playlist_table(channel_name)
        videos_table(channel_name)
        comments_table(channel_name)

    return "Tables Created Successfully"

def show_channels_table():
    ch_list=[]
    db=client["Youtube_data"]
    coll1=db["channel_details"]
    for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
        ch_list.append(ch_data["channel_information"])
    df=st.dataframe(ch_list)

    return df

def show_playlists_table():
    pl_list=[]
    db=client["Youtube_data"]
    coll1=db["channel_details"]
    for pl_data in coll1.find({},{"_id":0,"Playlist_information":1}):
        for i in range(len(pl_data["Playlist_information"])):
            pl_list.append(pl_data["Playlist_information"][i])
    df1=st.dataframe(pl_list)

    return df1

def show_videos_table():
    vi_list=[]
    db=client["Youtube_data"]
    coll1=db["channel_details"]
    for vi_data in coll1.find({},{"_id":0,"video_information":1}):
        for i in range(len(vi_data["video_information"])):
            vi_list.append(vi_data["video_information"][i])
    df2=st.dataframe(vi_list)

    return df2

def show_comments_table():
    com_list=[]
    db=client["Youtube_data"]
    coll1=db["channel_details"]
    for com_data in coll1.find({},{"_id":0,"comment_information":1}):
        for i in range(len(com_data["comment_information"])):
            com_list.append(com_data["comment_information"][i])
    df3=st.dataframe(com_list)

    return df3

#Streamlit 

import streamlit as st
import pandas as pd
import psycopg2

# Define functions and SQL connection

# Function to execute SQL query and fetch top 10 rows
def fetch_top_10(query):
    cursor.execute(query)
    data = cursor.fetchall()
    df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
    st.write(df.head(10))

# SQL connection
mydb = psycopg2.connect(host="localhost",
                        user="postgres",
                        password="123456",
                        database="youtube_data",
                        port="5432")
cursor = mydb.cursor()

# Define all_channels variable
all_channels = []

# Page 1: Data Collection
def page_data_collection():
    st.title("YouTube Data Harvesting and Warehousing")

    st.write("""
    Welcome to YouTube Data Harvesting and Warehousing! This Streamlit application allows you to easily access and analyze data from multiple YouTube channels. Retrieve channel details, video information, and more using the YouTube API. Store data for up to 10 channels in a MySQL or PostgreSQL database with just a click. Seamlessly search and retrieve data from the database, including advanced options like joining tables for comprehensive channel details.
    """)

    channel_id = st.text_input("Enter the channel ID")
    ch_ids=[]

    if st.button("Collect and Store Data"):
        db=client["Youtube_data"]
        coll1=db["channel_details"]
        for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
            ch_ids.append(ch_data["channel_information"]["Channel_id"])

        if channel_id in ch_ids:
            st.warning("Channel Details of the given channel id already exist.")
            # Display channel information similar to a document
            channel_data = coll1.find_one({"channel_information.Channel_id": channel_id})
            st.write("Channel Name:", channel_data["channel_information"]["Channel_Name"])
            st.write("Channel ID:", channel_data["channel_information"]["Channel_id"])
            st.write("Subscribers:", channel_data["channel_information"]["Subscribers"])
            st.write("Views:", channel_data["channel_information"]["Views"])
            st.write("Total Videos:", channel_data["channel_information"]["Total_Videos"])
            st.write("Channel Description:", channel_data["channel_information"]["Channel_Description"])
            st.write("Playlist ID:", channel_data["channel_information"]["Playlist_Id"])
        else:
            insert=channel_details(channel_id)
            st.success(insert)
            # Display channel information similar to a document
            channel_data = coll1.find_one({"channel_information.Channel_id": channel_id})
            st.write("Channel Name:", channel_data["channel_information"]["Channel_Name"])
            st.write("Channel ID:", channel_data["channel_information"]["Channel_id"])
            st.write("Subscribers:", channel_data["channel_information"]["Subscribers"])
            st.write("Views:", channel_data["channel_information"]["Views"])
            st.write("Total Videos:", channel_data["channel_information"]["Total_Videos"])
            st.write("Channel Description:", channel_data["channel_information"]["Channel_Description"])
            st.write("Playlist ID:", channel_data["channel_information"]["Playlist_Id"])

# Page 2: Display Relevant Details
def page_display_details():
    st.title("Display Relevant Details")

    show_table = st.radio("Select the table for view", ("Channels", "Playlists", "Videos", "Comments"))

    if show_table == "Channels":
        query = "SELECT * FROM channels"
        fetch_top_10(query)
    elif show_table == "Playlists":
        query = "SELECT * FROM playlists"
        fetch_top_10(query)
    elif show_table == "Videos":
        query = "SELECT * FROM videos"
        fetch_top_10(query)
    elif show_table == "Comments":
        query = "SELECT * FROM comments"
        fetch_top_10(query)

# Page 3: Select and Display Data
def page_select_display_data():
    st.title("Select and Display Data")

    question = st.selectbox("Select your Question", ("1. What are the names of all the videos and their corresponding channels",
                                                     "2. Channel with most number of videos",
                                                     "3. 10 most viewed videos",
                                                     "4. How many comments were made on each video, and what are their corresponding video names?",
                                                     "5. Videos with highest likes",
                                                     "6. Likes of all videos",
                                                     "7. Views of each channel",
                                                     "8. Videos Published in the Year of 2022",
                                                     "9. Average Duration of all videos in each channel",
                                                     "10. Videos with highest number of comments"))
    if question == "1. What are the names of all the videos and their corresponding channels":
        query = '''SELECT title AS "video title", channel_name AS "channel name" FROM videos'''
        fetch_top_10(query)

    elif question == "2. Channel with most number of videos":
        query = '''SELECT channel_name AS "channel name", total_videos AS "No of videos" 
                    FROM channels ORDER BY total_videos DESC'''
        fetch_top_10(query)

    elif question == "3. 10 most viewed videos":
        query = '''SELECT views AS views, channel_name AS "channel name", title AS "video title" 
                    FROM videos WHERE views IS NOT NULL ORDER BY views DESC'''
        fetch_top_10(query)

    elif question == "4. How many comments were made on each video, and what are their corresponding video names?":
        query = '''SELECT comments AS "no of comments", title AS "video title" 
                    FROM videos WHERE comments IS NOT NULL'''
        fetch_top_10(query)

    elif question == "5. Videos with highest likes":
        query = '''SELECT title AS "video title", channel_name AS "channel name", likes AS "like count"
                    FROM videos WHERE likes IS NOT NULL ORDER BY likes DESC'''
        fetch_top_10(query)

    elif question == "6. Likes of all videos":
        query = '''SELECT likes AS "like count", title AS "video title" FROM videos'''
        fetch_top_10(query)

    elif question == "7. Views of each channel":
        query = '''SELECT channel_name AS "channel name", views AS "total views" FROM channels'''
        fetch_top_10(query)

    elif question == "8. Videos Published in the Year of 2022":
        query = '''SELECT title AS "video title", published_date AS "published date", channel_name AS "channel name" 
                    FROM videos WHERE EXTRACT(YEAR FROM published_date) = 2022'''
        fetch_top_10(query)

    elif question == "9. Average Duration of all videos in each channel":
        query = '''SELECT channel_name AS "channel name", AVG(duration) AS "average duration" 
                    FROM videos GROUP BY channel_name'''
        cursor.execute(query)
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=[desc[0] for desc in cursor.description])
        st.write(df.head(10))

    elif question == "10. Videos with highest number of comments":
        query = '''SELECT title AS "video title", channel_name AS "channel name", comments AS "comments"
                    FROM videos WHERE comments IS NOT NULL ORDER BY comments DESC'''
        fetch_top_10(query)
 
# Page 4: Migration to SQL
def page_migration_to_sql():
    st.title("Migration to SQL")
    all_channels= []
    coll1=db["channel_details"]
    for ch_data in coll1.find({},{"_id":0,"channel_information":1}):
        all_channels.append(ch_data["channel_information"]["Channel_Name"])
        
        
    unique_channel= st.selectbox("Select the Channel",all_channels)

    if st.button("Migrate to Sql"):
        Table=tables(unique_channel)
        st.success(Table)


# Sidebar navigation
st.sidebar.title("Explorer Hub")
page = st.sidebar.selectbox("Go to", ("Data Collection", "Display Relevant Details", "Select and Display Data", "Migration to SQL"))

# Render the selected page
if page == "Data Collection":
    page_data_collection()
elif page == "Display Relevant Details":
    page_display_details()
elif page == "Select and Display Data":
    page_select_display_data()
elif page == "Migration to SQL":
    page_migration_to_sql()

# Finally, close SQL connection
cursor.close()
mydb.close()
