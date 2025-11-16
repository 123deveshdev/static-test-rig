# sck--2
# dt--3
#r----recording start of stop
#s---saving start or stop
#d----display graph
import cv2
import serial
import datetime
import cvzone
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import pyaudio
import wave
import threading

#audio
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
au = pyaudio.PyAudio()
stream = au.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)


#serial
ser = serial.Serial('COM9', 9600)
ser.write(b"OFF")

# data aquisition
file_object = open('data.csv', 'w')
file_object.write("time,force\n")

# video object
cap = cv2.VideoCapture(1)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output.avi', fourcc, 11.0, (1024, 720))

#random variable
p=0
sdat=False
recording = False

#audio function
def record_audio():
    global recording
    frames = []
    while recording:
        data = stream.read(CHUNK)
        frames.append(data)
    stream.stop_stream()
    stream.close()
    au.terminate()
    wf = wave.open('audio.wav', 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(au.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

audio_thread = threading.Thread(target=record_audio)

try:
    while True:
        # Capture frame-by-frame
        if p==0:
            ret, frame = cap.read()
            frame = cv2.resize(frame, (1024, 720))

        # DATA PROCESSING
        a = datetime.datetime.now()
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")
        sensor_data = ser.readline().decode('utf-8')
        k = sensor_data.replace('\r\n', '')
        newtons = abs(float(k) * 0.00981)
        n = str(round(newtons, 6))
        o = timestamp + "," + n + '\n'
        # print(o)

        #WINODW DISPLAY
        cv2.putText(frame, "Force: ", (642, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 2)
        cv2.putText(frame, str(abs(round(newtons, 2))) + "N", (840, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 2)
        cv2.putText(frame, str(a), (3, 715), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        print(sdat,recording,n)
        if p==1:
            imgFront = cv2.imread("graph.png", cv2.IMREAD_UNCHANGED)
            imgFront = cv2.resize(imgFront, (1024, 720))

            frame = cvzone.overlayPNG(frame, imgFront, [0, 0])
            cap.release()


        cv2.imshow('Frame', frame)
        key = cv2.waitKey(1)


        if key == ord('r'):
            if not recording:
                recording = True
                audio_thread.start()
                print("Recording started...")
            else:
                print("rec stopped")
                recording = False


        if recording:
            out.write(frame)

        if key==ord('s'):
            if not sdat:
                ser.write(b"ON")

                sdat=True
            elif sdat:
                sdat=False
                ser.write(b"OFF")


        if key==ord('d'):
            file_object.close()
            sdat=False
            data = pd.read_csv('data.csv')
            j = data.iloc[:, 0].tolist()
            print(j)
            plt.figure(figsize=(10.5, 7.5))

            plt.rcParams.update({"grid.linewidth": 0.5, "grid.alpha": 0.5})
            # plt.style.use("dark_background")

            sns.set_style("darkgrid", {"grid.linewidth": 0.5, "grid.alpha": 0.5})
            sns.lineplot(x='time', y='force', data=data)

            # plt.xticks(data["force"].head(10), rotation=45)
            plt.xticks([])
            plt.savefig("graph.png", dpi=300)
            sdat=False
            p=1

        if sdat:
            # file_object = open('data.csv', 'a')
            file_object.write(o)

            # print("data being recorded")

        if key == ord('q'):
            break

except KeyboardInterrupt:

    recording=False
    file_object.close()
    ser.write(b"OFF")
    ser.close()
    print("rec stopped")

cap.release()
ser.close()
out.release()
cv2.destroyAllWindows()
audio_thread.join()

