import tkinter as tk
from tkinter import *
from tkinter import filedialog
from datetime import datetime
import re


def CAN_Decoder():
    dataFile = filedialog.askopenfilename()
    inputFrameData = []

    # Extract frame from text file using regex approach
    typicalFrameForm = r"can(\d)\s+([(\w)]{1,3})\s+\[(\d+)\]\s+([\w]{2}(?:\s[\w]{2})*)"
    for dataFrame in re.findall(typicalFrameForm, open(dataFile).read()):
        messageID = int(dataFrame[1], 16)
        dataSeg = dataFrame[3].split(" ")
        fData = split(dataSeg[0])
        fSize = 0
        fType = int(fData[0], 16)
        if fType == 0:
            fSize = int(fData[1], 16)
        elif fType == 1:
            fSize = int(fData[1] + dataSeg[1], 16)
        else:
            print("Continuous/Flow control Frame: " + str(fType))
        data = list(map(lambda x: int(x, 16), dataFrame[3].split(" ")))
        frameMap = {"MessageID": messageID,
                    "FrameType": fType,
                    "FrameSize": fSize,
                    "PayloadData": data}
        inputFrameData.append(frameMap)
    extractedData = CAN_ReAssembly(inputFrameData)

    # Output file
    dateTime = datetime.today().strftime('_%Y%m%d_%H%M%S')
    outputFileName = dataFile.split(".", 1)[0] + dateTime + '_Output.txt'
    decodedTextFile = open(outputFileName, "w")
    for element in extractedData:
        for item in element:
            decodedTextFile.write(str(item) + " ")
        decodedTextFile.write("\n")
    decodedTextFile.close()
    print('Decoded file generated. Please check at input file location.')


def split(word):
    return [char for char in word]


def CAN_ReAssembly(formattedRawData):
    extractedData = []
    lineCount = len(formattedRawData)
    inputData_dict = {}
    newLineCount = 0
    cFrameCount = 0
    for dataLineIndex, dataLine in enumerate(formattedRawData):
        frameType = dataLine["FrameType"]
        messageID = dataLine["MessageID"]
        frameSize = dataLine["FrameSize"]
        if frameType == 0:  # Single frame
            sFrameIndex = 1  # Single frame index
            payloadData = []
            for pData in dataLine["PayloadData"][sFrameIndex: sFrameIndex + frameSize]:
                payloadData.append(pData)
            frameMap = {"MessageID": messageID,
                        "FrameType": frameType,
                        "FrameSize": frameSize,
                        "PayloadData": payloadData}
            newLineCount += 1
            inputData_dict[str(newLineCount)] = frameMap
        elif frameType == 1:  # Continuous frame
            frameSize = dataLine["FrameSize"]
            eleCount = 0
            fFrameIndex = 2  # First frame index
            payloadData = []
            for pData in dataLine["PayloadData"][fFrameIndex:]:
                payloadData.append(pData)
                eleCount += 1
            startLineIndex = dataLineIndex + 1
            cFrameIndex = 1  # Consecutive frame index
            seqCount = -1
            startSeqNum = 33
            for i in range(startLineIndex, lineCount):
                dataLine_CF = formattedRawData[i]
                messageID_CF = dataLine_CF["MessageID"]
                if messageID == messageID_CF:
                    seqNum = dataLine_CF["PayloadData"][0]
                    if seqNum != 1:
                        seqCount += 1
                        if seqNum == startSeqNum + seqCount:
                            for pData in dataLine_CF["PayloadData"][cFrameIndex:]:
                                if eleCount <= frameSize:
                                    payloadData.append(pData)
                                    eleCount += 1
                    else:
                        break
            frameMap = {"MessageID": messageID,
                        "FrameType": frameType,
                        "FrameSize": frameSize,
                        "PayloadData": payloadData}
            newLineCount += 1
            inputData_dict[str(newLineCount)] = frameMap

        elif frameType > 2 and frameType >= 3:
            cFrameCount += 1  # No action required
    print(str(cFrameCount) + " consecutive frames found")

    for key, value in inputData_dict.items():
        newDataLine = [value["MessageID"]]
        for item in value["PayloadData"]:
            newDataLine.append(item)
        extractedData.append(newDataLine)
    return extractedData


# Create UI
parent = tk.Tk()
parent.title('CAN Decoder')
parent.geometry('300x50')
frame = tk.Frame(parent)
frame.pack()
fileButton = tk.Button(frame, text="Select CANData file(.txt)", fg="Green", command=CAN_Decoder())
fileButton.pack(side=LEFT)
exit_button = tk.Button(frame, text="Exit", fg="Red", command=quit)
exit_button.pack(side=RIGHT)
parent.mainloop()

