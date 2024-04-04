from pytube import YouTube
from pytube.innertube import _default_clients

_default_clients["ANDROID_MUSIC"] = _default_clients["ANDROID_CREATOR"]



url="https://youtube.com/shorts/2coq198v1vs?si=q3tVYAILOwXhfJ2e"

url= YouTube(url,use_oauth=False, allow_oauth_cache=True)

url_filter= url.streams.filter(progressive=True)

print(url_filter)


url.streams.get_by_itag(18).download(filename="video.mp4")
