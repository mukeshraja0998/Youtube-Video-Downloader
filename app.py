from pytube import YouTube 
from flask import Flask, send_file,render_template,request,session
from io import BytesIO
from flask_session import Session
import re
import os
import ffmpeg
from flask import send_file
import io
import shutil
from pytube.innertube import _default_clients
_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.secret_key = "YouTube Download"

@app.route("/")
def index():
    try:
        shutil.rmtree(os.path.join("/app/.git"))
        print(".git deleted")
    except:
        pass
    if not os.path.exists('/tmp/mukesh/'):
        os.makedirs('/tmp/mukesh/')
    clearEnv(os.path.join('/tmp/mukesh'))
    return render_template('index.html')

@app.route("/next_page", methods=["GET","POST"])
def next_page():
    _default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]
    
    try:
        shutil.rmtree(os.path.join("/app/.git"))
    except:
        pass
    if not os.path.exists('/tmp/mukesh/'):
        os.makedirs('/tmp/mukesh/')
    clearEnv(os.path.join('/tmp/mukesh'))
    validateVideoUrl = (r'(https?://)?(www\.)?''(youtube|youtu|youtube-nocookie)\.(com|be)/''(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    session['url']=request.form["video_url"]
    session['optradio']=request.form["optradio"]
    session['validVideoUrl'] = str(re.match(validateVideoUrl, session['url']))
    if(session['validVideoUrl']):
        session['count']=0
        global url
        url=None
        while url is None:
            session['count']+=1
            try:
                url= YouTube(str(session['url']),use_oauth=False, allow_oauth_cache=True)
                session['thumbnail_url']=url.thumbnail_url
            except Exception as e:
                try:
                    url= YouTube(str(session['url']))
                    session['thumbnail_url']=url.thumbnail_url
                except:
                    if(session['count']>=10):
                        return render_template('index.html',mesage = "Dear user, Age Restricted Video")
                    print(e)
                    pass
    else:
        return render_template('index.html',mesage = "Dear user, please enter correct Youtube URL ")
    if(session['optradio']=="option1"): #Video
        li=[]
        url_filter=None
        session['count']=0
        while url_filter is None:
            session['count']+=1
            try:
                url_filter= url.streams.filter(only_video=True)
                #print(url_filter)
            except Exception as e:
                if(session['count']>=10):
                    return render_template('index.html',mesage = "Dear user, Age Restricted Video ")
                print(e)
                pass        
        for i,b in url_filter.itag_index.items():
            temp=[]
            if(int(b.filesize_mb<5000)):
                temp.append(b.resolution)
                temp.append(b.filesize_mb)
                temp.append(b.fps)
                temp.append(i)
                li.append(temp)
                session['name']=b.title
        li=sorted(li, key=lambda x: x[1])
        return render_template('index2.html',videoList=li,name=session['name'],image=session['thumbnail_url'])
    
    elif(session['optradio']=="option2"): #Audio
        li=[]
        url_filter=None
        session['count']=0
        while url_filter is None:
            session['count']+=1
            try:
                url_filter= url.streams.filter(only_audio=True)
            except Exception as e:
                if(session['count']>=10):
                    return render_template('index.html',mesage = "Dear user, Age Restricted Video")
                print(e)
                pass
        for i,b in url_filter.itag_index.items():
            temp=[]
            if(int(b.filesize_mb<150)):
                temp.append(b.abr)
                temp.append(b.filesize_mb)
                temp.append(i)
                session['name']=b.title
                li.append(temp)
        li=sorted(li, key=lambda x: x[1])
        return render_template('index2.html',audioList=li,name=session['name'],image=session['thumbnail_url'])


@app.route("/download", methods=["GET","POST"])
def download():
    try:
        shutil.rmtree(os.path.join("/app/.git"))
    except:
        pass
    try:
        global url        
        if(session['optradio']=="option2"): #Audio
            clearEnv(os.path.join('/tmp/mukesh'))
            session['id1']=request.form["hiddenValueToRoute"]
            video=None
            session['count']=0
            session['title']=url.streams[0].title
            session['title']=str(session['title']).replace(" ","_")
            session['title']=str(url.streams[0].title).replace('/','')
            path=os.path.join('/tmp', 'mukesh/'+session['title']+".mp3")
            while video is None:
                session['count']+=1
                try:
                    video = url.streams.get_by_itag(int(session['id1'])).download(filename=path)
                except Exception as e:
                    if(session['count']>=10):
                        break
                    print(e)
                    pass
            path=os.path.join('/tmp', 'mukesh/'+session['title']+".mp3")
            return send_file(str(path), as_attachment=True)   
        elif(session['optradio']=="option1"): #Video
            session['id1']=request.form["hiddenValueToRoute"]
            clearEnv(os.path.join('/tmp/mukesh'))
            downloadAudio(url)            
            video=None
            session['count']=0
            while video is None:
                session['count']+=1
                try:
                    output_path = os.path.join('/tmp/mukesh', "video" + '.' + "mp4")
                    video = url.streams.get_by_itag(int(session['id1'])).download(filename=output_path)
                except Exception as e:
                    if(session['count']>=10):
                        break
                    print(e)
                    pass
            # Merge audio and video
            audio = ffmpeg.input('/tmp/mukesh/'+'audio.mp3')
            video = ffmpeg.input('/tmp/mukesh/'+'video.mp4')
            session['title']=str(url.streams[0].title).replace('/','')
            path=os.path.join('/tmp', 'mukesh/'+session['title']+".mp4")
            newpath = (os.path.join(app.root_path, 'ffmpeg-6.1-amd64-static'))
            ffmpeg.output(audio, video, path, codec='copy').run(overwrite_output=True, cmd=newpath+'/ffmpeg')
            return send_file(path, as_attachment=True)                   
    except Exception as e:
        mesage="Dear user,Please reload server is busy"
        print(e)
        return render_template('index.html',mesage = mesage)

def clearEnv(path):
    files = os.listdir(path)
    for file in files:
        if file.endswith('.mp4') or file.endswith('.mp3'):
            file_path = os.path.join(path, file)
            os.remove(file_path)
   
def downloadAudio(yt):
    tempName=''
    output_path = os.path.join('/tmp/mukesh', "audio" + '.' + "mp3")
    try:
        audio=yt.streams.filter(abr='128kbps', progressive=False).first().download(filename=output_path)
        tempName='128kbps'
    except:
        try:
            audio=yt.streams.filter(abr='70kbps', progressive=False).first().download(filename=output_path)
            tempName='70kbps'
        except:
            try:
                audio=yt.streams.filter(abr='50kbps', progressive=False).first().download(filename=output_path)
                tempName='50kbps'
            except:
                    pass
    print('Audio Completed BitRate found : '+tempName)


@app.route("/about")
def about():
    return "Developed BY Mukesh"

if __name__ == '__main__':
    app.run(debug=True) 
