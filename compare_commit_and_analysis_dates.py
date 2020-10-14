# This is a sample Python script.
import json
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
import math


def compare_commit_and_analysis_dates(save_file_path, analysis_file, commit_file, project_name):
    # The analysis of the given project in /sonar_data/analysis/ directory
    # print(analysis_file)
    issues_df = pd.read_csv(save_file_path + "/issues/" + "{0}.csv".format(
        analysis_file.replace(' ', '_').replace(':', '_')))
    creation_dates = issues_df['creation_date'].tolist()
    close_dates = issues_df['close_date'].tolist()
    no_duplicates = sorted(np.unique(creation_dates + close_dates))
    no_duplicates = list(filter(None, no_duplicates))

    analysis_df = pd.read_csv(save_file_path + "/analysis/" + "{0}.csv".format(
            analysis_file.replace(' ', '_').replace(':', '_')))

    missing_dates_in_analysis = list(set(no_duplicates) - set(analysis_df['date']))
    missing_dates_in_analysis = [x for x in missing_dates_in_analysis if str(x) != 'nan']
    new_dates = {'date': missing_dates_in_analysis}
    analysis_df = analysis_df.append(pd.DataFrame(new_dates))

    commits_df = pd.read_csv(save_file_path + "/Git_Logs/" + "{0}.csv".format(
                commit_file.replace(' ', '_').replace(':', '_')))

    analysis_commit_df = pd.merge(analysis_df, commits_df, how='left', left_on=['date'], right_on=['AUTHOR_DATE'])
    analysis_commit_df = analysis_commit_df.drop_duplicates(subset=['date'])
    analysis_commit_df = analysis_commit_df.drop(columns=['AUTHOR_NAME', 'AUTHOR_EMAIL', 'AUTHOR_DATE',
                                                          'AUTHOR_TIMEZONE', 'COMMITTER_NAME', 'COMMITTER_EMAIL',
                                                          'COMMITTER_DATE', 'COMMITTER_TIMEZONE', 'BRANCHES',
                                                          'IN_MAIN_BRANCH', 'IS_MERGE_COMMIT', 'MODIFIED_FILES',
                                                          'NUM_LINES_ADDED', 'NUM_LINES_REMOVED', 'COMMIT_PARENTS',
                                                          'PROJECT_NAME', 'DMM_UNIT_SIZE', 'DMM_UNIT_COMPLEXITY',
                                                          'DMM_UNIT_INTERFACING', 'revision'])
    analysis_commit_df.rename(columns={'HASH': 'revision'}, inplace=True)
    analysis_commit_df.dropna(subset=['revision'], inplace=True)
    new_analysis_path = Path(save_file_path).joinpath("updated_analysis")
    new_analysis_path.mkdir(parents=True, exist_ok=True)
    analysis_file_path = new_analysis_path.joinpath("{0}.csv".format(
        analysis_file.replace(' ', '_').replace(':', '_')))

    analysis_commit_df.to_csv(analysis_file_path, index=False, header=True)

    analysis_commit_df = analysis_commit_df.assign(DATE_MATCH=analysis_commit_df.date.isin(commits_df.AUTHOR_DATE).astype(int))
    analysis_commit_df['COMMIT_DATE'] = analysis_commit_df['date']
    compared = json.loads(analysis_commit_df['DATE_MATCH'].value_counts().to_json())
    not_matched = 0 if '0' not in compared else compared['0']
    matched = 0 if '1' not in compared else compared['1']
    frac, whole = math.modf((matched/(len(analysis_commit_df.index))*100))
    percentage = whole if whole > 95 else math.ceil(matched/(len(analysis_commit_df.index))*100)
    return project_name, not_matched, matched, percentage


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output-path", default='./sonar_data', help="Path to output file directory.")
    args = vars(ap.parse_args())
    output_path = args['output_path']
    projects = pd.read_csv(output_path + "/projects_list.csv")
    compare_dates = []
    for pos, row in projects.iterrows():
        if row.projectID == 'el':
            continue
        sonar_project_key = row.sonarProjectKey
        commit_file = row.sonarProjectKey
        if row.projectID == 'zookeeper':
            sonar_project_key = 'org_apache_zookeper2'
            commit_file = 'org.apache_zookeeper'
        if row.projectID == 'accumulo':
            result = compare_commit_and_analysis_dates(save_file_path=output_path, analysis_file=sonar_project_key,
                                                       commit_file=commit_file, project_name=row.projectID)
            print(result)
            compare_dates.append(result)

    df = pd.DataFrame(data=compare_dates, columns={
           "project": "object",
           "not_matched": "object",
           "matched": "object",
           "matched%": "object"})

    output_path = Path(output_path)
    output_path = output_path.joinpath("commit-hash-analysis")
    output_path.mkdir(parents=True, exist_ok=True)
    file_path = output_path.joinpath("Commit-hash-sonar-analysis-match-report.csv")
    df.to_csv(file_path, index=False, header=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
