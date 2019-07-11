# The Technical Debt Dataset

This is the official repository of the "Tecnical Debt Dataset"[1]. 



## Table of contents
* **[How to cite the Technical Debt Dataset](#how-to-cite)**
* **[How To Use it](#requirements)**
* **[Install](#install)**
* **[Source code](#source-code)**
* **[Tutorial](#tutorial)**
* **[How to contribute](#how-to-contribute)**

## How to cite 


Plain Citation

Valentina Lenarduzzi, Nyyti Saarimäki, Davide Taibi. The Technical Debt Dataset. Proceedings for the 15th Conference on Predictive Models and Data Analytics in Software Engineering. Brazil. 2019. 

Bibtex: 

```
@INPROCEEDINGS{Lenarduzzi2019,
  author = {Lenarduzzi, Valentina and Saarim{\"a}ki, Nyyti and Taibi, Davide},
  title = {The Technical Debt Dataset},
  booktitle={15th Conference on Predictive Models and Data Analytics in Software Engineering}, 
  year={2019}, 
  month={January},
  }
```

## What is it

Technical Debt Dataset  is a curated dataset containing measurement data from four tools executed on all commits to enable researchers to work on a common set of data and thus compare their results.

The dataset was built by extracting the projects' data and analyzing all the comments it using several tools. To get the data, the projects' GitHub repositories were cloned, commit information was collected from the git log using PyDriller, and fault information was obtained by extracting issues from the Jira issue tracker. After that, code quality was inspected using two tools: Technical Debt items were analyzed with SonarQube, and code smells~\cite{Fowler1999} and anti-patterns~\cite{BrownAntipatterns} with Ptidej~\cite{Ptidej}. In addition, the fault-inducing and -fixing commits were identified by applying our implementation~\cite{OpenSZZ} of the SZZ algorithm~\cite{SZZLiterature}.



 

