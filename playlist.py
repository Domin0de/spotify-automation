import requests
import json
import spotipy
import spotipy.util as util
import time
import datetime
import random
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
frienduris = []

#username = input("What is your spotify username? ")
#print("A browser page will open in 5 seconds, you will need to login and copy the url when you see a 404 Error. Do NOT close the window until you have copied the url!")
#time.sleep(5)
print("Logging in as Wolfdragon24")

token = util.prompt_for_user_token("Wolfdragon24", scopes,client_id=clientID,client_secret=clientScrt,redirect_uri=callback)

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
            playlists["items"] += (sp.current_user_playlists(offset=100))["items"]
        except:
            pass
    except:
        pass
    return playlists

def getFollowedAll():
    endfollowed = []
    followed = sp.current_user_followed_artists(limit=50)
    next = followed["artists"]["cursors"]["after"]

    for artist in followed["artists"]["items"]:
        endfollowed.append(artist["id"])

    while next:
        followed = sp.current_user_followed_artists(limit=50,after=next)
        next = followed["artists"]["cursors"]["after"]

        for artist in followed["artists"]["items"]:
            endfollowed.append(artist["id"])

    endfollowed += frienduris

    return endfollowed

def reloadSongCache():
    endplaylist = []

    playlists = getOwnPlaylists()

    for i in playlists['items']:
        plylist = sp.playlist(i['id'],fields='tracks')
        for x in plylist['tracks']['items']:
            if x['track']['uri'] not in endplaylist and not x['is_local']:
                endplaylist.append(x['track']['uri'])

    now = datetime.now().strftime("%d/%m/%Y")
    data = {"songs":endplaylist,"saveDate":now}

    with open("allsongs.json","w+") as songsa:
        json.dump(data, songsa)

def reloadFriendSongCache():
    endplaylist = []

    accounts = getFollowedAll()

    for account in accounts:
        try:
            playlists = sp.user_playlists(account,limit=50)

            for i in playlists['items']:
                plylist = sp.playlist(i['id'],fields='tracks')
                for x in plylist['tracks']['items']:
                    try:
                        if x['track']['uri'] not in endplaylist and x['is_local'] == False:
                            endplaylist.append(x['track']['uri'])
                    except:
                        pass
        except:
            pass

    now = datetime.now().strftime("%d/%m/%Y")
    data = {"songs":endplaylist,"saveDate":now}

    with open("allfriendsongs.json","w+") as songsa:
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

def getFriendsCompiled():
    try:
        with open("allfriendsongs.json","r+") as songsa:
            data = json.load(songsa)
            endplaylist = data["songs"]
    except:
        reloadFriendSongCache()

        with open("allfriendsongs.json","r+") as songsa:
            data = json.load(songsa)
            endplaylist = data["songs"]

    try:
        date = datetime.strptime(data["saveDate"],"%d/%m/%Y")

        if (datetime.now()-date).days >= 8:
            followed = getFollowedAll()

            for account in followed:
                try:
                    playlists = sp.user_playlists(account,limit=50)

                    for i in playlists['items']:
                        plylist = sp.playlist(i['id'],fields='tracks')
                        for x in plylist['tracks']['items']:
                            try:
                                if x['track']['uri'] not in endplaylist and x['is_local'] == False:
                                    endplaylist.append(x['track']['uri'])
                            except:
                                pass
                except:
                    pass

            now = datetime.now().strftime("%d/%m/%Y")
            data = {"songs":endplaylist,"saveDate":now}
            with open("allfriendsongs.json","w+") as songsa:
                json.dump(data, songsa)

    except:
        followed = getFollowedAll()

        for account in followed:
            playlists = sp.user_playlists(account,limit=50)

            for i in playlists['items']:
                plylist = sp.playlist(i['id'],fields='tracks')
                for x in plylist['tracks']['items']:
                    try:
                        if x['track']['uri'] not in endplaylist and x['is_local'] == False:
                            endplaylist.append(x['track']['uri'])
                    except:
                        pass

        now = datetime.now()
        data = {"songs":endplaylist,"saveDate":now}
        with open("allfriendsongs.json","w+") as songsa:
            json.dump(data, songsa)

    return endplaylist

def split(l,n):
    for i in range(0, len(l), n):
        yield l[i:i + n]

