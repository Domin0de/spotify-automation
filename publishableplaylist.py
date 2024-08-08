import requests
import json
import spotipy
import spotipy.util as util
import time
import datetime
import secrets
from datetime import datetime, timedelta
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

clientID = ""
clientScrt = ""
appauthURL = "https://accounts.spotify.com/api/token"
usrauthURL = 'https://accounts.spotify.com/authorize'
baseURL = 'https://api.spotify.com/v1/'

scopes = "playlist-modify-public playlist-modify-private user-library-read playlist-read-private user-follow-read"
callback = "https://example.com/callback/"

def login():
    username = input("What is your spotify username? ")
    print("A browser page will open in 5 seconds, you will need to login and copy the url when you see a 404 Error. Do NOT close the window until you have copied the url!")
    time.sleep(5)
    print(f"Logging in as {username}")

    token = util.prompt_for_user_token(username, scopes,client_id=clientID,client_secret=clientScrt,redirect_uri=callback)
    return token, username

token, username = login()

if token:
    sp = spotipy.Spotify(auth=token)
    print("Successfully connected to Spotify!")
    true = True
else:
    print("Encountered error, please try again.")
    true = False

def getOwnPlaylists():
    playlists = sp.current_user_playlists()
    try:
        playlists["items"] += (sp.current_user_playlists(offset=50))["items"]
        try:
            playlists["itemss"] += (sp.current_user_playlists(offset=100))["items"]
        except:
            pass
    except:
        pass
    return playlists

def reloadSongCache():
    endplaylist = []

    playlists = getOwnPlaylists()

    for i in playlists['items']:
        plylist = sp.playlist(i['id'],fields='tracks')
        for x in plylist['tracks']['items']:
            if x['track']['uri'] not in endplaylist and x['is_local'] == False:
                endplaylist.append(x['track']['uri'])

    now = datetime.now().strftime("%d/%m/%Y")
    data = {"songs":endplaylist,"saveDate":now}

    with open("allsongs.json","w+") as songsa:
        json.dump(data, songsa)

def GetCompiled():
    try:
        with open("allsongs.json","r+") as songsa:
            data = json.load(songsa)
            endplaylist = data["songs"]
    except:
        reloadSongCache()

        with open("allsongs.json","r+") as songsa:
            data = json.load(songsa)
            endplaylist = data["songs"]

    try:
        date = datetime.strptime(data["saveDate"],"%d/%m/%Y")

        if (datetime.now()-date).days >= 4:
            playlists = getOwnPlaylists()

            for i in playlists['items']:
                plylist = sp.playlist(i['id'],fields='tracks')
                for x in plylist['tracks']['items']:
                    if x['track']['uri'] not in endplaylist and x['is_local'] == False:
                        endplaylist.append(x['track']['uri'])

            now = datetime.now().strftime("%d/%m/%Y")
            data = {"songs":endplaylist,"saveDate":now}
            with open("allsongs.json","w+") as songsa:
                json.dump(data, songsa)

    except:
        playlists = getOwnPlaylists()

        for i in playlists['items']:
            plylist = sp.playlist(i['id'],fields='tracks')
            for x in plylist['tracks']['items']:
                if x['track']['uri'] not in endplaylist and x['is_local'] == False:
                    endplaylist.append(x['track']['uri'])

        now = datetime.now()
        data = {"songs":endplaylist,"saveDate":now}
        with open("allsongs.json","w+") as songsa:
            json.dump(data, songsa)

    return endplaylist

