import random, os, sys, requests, spotipy, ffmpeg, subprocess
from twython import Twython
from spotipy.oauth2 import SpotifyClientCredentials

# Importation des variables d'authentification du fichier auth.py
from auth import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET, someid, somesecret

# Procedure d'authentification
twitter = Twython(
    CONSUMER_KEY,
    CONSUMER_SECRET,
    ACCESS_KEY,
    ACCESS_SECRET)
client_credentials_manager = SpotifyClientCredentials(someid, somesecret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

#Playlist Daily Mix
playlist = random.choice(open('/home/pi/bot_twitter/liste_daily.txt').readlines())

#Acces du dossier
path='/home/pi/Videos/'
pathtw = '/home/pi/bot_twitter/'

count = 0

#Compte le nombre de dossier
while os.path.isdir(os.path.join(path,str(count))) == True:
    count += 1

#Fonction Spotify, recupere artiste, nom du son, cover et preview

def get_track_info(playlist_id):
    x = 0
    track_artist_list = []
    track_name_list = []
    cover_url_list = []
    preview_url_list = []
    playlist = sp.playlist(playlist_id)
    for item in playlist ['tracks']['items']:
        track = item['track']
        cover = item['track']['album']
        if track['preview_url'] != None:
            preview_url_list.append(track['preview_url'])
            cover_url_list.append(cover['images'][0]['url'])
            track_name_list.append(track['name'])
            track_artist_list.append(track['artists'][0]['name'])
            x += 1 
    return {'artist' : track_artist_list, 'name' : track_name_list, 'cover_url' : cover_url_list, 'preview_url' : preview_url_list, 'count' : x}


# Initialisation des listes
artist_list = get_track_info(playlist)['artist']
name_list = get_track_info(playlist)['name']
preview_list = get_track_info(playlist)['preview_url']
cover_list = get_track_info(playlist)['cover_url']
c = get_track_info(playlist)['count']

# Initialisation du son
k = int(random.randint(0, c - 1))
print(k)
artist = artist_list[k]
name = name_list[k]
title = artist+' - '+name
cover_url = cover_list[k]
preview_url = preview_list[k]
print('Song: '+title)
with open(pathtw+"tweets.txt", "r") as ftweet:
    for line in ftweet:
        while line.rstrip() == title:
            n = int(random.randint(0, c - 1))
            artist = artist_list[ka]
            name = name_list[ka]
            title = artist+' - '+name
            print('Song changed: '+title)
            cover_url = cover_list[n]
            preview_url = preview_list[n]
        
# Telechargement du preview et cover
print('Downloading '+title+' cover...')
cover = requests.get(cover_url)
with open(path+str(count)+'.jpeg', 'wb') as f:
    f.write(cover.content)
print('Downloaded!')
print('Downloading '+title+' preview...')
preview = requests.get(preview_url)
with open(path+str(count)+'.mp3', 'wb') as f:
    f.write(preview.content)
print('Downloaded!')

#Creation du repertoire
directory = os.path.join(path,str(count))
os.mkdir(directory)
print("Directory created")

#Creation de la video
cmd = 'ffmpeg -loop 1 -i '+path+str(count)+'.jpeg -i '+path+str(count)+'.mp3 -c:v libx264 -pix_fmt yuv420p -tune stillimage -c:a aac -t 30 -shortest '+directory+'/'+str(count)+'.mp4'
subprocess.call(cmd, shell=True)
print(str(count)+'.mp4 was created!')

video = open(os.path.join(directory,str(count))+'.mp4', 'rb')

#Upload de la video
print("Uploading on Twitter...")
response = twitter.upload_video(media=video, media_type='video/mp4', media_category='tweet_video', check_progress=True)
print("Uploaded!")

#Envoi du tweet
print('Tweeting...')
twitter.update_status(status=title, media_ids=[response['media_id']])
print('Tweeted!')

with open(pathtw+"tweets.txt", "a") as ft:
    ft.write("\n"+title)

print('Done!')


