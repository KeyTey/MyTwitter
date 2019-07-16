import MyTwitter, random, json

def get_friends(name):
    twitter, user_id = MyTwitter.login(name)
    with open('data/follower.pickle', 'rb') as f:
        friends = pickle.load(f)
    friends = MyTwitter.get_user_list(twitter, friends)
    return friends

def get_fav_data(tweets, day):
    tweets_after = [t for t in tweets if not MyTwitter.is_timeover(t['created_at'], day)]
    tweets_before = [t['id_str'] for t in tweets if not MyTwitter.is_timeover(t['created_at'], day - 1)]
    tweets_after = [t for t in tweets_after if t['id_str'] not in tweets_before]
    favourites = len(tweets_after)
    favourites_people = len(list(set([(t['user']['id_str'], t['user']['screen_name']) for t in tweets_after])))
    return favourites, favourites_people

def preprocess(twitter, users, count = 0):
    data = []
    print("Number of User")
    print(f"Before:\t{len(users)}")
    users = [user for user in users if user['followers_count'] < user['friends_count'] < 800]
    relations = MyTwitter.get_friendship(twitter, user_id_list = [user['id_str'] for user in users])
    users = [user for user, relation in zip(users, relations) if 'following' not in relation['connections']]
    print(f"After:\t{len(users)}\n")
    users = random.sample(users, count) if count else users
    for i, user in enumerate(users):
        if user['protected']: continue
        print(f"{i+1} / {len(users)}")
        tweets = MyTwitter.get_fav_tweet_list(twitter, user['id_str'], 5000, loop = True, day = 5)
        print(f"Tweets: {len(tweets)}", end = '\t')
        tweets = [t for t in tweets if t['retweet_count'] < 20 and t['favorite_count'] < 50 and not t['entities'].get('media')]
        print(f"Preprocess: {len(tweets)}\n")
        data_dict = {
            'id_str': user['id_str'],
            'name': user['name'],
            'screen_name': user['screen_name'],
            'friends_count': user['friends_count'],
            'followers_count': user['followers_count'],
            'statuses_count': user['statuses_count'],
            'favourites_count': user['favourites_count']
        }
        data_dict['favourites_1day'], data_dict['favourites_people_1day'] = get_fav_data(tweets, 1)
        data_dict['favourites_2day'], data_dict['favourites_people_2day'] = get_fav_data(tweets, 2)
        data_dict['favourites_3day'], data_dict['favourites_people_3day'] = get_fav_data(tweets, 3)
        data_dict['favourites_4day'], data_dict['favourites_people_4day'] = get_fav_data(tweets, 4)
        data_dict['favourites_5day'], data_dict['favourites_people_5day'] = get_fav_data(tweets, 5)
        data.append(data_dict)
    return data

def show_friends():
    friends = get_friends('main')
    for friend in friends:
        print(f"{friend['name']}\n{friend['id_str']}\n")

def get_data_from_target(user_id):
    twitter, _ = MyTwitter.login('main')
    users = MyTwitter.get_following(twitter, user_id)
    data = preprocess(twitter, users)
    return data

def get_data_from_tag():
    twitter, user_id = MyTwitter.login('main')
    tag_list = [
        "#ハムスター",
        "#ハムスターのいる生活",
        "#ハムスター好きと繋がりたい"
    ]
    keyword = " OR ".join(tag_list)
    url = "https://api.twitter.com/1.1/search/tweets.json"
    params = {
        'q': keyword,
        'lang': 'ja',
        'result_type': 'recent',
        'count': 100
    }
    tweet_list, users = [], []
    for i in range(50):
        res = twitter.get(url, params = params)
        if res.status_code == 200:
            timeline = json.loads(res.text)
            tweet_list.extend(timeline['statuses'])
        else:
            break
    user_list = [tweet['user'] for tweet in tweet_list if tweet['entities']['user_mentions'] == [] and tweet['entities']['urls'] == [] and tweet['entities'].get('media')]
    for user in user_list:
        if user not in users:
            users.append(user)
    data = preprocess(twitter, users)
    return data

def show_data(data):
    key = lambda i: f'favourites_people_{i}day'
    total = lambda d: d[key(1)] + d[key(2)] + d[key(3)] + d[key(4)] + d[key(5)]
    data = sorted(data, key = lambda d: total(d), reverse = True)
    for d in data:
        for k, v in d.items():
            print(f"{k}\t{v}")
        print(f"link: https://twitter.com/{d['screen_name']}\n")

if __name__ == '__main__':
    while True:
        print("1: show_friends()")
        print("2: get_data_from_target(user_id)")
        print("3: get_data_from_tag()")
        mode = int(input("\n>> "))
        if mode == 1:
            print('\n', '=' * 50, '\n', sep = '')
            show_friends()
            print('=' * 50, '\n', sep = '')
        elif mode == 2:
            user_id = input("\nuser_id: ")
            print('\n', '=' * 50, '\n', sep = '')
            data = get_data_from_target(user_id)
            print('=' * 50, '\n', sep = '')
            show_data(data)
            print('=' * 50, '\n', sep = '')
        elif mode == 3:
            print('\n', '=' * 50, '\n', sep = '')
            data = get_data_from_tag()
            print('=' * 50, '\n', sep = '')
            show_data(data)
            print('=' * 50, '\n', sep = '')