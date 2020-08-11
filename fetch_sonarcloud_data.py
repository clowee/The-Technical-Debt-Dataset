import requests
import math
from datetime import datetime, timedelta
from pathlib import Path
import sys
import pandas as pd
from collections import OrderedDict
import argparse
import numpy as np
import os
import csv
from urllib.parse import quote

SERVER = "https://course-sonar.rd.tuni.fi/"
ORGANIZATION = "default-organization"
SONAR_MEASURES_DTYPE = OrderedDict({
    'project': 'object',
    'analysis_key': 'object',
})

SONAR_ISSUES_DTYPE = OrderedDict({
    "project": "object",
    "current_analysis_key": "object",
    "creation_analysis_key": "object",
    "issue_key": "object",
    "type": "object",
    "rule": "object",
    "severity": "object",
    "status": "object",
    "resolution": "object",
    "effort": "Int64",
    "debt": "Int64",
    "tags": "object",
    "creation_date": "object",
    "update_date": "object",
    "close_date": "object",
})

SONAR_ANALYSES_DTYPE = OrderedDict({
    "project": "object",
    "analysis_key": "object",
    "date": "object",
    "project_version": "object",
    "revision": "object"
})

TYPE_CONVERSION = {
    "INT": "Int64",
    "FLOAT": 'float64',
    "DISTRIB": 'object',
    "PERCENT": 'float64',
    "MILLISEC": 'float64',
    "DATA": 'object',
    "BOOL": 'bool',
    "STRING": 'object',
    "WORK_DUR": 'float64',
    "RATING": 'float64',
    "LEVEL": 'float64'
}

