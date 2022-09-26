# Implementation and optimization of the mean-timer technique in drift tube detectors

<p align="center">
<b>Group 1</b> // Francesco Pio Barone, Gianmarco Nagaro Quiroz, Daniele Ninni, Lorenzo Valentini
</p>

This is our final project for *Laboratory of Computational Physics (Module A)*. In this work, we implement the mean-timer technique and use it to process the data gathered by a series of drift tube detectors.

An **event** can be thought as the passage of a particle through the detector(s), i.e. a collection of hits produced by the particle's track. The datasets are not composed of events, instead they consist of just a series of hits. The goal of this project is to process the data to reformat it as a list of events.

<br>

## File structure

```
.
├── bin                                   (collection of useful Python functions)
│   ├── data_selection.py
│   ├── meantimers.py
│   └── plotters.py
|
├── doc                                   (documentation)
│   ├── meantimer.png
│   ├── NOTE2007_034.pdf
│   └── project_assignment.ipynb          (assignment of this project)
|
├── img                                   (images)
│   ├── angles.png
│   ├── builder_animations_images.ipynb   
│   ├── pattern_new_crop.png
│   └── pattern_tdc_crop.png
|
├── tmp                                   (temporary files)
|   ├── 262_0000_meantimers.txt
|   ├── 262_0000_preprocessed.txt
|   ├── animation_tools.py
|   └── data_000000.txt
|
├── part1_data_selection.ipynb            (project)
├── part2_meantimers.ipynb
├── part3_algorithm_efficiency.ipynb
|
├── run_262.ipynb                         (appendices)
└── run_333.ipynb
```

***

<h5 align="center">Laboratory of Computational Physics (Module A)<br>University of Padua, A.Y. 2021/22</h5>

<p align="center">
  <img src="https://user-images.githubusercontent.com/62724611/166108149-7629a341-bbca-4a3e-8195-67f469a0cc08.png" alt="" height="70"/>
</p>