# This is a sample Python script.
import argparse
import pandas as pd
from pathlib import Path


def compare_analysis_measures(save_file_path, analysis_file, measure_file, project_name):
    # The analysis of the given project in /sonar_data/analysis/ directory
    try:
        analysis_df = pd.read_csv(save_file_path + "/updated_analysis/" + "{0}.csv".format(
                analysis_file.replace(' ', '_').replace(':', '_')))

        measures_df = pd.read_csv(save_file_path + "/measures/" + "{0}.csv".format(
            measure_file.replace(' ', '_').replace(':', '_')))

        modified_measures_df = measures_df[measures_df.analysis_key.isin(analysis_df.analysis_key.values)]
        new_measure_path = Path(save_file_path).joinpath("updated_measures")
        new_measure_path.mkdir(parents=True, exist_ok=True)
        measure_file_path = new_measure_path.joinpath("{0}.csv".format(
            analysis_file.replace(' ', '_').replace(':', '_')))
        modified_measures_df.to_csv(measure_file_path, index=False, header=True)
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
        compare_analysis_measures(save_file_path=output_path, analysis_file=row.sonarProjectKey,
                                  measure_file=row.sonarProjectKey, project_name=row.projectID)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