MISSING_IN_HUNGS_SCRIPT = [
    "Structure101_Web_Application_URL",
    "accessors",
    "afferent-couplings",
    "arch-diagrams",
    "arch_violations",
    "arch_violations_weighted",
    "burned_budget",
    "business_value",
    "class_complexity_distribution",
    "commented_out_code_lines",
    "conditions_by_line",
    "coverage_line_hits_data",
    "covered_conditions_by_line",
    "efferent-couplings",
    "fat_class",
    "fat_design",
    "fat_leaf_package",
    "fat_method",
    "fat_method_list",
    "it_branch_coverage",
    "it_conditions_by_line",
    "it_conditions_to_cover",
    "it_coverage",
    "it_coverage_line_hits_data",
    "it_covered_conditions_by_line",
    "it_line_coverage",
    "it_lines_to_cover",
    "it_uncovered_conditions",
    "it_uncovered_lines",
    "java_count",
    "missing_package_info",
    "missing_package_info_count",
    "new_it_branch_coverage",
    "new_it_conditions_to_cover",
    "new_it_coverage",
    "new_it_line_coverage",
    "new_it_lines_to_cover",
    "new_it_uncovered_conditions",
    "new_it_uncovered_lines",
    "new_overall_branch_coverage",
    "new_overall_conditions_to_cover",
    "new_overall_coverage",
    "new_overall_line_coverage",
    "new_overall_lines_to_cover",
    "new_overall_uncovered_conditions",
    "new_overall_uncovered_lines",
    "number-of-classes-and-interfaces",
    "overall_branch_coverage",
    "overall_conditions_by_line",
    "overall_conditions_to_cover",
    "overall_coverage",
    "overall_coverage_line_hits_data",
    "overall_covered_conditions_by_line",
    "overall_line_coverage",
    "overall_lines_to_cover",
    "overall_uncovered_conditions",
    "overall_uncovered_lines",
    "package",
    "package-dependency-cycles",
    "package_count",
    "package_info_count",
    "s101.buildbreaker",
    "s101_model_alignment",
    "s101_model_class_mappings",
    "s101_model_name",
    "s101_model_refactoring_actions",
    "s101_model_sequential_actions",
    "sg_i.ARCHITECTURE_FEATURE_AVAILABLE,"
    "sg_i.CORE_ACD",
    "sg_i.CORE_ARTIFACT_COUNT",
    "sg_i.CORE_BIGGEST_COMPONENT_CYCLE_GROUP",
    "sg_i.CORE_CCD",
    "sg_i.CORE_CODE_COMMENT_LINES",
    "sg_i.CORE_COMMENT_LINES",
    "sg_i.CORE_COMPONENTS",
    "sg_i.CORE_COMPONENT_CYCLE_GROUPS",
    "sg_i.CORE_COMPONENT_DEPENDENCIES_TO_REMOVE_COMPONENTS",
    "sg_i.CORE_CYCLICITY_COMPONENTS",
    "sg_i.CORE_CYCLIC_COMPONENTS",
    "sg_i.CORE_DUPLICATED_LINES",
    "sg_i.CORE_DUPLICATES",
    "sg_i.CORE_EMPTY_ARTIFACT_COUNT",
    "sg_i.CORE_IGNORED_CYCLIC_COMPONENTS",
    "sg_i.CORE_IGNORED_DUPLICATES",
    "sg_i.CORE_IGNORED_THRESHOLD_VIOLATIONS",
    "sg_i.CORE_IGNORED_VIOLATIONS_PARSER_DEPENDENCIES",
    "sg_i.CORE_LINES_OF_CODE",
    "sg_i.CORE_MAX_ACD",
    "sg_i.CORE_NCCD",
    "sg_i.CORE_PARSER_DEPENDENCIES_TO_REMOVE_COMPONENTS",
    "sg_i.CORE_RACD",
    "sg_i.CORE_RELATIVE_CYCLICITY_COMPONENTS",
    "sg_i.CORE_SOURCE_ELEMENT_COUNT",
    "sg_i.CORE_STATEMENTS",
    "sg_i.CORE_STRUCTURAL_DEBT_INDEX_COMPONENTS",
    "sg_i.CORE_THRESHOLD_VIOLATIONS",
    "sg_i.CORE_TOTAL_LINES",
    "sg_i.CORE_UNASSIGNED_COMPONENTS",
    "sg_i.CORE_VIOLATING_COMPONENTS",
    "sg_i.CORE_VIOLATIONS_COMPONENT_DEPENDENCIES",
    "sg_i.CORE_VIOLATIONS_PARSER_DEPENDENCIES",
    "sg_i.CURRENT_VIRTUAL_MODEL",
    "sg_i.JAVA_BIGGEST_PACKAGE_CYCLE_GROUP",
    "sg_i.JAVA_BYTE_CODE_INSTRUCTIONS",
    "sg_i.JAVA_COMPONENT_DEPENDENCIES_TO_REMOVE_PACKAGES",
    "sg_i.JAVA_CYCLICITY_PACKAGES",
    "sg_i.JAVA_CYCLIC_PACKAGES",
    "sg_i.JAVA_CYCLIC_PACKAGES_PERCENT",
    "sg_i.JAVA_IGNORED_CYCLIC_PACKAGES",
    "sg_i.JAVA_PACKAGES",
    "sg_i.JAVA_PACKAGE_CYCLE_GROUPS",
    "sg_i.JAVA_PARSER_DEPENDENCIES_TO_REMOVE_PACKAGES",
    "sg_i.JAVA_RELATIVE_CYCLICITY_PACKAGES",
    "sg_i.JAVA_STRUCTURAL_DEBT_INDEX_PACKAGES",
    "sg_i.MAX_MODULE_NCCD",
    "sg_i.NUMBER_OF_CRITICAL_ISSUES_WITHOUT_RESOLUTION",
    "sg_i.NUMBER_OF_IGNORED_CRITICAL_ISSUES",
    "sg_i.NUMBER_OF_ISSUES",
    "sg_i.NUMBER_OF_PARSER_DEPENDENCIES_AFFECTED_BY_REFACTORINGS",
    "sg_i.NUMBER_OF_REFACTORINGS",
    "sg_i.NUMBER_OF_RESOLUTIONS",
    "sg_i.NUMBER_OF_TASKS",
    "sg_i.NUMBER_OF_THRESHOLD_VIOLATIONS",
    "sg_i.NUMBER_OF_UNAPPLICABLE_REFACTORINGS",
    "sg_i.NUMBER_OF_UNAPPLICABLE_RESOLUTIONS",
    "sg_i.NUMBER_OF_UNAPPLICABLE_TASKS",
    "sg_i.NUMBER_OF_WORKSPACE_WARNINGS",
    "sg_i.PERCENTAGEOFDEADCODE",
    "sg_i.STRUCTURAL_DEBT_COST",
    "sg_i.UNASSIGNED_COMPONENTS_PERCENT",
    "sg_i.VIOLATING_COMPONENTS_PERCENT",
    "sg_i.VIRTUAL_MODEL_FEATURE_AVAILABLE",
    "tangle_design",
    "team_size",
    "test_data",
    "xs",
    "xs_percent"
]


