import cv2, os, re, time
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials

# azure prereqs
region = 'eastus' # os.environ['ACCOUNT_REGION']
key =  os.environ['ACCOUNT_KEY'] # you will need to get your own key if you want to test the app
credentials = CognitiveServicesCredentials(key)
client = ComputerVisionClient(
    endpoint="https://" + region + ".api.cognitive.microsoft.com/",
    credentials=credentials
)

### start a live video feed with (mac) webcam
cap = cv2.VideoCapture(0)
while(True):
    ret, frame = cap.read()
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2BGRA)
    cv2.imshow('frame', rgb)
    if cv2.waitKey(1) & 0xFF == ord('q'): # on 'q' key, take an image (with desired phone number in it)
        out = cv2.imwrite('cap.jpeg', frame)
        break
cap.release()
cv2.destroyAllWindows()
###


img = 'cap.jpeg'

raw = True
numberOfCharsInOperationId = 36

# SDK call
with open(img, 'rb') as f:
    rawHttpResponse = client.read_in_stream(f, language="en", raw=True)

# Get ID from returned headers
operationLocation = rawHttpResponse.headers["Operation-Location"]
idLocation = len(operationLocation) - numberOfCharsInOperationId
operationId = operationLocation[idLocation:]

# SDK call
result = client.get_read_result(operationId)

print(result) # => result.running

while result.status != OperationStatusCodes.succeeded:
    print('waiting', result.status)
    time.sleep(1)
    result = client.get_read_result(operationId)

total = []

# Get data
if result.status == OperationStatusCodes.succeeded:

    for line in result.analyze_result.read_results[0].lines:
        print(line.text)
        # print(line.bounding_box)
        total.append(line.text)
else:
    print('unsuccessful', result.status)

print(total)

# regex key:
# [0-9(+][0-9() -]{9,16}

pattern = '[0-9(+][0-9() -]{9,16}' # the regex key is what points out the phone numbers
test_string = total

# collects captured phone numbers in image
result = []
for item in total:
    result = result + re.findall(pattern, item)

if result:
    print("Search successful.")
    print(result) # prints out all captured phone numbers
else:
    print("Search unsuccessful.")


