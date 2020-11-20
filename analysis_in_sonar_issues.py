# This is a sample Python script.
import argparse
import pandas as pd
from pathlib import Path


def fix_analysis(save_file_path, sonarProjectKey, project_name):
    try:
        analysis_df = pd.read_csv(save_file_path + "/updated_analysis/" + "{0}.csv".format(
                sonarProjectKey.replace(' ', '_').replace(':', '_')))

        issues_df = pd.read_csv(save_file_path + "/updated_issues/" + "{0}.csv".format(
            sonarProjectKey.replace(' ', '_').replace(':', '_')))

        issues_df.rename(columns={'close_date': 'date'}, inplace=True)
        new_issues_df = (issues_df[['date']].merge(analysis_df, on='date', how='left')
                         .rename(columns={'analysis_key': 'close_analysis_key'}))

        print((new_issues_df['date'].values == '').sum())
        print((new_issues_df['close_analysis_key'].values == '').sum())
        # new_issues_path = Path(save_file_path).joinpath("issue_with_analysis")
        # new_issues_path.mkdir(parents=True, exist_ok=True)
        # issues_file_path = new_issues_path.joinpath("{0}.csv".format(
        #     sonarProjectKey.replace(' ', '_').replace(':', '_')))
        # new_issues_df.to_csv(issues_file_path, index=False, header=True)
    except FileNotFoundError:
        print("Not found {0}".format(project_name))


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
            if (row.projectID == 'el') | \
                    (row.projectID == 'Lucene-core') | \
                    (row.projectID == 'accumulo') | \
                    (row.projectID == 'syncope'):
                continue
            fix_analysis(save_file_path=output_path, sonarProjectKey=row.sonarProjectKey,
                         project_name=row.projectID)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