def write_metrics_file(metric_list):
    metric_list.sort(key=lambda x: ('None' if 'domain' not in x else x['domain'], int(x['id'])))

    with open('./all_metrics.csv', 'w') as f:
        f.write("Domain,Key,Type,Description\n")
        for metric in metric_list:
            # Ignore this, extremely long
            if metric == 'sonarjava_feedback':
                continue

            SONAR_MEASURES_DTYPE[metric['key']] = TYPE_CONVERSION[metric['type']]
            f.write("{},{},{},{}\n".format(
                'No Domain' if 'domain' not in metric else metric['domain'],
                'No Key' if 'key' not in metric else metric['key'],
                'No Type' if 'type' not in metric else metric['type'],
                'No Description' if 'description' not in metric else metric['description']
            ))


def query_server(type, iter=1, project_key=None, metric_list=None, from_ts=None, issue_type=None, issue_severity=None,
                 page_size=None, created_at=None, created_after=None):
    if metric_list is None:
        metric_list = []
    page_size = 200 if page_size is None else page_size
    params = {'p': iter, 'ps': page_size}

    if type == 'projects':
        endpoint = SERVER + "api/components/search"
        params['organization'] = ORGANIZATION
        params['qualifiers'] = 'TRK'

    elif type == 'metrics':
        endpoint = SERVER + "api/metrics/search"

    elif type == 'analyses':
        endpoint = SERVER + "api/project_analyses/search"
        if from_ts:
            params['from'] = from_ts
        params['project'] = project_key

    elif type == 'measures':
        endpoint = SERVER + "api/measures/search_history"
        if from_ts:
            params['from'] = from_ts
        params['component'] = project_key
        params['metrics'] = ','.join(metric_list)

    elif type == 'issues':
        endpoint = SERVER + "api/issues/search"
        params['componentKeys'] = project_key
        params['types'] = issue_type
        params['severities'] = issue_severity
        if created_at:
            params['createdAt'] = created_at
        if created_after:
            params['createdAfter'] = created_after
    else:
        print("ERROR: Illegal info type.")
        return []

    r = requests.get(endpoint, params=params)
    if r.status_code != 200:
        print("ERROR: HTTP Response code {0} for request {1}".format(r.status_code, r.request.path_url))
        return []
    r_dict = r.json()

    total_num_elements = 0

    if type == 'projects':
        element_list = r_dict['components']
        total_num_elements = r_dict['paging']['total']
    elif type == 'metrics':
        element_list = r_dict['metrics']
        total_num_elements = r_dict['total']
    elif type == 'analyses':
        element_list = r_dict['analyses']
        total_num_elements = r_dict['paging']['total']
    elif type == 'measures':
        element_list = r_dict['measures']
        total_num_elements = r_dict['paging']['total']
    elif type == 'issues':
        element_list = r_dict['issues']
        total_num_elements = r_dict['paging']['total']
        print(r.request.path_url)

    if iter * page_size < total_num_elements:
        if type == 'measures':
            element_list = concat_measures(element_list, query_server(type, iter + 1, project_key,
                                                                      metric_list=metric_list, from_ts=from_ts))
        elif type == 'issues':
            element_list = element_list + query_server(type, iter + 1, project_key, from_ts=from_ts,
                                                       issue_type=issue_type, page_size=page_size,
                                                       issue_severity=issue_severity, created_at=created_at,
                                                       created_after=created_after)
        else:
            element_list = element_list + query_server(type, iter + 1, project_key, from_ts=from_ts)

    return element_list


