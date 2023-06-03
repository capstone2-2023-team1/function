import os
import time

import cv2
import numpy as np
from django.http import HttpResponse
from google.cloud import storage

import run
import colmap2nerf


def transform(video, mask_id, identifier):
	w_start = time.time()
	f = open("log.txt", 'w')
	# storageURL = "https://storage.googleapis.com/nerf-video/"
	# videoName = "WIN_20220711_23_14_54_Pro.mp4" # 여기에 public 주소 되는지 확인하고 parameter로 받기
	videoFps = "2"
	aabb_scale = "1"
	# mask_id = "cup" # parameter
	imageFolderPath = os.path.dirname(os.path.abspath(__file__)) + '/server/images/'
	# 콜맵으로 영상 -> 이미지, 메타정보
	start = time.time()
	colmap2nerf.video2nerf(
		["--video_in", video, "--video_fps", videoFps, "--run_colmap", "--overwrite", "--aabb_scale", aabb_scale,
		 "--mask_categories", mask_id, "--images", imageFolderPath])
	end = time.time()
	f.write(f"{end - start:.5f} sec - colmap \n")

	start = time.time()

	for k in range(1000):

		img = cv2.imread(imageFolderPath + str(k + 1).zfill(4) + ".png")
		if img is None:
			break
		img_mask = cv2.imread(imageFolderPath + "dynamic_mask_" + str(k + 1).zfill(4) + ".png") / 255
		img = img * img_mask

		tempList = [[[0 for col in range(4)] for row in range(len(img[0]))] for depth in range(len(img))]

		for i in range(len(img)):
			for j in range(len(img[i])):
				tempList[i][j][0] = img[i][j][0]
				tempList[i][j][1] = img[i][j][1]
				tempList[i][j][2] = img[i][j][2]
				tempList[i][j][3] = 0 if (img[i][j][0] == 0 and img[i][j][1] == 0 and img[i][j][2] == 0) else 255
		result = np.array(tempList)
		if result.sum() != 0:
			cv2.imwrite(imageFolderPath + str(k + 1).zfill(4) + ".png", result)
		else:
			os.remove(imageFolderPath + str(k + 1).zfill(4) + ".png")
		os.remove(imageFolderPath + "dynamic_mask_" + str(k + 1).zfill(4) + ".png")
		print(k)

	end = time.time()
	f.write(f"{end - start:.5f} sec - image masking \n")

	folderPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	savePath = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/obj/' + identifier + '.obj'
	epoch = "3000"
	marching_cubes_res = "256"
	# 이미지, 메타정보 -> .obj or .ply
	print(folderPath)
	print(savePath)
	run.nerf2trd(["--scene", folderPath, "--save_mesh", savePath, "--train", "--n_steps", epoch, "--marching_cubes_res",
				  marching_cubes_res])
	w_end = time.time()
	f.write(f"{w_end - w_start:.5f} sec - all")
	f.close()

	# .obj 클라우드에 업로드
	file_path = savePath
	bucket_name = 'nerf-video'
	destination_blob_name = "obj/" + identifier + '.obj'

	client = storage.Client.from_service_account_json(
		os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/server/protean-pager-386913-984d487862d2.json')
	bucket = client.get_bucket(bucket_name)
	blob = bucket.blob(destination_blob_name)

	with open(file_path, 'rb') as file:
		content = file.read()

	blob.upload_from_string(content, content_type='application/octet-stream')

	response = 'https://storage.googleapis.com/nerf-video/' + destination_blob_name

	return HttpResponse(response)
