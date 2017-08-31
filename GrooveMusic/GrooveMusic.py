import requests
import json
import webbrowser
import socket 
import sys
import os
import time

# import logging
# import http.client as http_client
# http_client.HTTPConnection.debuglevel = 1

class GrooveMusic:
	client_id=""
	client_secret=""
	access_token=""
	def __init__(self):
		filename = os.path.join(os.path.dirname(__file__), 'access.json')

		f=open(filename,'r');
		auth=json.load(f);
		#print(auth['access_token'])
		self.access_token=auth['access_token']
		f.close()
		# logging.basicConfig()
		# logging.getLogger().setLevel(logging.DEBUG)
		# requests_log = logging.getLogger("requests.packages.urllib3")
		# requests_log.setLevel(logging.DEBUG)
		# requests_log.propagate = True
		# f=open("./api_access.json",'r');
		# api=json.load(f);
		# f.close()
		# receive_socket=socket.socket(socket.AF_INET)
		# port=('localhost',3000)
		# receive_socket.bind(port)
		# receive_socket.listen(1)
		# webbrowser.open_new('https://login.live.com/oauth20_authorize.srf?client_id='+api['client_id']+'&scope=MicrosoftMediaServices.GrooveApiAccess&response_type=code&redirect_uri=http://localhost:3000')
		# conn,port=receive_socket.accept()
		# message=conn.recv(48)
		# print(message.decode()[11:])
		# auth_code=message.decode()[11:]
		# #auth_code = input('Enter the auth code: ')
		# r = requests.post("https://login.live.com/oauth20_token.srf", data={'client_id': api['client_id'], 'client_secret': api['client_secret'],'redirect_uri':'http://localhost:3000','grant_type':'authorization_code', 'code':auth_code})
		# auth=json.loads(r.text[:]);
		# f=open("./access.json",'w')
		# f.write(json.dumps(auth,indent=4));
		# access_token=auth['access_token']
	## 
	#  @brief checks if a piece of music exists with isrc
	#  
	#  @param [in] artist string containing the name of the artist
	#  @param [in] title string containing the title of the song
	#  @param [in] isrc string containing the isrc
	#  @return returns the groove music id on success and -1 on failure
	#  
	#  @details looks up a title by isrc if there is no direct resutl it searches for a match with artist and title
	#  
	def check_isrc(self,artist,title,isrc):
		isrc=isrc.strip()
		query=artist+" "+title
		#query=query.replace(" ","+")
		answer=self.lookup("music.isrc."+isrc,"catalog")
		if self.check_valid(answer)==1:
			if self.check_streamable(answer)==1:
				#print(json.dumps(answer,indent=1))

				return answer['Tracks']['Items'][0]['Id']
		answer=self.search(query,'tracks','catalog',0)
		#print(query)
		if self.check_valid(answer)==1:
			#print(json.dumps(answer,indent=1))
			#print(query)
			if self.check_quality(answer,query)==1:
				#webbrowser.open_new(answer['Tracks']['Items'][0]['Link'])
				return answer['Tracks']['Items'][0]['Id']
			else:
				while self.check_next(answer)!=0:
					answer=self.search(query,'','',self.check_next(answer))
					if self.check_quality(answer,query)==1:
						#webbrowser.open_new(answer['Tracks']['Items'][0]['Link'])
						return answer['Tracks']['Items'][0]['Id']
		return -1
				

	## 
	#  @brief authenticates the programm for user content access
	#  
	#  @details Opens the microsoft login page in a browser. After succesfull login, the the user specific access token is 
	#  automatically generated and stored in the access.json file. Token currently expires after 4 hours.
	#  
	def authenticate_user():
		filename = os.path.join(os.path.dirname(__file__), 'api_access.json')
		f=open(filename,'r');
		api=json.load(f);
		f.close()
		receive_socket=socket.socket(socket.AF_INET)
		port=('localhost',3000)
		receive_socket.bind(port)
		receive_socket.listen(1)
		webbrowser.open_new('https://login.live.com/oauth20_authorize.srf?client_id='+api['client_id']+'&scope=MicrosoftMediaServices.GrooveApiAccess&response_type=code&redirect_uri=http://localhost:3000')
		conn,port=receive_socket.accept()
		message=conn.recv(48)
		#print(message.decode()[11:])
		auth_code=message.decode()[11:]
		#auth_code = input('Enter the auth code: ')
		r = requests.post("https://login.live.com/oauth20_token.srf", data={'client_id': api['client_id'], 'client_secret': api['client_secret'],'redirect_uri':'http://localhost:3000','grant_type':'authorization_code', 'code':auth_code})
		auth=json.loads(r.text[:]);
		f=open("./access.json",'w')
		f.write(json.dumps(auth,indent=4));
	## 
	#  @brief gets the id(s) of user playlists with a certain name
	#  
	#  @param [in] playist_name the name of the playlist, if this is an empty string all playlists will be returned
	#  @return playlist_id and track_count
	#  
	#  @details this searches the user's playlists for playlists with name==playlist_name.
	#  Since Groove allows multiple playlists to have the same name, the result is a list containing elements of type [playlist_id, track_count].
	#  If no playlists matching the name are found, the list will be empty.
	#  This function requires user authentication.
	#  
	def get_playlist_id(self,playist_name):
		status=429
		while status==429:
			g=requests.get("https://music.xboxlive.com/1/content/music/collection/playlists/browse",
			headers={'Authorization':'bearer '+self.access_token, 'Accept':'application/json'})
			status=g.status_code
		answer=json.loads(g.text[:])
		ids=[]
		for playlist in answer["Playlists"]["Items"]:
			#print(playlist['Name'])
			if playlist["Name"]==playist_name or not playist_name:
				ids.append(playlist["Id"])
		return ids
	## 
	#  @brief reads all titles from a playlist
	#  
	#  @param [in] playlist_id The id of the playlist
	#  @return list containing groove music ids of the songs
	#  
	#  @details reads all the groove music ids of the titles in a playlist
	#  This function requires user authentication.
	def dump_playlist(self,playlist_id):
		g=requests.get("https://music.xboxlive.com/1/content/"+playlist_id+"/collection/playlist/tracks/browse?maxItems=25",
		headers={'Authorization':'bearer '+self.access_token, 'Accept':'application/json'},
		data={'maxItems':1})
		answer=json.loads(g.text[:])
		#print(json.dumps(answer,indent=1))
		to_write=[]
		for items in answer['Playlists']['Items']:
			for track in items['Tracks']['Items']:
				#print(track['Name']+";"+track['Artists'][0]['Artist']['Name']+";"+track['Id']+";"+str(track['TrackNumber'])) #ausgabe mit Titel und Artist
				to_write.append(track['Id'])
				
		#print(answer['Playlists']['Items']['Tracks']['ContinuationToken'])
		next_value=self.check_next(answer);
		#print(next_value)
		while next_value!=0:
			g=requests.get("https://music.xboxlive.com/1/content/"+playlist_id+"/collection/playlist/tracks/browse?continuationToken="+next_value,
			headers={'Authorization':'bearer '+self.access_token, 'Accept':'application/json'},
			data={'continuationToken':next_value})	
			answer=json.loads(g.text[:])
			#print(json.dumps(answer,indent=1))
			#f=open("./test.json",'a')
			#f.write(json.dumps(answer,indent=1));
			#to_write=merge(answer,to_write)
			#f.close()
			next_value=self.check_next(answer)
			for items in answer['Playlists']['Items']:
				for track in items['Tracks']['Items']:
					#print(track['Name']+";"+track['Artists'][0]['Artist']['Name']+";"+track['Id']+";"+str(track['TrackNumber']))
					to_write.append(track['Id'])
		return to_write
	## 
	#  @brief creates a new playlist
	#  
	#  @param [in] name name for the playlist
	#  @return id of the new playlist, -1 on failure
	#  
	#  @details creates a new playlist and returns the id. Multiple playlists can have the same name.
	#  This function requires user authentication.
	#  
	def create_playlist(self,playlist_name):
		status=429
		while status==429:
			g=requests.post("https://music.xboxlive.com/1/content/music/collection/playlists/create",
			headers={'Authorization':'bearer '+self.access_token, 'Accept':'application/json'},
			json={
			  "Name": playlist_name,
			  "IsPublished": 'false',})
			status=g.status_code
		response=json.loads(g.text[:])
		if self.check_error(response)==1:
			return -1
		else:
			return response["PlaylistActionResult"]["Id"]
	## 
	#  @brief adds a song to the playlist
	#  
	#  @param [in] playlist_id the id of the playlist (must be a list)
	#  @param [in] song_id the groove music id of the song
	#  @return 1 on success, -1 on failure
	#  
	#  @details adds a new song to the playlist. Limit is 1000 titles per playlist.
	#  This function requires user authentication.
	#  
	def add_song_to_playlist(self,playlist_id=[],song_id=[]):
		playlist_json={}
		playlist_json['Id']=playlist_id
		
		#playlist_id=playlist_id.strip()
		#json_start='{"Id":'+str(playlist_id)+' ,"TrackActions": ['
		#json_end="""]}"""
		
		i=0
		return_value=1
		while i<len(song_id):
			song_limit=0
			playlist_json['TrackActions']=[]
			while i<len(song_id) and song_limit<100:
				action_json={}
				action_json['Id']=song_id[i]
				#print(song_id[i])
				action_json['Action']="Add"
				#playlist_json['TrackActions'].append({"Id":song_id[i],
				#										"Action:":"Add"})
				playlist_json['TrackActions'].append(action_json)
				i+=1
				song_limit+=1
			#json_payload=json_start+track+json_end
			status=429
			#print(json.dumps(playlist_json,indent=1))
			#print(json.dumps(json.loads(str(json_payload)),indent=1))

			while status==429:
				g=requests.post("https://music.xboxlive.com/1/content/music/collection/playlists/update",
				headers={'Authorization':'bearer '+self.access_token, 'Accept':'application/json'},
				json=playlist_json)
				status=g.status_code
			#print(g.text[:])
			response=json.loads(g.text[:])
			if self.check_error(response)==1:
				return_value=-1
		return return_value
	## 
	#  @brief calls the look up endpoint
	#  
	#  @param [in] content_id content identifier this can be groove music id, amg, isrc, iscpn or onedrive. Check api documentation for namespace formating.
	#  @param [in] source catalog, collection or collection+catalog
	#  @return response json
	#  
	#  @details calls the look up endpoint. If source includes the collection, user authentication is required.
	#  
	def lookup(self,content_id,source):
		status=429
		while status==429:
			g=requests.get("https://music.xboxlive.com/1/content/"+content_id+"/lookup?source="+source,
			headers={'Authorization':'bearer '+self.access_token, 'Accept':'application/json'},
			data={'maxItems':1})
			status=g.status_code
			if status==429:
				time.sleep(0.05)
			#print(g.text[:])
		answer=json.loads(g.text[:])
		return answer
		
	## 
	#  @brief calls the query endpoint with query
	#  
	#  @param [in] query the query to be searched
	#  @param [in] filters artist, tracks, albums, playlists or a combination of those (e.g. artist+alblum)
	#  @param [in] source source catalog, collection or collection+catalog
	#  @param [in] continuation_token to get more results, 0 if not used
	#  @return response json
	#  
	#  @details Non streamable results are excluded. 
	#  If source includes the collection, user authentication is required.
	#  
	def search(self,query,filters,source,continuation_token):
		if continuation_token==0:
			query=query.replace(" ","+")
			status=429
			while status==429:
				g=requests.get("https://music.xboxlive.com/1/content/music/search?q="+query+"&maxItems=1&filters="+filters+"&source="+source,
				headers={'Authorization':'bearer '+self.access_token, 'Accept':'application/json'})
				status=g.status_code
				if status==429:
					time.sleep(0.05)
			response=json.loads(g.text[:])
		else:
			status=429
			while status==429:
				g=requests.get("https://music.xboxlive.com/1/content/music/search?continuationToken="+continuation_token,
				headers={'Authorization':'bearer '+self.access_token, 'Accept':'application/json'})
				status=g.status_code
				if status==429:
					time.sleep(0.05)
			response=json.loads(g.text[:])
		return response

	
	## 
	#  @brief checks if the api response contains a track
	#  
	#  @param [in] result_set json response from the api
	#  @return 1 if valid, 0 if not
	#  
	def check_valid(self,result_set):
		try:
			result_set['Tracks']
			return 1
		except KeyError:
			return 0
	## 
	#  @brief checks the result quality
	#  
	#  @param [in] result_set json response from the api
	#  @return 1 if quality is good, 0 is not
	#  
	#  @details the search api will sometimes find live, cover or remix versions.
	#  This function attempts to filter such false positives.
	#  
	def check_quality(self,result_set,query):
		streamable=0
		remix=0
		live=0
		remix_should=0
		live_should=0
		streamable=self.check_streamable(result_set)
		if streamable==0:
			return 0
		title=result_set['Tracks']['Items'][0]['Name']
		album=result_set['Tracks']['Items'][0]['Album']['Name']
		#print(album)
		try:
			subtitle=result_set['Tracks']['Items'][0]['Subtitle']
		except KeyError:
			subtitle=str(0);
		if query.find("remix") != -1:
			remix_should=1
		if query.find("Remix") != -1:	
			remix_should=1
		if query.find("live") != -1:
			live_should=1
		if query.find("Live") != -1:
			live_should=1
		if title.find("remix") != -1 or subtitle.find("remix") !=-1 or title.find("Tribute") !=-1 or title.find("Karaoke") !=-1 or album.find("Karaoke") !=-1 or album.find("Sound") !=-1:
			remix=1
		if title.find("Remix") != -1 or subtitle.find("Remix") !=-1 or title.find("tribute") !=-1 or title.find("karaoke") !=-1 or album.find("karaoke") !=-1 or album.find("sound") !=-1:
			remix=1
		if title.find("live") != -1 or subtitle.find("live") !=-1 or title.find("Made Famous") !=-1  or title.find("Performed By") !=-1:
			live=1
		if title.find("Live") != -1 or subtitle.find("Live") !=-1:
			live=1
		if remix==remix_should and live==live_should:
			return 1
		else:
			return 0
			
	## 
	#  @brief checks if there are more results
	#  
	#  @param [in] result_set json response from the api
	#  @return the continuation token if there is one, 0 if not
	#  
	#  @details checks if there are more results to come
	#  
	def check_next(self,result_set):
		#print(json.dumps(result_set,indent=1))
		playlist_next=0
		track_next=0
		try:
			result=result_set['Tracks']['ContinuationToken']
			#print (result)
			return result
		except KeyError:
			track_next=0
		try:
			result=result_set['Playlists']['Items'][0]['Tracks']['ContinuationToken']
			#print(result)
			return result
		except KeyError:
			playlist_next=0
		return 0
			
	## 
	#  @brief checks if a track is streamable
	#  
	#  @param [in] result_set json response from the api
	#  @return 1 if streamable, 0 if not
	#  
	#  @details checks if the tracks can be streamed or downloaded
	#  
	def check_streamable(self,result_set):
		streamable=0
		try:
			for rights in result_set['Tracks']['Items'][0]['Rights']:
				if rights=="Stream":
					streamable=1
			return streamable
		except KeyError:
			return streamable
	## 
	#  @brief checks if result_set contains an error message
	#  
	#  @param [in] result_set api response json
	#  @return 0 if the message doesn't conain an error message, 1 otherwise
	#  	
	def check_error(self,result_set):
		error=0
		try:
			result_set["Error"]
			error=1
		except KeyError:
			error=0
		return error