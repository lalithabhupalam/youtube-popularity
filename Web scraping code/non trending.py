import http.client
import json
import requests, sys, time, os, argparse

# List of simple to collect features
snippet_features = ["title",
                    "publishedAt",
                    "channelId",
                    "channelTitle",
                    "categoryId"]

# Any characters to exclude, generally these are things that become problematic in CSV files
unsafe_characters = ['\n', '"']

# Used to identify columns, currently hardcoded order
header = ["video_id"] + snippet_features + ["trending_date", "tags", "view_count", "likes", "dislikes",
                                            "comment_count", "thumbnail_link", "comments_disabled",
                                            "ratings_disabled", "description"]


def setup(api_path):
    with open(api_path, 'r') as file:
        api_key = file.readline()


    return api_key


def prepare_feature(feature):
    # Removes any character from the unsafe characters list and surrounds the whole item in quotes
    for ch in unsafe_characters:
        feature = str(feature).replace(ch, "")
    return f'"{feature}"'


def api_request(page_token):
    # Builds the URL and requests the JSON from it
    request_url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,contentDetails,statistics&id={id}&maxResults=50&key={api_key}"
    request = requests.get(request_url)
    if request.status_code == 429:
        print("Temp-Banned due to excess requests, please wait and continue later")
        sys.exit()
    return request.json()


def get_tags(tags_list):
    # Takes a list of tags, prepares each tag and joins them into a string by the pipe character
    return prepare_feature("|".join(tags_list))


def get_videos(items):
    lines = []
    for video in items:
        comments_disabled = False
        ratings_disabled = False

        # We can assume something is wrong with the video if it has no statistics, often this means it has been deleted
        # so we can just skip it
        if "statistics" not in video:
            continue

        # A full explanation of all of these features can be found on the GitHub page for this project
        video_id = prepare_feature(video['id'])

        # Snippet and statistics are sub-dicts of video, containing the most useful info
        snippet = video['snippet']
        statistics = video['statistics']

        # This list contains all of the features in snippet that are 1 deep and require no special processing
        features = [prepare_feature(snippet.get(feature, "")) for feature in snippet_features]

        # The following are special case features which require unique processing, or are not within the snippet dict
        description = snippet.get("description", "")
        thumbnail_link = snippet.get("thumbnails", dict()).get("default", dict()).get("url", "")
        trending_date = time.strftime("%y.%d.%m")
        tags = get_tags(snippet.get("tags", ["[none]"]))
        view_count = statistics.get("viewCount", 0)

        # This may be unclear, essentially the way the API works is that if a video has comments or ratings disabled
        # then it has no feature for it, thus if they don't exist in the statistics dict we know they are disabled
        if 'likeCount' in statistics and 'dislikeCount' in statistics:
            likes = statistics['likeCount']
            dislikes = statistics['dislikeCount']
        else:
            ratings_disabled = True
            likes = 0
            dislikes = 0

        if 'commentCount' in statistics:
            comment_count = statistics['commentCount']
        else:
            comments_disabled = True
            comment_count = 0

        # Compiles all of the various bits of info into one consistently formatted line
        line = [video_id] + features + [prepare_feature(x) for x in [trending_date, tags, view_count, likes, dislikes,
                                                                       comment_count, thumbnail_link, comments_disabled,
                                                                       ratings_disabled, description]]
        lines.append(",".join(line))
    return lines


def get_pages(next_page_token="&"):
    country_data = []

    # Because the API uses page tokens (which are literally just the same function of numbers everywhere) it is much
    # more inconvenient to iterate over pages, but that is what is done here.
        # A page of data i.e. a list of videos and all needed data
    video_data_page = api_request(next_page_token)

        # Get the next page token and build a string which can be injected into the request with it, unless it's None,
        # then let the whole thing be None so that the loop ends after this cycle
    
    

        # Get all of the items as a list and let get_videos return the needed features
    items = video_data_page.get('items', [])
    country_data += get_videos(items)

    return country_data


def write_to_file( country_data):

    print(f"Writing data to file...")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(f"{output_dir}/{time.strftime('%y.%d.%m')}videos.csv", "a", encoding='utf-8') as file:
        for row in country_data:
            file.write(f"{row}\n")


def get_data():
        country_data = [",".join(header)] + get_pages()
        write_to_file(country_data)


if __name__ == "__main__":

  idlist=[]
  for i in range(1,16):
    conn = http.client.HTTPSConnection("devpicker.com")
    payload = "{\"timestampReal\":1700447027235,\"userQuery\":\"\"}"
    headers = {
    'authority': 'devpicker.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'text/plain;charset=UTF-8',
    'cookie': 'google-analytics_v4_qvPA__ga4=409d1c62-661b-4fb9-9bb9-2302b0b2df06; google-analytics_v4_qvPA__ga4sid=886772708; google-analytics_v4_qvPA__session_counter=3; google-analytics_v4_qvPA__engagementPaused=1700446164531; google-analytics_v4_qvPA__engagementStart=1700447008692; google-analytics_v4_qvPA__counter=8; google-analytics_v4_qvPA__let=1700447008692',
    'origin': 'https://devpicker.com',
    'referer': 'https://devpicker.com/random-youtube-video',
    'sec-ch-ua': '"Microsoft Edge";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
     }
    conn.request("POST", "/public/api/random-youtube-videos.php", payload, headers)
    res = conn.getresponse()
    data = res.read()
    y = json.loads(data)
    print(y)
    print(y['video']['id'])
    if y['video']['published'].find("2023")!=-1 or y['video']['published'].find("2022")!=-1 or y['video']['published'].find("2021")!=-1 or y['video']['published'].find("2020")!=-1:
      idlist.append(y['video']['id'])
    time.sleep(2)
  print(idlist)
  id=','.join(idlist)

  parser = argparse.ArgumentParser()
  parser.add_argument('--key_path', help='Path to the file containing the api key, by default will use api_key.txt in the same directory', default='api_key.txt')
  parser.add_argument('--output_dir', help='Path to save the outputted files in', default='output/')

  args = parser.parse_args()

  output_dir = args.output_dir
  api_key = setup(args.key_path)

  get_data()



