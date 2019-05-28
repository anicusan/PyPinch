# PyPinch: a Python-based Pinch Analyser

PyPinch is a lightweight Python module that applies Pinch Technology principles, analysing a given set of stream data to find the Maximum Energy Recovery (MER) target.

### Input: 
A CSV set of stream data including:
- Stream Enthalpy CP (kW / ºC)
- Stream Supply Temperature ($T_S$)
- Stream Target Temperature ($T_T$)

And a minimum temperature difference $\Delta T_{min}$

### Output:
Currently, PyPinch can _calculate_, _plot_, and _export as CSV_ the following:
- The Temperature Interval Diagram
- The Problem Table
- The Heat Cascade
- The Minimum Cold Utility $Q_{Cmin}$ and the Minimum Hot Utility $Q_{Hmin}$
- The Pinch Point $T_{pinch}$
- The Shifted Temperature-Enthalpy Composite Diagram
- The Temperature-Enthalpy Composite Diagram
- The Grand Composite Curve

---
