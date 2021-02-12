# How to generate the dataset 

1. Prepare a list of projects you want to analyze adding all the metadata required (see projects.csv)
2. Clone the git projects you want to analyze
  `git clone http://...`
3. GIT_COMMITS Table generation 
   * Execute the CommitTable.py file. This script will generate a csv for each project you cloned.  
   * Merge the csv files of each project, if needed
4. Analyzer all commits with SonarQube 
   * The analysis depends on the language. Please, refer to the [SonarQube documentation](https://docs.sonarqube.org/latest/analysis/overview/)
5. REFACTORING_MINER
    * Download [Refactoring miner](https://github.com/tsantalis/RefactoringMiner) 
   * Execute refactoring miner on all the projects. You can execute it on all the commits or on a subset of commits.  
  `example: RefactoringMiner -bc archiva 374fc983abc92df8aa4f8ef30caee94b34312ad2 b2332f00ba4bcdc76aebaf03d93916faf132cbd8` 
6. SZZ and Jira issues
    * Execute [OpenSZZ](https://github.com/clowee/OpenSZZ)
        * OpenSZZ enable to extract both the table Jira Issues and SZZ_FAULT_INDUCING_COMMITS


