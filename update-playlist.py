#!/usr/bin/python3
import os
import json
import argparse
import subprocess

#this command produces a list of json objects, which can be processed in order to get
#id and title
#bin/yt-dlp --flat-playlist -j https://www.youtube.com/playlist?list=PL8t707flkqpfRW-KEWIjQnIWs_akYpmI6 > playlist.txt

#this command downloads the videos and thumbnails
#bin/yt-dlp -o "%(id)s.%(ext)s" --write-thumbnail --datebefore 20230827 --dateafter 20230601 https://www.youtube.com/playlist?list=PL8t707flkqpfRW-KEWIjQnIWs_akYpmI6
#--convert-thumbnails

parser=argparse.ArgumentParser(prog='update-playlist',
                        description='Utility for getting videos from a playlist for jellyfin')
parser.add_argument('bin', help="yt-dlp executble")
parser.add_argument('playlist', help='playlist to download')
parser.add_argument('publish', help='Folder to place videos into')


#get playlist metadata
#download videos + thumbnails
#create nfo files for each video that was downloaded
#move nfo file, thumbnail, video into publish folder
args=parser.parse_args()
#download playlist metadata
outfilename=os.path.join(args.publish,"playlist-data.txt")
playlist_process=subprocess.run([args.bin,"--flat-playlist", "-j", args.playlist],capture_output=True)
playlist_data=playlist_process.stdout.decode()
playlist_entries=playlist_data.split("\n")
ep_num=0
#turn playlist metadata into nfo files:
for entry in playlist_entries:
    if entry.startswith('{'):
        ep_num+=1
        videojson=json.loads(entry)
        #don't overwrite existing nfo
        new_nfo=os.path.join(args.publish,videojson["id"]+".nfo")
        if not os.path.isfile(new_nfo):
            print("Writing new nfo file for "+videojson["id"])
            outfile=open(new_nfo,'w')
            outfile.write('<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>\n')
            outfile.write('<episodedetails>\n')
            outfile.write('<title>')
            outfile.write(videojson["title"])
            outfile.write('</title>\n')
            outfile.write('<uniqueid type="hermitcraft" default="true">'+videojson["id"]+'</uniqueid>\n')
            outfile.write('<episode>'+str(ep_num)+'</episode>\n')
            outfile.write('<thumb aspect="landscape">'+videojson['id']+".png"+'</thumb>')
            outfile.write('</episodedetails>\n')
            outfile.close()
archive_file=os.path.join(args.publish,videojson["id"]+".archive")
#download the videos
get_video_process=subprocess.run([args.bin,"-o",args.publish+'/%(id)s.%(ext)s',"--download-archive",archive_file,"--convert-thumbnails","png","--write-thumbnail","--dateafter","20230601",args.playlist]) 
 #   print(entry[0:40])