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
    i = 1
    for project in projects:
        if project['name'] not in ['QC - aspectj','QC - azureus' ,'QC - castor', 'QC - compiere', 'QC - derby'
            ,'QC - hadoop', 'QC - jboss', 'QC - jrefactory', 'QC - jruby', 'QC - jtopen', 'QC - megamek',
            'QC - myfaces core', 'QC - poi', 'QC - weka', 'Kactus2', 'Apache_Airavata', 'Apache_Allura', 'Apache_Beam',
            'Apache_Hive', 'Apache_Lucene', 'Apache_Santuario', 'Apache_Syncope', 'Apache_Allura', 'Apache_Accumulo']:
            print('{0} - {1}'.format(i, project['name']))
            i += 1
        # print('{0} analysis starts'.format(project['name']))
        # analysis = Analysis(SONAR63, output_path, project['key'])
        # new_analysis = analysis.get_analysis()
        # print('{0} analysis completed'.format(project['name']))
        #
        # if new_analysis is None:
        #     continue
        #
        # print('{0} measure starts'.format(project['name']))
        # measure = Measures(SONAR63, project_key=project['key'], output_path=output_path,
        #                    analyses=new_analysis, measures_type=metrics_list)
        # measure.get_measures()
        # print('{0} measure completed'.format(project['name']))
        #
        # print('{0} issues starts'.format(project['name']))
        # issues = Issues(SONAR63, output_path, project['key'], analyses=new_analysis)
        # issues.get_issues()
        # print('{0} issues completed'.format(project['name']))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output-path", default='./sonar_data', help="Path to output file directory.")
    args = vars(ap.parse_args())
    output_path = args['output_path']
    fetch_sonar_data(output_path)


if __name__ == '__main__':
    main()