def concat_measures(measures_1, measures_2):
    for measure_1, measure_2 in zip(measures_1, measures_2):
        measure_1['history'] = measure_1['history'] + measure_2['history']
    return measures_1


def process_datetime(time_str):
    if time_str is None:
        return None

    ts = datetime.strptime(time_str[:19], "%Y-%m-%dT%H:%M:%S")

    offset = timedelta(hours=int(time_str[20:22]), minutes=int(time_str[22:24]))

    if time_str[19] == '-':
        ts = ts + offset
    elif time_str[19] == '+':
        ts = ts - offset

    return ts


def load_metrics(path=None):
    if path is None:
        current_file_path = os.path.realpath(__file__)
        parent_path = '/'.join(current_file_path.split("/")[:-1])
        path = '{0}/all_metrics.csv'.format(parent_path)
    p = Path(path)
    if not p.exists():
        print("ERROR: Path for metrics {0} does not exists.".format(p.resolve()))
        sys.exit(1)
    try:
        metrics_order = {}
        with open(p, 'r') as f:
            csvreader = csv.reader(f)
            next(csvreader)
            order = 0
            for line in csvreader:
                metric = line[1]
                metric_type = line[2]
                metrics_order[metric] = (order, metric_type)
                order += 1
        return metrics_order
    except:
        print("ERROR: Reading metrics file")
        sys.exit(1)


def get_duration_from_str(input_str):
    if input_str is not None:
        idx_min = input_str.find('min')
        idx_h = input_str.find('h')
        idx_d = input_str.find('d')

        if idx_d != -1:
            days = int(input_str[:idx_d])
            if len(input_str) == idx_d + 1:
                return 24 * 60 * days
            return 24 * 60 * days + get_duration_from_str(input_str[idx_d + 1:])

        if idx_h != -1:
            hours = int(input_str[:idx_h])
            if len(input_str) == idx_h + 1:
                return 60 * hours
            return 60 * hours + get_duration_from_str(input_str[idx_h + 1:])

        if idx_min != -1:
            mins = int(input_str[:idx_min])
            return mins

        print("ERROR: duration string '{0}' does not contain 'min', 'h' or 'd'.".format(input_str))
        sys.exit(1)


def safe_cast(val, to_type, contain_comma=False, list_with_semicolon=False):
    if to_type in ['INT', 'WORK_DUR']:
        try:
            return int(val)
        except (ValueError, TypeError):
            print("WARNING: exception casting value {0} to type {1}".format(str(val), to_type))
            return None
    elif to_type in ['FLOAT', 'PERCENT', 'RATING']:
        try:
            return float(val)
        except (ValueError, TypeError):
            print("WARNING: exception casting value {0} to type {1}".format(str(val), to_type))
            return None
    elif to_type == 'BOOL':
        try:
            return bool(val)
        except (ValueError, TypeError):
            print("WARNING: exception casting value {0} to type {1}".format(str(val), to_type))
            return None
    elif to_type == 'MILLISEC':
        try:
            if len(val) >= 12:
                return datetime.fromtimestamp(int(val) / 1000)
            else:
                return int(val)
        except (ValueError, TypeError):
            print("WARNING: exception casting value {0} to type {1}".format(str(val), to_type))
            return None
    else:
        try:
            value = str(val)
            if contain_comma:
                value = value.replace(',', ';')
            if list_with_semicolon:
                value = value.replace(';', ',')
            return value
        except (ValueError, TypeError):
            print("ERROR: error casting to type {0}".format(to_type))
            return None


