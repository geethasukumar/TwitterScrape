# importing libraries and packages
import snscrape.modules.twitter as sntwitter
import pandas as pd
import json
from datetime import datetime
import pymongo
import streamlit as st
from pandas import json_normalize
import pprint
import streamlit_ext as ste
import time


m = st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: #0099ff;
    color:#ffffff;
}


</style>""", unsafe_allow_html=True)

## Twitter scraping function
def tweet_scrape(hashword,tweet_since,tweet_until,limit_tweet):

    # Creating list to append tweet data 
    tweets_list1 = []
    
    #try:
        # Using TwitterSearchScraper to scrape data and append tweets to list
    for i,tweet in enumerate(sntwitter.TwitterSearchScraper(hashword+' max-results:'+ limit_tweet +' since:'+tweet_since+' until:'+tweet_until).get_items()): 
     
        tweets_list1.append([tweet.date, tweet.id, tweet.url, tweet.rawContent, tweet.user.username, tweet.replyCount, tweet.retweetCount, tweet.lang, tweet.source, tweet.likeCount]) #declare the attributes to be returned
        
    # Creating a dataframe from the tweets list above 
    #date, id, url, tweet content, user,reply count, retweet count,language, source, like count
    tweets_df1 = pd.DataFrame(tweets_list1, columns=['Tweet_Date', 'Tweet_id', 'URL', 'Text', 'Username', 'Replies', 'Retweets', 'Language', 'Source', 'Likes'])
    
    st.write('Twitter Scraping done!!')
   # except:
     #   st.write('Error occurred while Scraping Twitter')
    #    exit()
    
    return tweets_df1



## DB connection definition
def db_connect():
    try:
        client=pymongo.MongoClient("mongodb+srv://gkg:1234@cluster0.eeit1pl.mongodb.net/?retryWrites=true&w=majority")
        db = client.capstone_project
        collections=db.twitter_scrape
        print("Successfully connected to DB - twitter_scrape")
        return collections
    except:
        st.write("Connecting to DB - twitter_scrape failed!")



## connect to DB and save the tweets as documents in DB
def save_tweets(scraped_data):
    # connect to DB
    st.write('');
    collections=db_connect()
    
    try:
        collections.insert_one(scraped_data)
            
        st.write("Tweets successfully stored in DB") 
    except:
        st.write("Saving Tweets in DB failed!!")


## convert dataframe to format as mentioned in the parameter
def convert_df_to_file(tweets_df,format): 
    if format=='CSV':
        return tweets_df.to_csv(index=False).encode('utf-8')
    elif format=='JSON':
        return tweets_df.to_json(orient='records', indent=True)

        



#Main program for Twitter scraping

hashword='Elon Musk'
since='2023-03-09'
until='2023-03-10'
limit='1000'


#geethasuku68156
#QazWsxEdc#123456
    
    
#to be delete code#
tweets_list1='{"tweets":[{"Tweet_Date":1678406271000,"Tweet_id":1633980449541201926,"Replies":0,"Retweets":0,"Language":"en","Likes":2},{"Tweet_Date":1678388447000,"Tweet_id":1633905691386626065,"Replies":0,"Retweets":0,"Language":"en","Likes":0}]}'
tweets_dict=json.loads(tweets_list1)
#tweets=pd.DataFrame(tweets_list1, columns=['Tweet_Date', 'Tweet_id',  'Replies', 'Retweets', 'Language',  'Likes'],index=[0,1])
tweets=json_normalize(tweets_dict['tweets'])

#to be delete code#



# --- Initialising SessionState ---
if "load_state" not in st.session_state:
     st.session_state.load_state = False



##### Sidebar Twitter scraping inputs

st.sidebar.title("Search in Twitter")

hashword=st.sidebar.text_input("Keyword")
since=st.sidebar.date_input("Since").strftime("%Y-%m-%d")
until=st.sidebar.date_input("Until").strftime("%Y-%m-%d")
limit=str(st.sidebar.number_input("Limit Results by", 0, 5000))

if st.sidebar.button("Scrape Twitter"):
     with st.spinner():
        #Pass the hashword, since, until and max records and search for tweets
         #tweets = tweet_scrape(hashword,since,until,limit);
         st.write(since)
         


#### Main Page for Tweets output

st.title('Tweets for Keyword '+hashword)


#Store the Scraped data in DB/ download data to CSV/JSON
st.dataframe(tweets)
col1, col2, col3 = st.columns([1,1,1])

with col1:
    if st.button("Save Tweets") or st.session_state.load_state: #, on_click='save_tweets', kwargs=data)
        st.session_state.load_state = True
        with st.spinner():
            # convert the output to json
            tweets_json = tweets.to_json(orient='records', lines=True)
            
            data = {
                "Scraped Word": hashword ,
                "Scraped Date": datetime.now(),
                "Scraped Data": tweets_json
               };
            # save to DB
            save_tweets(data)
    
            
with col2:
   ste.download_button(
      label="Download as CSV",
      data=convert_df_to_file(tweets,'CSV'),
      file_name='scraped_tweets.csv',
      mime='text/csv'
    ) 

with col3:
    ste.download_button(
      label="Download as JSON",
      data=convert_df_to_file(tweets,'JSON'),
      file_name='scraped_tweets.json',
      mime='application/json'
    )








