from GrooveMusic import GrooveMusic
import glob, os,csv,time
os.chdir("./playlists")

import threading

groovy=GrooveMusic()

class Finder(threading.Thread):
	lock_song_id = threading.Lock()
	lock_not_found=threading.Lock()
	
	def __init__(self, artist,title,isrc, number): 
		threading.Thread.__init__(self) 
		self.artist = artist
		self.title=title
		self.isrc=isrc
		self.number=number
	def run(self): 
		result=groovy.check_isrc(self.artist,self.title,self.isrc)
		if result==-1:
			#print(song)
			Finder.lock_not_found.acquire()
			not_found[self.number]=self.artist+' - '+self.title
			Finder.lock_not_found.release()
		else:
			Finder.lock_song_id.acquire() 
			song_ids[self.number]=result
			Finder.lock_song_id.release() 
			
for file in glob.glob("*.csv"):
	dataset=[]
	with open('./'+file, newline='') as csvfile:
		datareader = csv.reader(csvfile, delimiter=';', quotechar='|')
		for row in datareader:
			dataset.append(row)
	song_ids=[""]*len(dataset)
	not_found=[""]*len(dataset)
	threads=[]
	i=0
	for data in dataset:
		thread=Finder(data[0],data[1],data[2],i)
		threads+=[thread]
		thread.start()
		time.sleep(0.05)
		i+=1
	for x in threads: 
		x.join()
	song_ids=list(filter(None,song_ids))
	not_found=list(filter(None,not_found))
	file=file.replace(".csv","")
	f=open("./"+file+"not_found.txt",'w')
	for item in not_found:
		f.write("%s\n" % item);
	f.close()
	playlist_id=groovy.create_playlist(file)
	groovy.add_song_to_playlist(playlist_id,song_ids[:])