def extract_measures_value(measures, metrics_order_type, columns, data):
    length_of_history = max(map(lambda s: len(s['history']), measures))

    for measure in measures:
        metric = measure['metric']
        metric_type = metrics_order_type[metric][1]
        columns.append(metric)
        history = measure['history']

        contain_comma = False
        if metric in ['quality_profiles', 'quality_gate_details']:
            contain_comma = True

        list_with_semicolon = False
        if metric in ['class_complexity_distribution', 'function_complexity_distribution',
                      'file_complexity_distribution', 'ncloc_language_distribution']:
            list_with_semicolon = True

        values = list(
            (map(lambda x: None if 'value' not in x else safe_cast(x['value'], metric_type, contain_comma,
                                                                   list_with_semicolon),
                 'None' if not history else history)))

        values.reverse()
        values = values[:len(data['analysis_key'])]

        if len(values) < length_of_history:
            for i in range(length_of_history - len(values)):
                values.append(None)

        # Resolving None Integer values
        if SONAR_MEASURES_DTYPE[metric] == "Int64":
            values = pd.array(values, dtype=pd.Int64Dtype())

        data[metric] = values
        if metric in MISSING_IN_HUNGS_SCRIPT and values:
           print("metric: {0}\t\t values: {1}".format(metric, values))
    return columns, data


def get_analysis_key(date, key_date_list):
    date = np.datetime64(date)

    for i in range(len(key_date_list)):

        analysis_date = key_date_list[i][1]

        if date > analysis_date:
            return key_date_list[i - 1][0]

    return key_date_list[-1][0]


def process_project_measures(project, output_path, new_analyses, metrics_path=None):
    project_key = project['key']

    output_path = Path(output_path).joinpath("measures")
    output_path.mkdir(parents=True, exist_ok=True)
    staging_file_path = output_path.joinpath("{0}_staging.csv".format(project_key.replace(' ', '_').replace(':', '_')))

    min_ts_str = None if new_analyses is None else new_analyses['date'].min().strftime(format='%Y-%m-%d')

    metrics_order_type = load_metrics(metrics_path)
    metrics = list(metrics_order_type.keys())
    measures = []
    for i in range(0, len(metrics), 15):
        # Get measures
        measures = measures + query_server('measures', 1, project_key, metrics[i:i + 15], from_ts=min_ts_str)

    measures.sort(key=lambda x: metrics_order_type[x['metric']][0])
    data = OrderedDict()
    data['analysis_key'] = new_analyses['analysis_key'].values.tolist()

    columns = ['project', 'analysis_key']

    print('*' * 30)
    print('{0}'.format(project['name']))
    columns_with_metrics, data_with_measures = extract_measures_value(measures, metrics_order_type, columns, data)
    print('*' * 30)

    # Create DF
    data_with_measures['project'] = [project_key] * len(new_analyses)
    df = pd.DataFrame(data_with_measures, columns=columns_with_metrics)
    df.to_csv(path_or_buf=staging_file_path, index=False, header=True, sep=',')


def get_creation_analysis_key(issue_key, archive_file_path, key_date_list):
    if archive_file_path.exists():

        df = pd.read_csv(archive_file_path.absolute(), dtype=SONAR_ISSUES_DTYPE,
                         parse_dates=["creation_date", "update_date", "close_date"])
        issue_key_df = df[df['issue_key'] == issue_key]
        if not issue_key_df.empty:
            lst = issue_key_df['creation_analysis_key'].unique().tolist()
            if len(lst) > 1:
                print(
                    "ERROR: More than 1 creation_analysis_key(s) at [{0}] - [{1}]".format(issue_key, str(archive_file_path.absolute())))
                sys.exit(1)
            return lst.values[0]

    return get_analysis_key(issue_key, key_date_list)


