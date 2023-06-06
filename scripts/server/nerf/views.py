from django.shortcuts import render
import sys
sys.path.append("/home/ysndy123/instant-ngp/scripts")
import run
import video2trd

def index(request):
    return render(request,'nerf/index.html')

# Create your views here.
def trans(request):
	if request.method == 'GET':
		video = request.GET.get('video')
		identifier = request.GET.get('identifier')
		mask_id = request.GET.get('mask_id')
		return video2trd.transform(video, mask_id, identifier)
