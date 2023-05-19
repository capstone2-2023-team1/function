from django.shortcuts import render
import sys
sys.path.append("/home/ysndy123/instant-ngp/scripts")
import run
import video2trd

def index(request):
    return render(request,'main/index.html')

# Create your views here.
def trans(request):
	if request.method == 'GET':
		print(request.GET)
		video = request.GET.get('video')
		identifier = request.GET.get('identifier')
		print(video, identifier)
		video2trd.transform(video, identifier)