def split(l,n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

if true:
    print('Input "cancel" at any time to return to options.')
while true:
    action = input("What would you like to do?: (newplaylist/addtrack/playlistinfo/compile/reload/random/delete/fdel/quit)\n> ")
    if action != "quit":
        try:
            usid = sp.me()['id']
        except:
            token = util.prompt_for_user_token(username, scopes,client_id=clientID,client_secret=clientScrt,redirect_uri=callback)

            if token:
                sp = spotipy.Spotify(auth=token)
                print("Successfully reconnected to Spotify!")

    if action == "newplaylist" or action == "npl":
        name = input("Playlist Name: ")
        if name == "cancel":
            break
        songs = input("List of songs separated by commas: ")
        if songs == "cancel":
            break

        if songs:
            try:
                songl = songs.split(', ')
            except:
                songl = []
                songl.append(songs)
            tracks = []
            fcount = 0

            for nsong in songl:
                nsongl = nsong.split(" - ")
                try:
                    searchs = nsongl[0].replace(" ","+") + "+" + nsongl[1].replace(" ","+")
                    results = sp.search(searchs,type='track')
                    songuri = results['tracks']['items'][0]['uri']
                    tracks.append(songuri)
                except:
                    try:
                        searchs = nsongl[0].replace(" ","+")
                        results = sp.search(searchs,type='track')
                        songuri = results['tracks']['items'][0]['uri']
                        tracks.append(songuri)
                    except:
                        print(f"Could not find {nsong} on Spotify.")
                        fcount += 1

            playlist = sp.user_playlist_create(usid, name)
            plistid = playlist['id']
            sp.user_playlist_add_tracks(usid, plistid, tracks)

            print(f"Added {len(songl)-fcount} songs to the playlist {name}")
        else:
            playlist = sp.user_playlist_create(usid, name)
            print(f"Created playlist {name}")

    elif action == "addtrack" or action == "at":
        playlists = sp.current_user_playlists()

        for i in playlists['items']:
            nentry = f" - {i['name']}({i['id']}): {i['tracks']['total']} songs"
            print(nentry)

        eplist = input("Which playlist would you like to add to?(id): ")
        if eplist == "cancel":
            break
        try:
            playlist = sp.user_playlist(usid, eplist)
            pname = playlist['name']
            name = input(f"What song would you like to add to the playlist: {pname}? ")
            if name == "cancel":
                break
            nsong = name.split(" - ")
            try:
                searchs = nsongl[0].replace(" ","+") + "+" + nsongl[1].replace(" ","+")
                results = sp.search(searchs,type='track')
                songuri = results['tracks']['items'][0]['uri']
                tracks.append(songuri)
                sp.user_playlist_add_tracks(usid, playlist['id'], tracks)
                print(f"Added the song {results['tracks']['items'][0]['name']} to the playlist {pname}")
            except:
                try:
                    searchs = nsongl[0].replace(" ","+")
                    results = sp.search(searchs,type='track')
                    songuri = results['tracks']['items'][0]['uri']
                    tracks.append(songuri)
                    sp.user_playlist_add_tracks(usid, playlist['id'], tracks)
                    print(f"Added the song {results['tracks']['items'][0]['name']} to the playlist {pname}")
                except:
                    print(f"Could not find {name} on Spotify.")
        except:
            print("This id does not correspond to a playlist you own.")

    elif action == "playlistinfo" or action == "pl":
        playlists = getOwnPlaylists()

        for i in playlists['items']:
            nentry = f" - {i['name']}({i['id']}): {i['tracks']['total']} songs"
            print(nentry)

    elif action == "compile":

        flnplylist = GetCompiled()

        plchunks = list(split(flnplylist,500))

        count = 0
        while count < len(plchunks):
            songs = list(split(plchunks[count],100))
            title = f"Compiled [{count+1}]"
            newplylist = sp.user_playlist_create(usid, title)
            for set in songs:
                sp.user_playlist_add_tracks(usid, newplylist['id'],set)
            count += 1

        print("Created compiled playlists and added all songs")

    elif action == "random":
        amount = input("How many songs would you like in this playlist?: ")
        if amount == "cancel":
            break
        else:
            try:
                amount = int(amount)
            except:
                print("Invalid number of songs entered.")

        totplylist = GetCompiled()
        fnlist = []

        print("Compiled list of all songs...")

        count = 1
        while count < amount:
            while count != len(fnlist):
                if count == amount:
                    song = secrets.choice(totplylist)
                    if song not in fnlist:
                        fnlist.append(song)
                        count += 1
                    break
                song = secrets.choice(totplylist)
                if song not in fnlist:
                    fnlist.append(song)
                    count += 1

        rndplylist = sp.user_playlist_create(usid, "Randomised Playlist")
        songs = list(split(fnlist,100))
        for set in songs:
            sp.user_playlist_add_tracks(usid, rndplylist['id'],set)

        link = rndplylist['external_urls']['spotify']

        print(f"Randomised Playlist [{rndplylist['id']}] created with link: {link}")

    elif action == "reload":
        reloadSongCache()
        print("Reloaded personal stored songs.")

    elif action == "delete" or action == "del":
        playlists = getOwnPlaylists()

        for i in playlists['items']:
            nentry = f" - {i['name']}({i['id']}): {i['tracks']['total']} songs"
            print(nentry)

        eplist = input("Which playlist would you like to delete?(id): ")
        if eplist == "cancel":
            break

        try:
            playlist = sp.user_playlist(usid, eplist)
            pname = playlist['name']
            conf = input(f'Are you sure you want to delete the playlist, "{pname}" (y/n): ')
            if conf == "y":
                sp.user_playlist_unfollow(usid, playlist['id'])
                print(f"Deleted playlist: {pname}")
        except:
            print("This id does not correspond to a playlist you own.")

    elif action == "fdel":
        playlists = getOwnPlaylists()

        for i in playlists['items']:
            nentry = f" - {i['name']}({i['id']}): {i['tracks']['total']} songs"
            print(nentry)

        eplist = input("Which playlist would you like to delete?(id): ")
        if eplist == "cancel":
            break

        try:
            playlist = sp.user_playlist(usid, eplist)
            pname = playlist['name']
            sp.user_playlist_unfollow(usid, playlist['id'])
            print(f"Deleted playlist: {pname}")
        except:
            print("This id does not correspond to a playlist you own.")

    elif action == "quit":
        print("Disconnecting from Spotify and ending program...")
        true = False
        break

    else:
        print("This is an invalid command")
