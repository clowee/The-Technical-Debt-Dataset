# This is a sample Python script.
import argparse
from collections import OrderedDict
import pandas as pd
from ast import literal_eval
import os
from pathlib import Path
import numpy as np
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def compare_commit_and_analysis_dates(save_file_path, analysis_file, commit_file, project_name):
    # Use a breakpoint in the code line below to debug your script.
    # The analysis of the given project in /sonar_data/analysis/ directory
    analysis_df = pd.read_csv(save_file_path + "/analysis/" + analysis_file)

    # The commit hash file of the given project in /sonar_data/Git_Logs/ directory
    # For this file, I have used Savanna's script which generates the commit log history of a project and
    # saved it in /sonar_data/Git_logs/ directory manually
    commits_df = pd.read_csv(save_file_path + "/Git_Logs/" + commit_file)
    analysis_df = analysis_df.assign(DATE_MATCH=analysis_df.date.isin(commits_df.AUTHOR_DATE).astype(int))
    # analysis_df = analysis_df.assign(TEST=True)
    analysis_df['COMMIT_DATE'] = analysis_df['date']
    print(analysis_df['DATE_MATCH'].value_counts())
    analysis_df.loc[analysis_df['DATE_MATCH'] == 0, 'COMMIT_DATE'] = None
    # print(analysis_df)
    compare_date_path = Path(save_file_path).joinpath("compare_date")
    compare_date_path.mkdir(parents=True, exist_ok=True)
    compare_date_path = compare_date_path.joinpath(commit_file)
    del analysis_df['project_version']
    del analysis_df['revision']
    analysis_df.to_csv(compare_date_path, index=False, header=True)
    exit(1)

    # The issues of the given project in /sonar_data/issues/ directory
    issues_df = pd.read_csv(save_file_path + "/issues/" + analysis_file)

    headers = OrderedDict({
        "PROJECT": "object",
        "ANALYSIS_KEY": "object",
        "DATE": "object",
        "HASH": "object",
    })

    matched_commits = commits_df[commits_df.AUTHOR_DATE.isin(analysis_df.date)].drop_duplicates(subset=['AUTHOR_DATE'],
                                                                                                keep='last')
    print("matched_commits_date_with_analysis_date: {0}".format(len(matched_commits)))
    matched_analysis = analysis_df[analysis_df.date.isin(commits_df.AUTHOR_DATE)]
    matched_commits['MODIFIED_FILES'] = matched_commits.MODIFIED_FILES.apply(literal_eval)

    rows = []
    for index, item in matched_commits.iterrows():
        modified_files = sorted(item.loc['MODIFIED_FILES'])

        result = issues_df[(
                (issues_df['creation_date'] == item.loc['AUTHOR_DATE']) |
                # (issues_df['update_date'] == item.loc['AUTHOR_DATE']) |
                (issues_df['close_date'] == item.loc['AUTHOR_DATE'])
        )].drop_duplicates(subset=['component'], keep='last')['component'].array

        if result:
            component_files = sorted([os.path.basename(component) for component in result])

            if all(item in modified_files for item in component_files):
                analysis_row = matched_analysis[(matched_analysis['date'] == item.loc['AUTHOR_DATE'])]
                line = (analysis_row['project'].values[0], analysis_row['analysis_key'].values[0],
                        analysis_row['date'].values[0], item.loc['HASH'])
                rows.append(line)


    two_dates = list(zip(rows, rows[1:]))

    for row in two_dates:
        first_date = row[0][2]
        second_date = row[1][2]
        print((analysis_df['date'] > first_date) & (analysis_df['date'] <= second_date))
        break
    # print(len(rows))
    # save_file_path = Path(save_file_path).joinpath("analysis_commit")
    # save_file_path.mkdir(parents=True, exist_ok=True)
    # file_path = save_file_path.joinpath("sonar_analysis_commits_{0}.csv".format(project_name))
    # df = pd.DataFrame(data=rows, columns=headers)
    # df.to_csv(file_path, index=False, header=True)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output-path", default='./sonar_data', help="Path to output file directory.")
    args = vars(ap.parse_args())
    output_path = args['output_path']
    projects = pd.read_csv(output_path + "/projects_list.csv")
    for pos, row in projects.iterrows():
        compare_commit_and_analysis_dates(save_file_path=output_path, analysis_file=row.sonarProjectKey,
                                          commit_file=row.sonarProjectKey, project_name=row.projectID)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