def process_project_issues(project, output_path, new_analyses, latest_analysis_ts_on_file):
    issue_types = ['CODE_SMELL', 'BUG', 'VULNERABILITY']
    severity_types = ['INFO', 'MINOR', 'MAJOR', 'CRITICAL', 'BLOCKER']
    project_key = project['key']

    output_path = Path(output_path).joinpath("issues")
    output_path.mkdir(parents=True, exist_ok=True)
    file_path = output_path.joinpath("{0}_staging.csv".format(project_key.replace(' ', '_').replace(':', '_')))
    archive_file_path = output_path.joinpath("{0}.csv".format(project_key.replace(' ', '_').replace(':', '_')))

    endpoint = SERVER + "api/issues/search"
    params = {'componentKeys': project_key, 'createdAfter': '1900-01-01T01:01:01+0100', 's': 'CREATION_DATE'}
    created_after = {'createdAfter': '1900-01-01T01:01:01+0100'}
    project_issues = []
    # for issue_type in issue_types:
    #     params['types'] = issue_type
    #     for severity_type in severity_types:
    #         params['severities'] = severity_type
    r = requests.get(endpoint, params=params)

    if r.status_code != 200:
        print("ERROR: HTTP Response code {0} for request {1}".format(r.status_code, r.request.path_url))

    r_dict = r.json()

    total_num_elements = r_dict['paging']['total']

    i = 0
    first_issue_date = '1900-01-01T01:01:01+0100'
    while total_num_elements > 10000:
        i = i + 1
        issues = r_dict['issues']
        if issues:
            print(issues[0])
            first_issue = issues[0]
            first_issue_date = first_issue['creationDate']

            project_issues += query_server('issues', 1, project_key=project_key, issue_type=None,
                                           issue_severity=None, page_size=500,
                                           created_at=first_issue_date)
            next_date = datetime.strptime(first_issue_date[:19], "%Y-%m-%dT%H:%M:%S")+timedelta(days=1)
        else:
            first_issue_date = first_issue_date
            next_date = datetime.strptime(first_issue_date[:19], "%Y-%m-%dT%H:%M:%S") + timedelta(days=1)

        next_datetime = '{0}-{1}-{2}T{3}:{4}:{5}+0000'.format(next_date.strftime('%Y'), next_date.strftime('%m'),
                                                              next_date.strftime('%d'), next_date.strftime('%H'),
                                                              next_date.strftime('%M'), next_date.strftime('%S'))
        created_after['createdAfter'] = next_datetime

        params['createdAfter'] = next_datetime
        r = requests.get(endpoint, params=params)

        if r.status_code != 200:
            print("ERROR: HTTP Response code {0} for request {1}".format(r.status_code, r.request.path_url))

        r_dict = r.json()

    project_issues += query_server('issues', 1, project_key=project_key, issue_type=None,
                                   issue_severity=None, page_size=200, created_after=created_after['createdAfter'])

    print('\nanalyze\n')
    new_analysis_keys = new_analyses['analysis_key'].values.tolist()
    new_analysis_dates = new_analyses['date'].values
    # dates are in decreasing order
    key_date_list = list(zip(new_analysis_keys, new_analysis_dates))

    issues = []
    for project_issue in project_issues[0:20000]:

        update_date = None if 'updateDate' not in project_issue else process_datetime(project_issue['updateDate'])
        # belong to the analyses on file
        if update_date is not None and latest_analysis_ts_on_file is not None and update_date <= latest_analysis_ts_on_file:
            continue
        current_analysis_key = None if update_date is None else get_analysis_key(update_date, key_date_list)

        creation_date = None if 'creationDate' not in project_issue else process_datetime(project_issue['creationDate'])
        creation_analysis_key = None if creation_date is None else get_creation_analysis_key(creation_date,
                                                                                             archive_file_path,
                                                                                             key_date_list)

        close_date = None if 'closeDate' not in project_issue else process_datetime(project_issue['closeDate'])

        issue_key = None if 'key' not in project_issue else project_issue['key']
        rule = None if 'rule' not in project_issue else project_issue['rule']
        severity = None if 'severity' not in project_issue else project_issue['severity']
        status = None if 'status' not in project_issue else project_issue['status']
        resolution = None if 'resolution' not in project_issue else project_issue['resolution']

        effort = None if 'effort' not in project_issue else get_duration_from_str(project_issue['effort'])
        debt = None if 'debt' not in project_issue else get_duration_from_str(project_issue['debt'])

        if 'tags' not in project_issue or len(project_issue['tags']) == 0:
            tags = None
        else:
            tags = ','.join(project_issue['tags'])

        type = None if 'type' not in project_issue else project_issue['type']

        issue = (
        project_key, current_analysis_key, creation_analysis_key, issue_key, type, rule, severity, status, resolution,
        effort, debt, tags, creation_date, update_date, close_date)
        issues.append(issue)

    print("\t\t{0} - {1} new issues".format(project_key, len(issues)))
    if issues:
        df = pd.DataFrame(data=issues, columns=SONAR_ISSUES_DTYPE.keys())
        df = df.astype({
            "effort": "Int64",
            "debt": "Int64"
        })

        df.to_csv(file_path, index=False, header=True)


