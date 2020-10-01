# This is a sample Python script.
import json
import argparse
from collections import OrderedDict
import pandas as pd
from ast import literal_eval
import os
import itertools
from pathlib import Path
import numpy as np
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def compare_commit_and_analysis_dates(save_file_path, analysis_file, commit_file, project_name):
    # The analysis of the given project in /sonar_data/analysis/ directory
    analysis_df = pd.read_csv(save_file_path + "/analysis/" + "{0}.csv".format(
            analysis_file.replace(' ', '_').replace(':', '_')))

    print(len(analysis_df))

    # The commit hash file of the given project in /sonar_data/Git_Logs/ directory
    # For this file, I have used Savanna's script which generates the commit log history of a project and
    # saved it in /sonar_data/Git_logs/ directory manually
    commits_df = pd.read_csv(save_file_path + "/Git_Logs/" + "{0}.csv".format(
            commit_file.replace(' ', '_').replace(':', '_')))
    print(len(commits_df))
    analysis_df = analysis_df.assign(DATE_MATCH=analysis_df.date.isin(commits_df.AUTHOR_DATE).astype(int))
    analysis_df['COMMIT_DATE'] = analysis_df['date']
    # compared = json.loads(analysis_df['DATE_MATCH'].value_counts().to_json())
    # not_matched = 0 if '0' not in compared else compared['0']
    # matched = 0 if '1' not in compared else compared['1']
    # return (project_name, not_matched, matched, (matched/(len(analysis_df.index))*100))
    # print('PROJECT: {0}, NOT MATCHED: {1}, MATCHED: {2}, MATCHED%: {3}'.format(project_name, not_matched, matched, (matched/(len(analysis_df.index))*100)))
    # print('-'*100)
    analysis_df.loc[analysis_df['DATE_MATCH'] == 0, 'COMMIT_DATE'] = None
    # print(analysis_df)
    # compare_date_path = Path(save_file_path).joinpath("compare_date")
    # compare_date_path.mkdir(parents=True, exist_ok=True)
    # compare_date_path = compare_date_path.joinpath(commit_file)
    # del analysis_df['project_version']
    # del analysis_df['revision']
    # analysis_df.to_csv(compare_date_path, index=False, header=True)
    # exit(1)
    #
    # # The issues of the given project in /sonar_data/issues/ directory
    issues_df = pd.read_csv(save_file_path + "/issues/"+ "{0}.csv".format(
            analysis_file.replace(' ', '_').replace(':', '_')))
    print(len(issues_df))
    headers = OrderedDict({
        "PROJECT": "object",
        "ANALYSIS_KEY": "object",
        "DATE": "object",
        "HASH": "object",
    })
    #
    matched_commits = commits_df[commits_df.AUTHOR_DATE.isin(analysis_df.date)].drop_duplicates(subset=['AUTHOR_DATE'],
                                                                                                 keep='last')
    print("matched_commits_date_with_analysis_date: {0}".format(len(matched_commits)))
    matched_analysis = analysis_df[analysis_df.date.isin(commits_df.AUTHOR_DATE)]
    matched_commits['MODIFIED_FILES'] = matched_commits.MODIFIED_FILES.apply(literal_eval)

    creation_date = issues_df['creation_date'].tolist()
    update_date = issues_df['update_date'].tolist()
    close_date = issues_df['close_date'].tolist()
    date_list = creation_date + update_date + close_date
    unique_issues_date = list(set(date_list))
    issues_df_dates = pd.DataFrame({"dates": unique_issues_date})
    matched_issues = analysis_df['date'].isin(issues_df_dates['dates']).value_counts()
    print(matched_issues)

    rows = []
    not_found = False
    for index, item in matched_commits.iterrows():
        modified_files = sorted(item.loc['MODIFIED_FILES'])
        issues_of_create_date = issues_df[(issues_df['creation_date'] == item.loc['AUTHOR_DATE'])].drop_duplicates(
            subset=['component'], keep='last')['component'].array

        if issues_of_create_date:
            component_files = sorted([os.path.basename(component) for component in issues_of_create_date])
            for i, _ in enumerate(component_files):
                if component_files[i] == "org.apache:felix:pom.xml":
                    component_files[i] = 'pom.xml'

            if all(item in modified_files for item in component_files):
                analysis_row = matched_analysis[(matched_analysis['date'] == item.loc['AUTHOR_DATE'])]
                line = (analysis_row['project'].values[0], analysis_row['analysis_key'].values[0],
                        analysis_row['date'].values[0], item.loc['HASH'])
                rows.append(line)
                not_found = False
            else:
                not_found = True
        else:
            not_found = True

        if not_found:
            issues_of_create_update_date = issues_df[
                (issues_df['creation_date'] == item.loc['AUTHOR_DATE']) |
                (issues_df['update_date'] == item.loc['AUTHOR_DATE'])].drop_duplicates(
                subset=['component'], keep='last')['component'].array

            if issues_of_create_update_date:
                component_files = sorted([os.path.basename(component)
                                          for component in issues_of_create_update_date])

                for i, _ in enumerate(component_files):
                    if component_files[i] == "org.apache:felix:pom.xml":
                        component_files[i] = 'pom.xml'

                if all(item in modified_files for item in component_files):
                    analysis_row = matched_analysis[(matched_analysis['date'] == item.loc['AUTHOR_DATE'])]
                    line = (analysis_row['project'].values[0], analysis_row['analysis_key'].values[0],
                            analysis_row['date'].values[0], item.loc['HASH'])
                    rows.append(line)
                    not_found = False
                else:
                    not_found = True
            else:
                not_found = True

        if not_found:
            issues_of_create_update_close_date = issues_df[(
                    (issues_df['creation_date'] == item.loc['AUTHOR_DATE']) |
                    (issues_df['update_date'] == item.loc['AUTHOR_DATE']) |
                    (issues_df['close_date'] == item.loc['AUTHOR_DATE'])
            )].drop_duplicates(subset=['component'], keep='last')['component'].array

            if issues_of_create_update_close_date:
                component_files = sorted([os.path.basename(component)
                                          for component in issues_of_create_update_close_date])

                for i, _ in enumerate(component_files):
                    if component_files[i] == "org.apache:felix:pom.xml":
                        component_files[i] = 'pom.xml'

                if all(item in modified_files for item in component_files):
                    analysis_row = matched_analysis[(matched_analysis['date'] == item.loc['AUTHOR_DATE'])]
                    line = (analysis_row['project'].values[0], analysis_row['analysis_key'].values[0],
                            analysis_row['date'].values[0], item.loc['HASH'])
                    rows.append(line)
                    not_found = False
                else:
                    not_found = True
            else:
                not_found = True

    print(len(rows))
    two_dates = list(zip(rows, rows[1:]))
    #
    # analysis_df['date'] = pd.to_datetime(analysis_df['date'])
    # analysis_df = analysis_df.sort_values(by=['date'])
    #
    print(not_found)
    new_rows = []
    for row in two_dates:
        first_date = row[0][2]
        second_date = row[1][2]
        missing_analysis_df = analysis_df.loc[
            ((analysis_df['date'] > first_date) & (analysis_df['date'] < second_date))
        ]

        if not missing_analysis_df.empty:
            # print('*'*40)
            # print(first_date + '  ' + second_date)
            modified_files_of_missing_analysis = commits_df.loc[commits_df['AUTHOR_DATE'].isin(
                missing_analysis_df['COMMIT_DATE'].tolist())]

            combined_modified_files_of_missing_analysis = []
            for files in modified_files_of_missing_analysis['MODIFIED_FILES'].apply(literal_eval):
                if files:
                    combined_modified_files_of_missing_analysis.extend(files)
            # print(combined_modified_files_of_missing_analysis)

            for index, row in missing_analysis_df.iterrows():
                # print('COMMIT_DATE' + row.loc['COMMIT_DATE'])
                if row.loc['COMMIT_DATE'] != '':
                    issues_of_missing_analysis_creation_date = issues_df[(
                            (issues_df['creation_date'] == row.loc['COMMIT_DATE'])
                    )].drop_duplicates(subset=['component'], keep='last')['component'].array
                    if issues_of_missing_analysis_creation_date:
                        component_files = sorted([os.path.basename(component)
                                                  for component in issues_of_missing_analysis_creation_date])
                        # print('CREATION')
                        # print(component_files)
                        # print()
                        for i, _ in enumerate(component_files):
                            if component_files[i] == "org.apache:felix:pom.xml":
                                component_files[i] = 'pom.xml'

                        if all(item in combined_modified_files_of_missing_analysis for item in component_files):
                            analysis_row = matched_analysis[(matched_analysis['date'] == item.loc['AUTHOR_DATE'])]
                            line = (analysis_row['project'].values[0], analysis_row['analysis_key'].values[0],
                                    analysis_row['date'].values[0], item.loc['HASH'])
                            new_rows.append(line)
                            not_found = False
                        else:
                            not_found = True
                    else:
                        not_found = True

                    if not_found:
                        issues_of_missing_analysis_creation_update_date = issues_df[(
                            (issues_df['creation_date'] == row.loc['COMMIT_DATE']) |
                            (issues_df['update_date'] == row.loc['COMMIT_DATE'])
                        )].drop_duplicates(subset=['component'], keep='last')['component'].array

                        if issues_of_missing_analysis_creation_update_date:
                            component_files = sorted([os.path.basename(component)
                                                      for component in issues_of_missing_analysis_creation_update_date])

                            # print('CREATION-UPDATE')
                            # print(component_files)
                            # print()
                            for i, _ in enumerate(component_files):
                                if component_files[i] == "org.apache:felix:pom.xml":
                                    component_files[i] = 'pom.xml'

                            if all(item in combined_modified_files_of_missing_analysis for item in component_files):
                                analysis_row = matched_analysis[(matched_analysis['date'] == item.loc['AUTHOR_DATE'])]
                                line = (analysis_row['project'].values[0], analysis_row['analysis_key'].values[0],
                                        analysis_row['date'].values[0], item.loc['HASH'])
                                new_rows.append(line)
                                not_found = False
                            else:
                                not_found = True
                        else:
                            not_found = True

                    if not_found:
                        issues_of_missing_analysis_creation_update_close_date = issues_df[(
                            (issues_df['creation_date'] == row.loc['COMMIT_DATE']) |
                            (issues_df['update_date'] == row.loc['COMMIT_DATE']) |
                            (issues_df['close_date'] == row.loc['COMMIT_DATE'])
                        )].drop_duplicates(subset=['component'], keep='last')['component'].array

                        if issues_of_missing_analysis_creation_update_close_date:
                            component_files = sorted(
                                [os.path.basename(component)
                                 for component in issues_of_missing_analysis_creation_update_close_date])

                            # print('CREATION-UPDATE-CLOSE')
                            # print(component_files)
                            # print()
                            for i, _ in enumerate(component_files):
                                if component_files[i] == "org.apache:felix:pom.xml":
                                    component_files[i] = 'pom.xml'

                            if all(item in combined_modified_files_of_missing_analysis for item in component_files):
                                analysis_row = matched_analysis[(matched_analysis['date'] == item.loc['AUTHOR_DATE'])]
                                line = (analysis_row['project'].values[0], analysis_row['analysis_key'].values[0],
                                        analysis_row['date'].values[0], item.loc['HASH'])
                                new_rows.append(line)
            # print('*'*40)
    print(len(new_rows))
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
        if row.projectID == 'felix':
            compare_commit_and_analysis_dates(save_file_path=output_path, analysis_file=row.sonarProjectKey, commit_file=row.sonarProjectKey, project_name=row.projectID)
    #compare_dates = []
    #for pos, row in projects.iterrows():
    #    if row.projectID != 'zookeeper':
    #        if pos < 34:
    #            result = compare_commit_and_analysis_dates(save_file_path=output_path, analysis_file=row.sonarProjectKey,
    #                                          commit_file=row.sonarProjectKey, project_name=row.projectID)
    #            compare_dates.append(result)
    #        else:
    #            break
    #df = pd.DataFrame(data=compare_dates, columns={
    #        "project": "object",
    #        "not_matched": "object",
    #        "matched": "object",
    #        "matched%": "object"})
    #print(df.sort_values(by='matched%', ascending=False))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
