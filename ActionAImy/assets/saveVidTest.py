import cv2

width = 1280
height = 720

#name = 'out.avi'
#fourcc = cv2.VideoWriter_fourcc(*'XVID')
#out = cv2.VideoWriter(name, fourcc, 30.0, (width, height))

name = 'out.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(name, fourcc, 30.0, (width, height))

#outMap = cv2.VideoWriter('outMap.avi', fourcc, 30, (1000,1000))
#outCanny = cv2.VideoWriter('outCanny.avi', fourcc, 30, (640,320),0) #because 1 channel

cap = cv2.VideoCapture('mago.mp4')

while True:
    ret, frame = cap.read()
    out.write(frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
out.release()
#cap.release()
