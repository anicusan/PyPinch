#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File              : usage.py
# License           : License: GNU v3.0
# Author            : Andrei Leonard Nicusan <aln705@student.bham.ac.uk>
# Date              : 28.05.2019


# This is a quick usage example of the PyPinch module
# The solve() method runs all available subroutines
# available, in order:
#       shiftTemperatures()
#       constructTemperatureInterval()
#       constructProblemTable()
#       constructHeatCascade()
#       constructShiftedCompositeDiagram()
#       constructCompositeDiagram()
#       constructGrandCompositeCurve()
#       showPlots()


from PyPinch import PyPinch

def DrawPinch():
    # Draws Matplotlib-based plots
    return {'draw'}

def CSVPinch():
    # Writes calculated data as CSV files
    return {'csv'}

def DebugPinch():
    # Outputs raw calculated data in the terminal
    return {'debug'}

def FullPinch():
    # Multiple options can be supplied at once
    return {'draw', 'csv', 'debug'}

pinch = PyPinch('streams/streams.csv')
options = DrawPinch()
pinch.solve(options)

