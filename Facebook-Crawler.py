import requests
import json

facebookUserAccessToken  = "YOUR_USER_ACCESS_TOKEN"

def getFacebookCampaignData(pageID=None, ID=None, paid=None):

    # Let's segregate data collection into two
    # 1. Data Collected using AdvertID(Paid Campaigns)
    # 2. Data Collected using PostID (Unpaid Campaigns)

    advertIDFlag    = False
    postIDFlag      = False
    objectIDFlag    = False

    # Allocating ID for Paid and Unpaid campaigns respectively
    if(paid==False):
        postID          = ID
        advertID        = None
        postIDFlag      = True
    else:
        advertID        = ID
        postID          = None
        advertIDFlag    = True

    # Creating structure to log data from facebook Servers
    facebookCampaignData = {}
    # The Base URL
    baseURL         = "https://graph.facebook.com/v2.10/"

    if(advertIDFlag):

        advertInfoURL   = baseURL + advertID + "?fields=targetingsentencelines,campaign_id,status&access_token=" + facebookUserAccessToken
        # 1st API Call
        # Get targeting and campaign status
        advertInfo = requests.get(advertInfoURL).json()
        campaignID = advertInfo['campaign_id']
        facebookCampaignData['campaign_id'] = campaignID
        advertInsightsInfoURL = baseURL + campaignID + "/insights?fields=unique_ctr,video_10_sec_watched_actions,video_30_sec_watched_actions," \
                                                 "video_15_sec_watched_actions,date_start,spend,clicks,ctr,unique_clicks,ad_name," \
                                                 "impressions,cpm,cpc,date_stop,reach,campaign_name,account_currency,objective," \
                                                 "adset_name,cpp&access_token=" + facebookUserAccessToken
        # 2nd API Call
        # Get advert Insights
        advertInsightsInfo = requests.get(advertInsightsInfoURL).json()
        # Checking for campaign category(Post/Page promotion) and fetching details accordingly
        # Get post ID
        try:
            # 3rd API call
            objectID = requests.get(baseURL + advertID + '?fields=creative{effective_object_story_id}&access_token='
                + facebookUserAccessToken).json()['creative']['effective_object_story_id']
            objectIDFlag = True
        except:
            objectIDFlag = False

        # 6th API call
        topAudienceData = \
        requests.get(baseURL + advertID + '/insights?metric=impressions&breakdowns=age,gender&access_token='
                     + facebookUserAccessToken).json()['data']
        # Getting dict with max impressions because that forms our top audience
        maxImpressions = 0
        for data in topAudienceData:
            if (int(maxImpressions) < int(data['impressions'])):
                maxImpressions = data['impressions']
                topAudience = data['gender'] + ' ' + data['age']

        facebookCampaignData['top_audience'] = topAudience

        # 7th API Call
        topLocationData = \
        requests.get(baseURL + advertID + '/insights?metric=impressions&breakdowns=region&access_token='
                     + facebookUserAccessToken).json()['data']
        # Getting dict with max impressions because that forms our top location
        maxImpressions = 0
        for data in topLocationData:
            if (int(maxImpressions) < int(data['impressions'])):
                maxImpressions = data['impressions']
                topLocation = data['region']
        facebookCampaignData['top_location'] = topLocation

    # Creating structure to cache unpaid data
    trivialPostData     = {}   
    postInsights        = {}

    # Setting flags for appropriate checks
    trivialPostDataFlag = False
    postInsightsFlag    = False

    if(postIDFlag):
        # # Get object ID to fetch further data
        # objectIDURL     = baseURL + postID + "?fields=page_story_id&access_token=" + facebookUserAccessToken
        # objectID        = requests.get(objectIDURL).json()['page_story_id']
        objectID          = pageID + '_' + postID
    # Get trivial campaign details
    # 4th API call
    try:
        trivialPostData = requests.get(baseURL + objectID +   '?fields=link,created_time,likes.limit(0).summary(true),comments.limit(0).summary(true)'
                                                            ',shares,type&access_token=' + facebookUserAccessToken).json()
        trivialPostDataFlag = True
    except:
        trivialPostDataFlag = False

    # Get post insights
    # 5th API call
    try:
        postInsights = requests.get(baseURL + objectID +  '/insights?metric=post_video_avg_time_watched,post_video_views,'
                                                        'post_impressions,post_impressions_unique,post_impressions_organic_unique,'
                                                        'post_impressions_paid_unique,post_engaged_users,post_negative_feedback'
                                                        '&access_token=' + facebookUserAccessToken).json()
        postInsightsFlag = True
    except:
        postInsightsFlag = False

    # Getting all data together in one dictionary
    # Cleaning up
    if(advertIDFlag):
        for data in advertInfo['targetingsentencelines']['targetingsentencelines']:
            if ('Location' in data['content']):
                facebookCampaignData['target_locations']    = data['children'][0]
            if('Excluded Connections' in data['content']):
                facebookCampaignData['excluded_audiences']  = data['children'][0]
            if ('Gender' in data['content']):
                facebookCampaignData['target_gender']       = data['children'][0]
            if ('Age' in data['content']):
                facebookCampaignData['age']                 = data['children'][0]
            if ('Language' in data['content']):
                facebookCampaignData['language']            = data['children'][0]
            if ('Placements' in data['content']):
                facebookCampaignData['placements']          = data['children'][0]
            if ('People Who Match' in data['content']):
                facebookCampaignData['matched_people']      = data['children'][0]
            if ('And Must Also Match' in data['content']):
                facebookCampaignData['extra_matches']       = data['children'][0]

        # Cleaning up to fetch data
        advertInsightsInfo = advertInsightsInfo['data'][0]

        facebookCampaignData['campaign_name'] = advertInsightsInfo['campaign_name']
        facebookCampaignData['date_start'] = advertInsightsInfo['date_start']
        facebookCampaignData['spend'] = advertInsightsInfo['spend']
        facebookCampaignData['clicks'] = advertInsightsInfo['clicks']
        facebookCampaignData['ctr'] = advertInsightsInfo['ctr']
        facebookCampaignData['impressions'] = advertInsightsInfo['impressions']
        facebookCampaignData['cpm'] = advertInsightsInfo['cpm']
        facebookCampaignData['cpc'] = advertInsightsInfo['cpc']
        facebookCampaignData['paid_reach'] = advertInsightsInfo['reach']
        facebookCampaignData['account_currency'] = advertInsightsInfo['account_currency']
        facebookCampaignData['date_stop'] = advertInsightsInfo['date_stop']
        facebookCampaignData['objective'] = advertInsightsInfo['objective']
        facebookCampaignData['cpp'] = advertInsightsInfo['cpp']

    # Getting Targeting Specifics
    facebookCampaignData['targeting_specifics'] = '| '
    if('target_locations' in facebookCampaignData):
        facebookCampaignData['targeting_specifics'] = facebookCampaignData['targeting_specifics'] + facebookCampaignData['target_locations']
    else:
        facebookCampaignData['targeting_specifics'] = facebookCampaignData['targeting_specifics'] + 'None'

    if('age' in facebookCampaignData):
        facebookCampaignData['targeting_specifics'] = facebookCampaignData['targeting_specifics'] + ' | ' + facebookCampaignData['age']
    else:
        facebookCampaignData['targeting_specifics'] = facebookCampaignData['targeting_specifics'] + ' | ' + 'None'

    if('language' in facebookCampaignData):
        facebookCampaignData['targeting_specifics'] = facebookCampaignData['targeting_specifics'] + ' | ' + facebookCampaignData['language']
    else:
        facebookCampaignData['targeting_specifics'] = facebookCampaignData['targeting_specifics'] + ' | ' + 'None'

    if('target_gender' in facebookCampaignData):
        facebookCampaignData['targeting_specifics'] = facebookCampaignData['targeting_specifics'] + ' | ' + facebookCampaignData['target_gender']
    else:
        facebookCampaignData['targeting_specifics'] = facebookCampaignData['targeting_specifics'] + ' | ' + 'None'

    if('matched_people' in facebookCampaignData):
        facebookCampaignData['targeting_specifics'] = facebookCampaignData['targeting_specifics'] + ' | ' + facebookCampaignData['matched_people']
    else:
        facebookCampaignData['targeting_specifics'] = facebookCampaignData['targeting_specifics'] + ' | ' + 'None'

    if('extra_matches' in facebookCampaignData):
        facebookCampaignData['targeting_specifics'] = facebookCampaignData['targeting_specifics'] + ' | ' + facebookCampaignData['extra_matches']
    else:
        facebookCampaignData['targeting_specifics'] = facebookCampaignData['targeting_specifics'] + ' | ' + 'None'

    facebookCampaignData['targeting_specifics'] += ' |'

    # Collecting all Unpaid Data
    if(trivialPostDataFlag):
        facebookCampaignData['likes']           = trivialPostData["likes"]["summary"]["total_count"]
        facebookCampaignData['comments']        = trivialPostData["comments"]["summary"]["total_count"]
        if(('shares' in trivialPostData) and ('count' in trivialPostData["shares"])):
            facebookCampaignData['shares']      = trivialPostData['shares']['count']
        facebookCampaignData['type']            = trivialPostData["type"]
        facebookCampaignData['link']            = trivialPostData['link']
        facebookCampaignData['created_time']    = trivialPostData['created_time']

    if(postInsightsFlag):

        postInsights = postInsights['data']
        for metrics in postInsights:
            if('post_impressions_unique' in metrics['name']):
                facebookCampaignData['post_impressions_unique']         = metrics['values'][0]['value']
            if('post_impressions_paid' in metrics['name']):
                facebookCampaignData['post_impressions_paid']           = metrics['values'][0]['value']
            if('engaged_users' in metrics['name']):
                facebookCampaignData['engagement']                      = metrics['values'][0]['value']
            if('post_impressions_organic_unique' in metrics['name']):
                facebookCampaignData['organic_reach']                   = metrics['values'][0]['value']
            if('post_video_avg_time_watched' in metrics['name']):
                facebookCampaignData['average_watch_time']              = metrics['values'][0]['value']

    return facebookCampaignData

# Testing the Crawler
if __name__=='__main__':

   print(getFacebookCampaignData(pageID='YOUR_PAGE_ID_HERE', ID='YOUR_POSTID_OR_ADVERTID', paid=False))
