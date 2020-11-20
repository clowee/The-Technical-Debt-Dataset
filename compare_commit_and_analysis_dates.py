# This is a sample Python script.
import json
import argparse
import pandas as pd
import numpy as np
from pathlib import Path
import math


def compare_commit_and_analysis_dates(save_file_path, analysis_file, commit_file, project_name):
    issues_df = pd.read_csv(save_file_path + "/issues/" + "{0}.csv".format(
        analysis_file.replace(' ', '_').replace(':', '_')))
    creation_dates = issues_df['creation_date'].tolist()
    close_dates = issues_df['close_date'].tolist()
    no_duplicate_dates = sorted(np.unique(creation_dates + close_dates))
    no_duplicate_dates = list(filter(None, no_duplicate_dates))

    analysis_df = pd.read_csv(save_file_path + "/analysis/" + "{0}.csv".format(
            analysis_file.replace(' ', '_').replace(':', '_')))
    missing_dates_in_analysis = list(set(no_duplicate_dates) - set(analysis_df['date']))
    missing_dates_in_analysis = [x for x in missing_dates_in_analysis if str(x) != 'nan']
    new_dates = {'date': missing_dates_in_analysis}
    analysis_df = analysis_df.append(pd.DataFrame(new_dates))

    commits_df = pd.read_csv(save_file_path + "/Git_Logs/" + "{0}.csv".format(
                commit_file.replace(' ', '_').replace(':', '_')))
    commits_df.rename(columns={'AUTHOR_DATE': 'date'}, inplace=True)
    analysis_commit_df = pd.merge(analysis_df, commits_df[['date', 'HASH']], how='left', on='date')
    analysis_commit_df = analysis_commit_df.drop_duplicates(subset=['date'])
    analysis_commit_df = analysis_commit_df.drop(columns=['revision'])
    analysis_commit_df.rename(columns={'HASH': 'revision'}, inplace=True)

    new_analysis_path = Path(save_file_path).joinpath("compared_analysis_and_commit")
    new_analysis_path.mkdir(parents=True, exist_ok=True)
    analysis_file_path = new_analysis_path.joinpath("{0}.csv".format(
        analysis_file.replace(' ', '_').replace(':', '_')))
    analysis_commit_df.to_csv(analysis_file_path, index=False, header=True)

    analysis_with_revision_value = analysis_commit_df.dropna(subset=['revision'])
    new_analysis_path = Path(save_file_path).joinpath("analysis_with_revision_value")
    new_analysis_path.mkdir(parents=True, exist_ok=True)
    analysis_file_path = new_analysis_path.joinpath("{0}.csv".format(
        analysis_file.replace(' ', '_').replace(':', '_')))
    analysis_with_revision_value.to_csv(analysis_file_path, index=False, header=True)

    # test_analysis_path = Path(save_file_path).joinpath("commit_analysis")
    # test_analysis_path.mkdir(parents=True, exist_ok=True)
    # test_analysis_path = test_analysis_path.joinpath("{0}.csv".format(
    #     analysis_file.replace(' ', '_').replace(':', '_')))
    #
    # analysis_df.to_csv(test_analysis_path, index=False, header=True)

    commits_df.rename(columns={'date': 'AUTHOR_DATE'}, inplace=True)
    analysis_with_commit_match_info = analysis_commit_df.assign(
        DATE_MATCH=analysis_commit_df.date.isin(commits_df.AUTHOR_DATE).astype(int))

    compared = json.loads(analysis_with_commit_match_info['DATE_MATCH'].value_counts().to_json())
    not_matched = 0 if '0' not in compared else compared['0']
    matched = 0 if '1' not in compared else compared['1']
    frac, whole = math.modf((matched/(len(analysis_with_commit_match_info.index))*100))
    percentage = whole if whole > 95 else math.ceil(matched/(len(analysis_with_commit_match_info.index))*100)
    return project_name, not_matched, matched, percentage


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output-path", default='./sonar_data', help="Path to output file directory.")
    args = vars(ap.parse_args())
    output_path = args['output_path']
    projects = pd.read_csv(output_path + "/projects_list.csv")
    compare_dates = []
    ignore_projects_index = [1, 2, 3, 6, 29, 33, 34, 39, 40, 42, 43, 45, 46, 47, 48, 49, 50, 51]
    for pos, row in projects.iterrows():
        if pos not in ignore_projects_index:
            if (row.projectID == 'el') |\
                    (row.projectID == 'Lucene-core') |\
                    (row.projectId == 'accumulo') |\
                    (row.projectId == 'syncope'):
                continue
            sonar_project_key = row.sonarProjectKey
            commit_file = row.sonarProjectKey
            '''
            if row.projectID == 'zookeeper':
                sonar_project_key = 'org_apache_zookeper2'
                commit_file = 'org.apache_zookeeper'
            if row.projectID == 'accumulo':
            '''
            print(row.projectID)
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
