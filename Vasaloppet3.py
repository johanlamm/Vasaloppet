
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, TextBox
import datetime


initFriction = 0.05
initVo2Max = 60
initWaxPenalty = 0
initMass = 70
initHeight = 170
initIntensityFactor = 0.7
initAbsolut = initVo2Max*initMass/1000
initPower = initAbsolut/60*5*4184*0.18*initIntensityFactor


df = pd.read_csv('vasaloppet.csv')
df = df.dropna()
onlyDP = False

def GetTime(frictionGlide,vo2Max,waxPenalty,mass,height,intensityFactor,courseProfile):

    height = int(height)
    mass = float(mass)
    intensityFactor = float(intensityFactor)

    cdA = 0.0035*height
    rho = 1.2
    G=9.82

    totalTime = 0
    fTime = 0
    dpTime = 0
    dpkTime = 0
    diaTime = 0
    totalTimeOnlyDP = 0
    fTimeOnlyDP = 0
    dpTimeOnlyDP = 0
    hbTimeOnlyDP = 0

    for index,data in courseProfile.iterrows():

        distance = data[0]
        gradient = data[1]

        frictionOnlyDP = frictionGlide
        friction = frictionGlide*(1+waxPenalty/100)

        effiency = 0.18 + (friction+gradient-0.04)*0.25
        effiencyOnlyDP = min(effiency,0.18)

        resistanceCoeff = mass*G*(friction+gradient)
        resistanceCoeffOnlyDP = mass*G*(frictionOnlyDP+gradient)

        dragCoeff = cdA*rho/2
        skiingPower = (vo2Max*mass/1000)/60*5*4184*effiency*intensityFactor
        skiingPowerOnlyDP = (vo2Max*mass/1000)/60*5*4184*effiencyOnlyDP*intensityFactor

        p = np.polynomial.Polynomial([-skiingPower,resistanceCoeff,0,dragCoeff])
        r = p.roots()
        r = r.real[abs(r.imag) < 1e-5]
        r = r.real[r.real > 0]
        r = r[0]

        time = distance/r

        pOnlyDP = np.polynomial.Polynomial([-skiingPowerOnlyDP, resistanceCoeffOnlyDP, 0, dragCoeff])
        rOnlyDP = pOnlyDP.roots()
        rOnlyDP = rOnlyDP.real[abs(rOnlyDP.imag) < 1e-5]
        rOnlyDP = rOnlyDP.real[rOnlyDP.real > 0]
        rOnlyDP = rOnlyDP[0]

        timeOnlyDP = distance / rOnlyDP

        if (friction+gradient < -0.02 and r > 5):
            fTimeOnlyDP += timeOnlyDP
        if (rOnlyDP < 2.5):
            hbTimeOnlyDP += timeOnlyDP
        else:
            dpTimeOnlyDP += timeOnlyDP
        totalTimeOnlyDP += timeOnlyDP

        if (friction+gradient < -0.02 and r > 5):
            fTime += time
        elif friction+gradient < 0.06:
            dpTime += time
        elif friction+gradient < 0.09:
            dpkTime += time
        else:
            diaTime += time

        totalTime += time

    return(totalTime,fTime,dpTime,dpkTime,diaTime,totalTimeOnlyDP,fTimeOnlyDP,dpTimeOnlyDP,hbTimeOnlyDP)


# Create the figure and the line that we will manipulate
fig, ax = plt.subplots()
ax.axis([0, 9*60*60, 0, 1])
plt.yticks([])
plt.xlabel('Åktid [h]')
plt.xticks([60*60*1,60*60*2,60*60*3,60*60*4,60*60*5,60*60*6,60*60*7,60*60*8],['1','2','3','4','5','6','7','8'])
plt.title('Åktid och tid i deltekniker för vasaloppet klassiskt/stakning')
plt.grid()

texts = ['Åktid: ','Tid CR: ','Tid DP :','Tid DPK: ','Tid DIA: ']
textsOnlyDP = ['Åktid bara DP: ', 'Tid CR: ','Tid DP: ','Tid HB: ']
colors = ['black','blue','green','yellow','orange']
colorsOnlyDP = ['black','blue','green','red']
positions = [0.9,0.8,0.7,0.6,0.5]
positionsOnlyDP = [0.9,0.8,0.7,0.6]
labels = ['DP','DPK','DIA']
labelsOnlyDP = ['DP','HB']

