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
    frameSize = 0
    for dataFrame in re.findall(typicalFrameForm, open(dataFile).read()):
        diagnosticID = int(dataFrame[1], 16)
        data = list(map(lambda x: int(x, 16), dataFrame[3].split(" ")))
        frameType = data[0]
        if frameType <= 6:
            frameSize = frameType  # Single frame
        elif frameType == 16:  # 10 for hex notation
            frameSize = data[1]
        frameMap = {"DiagnosticID": diagnosticID,
                    "FrameType": frameType,
                    "FrameSize": frameSize,
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


def CAN_ReAssembly(formattedRawData):
    extractedData = []
    lineCount = len(formattedRawData)
    inputData_dict = {}
    newLineCount = 0
    cFrameCount = 0
    for dataLineIndex in range(0, lineCount):
        dataLine = formattedRawData[dataLineIndex]
        frameType = dataLine["FrameType"]
        diagnosticId = dataLine["DiagnosticID"]
        frameSize = dataLine["FrameSize"]
        if frameType <= 6:      # Single frame
            sFrameIndex = 1     # Single frame index
            payloadData = []
            for i in range(sFrameIndex, sFrameIndex + frameSize):
                payloadData.append(dataLine["PayloadData"][i])
            frameMap = {"DiagnosticID": diagnosticId,
                        "FrameType": frameType,
                        "FrameSize": frameSize,
                        "PayloadData": payloadData}
            newLineCount += 1
            inputData_dict[str(newLineCount)] = frameMap
        elif frameType == 16:   # 10 for hex notation | Continuous frame
            frameSize = dataLine["FrameSize"]
            eleCount = 0
            fFrameIndex = 2     # First frame index
            payloadData = []
            for j in range(fFrameIndex, len(dataLine["PayloadData"])):
                payloadData.append(dataLine["PayloadData"][j])
                eleCount += 1
            startLineIndex = dataLineIndex + 1
            cFrameIndex = 1     # Consecutive frame index
            seqCount = -1
            startSeqNum = 33    # 21 for hex notation
            for i in range(startLineIndex, lineCount):
                dataLine_CF = formattedRawData[i]
                diagnosticID_CF = dataLine_CF["DiagnosticID"]
                if diagnosticId == diagnosticID_CF:
                    seqNum = dataLine_CF["PayloadData"][0]
                    if seqNum != 16:   # 10 for hex notation
                        seqCount += 1
                        if seqNum == startSeqNum + seqCount:
                            for j in range(cFrameIndex, len(dataLine_CF["PayloadData"])):
                                if eleCount <= frameSize:
                                    payloadData.append(dataLine_CF["PayloadData"][j])
                                    eleCount += 1
                    else:
                        break
            frameMap = {"DiagnosticID": diagnosticId,
                        "FrameType": frameType,
                        "FrameSize": frameSize,
                        "PayloadData": payloadData}
            newLineCount += 1
            inputData_dict[str(newLineCount)] = frameMap

        elif frameType > 32 and frameType >= 48:   # 20 & 30 for hex notation
            cFrameCount += 1     # No action required
    print(str(cFrameCount) + " consecutive frames found")

    for key, value in inputData_dict.items():
        newDataLine = [value["DiagnosticID"]]
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
