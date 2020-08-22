import argparse
from Projects import Projects
from Metrics import Metrics
from Analysis import Analysis
from Measures import Measures
from Issues import Issues

COURSE_SERVER = "https://course-sonar.rd.tuni.fi/"
SONAR63 = "http://sonar63.rd.tut.fi/"
ORGANIZATION = "default-organization"


def fetch_sonar_data(output_path):
    metrics = Metrics(SONAR63, ORGANIZATION, output_path)
    metrics_list = metrics.get_metrics()

    prj = Projects(SONAR63, ORGANIZATION, output_path)
    projects = prj.get_projects()
    projects.sort(key=lambda x: x['key'])

    print("Total: {0} projects.".format(len(projects)))

    for project in [projects[0]]:
        analysis = Analysis(SONAR63, output_path, project['key'])
        new_analysis = analysis.get_analysis()

        if new_analysis is None:
            continue
        measure = Measures(SONAR63, project_key=project['key'], output_path=output_path,
                           analyses=new_analysis, measures_type=metrics_list)
        measure.get_measures()

        issues = Issues(SONAR63, output_path, project['key'], analyses=new_analysis)
        issues.get_issues()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output-path", default='./sonar_data', help="Path to output file directory.")
    args = vars(ap.parse_args())
    output_path = args['output_path']
    fetch_sonar_data(output_path)


if __name__ == '__main__':
    main()
