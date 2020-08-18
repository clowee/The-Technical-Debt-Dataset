import argparse
from Projects import Projects
from Metrics import Metrics

COURSE_SERVER = "https://course-sonar.rd.tuni.fi/"
SONAR63 = "http://sonar63.rd.tut.fi/"
ORGANIZATION = "default-organization"


def fetch_sonar_data(output_path):
    prj = Projects(SONAR63, ORGANIZATION, output_path)
    projects = prj.get_projects()
    metrics = Metrics(SONAR63, ORGANIZATION, output_path)
    metrics.get_metrics()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output-path", default='./sonar_data', help="Path to output file directory.")
    args = vars(ap.parse_args())
    output_path = args['output_path']
    fetch_sonar_data(output_path)


if __name__ == '__main__':
    main()
