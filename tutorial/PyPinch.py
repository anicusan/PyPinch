#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : PyPinch.py
# License           : License: GNU v3.0
# Author            : Andrei Leonard Nicusan <aln705@student.bham.ac.uk>
# Date              : 25.05.2019


import          csv
import          matplotlib.pyplot      as plt


class Streams:


    def __init__(self, streamsDataFile):

        self.tmin =              0
        self.numberOf =          0
        self.streamsData =       []

        self._rawStreamsData =   []
        self._index =            0
        self._length =           0

        with open(streamsDataFile, newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                self._rawStreamsData.append(row)

        if (self._rawStreamsData[0][0].strip() != 'Tmin' or
                [ item.strip() for item in self._rawStreamsData[1] ] != ['CP', 'TSUPPLY', 'TTARGET']):
            raise Exception("""\n[ERROR] Bad formatting in streams data file. \n
                    The first two rows of the streams data file should be: \n
                    `` Tmin, <TMIN VALUE> ''
                    `` CP, TSUPPLY, TTARGET ''\n
                    Where CP is the heat capacity (kW / degC);
                    TSUPPLY is the starting temperature of the given stream (degC);
                    TTARGET is the ending temperature of the given stream (degC);\n""")

        self.createStreams()


    def createStreams(self):
        try:
            self.tmin = float(self._rawStreamsData[0][1])
        except ValueError:
            print("\n[ERROR] Wrong type supplied for Tmin in the streams data file. Perhaps used characters?\n")
            raise
        except IndexError:
            print("\n[ERROR] Missing value for Tmin in the streams data file.\n")
            raise
        except:
            print("\n[ERROR] Unexpected error for Tmin. Try using the supplied streams data file format.\n")
            raise


        for rawStream in self._rawStreamsData[2:]:
            try:
                stream = {}

                if float(rawStream[1]) > float(rawStream[2]):
                    stream["type"] = "HOT"
                else:
                    stream["type"] = "COLD"

                stream["cp"] = float(rawStream[0])
                stream["ts"] = float(rawStream[1])
                stream["tt"] = float(rawStream[2])

                self.streamsData.append(stream)

            except ValueError:
                print("\n[ERROR] Wrong number type supplied in the streams data file. Perhaps used characters?\n")
                raise
            except IndexError:
                print("\n[ERROR] Missing number in the streams data file.\n")
                raise
            except:
                print("\n[ERROR] Unexpected error. Try using the supplied streams data file format.\n")
                raise

        self._length = len(self.streamsData)
        self.numberOf = len(self.streamsData)
        if (self._length < 2):
            raise Exception("\n[ERROR] Need to supply at least 2 streams in the streams data file.\n")


    def __iter__(self):
        return self


    def __next__(self):
        if self._index == self._length:
            self._index = 0
            raise StopIteration
        self._index = self._index + 1

        return self.streamsData[self._index - 1]


    def printTmin(self):
        print(self.tmin)


    def printStreams(self):
        for stream in self.streamsData:
            print(stream)


    def printRawStreams(self):
        for rawStream in self._rawStreamsData:
            print(rawStream)




class PyPinch:


    def __init__(self, streamsDataFile, options = {}):

        self.tmin =                      0
        self.streams =                   []
        self.temperatureInterval =       []
        self.problemTable =              []
        self.hotUtility =                0
        self.coldUtility =               0
        self.unfeasibleHeatCascade =     []
        self.heatCascade =               []
        self.pinchTemperature =          0
        self.shiftedCompositeDiagram =   {'hot': {'H': [], 'T': []}, 'cold': {'H': [], 'T': []}}
        self.compositeDiagram =          {'hot': {'H': [], 'T': []}, 'cold': {'H': [], 'T': []}}
        self.grandCompositeCurve =       {'H': [], 'T': []}

        self._temperatures =             []
        self._deltaHHot =                []
        self._deltaHCold =               []
        self._options =                  {'debug': False, 'draw': False, 'csv': False}


        self.streams = Streams(streamsDataFile)
        self.tmin = self.streams.tmin

        if 'debug' in options:
            self._options['debug'] = True
        if 'draw' in options:
            self._options['draw'] = True
        if 'csv' in options:
            self._options['csv'] = True


    def shiftTemperatures(self):
        for stream in self.streams:
            if stream['type'] == 'HOT':
                stream['ss'] = stream['ts'] - self.tmin / 2
                stream['st'] = stream['tt'] - self.tmin / 2
            else:
                stream['ss'] = stream['ts'] + self.tmin / 2
                stream['st'] = stream['tt'] + self.tmin / 2

        if self._options['debug'] == True:
            print("\nStreams: ")
            for stream in self.streams:
                print(stream)
            print("Tmin = {}".format(self.tmin))


    def constructTemperatureInterval(self):
        # Take all shifted temperatures and reverse sort them,
        # removing all duplicates
        for stream in self.streams:
            self._temperatures.append(stream['ss'])
            self._temperatures.append(stream['st'])

        self._temperatures = list(set(self._temperatures))
        self._temperatures.sort(reverse = True)

        # Save the stream number of all the streams that pass
        # through each shifted temperature interval
        for i in range(len(self._temperatures) - 1):
            t1 = self._temperatures[i]
            t2 = self._temperatures[i + 1]
            interval = {'t1': t1, 't2': t2, 'streamNumbers': []}

            j = 0
            for stream in self.streams:
                if (stream['type'] == 'HOT'):
                    if (stream['ss'] >= t1 and stream['st'] <= t2):
                        interval['streamNumbers'].append(j)
                else:
                    if (stream['st'] >= t1 and stream['ss'] <= t2):
                        interval['streamNumbers'].append(j)
                j = j + 1

            self.temperatureInterval.append(interval)

        if self._options['debug'] == True:
            print("\nTemperature Intervals: ")
            i = 0
            for interval in self.temperatureInterval:
                print("Interval {} : {}".format(i, interval))
                i = i + 1

        if self._options['draw'] == True:
            self.drawTemperatureInterval()


    def drawTemperatureInterval(self):
        fig, ax = plt.subplots()

        plt.title('Shifted Temperature Interval Diagram')
        plt.ylabel('Shifted Temperature S (degC)')
        ax.set_xticklabels([])

        xOffset = 50

        for temperature in self._temperatures:
            plt.plot([0, xOffset * (self.streams.numberOf + 1)], [temperature, temperature], ':k', alpha=0.8)

        arrow_width = self.streams.numberOf * 0.05
        head_width = arrow_width * 15
        head_length = self._temperatures[0] * 0.02
        i = 1
        for stream in self.streams:
            if stream['type'] == 'HOT':
                plt.text(xOffset, stream['ss'], str(i), bbox=dict(boxstyle='round', alpha=1, fc='tab:red', ec="k"))
                plt.arrow(xOffset, stream['ss'], 0, stream['st'] - stream['ss'], color='tab:red', ec='k', alpha=1,
                        length_includes_head=True, width=arrow_width, head_width=head_width, head_length=head_length)
            else:
                plt.text(xOffset, stream['ss'], str(i), bbox=dict(boxstyle='round', alpha=1, fc='tab:blue', ec="k"))
                plt.arrow(xOffset, stream['ss'], 0, stream['st'] - stream['ss'], color='tab:blue', ec='k', alpha=1,
                        length_includes_head=True, width=arrow_width, head_width=head_width, head_length=head_length)
            xOffset = xOffset + 50
            i = i + 1


    def constructProblemTable(self):

        for interval in self.temperatureInterval:
            row = {}
            row['deltaS'] = interval['t1'] - interval['t2']
            row['deltaCP'] = 0

            for i in interval['streamNumbers']:
                if self.streams.streamsData[i]['type'] == 'HOT':
                    row['deltaCP'] = row['deltaCP'] + self.streams.streamsData[i]['cp']
                else:
                    row['deltaCP'] = row['deltaCP'] - self.streams.streamsData[i]['cp']

            row['deltaH'] = row['deltaS'] * row['deltaCP']
            self.problemTable.append(row)

        if self._options['debug'] == True:
            print("\nProblem Table: ")
            i = 0
            for interval in self.problemTable:
                print("Interval {} : {}".format(i, interval))
                i = i + 1

        if self._options['draw'] == True:
            self.drawProblemTable()

        if self._options['csv'] == True:
            self.csvProblemTable()


    def drawProblemTable(self):
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.axis('tight')
        ax.axis('off')
        ax.set_title('Problem Table')

        colLabels = ['$Interval: S_i - S_{i+1}$', '$\Delta S (\degree C)$', '$\Delta CP (kW / \degree C)$', '$\Delta H (kW)$', '']
        cellText = []

        i = 1
        for interval in self.problemTable:
            cellRow = []
            cellRow.extend(['{}: {} - {}'.format(i, self._temperatures[i - 1], self._temperatures[i]),
                interval['deltaS'], interval['deltaCP'], interval['deltaH']])

            if interval['deltaH'] > 0:
                cellRow.append('Surplus')
            elif interval['deltaH'] == 0:
                cellRow.append('-')
            else:
                cellRow.append('Deficit')
            cellText.append(cellRow)
            i = i + 1

        table = ax.table(cellText=cellText, colLabels=colLabels, loc='center')
        table.auto_set_column_width([0, 1, 2, 3, 4])
        table.scale(1.3, 1.3)


    def csvProblemTable(self):
        colLabels = ['$Interval: S_i - S_{i+1}$', '$\Delta S (\degree C)$', '$\Delta CP (kW / \degree C)$', '$\Delta H (kW)$', '']
        cellText = []

        i = 1
        for interval in self.problemTable:
            cellRow = []
            cellRow.extend(['{}: {} - {}'.format(i, self._temperatures[i - 1], self._temperatures[i]),
                interval['deltaS'], interval['deltaCP'], interval['deltaH']])

            if interval['deltaH'] > 0:
                cellRow.append('Surplus')
            elif interval['deltaH'] == 0:
                cellRow.append('-')
            else:
                cellRow.append('Deficit')
            cellText.append(cellRow)
            i = i + 1

        with open('ProblemTable.csv', 'w', newline='') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(['Interval: S1 - S2', 'delta S (degC)', 'delta CP (kW / degC)', 'delta H (kW)', ''])
            for rowText in cellText:
                writer.writerow(rowText)


    def constructHeatCascade(self):

        exitH = 0
        lowestExitH = 0

        i = 0
        pinchInterval = 0
        for interval in self.problemTable:
            row = {}
            row['deltaH'] = interval['deltaH']

            exitH = exitH + row['deltaH']
            row['exitH'] = exitH
            if exitH < lowestExitH:
                lowestExitH = exitH
                pinchInterval = i

            self.unfeasibleHeatCascade.append(row)
            i = i + 1

        self.hotUtility = -lowestExitH
        exitH = self.hotUtility

        for interval in self.problemTable:
            row = {}
            row['deltaH'] = interval['deltaH']

            exitH = exitH + row['deltaH']
            row['exitH'] = exitH

            self.heatCascade.append(row)

        self.coldUtility = exitH
        self.pinchTemperature = self.temperatureInterval[pinchInterval]['t2']

        if self._options['debug'] == True:
            print("\nUnfeasible Heat Cascade: ")
            i = 0
            for interval in self.unfeasibleHeatCascade:
                print("Interval {} : {}".format(i, interval))
                i = i + 1

            print("\nFeasible Heat Cascade: ")
            i = 0
            for interval in self.heatCascade:
                print("Interval {} : {}".format(i, interval))
                i = i + 1

            print("\nPinch Temperature (degC): {}".format(self.pinchTemperature))
            print("Minimum Hot Utility (kW): {}".format(self.hotUtility))
            print("Minimum Cold Utility (kW): {}".format(self.coldUtility))

        if self._options['draw'] == True:
            self.drawHeatCascade()

        if self._options['csv'] == True:
            self.csvHeatCascade()


    def drawHeatCascade(self):
        fig, axs = plt.subplots(1, 2, figsize=(10, 6))
        axs[0].axis('auto')
        axs[0].axis('off')
        axs[1].axis('auto')
        axs[1].axis('off')

        axs[0].set_title('Unfeasible Heat Cascade')
        axs[1].set_title('Feasible Heat Cascade')

        cellText = []
        cellText.append(['', '', 'Hot Utility: 0'])
        cellText.append(['Interval', '$\Delta H (kW)$', 'Exit H (total kW)'])

        i = 1
        for interval in self.unfeasibleHeatCascade:
            cellText.append([str(i), interval['deltaH'], interval['exitH']])
            i = i + 1

        cellText.append(['', '', 'Cold Utility: {}'.format(self.unfeasibleHeatCascade[-1]['exitH'])])
        table = axs[0].table(cellText=cellText, loc='center')
        table.auto_set_column_width([0, 1, 2])
        table.scale(1.3, 1.3)

        cellText = []
        cellText.append(['', '', 'Hot Utility: {}'.format(self.hotUtility)])
        cellText.append(['Interval', '$\Delta H (kW)$', 'Exit H (total kW)'])

        i = 1
        for interval in self.heatCascade:
            cellText.append([str(i), interval['deltaH'], interval['exitH']])
            i = i + 1

        cellText.append(['', '', 'Cold Utility: {}'.format(self.heatCascade[-1]['exitH'])])
        table = axs[1].table(cellText=cellText, loc='center')
        table.auto_set_column_width([0, 1, 2])
        table.scale(1.3, 1.3)


    def csvHeatCascade(self):
        cellText = [['Unfeasible Heat Cascade: ']]
        cellText.append(['', '', 'Hot Utility: 0 kW'])
        cellText.append(['Interval', 'Delta H (kW)', 'Exit H (total kW)'])

        i = 1
        for interval in self.unfeasibleHeatCascade:
            cellText.append([str(i), interval['deltaH'], interval['exitH']])
            i = i + 1

        cellText.append(['', '', 'Cold Utility: {} kW'.format(self.unfeasibleHeatCascade[-1]['exitH'])])
        cellText.append([''])

        cellText.append(['Feasible Heat Cascade: '])
        cellText.append(['', '', 'Hot Utility: {} kW'.format(self.hotUtility)])
        cellText.append(['Interval', 'Delta H (kW)', 'Exit H (total kW)'])

        i = 1
        for interval in self.heatCascade:
            cellText.append([str(i), interval['deltaH'], interval['exitH']])
            i = i + 1

        cellText.append(['', '', 'Cold Utility: {} kW'.format(self.heatCascade[-1]['exitH'])])
        cellText.append(['','', 'Pinch Temperature: {} degC'.format(self.pinchTemperature)])

        with open('HeatCascade.csv', 'w', newline='') as f:
            writer = csv.writer(f, delimiter=',')
            for rowText in cellText:
                writer.writerow(rowText)


    def constructShiftedCompositeDiagram(self):
        # Find enthalpy change deltaH for the hot and
        # cold composite streams
        for interval in self.temperatureInterval:
            hotH = 0
            coldH = 0
            # Add CP values for the hot and cold streams
            # in a given temperature interval
            for i in interval['streamNumbers']:
                if self.streams.streamsData[i]['type'] == 'HOT':
                    hotH = hotH + self.streams.streamsData[i]['cp']
                else:
                    coldH = coldH + self.streams.streamsData[i]['cp']

            # Enthalpy = CP * deltaT
            hotH = hotH * (interval['t1'] - interval['t2'])
            self._deltaHHot.append(hotH)

            coldH = coldH * (interval['t1'] - interval['t2'])
            self._deltaHCold.append(coldH)

        # Need temperatures and enthalpies in ascending order
        self._temperatures.reverse()
        self._deltaHHot.reverse()
        self._deltaHCold.reverse()

        totalHotH = 0.0
        self.shiftedCompositeDiagram['hot']['H'].append(totalHotH)
        self.shiftedCompositeDiagram['hot']['T'].append(self._temperatures[0])
        for i in range(1, len(self._temperatures)):
            if self._deltaHHot[i - 1] != 0:
                totalHotH = totalHotH + self._deltaHHot[i - 1]
                self.shiftedCompositeDiagram['hot']['H'].append(totalHotH)
                self.shiftedCompositeDiagram['hot']['T'].append(self._temperatures[i])

        totalColdH = self.coldUtility
        self.shiftedCompositeDiagram['cold']['H'].append(totalColdH)
        self.shiftedCompositeDiagram['cold']['T'].append(self._temperatures[0])
        for i in range(1, len(self._temperatures)):
            if self._deltaHCold[i - 1] != 0:
                totalColdH = totalColdH + self._deltaHCold[i - 1]
                self.shiftedCompositeDiagram['cold']['H'].append(totalColdH)
                self.shiftedCompositeDiagram['cold']['T'].append(self._temperatures[i])

        self._temperatures.reverse()

        if self._options['debug'] == True:
            print("\nShifted Composite Diagram Values: ")
            print("DeltaH Hot: {}".format(self._deltaHHot))
            print("DeltaH Cold: {}".format(self._deltaHCold))

            print("")
            print("Hot H: {}".format(self.shiftedCompositeDiagram['hot']['H']))
            print("Hot T: {}".format(self.shiftedCompositeDiagram['hot']['T']))

            print("")
            print("Cold H: {}".format(self.shiftedCompositeDiagram['cold']['H']))
            print("Cold T: {}".format(self.shiftedCompositeDiagram['cold']['T']))

        if self._options['draw'] == True:
            self.drawShiftedCompositeDiagram()

        if self._options['csv'] == True:
            self.csvShiftedCompositeDiagram()


    def drawShiftedCompositeDiagram(self):
        fig = plt.figure()
        plt.plot(self.shiftedCompositeDiagram['hot']['H'], self.shiftedCompositeDiagram['hot']['T'], 'tab:red')
        plt.plot(self.shiftedCompositeDiagram['cold']['H'], self.shiftedCompositeDiagram['cold']['T'], 'tab:blue')

        plt.plot(self.shiftedCompositeDiagram['hot']['H'], self.shiftedCompositeDiagram['hot']['T'], 'ro')
        plt.plot(self.shiftedCompositeDiagram['cold']['H'], self.shiftedCompositeDiagram['cold']['T'], 'bo')

        maxColdH = max(self.shiftedCompositeDiagram['cold']['H'])
        plt.fill_between([0, self.coldUtility], 0, self._temperatures[0], color = 'b', alpha = 0.5)
        plt.fill_between([maxColdH - self.hotUtility, maxColdH], 0, self._temperatures[0], color = 'r', alpha = 0.5)

        try:
            pinchIndex = self.shiftedCompositeDiagram['cold']['T'].index(self.pinchTemperature)
            pinchH = self.shiftedCompositeDiagram['cold']['H'][pinchIndex]
            plt.plot([pinchH, pinchH], [self._temperatures[0], self._temperatures[-1]], ':')
        except ValueError:
            pass

        plt.grid(True)
        plt.title('Shifted Temperature-Enthalpy Composite Diagram')
        plt.xlabel('Enthalpy H (kW)')
        plt.ylabel('Shifted Temperature S (degC)')


    def csvShiftedCompositeDiagram(self):
        with open('ShiftedCompositeDiagram.csv', 'w', newline='') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(['Hot H', 'Hot T'])
            for i in range(0, len(self.shiftedCompositeDiagram['hot']['H'])):
                writer.writerow([self.shiftedCompositeDiagram['hot']['H'][i],
                    self.shiftedCompositeDiagram['hot']['T'][i]])

            writer.writerow([''])
            writer.writerow(['Cold H', 'Cold T'])
            for i in range(0, len(self.shiftedCompositeDiagram['cold']['H'])):
                writer.writerow([self.shiftedCompositeDiagram['cold']['H'][i],
                    self.shiftedCompositeDiagram['cold']['T'][i]])


    def constructCompositeDiagram(self):
        self.compositeDiagram['hot']['T'] = [x + self.tmin / 2 for x in self.shiftedCompositeDiagram['hot']['T']]
        self.compositeDiagram['hot']['H'] = self.shiftedCompositeDiagram['hot']['H']
        self.compositeDiagram['cold']['T'] = [x - self.tmin / 2 for x in self.shiftedCompositeDiagram['cold']['T']]
        self.compositeDiagram['cold']['H'] = self.shiftedCompositeDiagram['cold']['H']

        if self._options['draw'] == True:
            self.drawCompositeDiagram()

        if self._options['csv'] == True:
            self.csvCompositeDiagram()


    def drawCompositeDiagram(self):
        fig = plt.figure()
        plt.plot(self.compositeDiagram['hot']['H'], self.compositeDiagram['hot']['T'], 'tab:red')
        plt.plot(self.compositeDiagram['cold']['H'], self.compositeDiagram['cold']['T'], 'tab:blue')

        plt.plot(self.compositeDiagram['hot']['H'], self.compositeDiagram['hot']['T'], 'ro')
        plt.plot(self.compositeDiagram['cold']['H'], self.compositeDiagram['cold']['T'], 'bo')

        maxColdH = max(self.compositeDiagram['cold']['H'])
        plt.fill_between([0, self.coldUtility], 0, self._temperatures[0] + self.tmin/2, color = 'b', alpha = 0.5)
        plt.fill_between([maxColdH - self.hotUtility, maxColdH], 0, self._temperatures[0] + self.tmin/2, color = 'r', alpha = 0.5)

        try:
            pinchIndex = self.shiftedCompositeDiagram['cold']['T'].index(self.pinchTemperature)
            pinchH = self.shiftedCompositeDiagram['cold']['H'][pinchIndex]
            plt.plot([pinchH, pinchH], [self._temperatures[0], self._temperatures[-1]], ':')
        except ValueError:
            pass

        plt.grid(True)
        plt.title('Temperature-Enthalpy Composite Diagram')
        plt.xlabel('Enthalpy H (kW)')
        plt.ylabel('Temperature T (degC)')


    def csvCompositeDiagram(self):
        with open('CompositeDiagram.csv', 'w', newline='') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(['Hot H', 'Hot T'])
            for i in range(0, len(self.compositeDiagram['hot']['H'])):
                writer.writerow([self.compositeDiagram['hot']['H'][i],
                    self.compositeDiagram['hot']['T'][i]])

            writer.writerow([''])
            writer.writerow(['Cold H', 'Cold T'])
            for i in range(0, len(self.compositeDiagram['cold']['H'])):
                writer.writerow([self.compositeDiagram['cold']['H'][i],
                    self.compositeDiagram['cold']['T'][i]])


    def constructGrandCompositeCurve(self):
        self.grandCompositeCurve['H'].append(self.hotUtility)
        self.grandCompositeCurve['T'].append(self._temperatures[0])
        for i in range(1, len(self._temperatures)):
            self.grandCompositeCurve['H'].append(self.heatCascade[i - 1]['exitH'])
            self.grandCompositeCurve['T'].append(self._temperatures[i])

        if self._options['debug'] == True:
            print("\nGrand Composite Curve: ")
            print("Net H (kW): {}".format(self.grandCompositeCurve['H']))
            print("T (degC): {}".format(self.grandCompositeCurve['T']))

        if self._options['draw'] == True:
            self.drawGrandCompositeCurve()

        if self._options['csv'] == True:
            self.csvGrandCompositeCurve()


    def drawGrandCompositeCurve(self):
        fig = plt.figure()
        plt.plot(self.grandCompositeCurve['H'], self.grandCompositeCurve['T'], 'tab:blue')
        plt.plot(self.grandCompositeCurve['H'], self.grandCompositeCurve['T'], 'bo')

        plt.fill_between([0, self.grandCompositeCurve['H'][0]], 0, self._temperatures[0], color = 'r', alpha = 0.5)
        plt.fill_between([0, self.grandCompositeCurve['H'][-1]], 0, self._temperatures[-1], color = 'b', alpha = 0.5)

        plt.plot([0, self.grandCompositeCurve['H'][-1]], [self.pinchTemperature, self.pinchTemperature], ':')

        plt.grid(True)
        plt.title('Grand Composite Curve')
        plt.xlabel('Net Enthalpy Change ∆H (kW)')
        plt.ylabel('Shifted Temperature S (degC)')


    def csvGrandCompositeCurve(self):
        with open('GrandCompositeCurve.csv', 'w', newline='') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(['Net H (kW)', 'T(degC)'])
            for i in range(0, len(self.grandCompositeCurve['H'])):
                writer.writerow([self.grandCompositeCurve['H'][i],
                    self.grandCompositeCurve['T'][i]])


    def showPlots(self):
        plt.show()


    def solve(self, options = {}):

        if 'debug' in options:
            self._options['debug'] = True
        if 'draw' in options:
            self._options['draw'] = True
        if 'csv' in options:
            self._options['csv'] = True

        self.shiftTemperatures()
        self.constructTemperatureInterval()
        self.constructProblemTable()
        self.constructHeatCascade()
        self.constructShiftedCompositeDiagram()
        self.constructCompositeDiagram()
        self.constructGrandCompositeCurve()

        if self._options['draw'] == True:
            self.showPlots()


