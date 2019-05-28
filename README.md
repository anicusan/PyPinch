[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/anicusan/PyPinch/master?filepath=tutorial%2F)

# PyPinch: a Python-based Pinch Analyser

PyPinch is a lightweight Python module that applies Pinch Technology principles, analysing a given set of stream data to find the Maximum Energy Recovery (MER) target.

### Input: 
A CSV set of stream data including:
- Stream Enthalpy CP (kW / ºC)
- Stream Supply Temperature (T<sub>S</sub>)
- Stream Target Temperature (T<sub>T</sub>)

And a minimum temperature difference ∆T<sub>min</sub>

### Output:
Currently, PyPinch can **_calculate_**, **_plot_**, and **_export as CSV_** the following:
- The Temperature Interval Diagram
- The Problem Table
- The Heat Cascade
- The Minimum Cold Utility Q<sub>Cmin</sub> and the Minimum Hot Utility Q<sub>Hmin</sub>
- The Pinch Point T<sub>pinch</sub>
- The Shifted Temperature-Enthalpy Composite Diagram
- The Temperature-Enthalpy Composite Diagram
- The Grand Composite Curve

---

## Usage

An example code:

```python
from PyPinch import PyPinch

pinch = PyPinch('streams/streams.csv')
options = {'draw'}
pinch.solve(options)
```

That's it. As simple as that.

The options available are:
- 'draw': draw Matplotlib-based plots
- 'csv': export the calculated data as CSV files
- 'debug': print the raw calculated data

---

## Pinch Analysis or Heat Integration

Pinch analysis is a methodology for systematically finding optimum energy targets for a chemical plant. It analyses thermodynamically feasible maximum energy recovery (MER) targets for the available streams in a given plant, achieving them by optimising heat exchanger networks, energy supply methods and process operating conditions (Kemp, Ian, _Pinch Analysis and Process Integration, 2nd Edition_, 2016).

It is based on the idea that all streams in a chemical plant can be combined based on their temperature intervals into _composite curves_: one for the hot streams (the ones that lose heat) and one for the cold streams (the ones that gain heat). These composite curves provide insight into the point of closest approach (the _pinch point_) and the intervals available for heat exchange. Hence the required extra heating and cooling utilities can be found.

---