def process_project_analyses(project, output_path):
    project_key = project['key']

    output_path = Path(output_path).joinpath("analyses")
    output_path.mkdir(parents=True, exist_ok=True)
    staging_file_path = output_path.joinpath("{0}_staging.csv".format(project_key.replace(' ', '_').replace(':', '_')))
    archive_file_path = output_path.joinpath("{0}.csv".format(project_key.replace(' ', '_').replace(':', '_')))

    last_analysis_ts = None
    if archive_file_path.exists():
        try:
            old_df = pd.read_csv(archive_file_path.absolute(), dtype=SONAR_ANALYSES_DTYPE, parse_dates=['date'])
            last_analysis_ts = old_df['date'].max()

        except ValueError as e:
            print("\t\tERROR: {0} when parsing {1} into DataFrame.".format(e, archive_file_path))

        except FileNotFoundError as e:
            # print(f"\t\tWARNING: No .{format} file found for project {project_key} in output path for")
            pass

    lines = []
    from_ts = None if last_analysis_ts is None else last_analysis_ts.strftime(format='%Y-%m-%d')
    analyses = query_server('analyses', 1, project_key=project_key, from_ts=from_ts)
    for analysis in analyses:
        analysis_key = None if 'key' not in analysis else analysis['key']

        date = None if 'date' not in analysis else process_datetime(analysis['date'])
        if date is not None and last_analysis_ts is not None:
            if date <= last_analysis_ts:
                continue

        project_version = None if 'projectVersion' not in analysis else analysis['projectVersion']
        revision = None if 'revision' not in analysis else analysis['revision']

        line = (project_key, analysis_key, date, project_version, revision)
        lines.append(line)

    print("\t\t {0} - {1} new analyses.".format(project_key, len(lines)))
    if len(lines) > 0:
        df = pd.DataFrame(data=lines, columns=SONAR_ANALYSES_DTYPE.keys())
        df.to_csv(staging_file_path, index=False, header=True)
        return df, last_analysis_ts

    return None, last_analysis_ts


def fetch_sonar_data(output_path):
    project_list = query_server(type='projects')
    project_list.sort(key=lambda x: x['key'])

    print("Total: {0} projects.".format(len(project_list)))
    i = 0
    with open('./projects.csv', 'w') as f:
        f.write(",".join(project_list[0].keys()) + "\n")
        for project in [project_list[0]]:
            f.write(",".join("{}".format(d) for d in project.values())+"\n")

            new_analyses, latest_analysis_ts_on_file = process_project_analyses(project, output_path)
            if new_analyses is None:
                continue
            # process_project_measures(project, output_path, new_analyses)
            process_project_issues(project, output_path, new_analyses, latest_analysis_ts_on_file)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output-path", default='./data', help="Path to output file directory.")

    args = vars(ap.parse_args())

    output_path = args['output_path']

    # Write all metrics to a file
    write_metrics_file(query_server(type='metrics'))

    fetch_sonar_data(output_path)