alltimes = GetTime(initFriction,initVo2Max,initWaxPenalty,initMass,initHeight,initIntensityFactor,df)

times = alltimes[0:5]
timeStrings = []
cumTime = np.cumsum(times[1:])
xPositions = np.insert(np.cumsum(times[1:]),0,0)

timesOnlyDP = alltimes[5:]
timeStringsOnlyDP = []
cumTimeOnlyDP = np.cumsum(timesOnlyDP[1:])
xPositionsOnlyDP = np.insert(np.cumsum(timesOnlyDP[1:]),0,0)

for t in times:
    tStr = str(datetime.timedelta(seconds=t))
    tStr = ':'.join(str(tStr).split(':')[:2])
    timeStrings.append(tStr)

for t in timesOnlyDP:
    tStr = str(datetime.timedelta(seconds=t))
    tStr = ':'.join(str(tStr).split(':')[:2])
    timeStringsOnlyDP.append(tStr)

textBoxes = []
textBoxesOnlyDP = []
annotates = []
annotatesOnlyDP = []

heigthInPlot = 0.1
heightInPlotOnlyDP = 0.3

for timeString,xpos,time in zip(timeStrings[1:],xPositions,times[1:]):
    if time > 30*60:
        annotates.append(ax.annotate(timeString,(xpos,heigthInPlot)))
    else:
        annotates.append(ax.annotate('', (xpos, heigthInPlot)))

for timeString,xpos,time in zip(timeStringsOnlyDP[1:],xPositionsOnlyDP,timesOnlyDP[1:]):
    if time > 30*60:
        annotatesOnlyDP.append(ax.annotate(timeString,(xpos,heightInPlotOnlyDP)))
    else:
        annotatesOnlyDP.append(ax.annotate('', (xpos, heightInPlotOnlyDP)))


for text,color,position,timeString in zip(texts,colors,positions,timeStrings):
    textBox = ax.text(400, position, text + timeString, style='italic',
        bbox={'facecolor': color, 'alpha': 0.5, 'pad': 1})
    textBoxes.append(textBox)

for text,color,position,timeString in zip(textsOnlyDP,colorsOnlyDP,positionsOnlyDP,timeStringsOnlyDP):
    textBox = ax.text(32000, position, text + timeString, style='italic',
        bbox={'facecolor': color, 'alpha': 0.5, 'pad': 1},ha='right')
    textBoxesOnlyDP.append(textBox)


timeBars = [ax.barh(heigthInPlot,times[1],color='blue',alpha=0.8,height=0.1,label='CR')]
timeBarsOnlyDP = [ax.barh(heightInPlotOnlyDP,timesOnlyDP[1],color='blue',alpha=0.8,height=0.1,label='CR')]

for time,lastTime,color,label in zip(times[2:],cumTime[:-1],colors[2:],labels):
    bar = ax.barh(heigthInPlot,time, left=lastTime,color=color,alpha=0.8,height=0.1,label= label)
    timeBars.append(bar)

for time,lastTime,color,label in zip(timesOnlyDP[2:],cumTimeOnlyDP[:-1],colorsOnlyDP[2:],labelsOnlyDP):
    bar = ax.barh(heightInPlotOnlyDP,time, left=lastTime,color=color,alpha=0.8,height=0.1,label= label)
    timeBarsOnlyDP.append(bar)





axcolor = 'lightgoldenrodyellow'
ax.margins(x=0)

# adjust the main plot to make room for the sliders
plt.subplots_adjust(left=0.25, bottom=0.3)

# Make a horizontal slider to control the frequency.
axfreq1 = plt.axes([0.25, 0.05, 0.65, 0.03], facecolor=axcolor)
axfreq2 = plt.axes([0.25, 0.15, 0.65, 0.03], facecolor=axcolor)
axfreq3 = plt.axes([0.25, 0.10, 0.65, 0.03], facecolor=axcolor)
axbox1 = plt.axes([0.15, 0.7, 0.05, 0.05])
axbox2 = plt.axes([0.15, 0.65, 0.05, 0.05])
axbox3 = plt.axes([0.15, 0.6, 0.05, 0.05])

axbox4 = plt.axes([0.15, 0.5, 0.05, 0.05])
axbox5 = plt.axes([0.15, 0.45, 0.05, 0.05])


