from pytube import YouTube 
from flask import Flask, send_file,render_template,request,session
from io import BytesIO
from flask_session import Session
import re
import os
import ffmpeg
from flask import send_file
import io


app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.secret_key = "YouTube Download"

@app.route("/")
def index():
    if not os.path.exists('/tmp/mukesh/'):
        os.makedirs('/tmp/mukesh/')
    clearEnv(os.path.join('/tmp/mukesh'))
    return render_template('index.html')

@app.route("/next_page", methods=["GET","POST"])
def next_page():
    if not os.path.exists('/tmp/mukesh/'):
        os.makedirs('/tmp/mukesh/')
    clearEnv(os.path.join('/tmp/mukesh'))
    validateVideoUrl = (r'(https?://)?(www\.)?''(youtube|youtu|youtube-nocookie)\.(com|be)/''(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    session['url']=request.form["video_url"]
    session['optradio']=request.form["optradio"]
    session['validVideoUrl'] = str(re.match(validateVideoUrl, session['url']))
    if(session['validVideoUrl']):
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
                    return render_template('index.html',mesage = "Dear user, Age Restricted Video ")
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
            except Exception as e:
                if(session['count']>=10):
                    break
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
                    break
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
        clearEnv(os.path.join('/tmp/mukesh'))
        buffer = BytesIO()
        if(session['url']):
            url=None
            session['count']=0
            while url is None:
                session['count']+=1
                try:
                    #url= YouTube(str(session['url']),use_oauth=True, allow_oauth_cache=True)
                    url= YouTube(str(session['url']))
                except Exception as e:
                    if(session['count']>10):
                        break
                    print(e)
                    pass
        else:
            clearEnv(os.path.join('/tmp/mukesh'))
            return render_template('index.html',mesage = "Dear user, please enter correct Youtube URL")
        
        
        if(session['optradio']=="option2"): #Audio
            session['id1']=request.form["hiddenValueToRoute"]
            video=None
            session['count']=0
            while video is None:
                session['count']+=1
                try:
                    video = url.streams.get_by_itag(int(session['id1']))
                except Exception as e:
                    if(session['count']>=10):
                        break
                    print(e)
                    pass
            
            video.stream_to_buffer(buffer)
            buffer.seek(0)
            session['title']=url.streams[0].title
            session['title']=str(session['title']).replace(" ","_")
            return send_file(buffer,as_attachment=True,download_name=session['title']+".mp3",mimetype="audio/mpeg",)
        elif(session['optradio']=="option1"): #Video
            session['id1']=request.form["hiddenValueToRoute"]
            # To download audio in app.rootpath
            clearEnv(os.path.join('/tmp/mukesh'))
            downloadAudio(session['url'])
            
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
            ffmpeg.output(audio, video, path, codec='copy').run(overwrite_output=True, cmd=r'/tmp/mukesh/ffmpeg-6.1-amd64-static')
            return send_file(path, as_attachment=True)                   
    except Exception as e:
        clearEnv(os.path.join('/tmp/mukesh'))
        mesage="Dear user,Please reload server is busy"
        print(e)
        return render_template('index.html',mesage = mesage)


@app.route('/downloadTest', methods=["GET","POST"])
def downloadTest ():
    session['url']=request.form["video_url"]
    if os.path.exists("audio.mp3"):
      os.remove("audio.mp3")
    if os.path.exists("video.mp3"):
      os.remove("video.mp4")
    if os.path.exists("out.mp4"):
      os.remove("out.mp4")
    else:
      print("The file does not exist")
    
    try:
        #yt= YouTube(session['url'])
        yt= YouTube(str(session['url']),use_oauth=False, allow_oauth_cache=True)
    except Exception as e:
        yt= YouTube(str(session['url']),use_oauth=False, allow_oauth_cache=True)
        print(e)
    print(yt.streams)
    tempName=''
    try:
        audio=yt.streams.filter(abr='128kbps', progressive=False).first().download(filename='audio.mp3')
        tempName='128kbps'
    except:
        try:
            audio=yt.streams.filter(abr='70kbps', progressive=False).first().download(filename='audio.mp3')
            tempName='70kbps'
        except:
            try:
                audio=yt.streams.filter(abr='50kbps', progressive=False).first().download(filename='audio.mp3')
                tempName='50kbps'
            except:
                    pass
    print('Audio Completed BitRate found :'+tempName)
    try:
        video=yt.streams.filter(res='2160p', progressive=False).first().download(filename='video.mp4')
        tempName='2160p'
    except Exception as e:
        print(e)
        try:
            video=yt.streams.filter(res='1440p', progressive=False).first().download(filename='video.mp4')
            tempName='1440p'
        except Exception as e:
            print(e)
            try:
                video=yt.streams.filter(res='1080p', progressive=False).first().download(filename='video.mp4')
                tempName='1080p'
            except Exception as e:
                print(e)
                try:
                    video=yt.streams.filter(res='720p', progressive=False).first().download(filename='video.mp4')
                    tempName='720p'
                except:
                    video=yt.streams.filter(res='360p').first().download(filename='video.mp4')
                    tempName='360p'
    print('Video Completed BitRate found :'+tempName)
    audio = ffmpeg.input('/tmp'+'/audio.mp3')
    video = ffmpeg.input('/tmp'+'/video.mp4')
    session['title']=str(yt.streams[0].title).replace('/','')
    path=os.path.join('/tmp', 'static/downloads/')
    #print(path)
    ffmpeg.output(audio, video, path+session['title']+".mp4", codec='copy').run()
    print('Video Completed BitRate Downloaded :'+tempName)
    message="Downloaded File"+str(session['title']) + "with "+ tempName + " Quality"
    return render_template('index.html',mesage = message)


def clearEnv(path):
    files = os.listdir(path)
    for file in files:
        if file.endswith('.mp4') or file.endswith('.mp3'):
            file_path = os.path.join(path, file)
            os.remove(file_path)
   
def downloadAudio(url):
    session['url']=url
    try:
        yt= YouTube(str(session['url']),use_oauth=False, allow_oauth_cache=True)
    except Exception as e:
        yt= YouTube(str(session['url']),use_oauth=False, allow_oauth_cache=True)
        print(e)
    #print(yt.streams)
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
    #audio = ffmpeg.input('/tmp'+'/audio.mp3')
    print('Audio Completed BitRate found : '+tempName)


@app.route("/about")
def about():
    return "Developed BY Mukesh"

if __name__ == '__main__':
    app.run(port=5000,debug=True) 
