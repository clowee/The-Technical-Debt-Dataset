# The Technical Debt Dataset

This is the official repository of the "Technical Debt Dataset" [1]. 
The current release is 1.0 [download here](download link)



## Table of contents
* **[What is it](#What-is-it)**
* **[How to cite the Technical Debt Dataset](#how-to-cite)**
* **[How to contribute](#how-to-contribute)**
* **[Empirical studies based on the Technical Debt Dataset](#Empirical-studies-based-on-the-Technical-Debt-Dataset)**
* **[References](#references)**

## What is it

Technical Debt Dataset is a curated dataset containing measurement data from four tools executed on all commits to enable researchers to work on a common set of data and thus compare their results.

The dataset was built by extracting the projects' data and analyzing all the commit using several tools. To get the data, the projects' GitHub repositories were cloned, commit information was collected from the git log using [PyDriller](https://github.com/ishepard/pydriller), and fault information was obtained by extracting issues from the Jira issue tracker. After that, code quality was inspected using two tools: Technical Debt items were analyzed with [SonarQube](https://www.sonarqube.org/), and code smells [2] and anti-patterns [3] with [Ptidej](http://www.ptidej.net/). In addition, the fault-inducing and -fixing commits were identified by applying [our implementation](https://github.com/clowee/OpenSZZ) of the SZZ algorithm [4].




## How to cite 

Please, cite as "The Technical Debt Dataset, Version 1.0 [1]"

[1] Valentina Lenarduzzi, Nyyti Saarimäki, Davide Taibi. The Technical Debt Dataset. Proceedings for the 15th Conference on Predictive Models and Data Analytics in Software Engineering. Brazil. 2019. 

```
@INPROCEEDINGS{Lenarduzzi2019,
  author = {Lenarduzzi, Valentina and Saarim{\"a}ki, Nyyti and Taibi, Davide},
  title = {The Technical Debt Dataset},
  booktitle={15th Conference on Predictive Models and Data Analytics in Software Engineering}, 
  year={2019}, 
  month={January},
  }
```

## How to contribute
If you analyzed a project with SonarQube and you are interested to share your data in our dataset, please send us an email ( davide [dot] taibi [ at ] tuni [ dot ] fi

To integrate your analysis please, report the following information 
* sonarqube_version
* project_name
* development_language
* github_url
* analyzed branch
* jira url 

We will run the SZZ tool and refactoring miner 1.0.0 on your repository and integrate your data in a new release of the dataset. 

We are also looking for contributors to automate the analysis pipeline. If you are interested to contribute, send us a message. 

## License
The Technical Debt Dataset has been developed only for research purposes. It includes the historical analysis of each public repository, including commit messages, timestamps, author names, and email addresses. Information from GitHub is stored in accordance with GitHub Terms of Service (GHTS), which explicitly allow extracting and redistributing public information for research purposes ([GitHub Terms of Service](goo.gl/yeZh1E) Accessed: May 2019). 

The _Technical Debt Dataset_ is licensed under a Creative Commons Attribution-NonCommercial- ShareAlike 4.0 International license.

 ## Empirical studies based on the Technical Debt Dataset
The _Technical Debt Dataset_ has been used in different works: 

* Nyyti Saarimäki, Valentina Lenarduzzi, and Davide Taibi. 2019. On the diffuseness of code technical debt in open source projects of the Apache Ecosystem. International Conference on Technical Debt (TechDebt 2019) 2019.

* Valentina Lenarduzzi, Antonio Martini, Davide Taibi, and Damian Andrew Tamburri. 2019. Towards Surgically-Precise Technical Debt Estimation: Early Results and Research Roadmap. In2019 IEEE Workshop on Machine Learning Techniques for Software Quality Evaluation (MaLTeSQuE)

* Valentina Lenarduzzi, Francesco Lomio, Davide Taibi, and Heikki Huttunen. 2019.On the Fault Proneness of SonarQube Technical Debt Violations: A comparison of eight Machine Learning Techniques.  arXiv:1907.00376


 ## References
[1] Valentina Lenarduzzi, Nyyti Saarimäki, and Davide Taibi. 2019. The Technical Debt Dataset. In 15th Conference on Predictive Models and Data Analytics in Software Engineering, 2019.

[2] Fowler, Martin. Refactoring: improving the design of existing code. Addison-Wesley Professional, 2018.

[3] Brown, William H., et al. AntiPatterns: refactoring software, architectures, and projects in crisis. John Wiley & Sons, Inc., 1998.

[4] Śliwerski, Jacek, Thomas Zimmermann, and Andreas Zeller. "When do changes induce fixes?." ACM sigsoft software engineering notes. Vol. 30. No. 4. ACM, 2005.
