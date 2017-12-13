import facebook
import requests
import json

app_id = 'APP_ID'
app_secret = 'APP_SECRET'

def getlikescount(post,graph):
	count = 0
	id = post['id']
	if 'likes' in post:
		likes = post['likes']
		while(True):
			count = count + len(likes['data'])
			if 'paging' in likes and 'after' in likes['paging']['cursors']:
				likes = graph.get_connections(id,'likes',after = likes['paging']['cursors']['after'])
			else:
				break
		return count
	else:
		return 0

def get_fb_token(app_id, app_secret):

    payload = {'grant_type': 'client_credentials', 'client_id': app_id, 'client_secret': app_secret}
    file = requests.post('https://graph.facebook.com/oauth/access_token?', params = payload)
    access_token = ((file.text.split(":")[1]).split(",")[0])
    print(access_token)
    graph = facebook.GraphAPI("USER_ACCESS_TOKEN")
    posts = graph.get_connections('me', 'posts', limit=1)
    print(json.dumps(posts,indent = 4))

    for post in posts['data']:
        likecount = getlikescount(post, graph)
        print(likecount)

get_fb_token(app_id, app_secret)
