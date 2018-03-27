import picamera
import time;

camera = picamera.PiCamera()

camera.resolution = (2592, 1944)
camera.framerate = (10)
#camera.start_preview(fullscreen=True)
camera.start_preview(fullscreen=False, window = (0, 0, 518, 388))


nr = 0;

def Shot(brightness, contrast):
	camera.brightness = brightness;
	camera.contrast = contrast;
	time.sleep(0.5);
	camera.capture('gopics/image' + str(nr) + '-b' + str(brightness) + 'c' + str(contrast) + '.jpg')

while(True):
	camera.brightness = 50;
	camera.contrast = 50;
	
	input("Press to shot");
	
	for c in range(0,100,20):
		for b in range(30,70,10):
			Shot(b,c);
	nr = nr+1;
	print(nr);
