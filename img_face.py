 # -*- coding:utf-8 -*-
import cv2
import os
import sys
import shutil
import time
from face import DBConnect
from face import FaceAPI
outer_id="0x024"

reload(sys)
sys.setdefaultencoding('utf8')
conn = DBConnect.dbconnect()
cur = conn.cursor()

if not os.path.exists("./data/log/img_search.log"):
	os.mknod('./data/log/img_search.log')

def main():
	global i,filesdir
	fileList=filelist('./data/img_search/')
	with open('./data/log/img_search.log','r') as f:
		content=f.read()
	for i in fileList:
		if i in content:
			filesdir=i.split('/')[3]
			print"{}:-----------Has Been exist!".format(filesdir)
		if i not in content:
			filesdir1=i.split('/')[3]
			filesdir=i.split('/')[3].split('.')[0]
			if not os.path.exists('./data/img_search/{}'.format(filesdir)):
				os.makedirs('./data/img_search/{}/'.format(filesdir))
				shutil.copyfile('./data/img_search/{}'.format(filesdir1),'./data/img_search/{}/{}'.format(filesdir,filesdir1))
			detect(i)
			with open("./data/log/img_search.log",'a') as f:
				f.write(i)
def filelist(dir,topdown=True):
	fileList = [] 
 	for root, dirs, files in os.walk(dir, topdown):
		for PicName in files:
			fileList.append(os.path.join(root,PicName))
		return fileList

def get_detail():
	cur.execute("select * from face_data where face_token='%s'"%face_token)
	line=cur.fetchone()
	stuID,stuname,gender=line[0],line[1],line[3]
	detail=[stuID,stuname]
	print"StuID：{}".format(stuID)
	print"StuName：{}".format(stuname)
	print"gender：{}".format(gender)
	return detail
def detect(filename):
	global face_token
	count=0
	faces=[]
	face_cascade = cv2.CascadeClassifier('./data/cascades/haarcascade_frontalface_alt.xml')
	img = cv2.imread(filename)
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	faces=face_cascade.detectMultiScale(gray, 1.3, 5)

	ft=cv2.freetype.createFreeType2()
	ft.loadFontData(fontFileName='./data/font/simhei.ttf',id =0)

	for (x,y,w,h) in faces:
		img = cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,255),3)
		f = cv2.resize(gray[y:y+h, x:x+w], (200, 200))
		cv2.imwrite('./data/img_search/{}/{}.pgm'.format(filesdir,count), f)
		result=FaceAPI.searchItoI(image_file='./data/img_search/{}/{}.pgm'.format(filesdir,count),outer_id="{}".format(outer_id))
		if len(result)==4:
			break
		if result["results"][0]["confidence"] >= 80.00:
			print result["results"][0]["confidence"]
			face_token=result["results"][0]["face_token"]
			print"face_token：{}".format(face_token)
			detail=get_detail()
			ft.putText(img=img,text=detail[1], org=(x, y - 10), fontHeight=30,line_type=cv2.LINE_AA, color=(0,255,165), thickness=1, bottomLeftOrigin=True)
		else:
			print"Unknow face"
			cv2.putText(img,"Unknow", (x, y - 10), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0,0,225), 2)
		count+=1
	cv2.imwrite(i,img)
if __name__ == '__main__':
	main()
	print "have done!"