while true:
    action = input("What would you like to do?: (newplaylist/addtrack/playlistinfo/getlink/compile/compileone/reload/random/friendrandom/delete/fdel/quit)\n> ")
    if action != "quit":
        try:
            usid = sp.me()['id']
        except:
            print("Disconnected from Spotify, and attempting reconnect...")
            token = util.prompt_for_user_token("Wolfdragon24", scopes,client_id=clientID,client_secret=clientScrt,redirect_uri=callback)

            if token:
                sp = spotipy.Spotify(auth=token)
                print("Successfully reconnected to Spotify!")

    if action == "newplaylist" or action == "npl":
        name = input("Playlist Name: ")
        songs = input("List of songs separated by commas: ")

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
        try:
            playlist = sp.user_playlist(usid, eplist)
            pname = playlist['name']
            name = input(f"What song would you like to add to the playlist: {pname}? ")
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

    elif action == "getlink":
        id = input("What is the id of the requested playlist?: ")

        try:
            playlist = sp.user_playlist(usid, id)
            pname = playlist["name"]
            link = playlist["external_urls"]["spotify"]

            print(f"Playlist '{pname}' has the link: {link}")
        except:
            print("No playlist was found with this id")

    elif action == "compile":

        flnplylist = GetCompiled()

        plchunks = list(split(flnplylist,500))

        count = 0
        while count < len(plchunks):
            songs = list(split(plchunks[count],100))
            title = f"Compiled [{count+1}]"
            newplylist = sp.user_playlist_create(usid, title)
            for group in songs:
                sp.user_playlist_add_tracks(usid, newplylist['id'],group)
            count += 1

        print("Created compiled playlists and added all songs")

    elif action == "compileone":

        flynplylist = GetCompiled()

        songs = list(split(flynplylist,100))
        title = f"Compiled [All]"
        newplylist = sp.user_playlist_create(usid, title)
        for group in songs:
            sp.user_playlist_add_tracks(usid, newplylist['id'],group)

        print("Created compiled playlists into one and added all songs")

    elif action == "random":
        amount = int(input("How many songs would you like in this playlist?: "))
        delchoose = input("Would you like to hide the playlist from Spotify after creation?(yes,y/no,n): ")

        totplylist = GetCompiled()
        fnlist = []

        print("Compiled list of all songs...")
        
        while len(fnlist) != amount:
            song = random.choice(totplylist)
            if song not in fnlist:
                fnlist.append(song)

        rndplylist = sp.user_playlist_create(usid, "Randomised Playlist")
        songs = list(split(fnlist,100))
        for group in songs:
            sp.user_playlist_add_tracks(usid, rndplylist['id'],group)

        link = rndplylist['external_urls']['spotify']

        if delchoose == "yes" or delchoose == "y":
            sp.user_playlist_unfollow(usid, rndplylist['id'])

        print(f"Randomised Playlist [{rndplylist['id']}] created with link: {link}")

    elif action == "friendrandom" or action == "frandom":
        amount = int(input("How many songs would you like in this playlist?: "))

        totfriendplylist = getFriendsCompiled()
        fnlist = []

        print("Compiled list of all friend songs...")

        count = 1
        while count < amount:
            while count != len(fnlist):
                if count == amount:
                    song = random.choice(totfriendplylist)
                    if song not in fnlist:
                        fnlist.append(song)
                        count += 1
                    break
                song = random.choice(totfriendplylist)
                if song not in fnlist:
                    fnlist.append(song)
                    count += 1

        rndplylist = sp.user_playlist_create(usid, "Randomised Playlist - Followed [Not My Songs - Listen At Own Risk]")
        songs = list(split(fnlist,100))
        for set in songs:
            try:
                sp.user_playlist_add_tracks(usid, rndplylist['id'],set)
            except:
                pass

        link = rndplylist['external_urls']['spotify']

        print(f"Randomised Playlist [{rndplylist['id']}] created with link: {link}")

    elif action == "reload":
        choice = input("What would you like to reload? (a[all]/p[personal]/f[friend]): ")
        if choice == "all" or choice == "a":
            reloadSongCache()
            reloadFriendSongCache()
            print("Reloaded all stored songs.")
        elif choice == "personal" or choice == "p":
            reloadSongCache()
            print("Reloaded personal stored songs.")
        elif choice == "friend" or choice == "f":
            reloadFriendSongCache()
            print("Reloaded friend stored songs.")
        else:
            print("Invalid option")

    elif action == "delete" or action == "del":
        playlists = getOwnPlaylists()

        for i in playlists['items']:
            nentry = f" - {i['name']}({i['id']}): {i['tracks']['total']} songs"
            print(nentry)

        eplist = input("Which playlist would you like to delete?(id): ")

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
