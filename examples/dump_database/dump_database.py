from GrooveMusic import GrooveMusic

groovy=GrooveMusic()
playlists=groovy.get_playlist_id("")

i=1
# crashes if an empty playlist is encountered
for playlist in playlists:
	tracks=groovy.dump_playlist(playlist)
	f=open('./dumps/'+str(i)+'.txt','w')
	for track in tracks:
		f.write("%s\n" % track);
	f.close()
	i+=1