import GrooveMusic

name= input("Please insert the name for the playlist")
groovy=GrooveMusic()
with open(".tracks.txt",'r') as f:
	song_ids=f.readlines()
song_ids=[x.strip() for x in song_ids]
playlist_id=groovy.create_playlist(name)
#playlist_id=groovy.get_playlist_id("BarPlaylist")[0]
print("Adding "+len(song_ids)+" songs to the playlist, this might take some time")
groovy.add_song_to_playlist(playlist_id,song_ids[:])