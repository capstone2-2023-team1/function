from django.shortcuts import render
import scripts.run
import scripts.video2trd


# Create your views here.
def trans(request):
	if request.method == 'GET':
		print(request.GET)
		video = request.GET.get('video')
		identifier = request.GET.get('identifier')
		print(video, identifier)
		scripts.video2trd.transform(video, identifier)
