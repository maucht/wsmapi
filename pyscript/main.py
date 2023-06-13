from hidden import SECRET
from hidden import CLIENT_ID
from hidden import PASS
from hidden import USER

from nrclex import NRCLex

import nltk
try:
    nltk.download("punkt")
except Exception:
    pass

import praw
import datetime

from django.http import JsonResponse

# emotion detection does count as AI btw according to chatgpt
# it falls under the category of Natural Language Processing


def getRefinedIndividualMoodDict(currMoodDict): 
    # run in each submission iteration, end result should be only positive/negative
    refinedDict = {}
    IRREV_MODIFER = 1
    if(currMoodDict['positive'] > currMoodDict['negative']):
        # nullify anger and fear and sadness, anticipation
        # redirect 0.5 - 0.75 of surprise and joy to positive
        surpriseVal = 0
        if('surprise' in currMoodDict):
            surpriseVal = currMoodDict['surprise']

        joyVal = 0
        if('joy' in currMoodDict):
            joyVal = currMoodDict['joy']

        surpriseVal = int(surpriseVal * IRREV_MODIFER)
        joyVal = int(joyVal*IRREV_MODIFER)

        refinedDict['positive'] = currMoodDict['positive'] + surpriseVal + joyVal
        refinedDict['negative'] = currMoodDict['negative']
        return refinedDict
    elif(currMoodDict['positive'] < currMoodDict['negative']):
        # redirect anger and fear and sadness to negative (same rate as above)
        # nullify surprise and anticipation
        angerVal = 0
        if('anger' in currMoodDict):
            angerVal = int((currMoodDict['anger']) * IRREV_MODIFER)

        fearVal = 0
        if('fear' in currMoodDict):
            fearVal = int((currMoodDict['fear']) * IRREV_MODIFER)

        sadVal = 0
        if('sad' in currMoodDict):
            int((currMoodDict['sad']) * IRREV_MODIFER)

        refinedDict['positive'] = currMoodDict['positive']
        refinedDict['negative'] = currMoodDict['negative'] + angerVal + fearVal + sadVal

        return refinedDict
    else:
        # positive = negative,
        # nullify everything but positive and negative
        refinedDict['positive'] = currMoodDict['positive']
        refinedDict['negative'] = currMoodDict['negative']
        return refinedDict

def getMoodRatio(totalMoodDict):
    totalCount = 0
    ratioDict = {}
    for key in totalMoodDict:
        totalCount += totalMoodDict[key]

    # perhaps setprecision to 2 float
    ratioDict['anger'] = totalMoodDict['anger'] / totalCount
    ratioDict['anticipation'] = totalMoodDict['anticipation'] / totalCount
    ratioDict['disgust'] = totalMoodDict['disgust'] / totalCount
    ratioDict['fear'] = totalMoodDict['fear'] / totalCount
    ratioDict['joy'] = totalMoodDict['joy'] / totalCount
    ratioDict['negative'] = totalMoodDict['negative'] / totalCount
    ratioDict['positive'] = totalMoodDict['positive'] / totalCount
    ratioDict['sadness'] = totalMoodDict['sadness'] / totalCount
    ratioDict['surprise'] = totalMoodDict['surprise'] / totalCount
    ratioDict['trust'] = totalMoodDict['trust'] / totalCount
    
    return ratioDict

reddit = praw.Reddit(
    client_id=CLIENT_ID,
    client_secret=SECRET,
    user_agent="my user agent",
)

today = datetime.date.today()
start_time = datetime.datetime.combine(today, datetime.datetime.min.time())
start_epoch = int(start_time.timestamp())
end_time = datetime.datetime.combine(today, datetime.datetime.max.time())
end_epoch = int(end_time.timestamp())

yesterday_start_time = start_time - datetime.timedelta(days=1)
yesterday_end_time = end_time - datetime.timedelta(days=1)
yesterday_start_epoch = int(yesterday_start_time.timestamp())
yesterday_end_epoch = int(yesterday_end_time.timestamp())

totalMoodDict = {}

# Loop for today's posts
for submission in filter(lambda s: s.media is None and s.selftext != '', reddit.subreddit("wallstreetbets").new(limit=100)):
    submission_utc = submission.created_utc
    submission_date_time_string = str(datetime.datetime.fromtimestamp(submission_utc))
    submission_date_split = submission_date_time_string.split("-")
    submission_month = int(submission_date_split[1])
    submission_day = int(submission_date_split[2][0:2])

    # Skip posts that are not from today
    if submission_month != today.month or submission_day != today.day:
        continue

    emotion = NRCLex(submission.selftext)

    if 'positive' not in emotion.raw_emotion_scores or 'negative' not in emotion.raw_emotion_scores:
        continue

    refinedEmotionScore = getRefinedIndividualMoodDict(emotion.raw_emotion_scores)

    for key in refinedEmotionScore:
        if key not in totalMoodDict:
            totalMoodDict[key] = refinedEmotionScore[key]
        else:
            totalMoodDict[key] += refinedEmotionScore[key]
#print({"today":totalMoodDict})
printHash = {}
if "positive" in totalMoodDict:
    printHash = totalMoodDict
else:
    printHash["positive"] = 1
    printHash["negative"] = 1
totalMoodDict = {}

# Loop for posts from 24-48 hours ago
for submission in filter(lambda s: s.media is None and s.selftext != '', reddit.subreddit("wallstreetbets").new(limit=100)):
    submission_utc = submission.created_utc
    submission_date_time_string = str(datetime.datetime.fromtimestamp(submission_utc))
    submission_date_split = submission_date_time_string.split("-")
    submission_month = int(submission_date_split[1])
    submission_day = int(submission_date_split[2][0:2])

    # Skip posts that are not from 24-48 hours ago
    if submission_month != yesterday_start_time.month or submission_day < yesterday_start_time.day or submission_day > yesterday_end_time.day:
        continue

    emotion = NRCLex(submission.selftext)

    if 'positive' not in emotion.raw_emotion_scores or 'negative' not in emotion.raw_emotion_scores:
        continue

    refinedEmotionScore = getRefinedIndividualMoodDict(emotion.raw_emotion_scores)

    for key in refinedEmotionScore:
        if key not in totalMoodDict:
            totalMoodDict[key] = refinedEmotionScore[key]
        else:
            totalMoodDict[key] += refinedEmotionScore[key]

# print out data to handle in django views
if "positive" not in totalMoodDict:
    totalMoodDict["positive"] = 1
    totalMoodDict["negative"] = 1

print(printHash["positive"],end=".")
print(printHash["negative"],end=".")
print(totalMoodDict["positive"],end=".")
print(totalMoodDict["negative"],end=".")

