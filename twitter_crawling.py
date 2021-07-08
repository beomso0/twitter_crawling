#%%
# 트위터 수집 코드

""" 
datetime: 2018년 11월 15일 5시 경
track keyword : '이수역, 이수'
"""


import tweepy
import json

consumer_key = 'lbQ6DE0xZp9y9b6k8t6F2QsGR'
consumer_secret = '0J3hYgrn9jTFdxWqUXpjOCufDdtaXoxbEhb7etaW0DyAwSwIZq'
access_token = '1061866271489150977-8f5TpM9ev34cYI6Kr0Cn1iOnHlIuRa'
access_secret = '2Q7sboqJaPritOm5GJdudVv9ufTVIwgvmj9XRATwWib1w'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

class MyListener(tweepy.StreamListener):

    def on_status(self, data):
        print(data.text + "\n----")

    def on_data(self, data):
        try:
            with open('tweet_stream.json', 'a', newline = '\n') as file:
                file.write(data)
                print(data)
                return True
        except BaseException as e:
            print("Error on_data: {}".format(str(e)))
        return True

twitter_stream = tweepy.Stream(auth, MyListener())
twitter_stream.filter(track=['이수역, 이수'], encoding = 'utf-8')

#%%
import json

#stream으로 수집한 json 파일 열기
isu_data = []
with open("isu_station.json") as file:
    data = file.readlines()
    for d in data:
        isu_data.append(json.loads(d))

#%%
# text list 생성
#retweet된 경우와 그렇지 않은 경우를 구분하고, retweet된 트윗은 텍스트가 생략되기도하므로, 생략된 경우는 full_text를 추출하여 분석에 사용했다.

isu_text = []
for tweet in isu_data:
    if ("text" in tweet) and ("user" in tweet):
        if 'retweeted_status' in tweet.keys():
            if 'extended_tweet' in tweet['retweeted_status'].keys():
                isu_text.append(tweet['retweeted_status']['extended_tweet']['full_text'])           
            else :                 
                isu_text.append(tweet['retweeted_status']['text'])          
        else :              
            isu_text.append(tweet['text'])
        #len(isu_text) :17025

#%%
# text 중 명사와 형용사를 추출하여 wordcloud를 그린다.
from konlpy.tag import Kkma
from konlpy.tag import Okt
%matplotlib inline
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from collections import Counter

#%%
# 5000개 text 추출하여 명사 tagging 후 most_common으로 정렬.
tagger = Okt()
tagged_texts = [tagger.pos(text, norm = True, stem=True) for text in isu_text[0:5000]]
tagged_texts
selec_list = []
for text in tagged_texts:
    for word,tag in text:        
        if tag == 'Noun':
            selec_list.append(word)
selec_counts = Counter(selec_list)
selec_counts = selec_counts.most_common()

#%%
# 대명사, 명사가 아님에도 명사로 분류된 것, 유의미성을 갖지 않는 것들 제외(제외의 기준이 모호한 것은 한계)
remove_noun = ['젠', '이나','이','것','명','안','거','그','뿐','비','메','일이','패','님','님들','중','계','곳임','그거','그냥','무슨',\
'내','이번','누가','자리','수','둘','팼다','대해','일어나서','건','등등','라며','그때','아닛','아유','고','저','후','주심','먼저','위','일',\
'등','안녕하십니까','젤','네','진','일도','것일','함','남사','당한','척','난','뭐','정말','모','사성','데','더','또','분','못','로','어쩌면'\
,'다시','우선','좀','모든','존나','통해','상대로','보아','퍼뜨리','계속','널리','강','자','달라','심지어','갑자기','라면','하라']

#tuple의 list를 cloud.fit_words()에 바로 넣으면 오류 발생 --> 딕셔너리 형태로 변환
selec_dict={}
for key, value in selec_counts:
    if key not in remove_noun:
        selec_dict[key] = value

#%%
cloud = WordCloud(width=900, height=600, 
                  font_path='‪C:\Windows\Fonts\oldbath.ttf',
                  background_color='white')
cloud = cloud.fit_words(selec_dict)
plt.figure(figsize=(15, 20)) 
plt.axis('off') 
plt.imshow(cloud)
plt.show()