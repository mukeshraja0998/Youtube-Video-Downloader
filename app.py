from pytube import YouTube 
from flask import Flask, send_file,render_template,request,session
from io import BytesIO
from flask_session import Session
import re
import os
#import ffmpeg
#from flask import send_file

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.secret_key = "calender"

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/next_page", methods=["GET","POST"])
def next_page():
    validateVideoUrl = (r'(https?://)?(www\.)?''(youtube|youtu|youtube-nocookie)\.(com|be)/''(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    session['url']=request.form["video_url"]
    session['optradio']=request.form["optradio"]
    session['validVideoUrl'] = str(re.match(validateVideoUrl, session['url']))
    if(session['validVideoUrl']):
        #session["ids_audio"]=[]
        #list = session["ids_audio"]
        session['count']=0
        url=None
        while url is None:
            session['count']+=1
            try:
                #url= YouTube(str(session['url']),use_oauth=True, allow_oauth_cache=True)
                url= YouTube(str(session['url']))
                session['thumbnail_url']=YouTube(str(session['url'])).thumbnail_url
            except Exception as e:
                if(session['count']>=10):
                    break
                print("line 30")
                pass
            
    else:
        return render_template('index.html',mesage = "Dear user, please enter correct Youtube URL ")
    if(session['optradio']=="option1"):
        li=[]
        url_filter=None
        session['count']=0
        while url_filter is None:
            session['count']+=1
            try:
                url_filter= url.streams.filter(progressive=True)
            except Exception as e:
                if(session['count']>=500):
                    break
                print(e)
                print("line42 "+str(session['count']))
                pass
        #url=url.streams.filter(progressive=True)
        
        #print(url)
        for i,b in url_filter.itag_index.items():
            temp=[]
            temp.append(b.resolution)
            temp.append(b.filesize_mb)
            temp.append(b.fps)
            temp.append(i)
            li.append(temp)
            session['name']=b.title
        #print(li)
        return render_template('index2.html',videoList=li,name=session['name'],image=session['thumbnail_url'])
    elif(session['optradio']=="option2"):
        li=[]
        
        url_filter=None
        session['count']=0
        while url_filter is None:
            session['count']+=1
            try:
                url_filter= url.streams.filter(only_audio=True)
            except Exception as e:
                if(session['count']>=500):
                    break
                print("line 64")
                pass
        for i,b in url_filter.itag_index.items():
            temp=[]
            temp.append(b.abr)
            temp.append(b.filesize_mb)
            temp.append(i)
            #list.append(i)
            session['name']=b.title
            li.append(temp)
        li=sorted(li, key=lambda x: x[1])
        #(li)
        #session["ids_audio"]=list
        #print("mukesh")
        #print(session["ids_audio"])
        return render_template('index2.html',audioList=li,name=session['name'],image=session['thumbnail_url'])


@app.route("/download", methods=["GET","POST"])
def download():
    try:
        buffer = BytesIO()
        #session['url']=request.form["video_url"]
        if(session['url']):
            url=None
            session['count']=0
            while url is None:
                session['count']+=1
                try:
                    #url= YouTube(str(session['url']),use_oauth=True, allow_oauth_cache=True)
                    url= YouTube(str(session['url']))
                except Exception as e:
                    if(session['count']>500):
                        break
                    print("line 89")
                    print(e)
                    pass
        else:
            return render_template('index.html',mesage = "Dear user, please enter correct Youtube URL")
        
        
        session['id1']=request.form["hiddenValueToRoute"]
        #print(session['id1'])
        video=None
        session['count']=0
        while video is None:
            session['count']+=1
            try:
                video = url.streams.get_by_itag(int(session['id1']))
            except Exception as e:
                if(session['count']>=500):
                    break
                print("line 101")
                print(e)
                pass
        
        video.stream_to_buffer(buffer)
        buffer.seek(0)
        session['title']=url.streams[0].title
        #session['title']=str(session['title']).replace(" ","_")
        
    except Exception as e:
        #print(e)
        mesage="Dear user,Unhandled Exception came please refresh"
        return render_template('index.html',mesage = mesage)
    try:
        if(session['optradio']=="option2"):
            return send_file(buffer,as_attachment=True,download_name=session['title']+".mp3",mimetype="audio/mpeg",)
        else:
            return send_file(buffer,as_attachment=True,download_name=session['title']+".mp4",mimetype="video/mp4",)
    except Exception as e:
        print(e)
        return "please reload server is busy"
    
'''@app.route('/downloadTest')
def downloadTest ():
    if os.path.exists("audio.mp3"):
      os.remove("audio.mp3")
      os.remove("video.mp4")
      os.remove("out.mp4")
    else:
      print("The file does not exist")
    yt= YouTube('https://www.youtube.com/watch?v=JZa7U91EflE',use_oauth=True, allow_oauth_cache=True)
    audio=yt.streams.filter(abr='160kbps', progressive=False).first().download(filename='/opt/render/audio.mp3')
    video=yt.streams.filter(res='1080p', progressive=False).first().download(filename='/opt/render/video.mp4')
    audio = ffmpeg.input('/opt/render/audio.mp3')
    video = ffmpeg.input('/opt/render/video.mp4')
    if os.path.exists("audio.mp3"):
        print('yessssssss')
    ffmpeg.output(audio, video, "/opt/render/out.mp4", codec='copy').run()
    path = "/opt/render/out.mp4"
    return send_file(path, as_attachment=True)'''



@app.route("/about")
def about():
    return "Developed BY Mukesh"

if __name__ == '__main__':
    app.run(port=5000,debug=True) 
