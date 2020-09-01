# This is a sample Python script.
import pandas as pd
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def compare_commit_and_analysis_dates(analysis_file, commit_file):
    # Use a breakpoint in the code line below to debug your script.
    analysis_df = pd.read_csv("/home/sazzad/The-Technical-Debt-Dataset/sonar_data/analysis/"+analysis_file)
    commits_df = pd.read_csv("/home/sazzad/Git_Logs/"+commit_file)
    # data["Gender"].isin(["Male"])
    print(commits_df[~commits_df.AUTHOR_DATE.isin(analysis_df.date)])


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    compare_commit_and_analysis_dates(analysis_file='org_apache_accumulo.csv', commit_file='accumulo_logs.csv')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