frictionSlider = Slider(
    ax=axfreq1,
    label='Friktion',
    valmin=0.01,
    valmax=0.08,
    valinit=initFriction,
)
vo2MaxSlider = Slider(
    ax=axfreq2,
    label='Relativt syreupptag [l/min kg]',
    valmin=30,
    valmax=90,
    valinit=initVo2Max,
)
waxPenaltySlider = Slider(
    ax=axfreq3,
    label='Ökad friktion från fästvalla [%]',
    valmin=0,
    valmax=20,
    valinit=initWaxPenalty,
)

massBox = TextBox(axbox1, 'Vikt [kg] ', initial=initMass)
heightBox = TextBox(axbox2, 'Längd [cm] ', initial=initHeight)
intensityBox = TextBox(axbox3, 'Intensitet ', initial=initIntensityFactor)
absolutBox = TextBox(axbox4, 'Syreupptag [l/min] ', initial=initAbsolut)
powerBox = TextBox(axbox5, 'Åkeffekt [W] ', initial="{:.0f}".format(initPower))




# The function to be called anytime a slider's value changes
def Update(val):



    absolutBox.set_val("{:.1f}".format(float(massBox.text)*vo2MaxSlider.val/1000))
    powerBox.set_val("{:.0f}".format((float(massBox.text)*vo2MaxSlider.val/1000)/60*5*4184*0.18*float(intensityBox.text)))

    alltimes = GetTime(frictionSlider.val, vo2MaxSlider.val,waxPenaltySlider.val,massBox.text,heightBox.text,intensityBox.text,df)

    times = alltimes[0:5]
    cumTime = np.cumsum(times[1:])
    xPositions = np.insert(np.cumsum(times[1:]),0,0)

    timesOnlyDP = alltimes[5:]
    cumTimeOnlyDP = np.cumsum(timesOnlyDP[1:])
    xPositionsOnlyDP = np.insert(np.cumsum(timesOnlyDP[1:]),0,0)

    timeStrings = []
    timeStringsOnlyDP = []

    for t in times:
        tStr = str(datetime.timedelta(seconds=t))
        tStr = ':'.join(str(tStr).split(':')[:2])
        timeStrings.append(tStr)

    for t in timesOnlyDP:
        tStr = str(datetime.timedelta(seconds=t))
        tStr = ':'.join(str(tStr).split(':')[:2])
        timeStringsOnlyDP.append(tStr)

    for textBox,text,timeString in zip(textBoxes,texts,timeStrings):
        textBox.set_text(text + timeString)

    for textBox,text,timeString in zip(textBoxesOnlyDP,textsOnlyDP,timeStringsOnlyDP):
        textBox.set_text(text + timeString)

    timeBars[0][0].set_width(times[1])
    timeBarsOnlyDP[0][0].set_width(timesOnlyDP[1])

    for timeBar,left,width in zip(timeBars[1:],cumTime[:-1],times[2:]):
        timeBar[0].set_width(width)
        timeBar[0].set_x(left)

    for timeBar,left,width in zip(timeBarsOnlyDP[1:],cumTimeOnlyDP[:-1],timesOnlyDP[2:]):
        timeBar[0].set_width(width)
        timeBar[0].set_x(left)

    for annotate,timeString, xpos,time in zip(annotates,timeStrings[1:], xPositions,times[1:]):

        if time > 30*60:
            annotate.set_text(timeString)
        else:
            annotate.set_text('')
        annotate.set_x(xpos)

    for annotate, timeString, xpos, time in zip(annotatesOnlyDP, timeStringsOnlyDP[1:], xPositionsOnlyDP, timesOnlyDP[1:]):
        if time > 30 * 60:
            annotate.set_text(timeString)
        else:
            annotate.set_text('')
        annotate.set_x(xpos)

    fig.canvas.draw_idle()

def UpdateVo2Abs(val):
    pass

def UpdateVo2Rel(val):
    newRel = 1000*float(absolutBox.text)/float(massBox.text)
    newRel = min(90,newRel)
    newRel = max(30, newRel)

    vo2MaxSlider.set_val(newRel)


# register the update function with each slider
frictionSlider.on_changed(Update)
vo2MaxSlider.on_changed(Update)
waxPenaltySlider.on_changed(Update)
intensityBox.on_submit(Update)
heightBox.on_submit(Update)


massBox.on_submit(UpdateVo2Rel)

absolutBox.on_submit(UpdateVo2Rel)



plt.show()




