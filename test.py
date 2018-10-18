from pathlib import Path

pol = []
IZA = []
VZA = []
data = []
wavelengths = []

pathToFile = Path("C:/Users/lanevsd1/Dmitri/Work files/Reflectance measurements/300818_1500_14_0i.csv")
f = open(pathToFile, 'r')

lines = []
for line in f:
    lines.append(line.strip())

Headers_string = lines[0]
Headers = Headers_string.split(',,')
Headers = Headers[3:(len(Headers)-1)]

for header in Headers:
    pol.append(header[0])
    hParts = header.split('/')
    IZA.append(float(hParts[0][1:]))
    VZA.append(float(hParts[1]))

for i in range(2,len(lines)):
    line = lines[i].split(',')
    line = line[0:len(line)-1]
    dataRow = []
    for j in range(0,len(line)):
        if j%2 != 0:
            dataRow.append(float(line[j]))
    data.append(dataRow)
    wavelengths.append(line[0])

