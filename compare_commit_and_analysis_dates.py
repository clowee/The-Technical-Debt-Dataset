# This is a sample Python script.
import json
import argparse
import pandas as pd


def compare_commit_and_analysis_dates(save_file_path, analysis_file, commit_file, project_name):
    # The analysis of the given project in /sonar_data/analysis/ directory
    analysis_df = pd.read_csv(save_file_path + "/analysis/" + "{0}.csv".format(
            analysis_file.replace(' ', '_').replace(':', '_')))

    commits_df = pd.read_csv(save_file_path + "/Git_Logs/" + "{0}.csv".format(
            commit_file.replace(' ', '_').replace(':', '_')))
    analysis_df = analysis_df.assign(DATE_MATCH=analysis_df.date.isin(commits_df.AUTHOR_DATE).astype(int))
    analysis_df['COMMIT_DATE'] = analysis_df['date']
    compared = json.loads(analysis_df['DATE_MATCH'].value_counts().to_json())
    not_matched = 0 if '0' not in compared else compared['0']
    matched = 0 if '1' not in compared else compared['1']
    return project_name, not_matched, matched, (matched/(len(analysis_df.index))*100)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output-path", default='./sonar_data', help="Path to output file directory.")
    args = vars(ap.parse_args())
    output_path = args['output_path']
    projects = pd.read_csv(output_path + "/projects_list.csv")
    compare_dates = []
    for pos, row in projects.iterrows():
       result = compare_commit_and_analysis_dates(save_file_path=output_path, analysis_file=row.sonarProjectKey,
                                                  commit_file=row.sonarProjectKey, project_name=row.projectID)
       compare_dates.append(result)
    df = pd.DataFrame(data=compare_dates, columns={
           "project": "object",
           "not_matched": "object",
           "matched": "object",
           "matched%": "object"})
    print(df.sort_values(by='matched%', ascending=False))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
