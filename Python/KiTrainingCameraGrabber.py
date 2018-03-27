from hardware.Light import Light
import picamera
import time;

camera = picamera.PiCamera()
camera.resolution = (2592, 1944)
camera.framerate = (10)
#camera.start_preview(fullscreen=True)
camera.start_preview(fullscreen=False,  window = (-600,-600, 2592, 1944))
#camera.start_preview(fullscreen=False,  window = (0, 0, 518, 388)) #window = (0, 0, 2592, 1944))


nr = 0;

def Shot(brightness, contrast):
	camera.brightness = brightness;
	camera.contrast = contrast;
	time.sleep(0.1);
	camera.capture('KiTrainingPics/image' + str(nr) + '-b' + str(brightness) + 'c' + str(contrast) + '.jpg')


groveLightDigitalPort = 8;
light = Light(groveLightDigitalPort);
light.On();


ended = False;
while(ended == False):
	print (camera.brightness);
	camera.brightness = 50;
	camera.contrast = 50;
	
	inp = input("Press to shot or x to exit");
	
	if (inp == "x"):
		ended = True;
	else:
		for contrast in range(0,100,20):
			for bright in range(30,70,10):
				print(str(nr) + " " + str(bright) + " " + str(contrast));
				Shot(bright,contrast);
		nr = nr+1;
		print(nr);
	
light.Off();
