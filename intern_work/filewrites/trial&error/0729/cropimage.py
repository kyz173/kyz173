import argparse
parser = argparse.ArgumentParser()
parser.add_argument("filename", help="puts filename")

args = parser.parse_args()
answer = args.filename

f1 = open("TestDebug2"+answer+".yuv", 'r')
data = f1.read(1280*720)
f2 = open("TestDebug2"+answer+"_croped.yuv", 'w')
f2.write(data)
#print(data)
f1.close()
f2.close()
