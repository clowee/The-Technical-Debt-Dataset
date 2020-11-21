# This is a sample Python script.
import argparse
import pandas as pd
from pathlib import Path
import numpy as np


def get_analysis_key(date, key_date_list, pos):
    for i in range(len(key_date_list)):

        analysis_date = key_date_list[i][1]
        try:
            if date == analysis_date:
                return key_date_list[i][0]
        except TypeError:
            print('{0}: {1}'.format(pos, date))

def fix_analysis(save_file_path, sonarProjectKey, project_name):
    try:
        analysis_df = pd.read_csv(save_file_path + "/updated_analysis/" + "{0}.csv".format(
                sonarProjectKey.replace(' ', '_').replace(':', '_')))

        issues_df = pd.read_csv(save_file_path + "/updated_issues/" + "{0}.csv".format(
            sonarProjectKey.replace(' ', '_').replace(':', '_')))

        issues_df['close_analysis_key'] = ""
        for _pos, _row in issues_df.iterrows():
            close_date = _row.close_date
            if not pd.isnull(close_date):
                analysis_key = analysis_df[analysis_df['date'] == close_date]
                issues_df.at[_pos, 'close_analysis_key'] = None if close_date is None else analysis_key.iloc[0]['analysis_key']

        issues_df.drop(['update_date', 'current_analysis_key'], axis=1, inplace=True)

        new_issues_path = Path(save_file_path).joinpath("issue_with_close_analysis_key")
        new_issues_path.mkdir(parents=True, exist_ok=True)
        issues_file_path = new_issues_path.joinpath("{0}.csv".format(
            sonarProjectKey.replace(' ', '_').replace(':', '_')))
        issues_df.to_csv(issues_file_path, index=False, header=True)
    except FileNotFoundError:
        print("Not found {0}".format(project_name))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output-path", default='./sonar_data', help="Path to output file directory.")
    args = vars(ap.parse_args())
    output_path = args['output_path']
    projects = pd.read_csv(output_path + "/projects_list.csv")
    compare_dates = []
    for pos, row in projects.iterrows():
        fix_analysis(save_file_path=output_path, sonarProjectKey=row.sonarProjectKey,
                     project_name=row.projectID)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
