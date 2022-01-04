import tkinter as tk
from tkinter import *
from tkinter import filedialog
from datetime import datetime


# Function for opening the file
def CAN_Decoder():
    lineNum = 0
    oldDataFile = filedialog.askopenfile(initialdir="/")
    listedOldData = []
    for dataLine in oldDataFile:
        segmentedDataLine = dataLine.split(" ")
        listedOldDataLine = []
        for stringSegment in segmentedDataLine:
            if stringSegment.strip():
                listedOldDataLine.append(stringSegment)
        listedOldData.append(listedOldDataLine)
        lineNum = lineNum + 1

    newData = []
    lineCount = len(listedOldData)
    for dataLineIndex in range(0, lineCount):
        dataLine = listedOldData[dataLineIndex]
        refinedDataLine = []
        frameType = int(dataLine[3])

        # SingleFrame
        if frameType <= 6:
            refinedDataLine.append(dataLine[1])
            index = 4
            for i in range(index, index + frameType):
                refinedDataLine.append(dataLine[i])
            p = ' '.join(refinedDataLine)
            newData.append(p)

        # Multi frame
        elif frameType == 10:
            # First frame data
            diagnosticID = dataLine[1]
            frameSize = int(dataLine[4], 16)
            refinedDataLine.append(dataLine[1])
            index = 5
            eleCount = 0
            for j in range(index, len(dataLine)):
                refinedDataLine.append(dataLine[j])
                eleCount += 1

            # Add consecutive frame data
            startLineIndex = dataLineIndex + 1
            index = 4
            seqCount = -1
            startSeqNum = 21
            for i in range(startLineIndex, lineCount):
                dataLineCF = listedOldData[i]
                CFdiagnosticID = dataLineCF[1]
                if diagnosticID == CFdiagnosticID:
                    seqNum = int(dataLineCF[3])
                    if seqNum != 10:
                        seqCount += 1
                        if seqNum == startSeqNum + seqCount:
                            for j in range(index, len(dataLineCF)):
                                if eleCount <= frameSize:
                                    refinedDataLine.append(dataLineCF[j])
                                    eleCount += 1
                        #else:
                            #print('Sequence Number mismatch found: ', seqNum, seqCount)
                    else:
                        break
            temp = []
            for element in refinedDataLine:
                temp.append(element.strip())
            refinedDataLine = temp
            p = ' '.join(refinedDataLine)
            newData.append(p)

        # Flow control frame
        #elif frameType == 30:
            # Do nothing
            #newData.append('FCF')

        # Consecutive frame
        #else:
            # Do nothing
            #newData.append('CF')

    # Output file
    dateTime = datetime.today().strftime('_%Y%m%d_%H%M%S')
    outputFileName = oldDataFile.name.split(".", 1)[0] + dateTime + '_Output.txt'
    decodedTextFile = open(outputFileName, "w")
    for element in newData:
        decodedTextFile.write(element + "\n")
    decodedTextFile.close()
    print('Decoded file generated. Please check at original file location.')


# Create UI
parent = tk.Tk()
parent.title('CAN Decoder')
parent.geometry('300x50')
frame = tk.Frame(parent)
frame.pack()
fileButton = tk.Button(frame, text="Select CANData file(.txt)", fg="Green", command=lambda: CAN_Decoder())
fileButton.pack(side=LEFT)
exit_button = tk.Button(frame, text="Exit", fg="Red", command=quit)
exit_button.pack(side=RIGHT)
parent.mainloop()
