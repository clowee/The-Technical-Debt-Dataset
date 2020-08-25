import pandas as pd
from collections import OrderedDict
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np
import sys
from Interface import Interface
from RouteConfig import RequestsConfig
from ResponseUtils import ResponseUtils
from common import Common


class Issues(Interface, Common):
    def __init__(self, server, output_path, project_key, analyses):
        Common.__init__(self)
        self.__server = server
        self.__endpoint = self.__server + "api/issues/search"
        self.__page_size = 500
        self.__project_key = project_key
        self.__params = {
            'p': 1,
            'ps': self.__page_size,
            'componentKeys': project_key,
            'createdAfter': '1900-01-01T01:01:01+0100',
            'createdAt': None,
            'severities': None,
            's': 'CREATION_DATE'
        }
        self.__issues_list = []
        self.__total_num_issues = 0
        self.__response = {}

        self.__route_config = RequestsConfig()
        self.__session = self.__route_config.route_session()
        self.__output_path = output_path
        self.__analysis = analyses
        self.__SONAR_ISSUES_TYPE = OrderedDict({
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
            "message": "object",
            "component": "object",
            "start_line": "Int64",
            "end_line": "Int64",
            "start_offset": "Int64",
            "end_offset": "Int64",
            "hash": "object",
            "from_hotspot": "object"
        })

    def __format_response(self):
        r_dict = self.__response.json()
        return r_dict

    def __call_the_api(self):
        return self.__route_config.call_api_route(session=self.__session, endpoint=self.__endpoint,
                                                  params=self.__params)

    def __check_num_of_elements(self):
        result = ResponseUtils.check_num_of_elements({
            'iter': self.__params['p'],
            'page_size': self.__page_size,
            'total_num_elements': self.__total_num_issues})
        return result

    def __do_search(self):
        response = self.__call_the_api()
        if not self.__route_config.check_invalid_status_code(response=response):
            return []
        response_dict = response.json()
        issues = response_dict['issues']
        self.__total_num_issues = response_dict['paging']['total']
        if self.__check_num_of_elements():
            self.__params['p'] = self.__params['p'] + 1
            issues = issues + self.__do_search()
        self.__params['p'] = 1
        return issues

    def __write_into_csv(self):
        output_path = Path(self.__output_path).joinpath("issues")
        output_path.mkdir(parents=True, exist_ok=True)
        file_path = output_path.joinpath("{0}.csv".format(
            self.__project_key.replace(' ', '_').replace(':', '_')))

        df = pd.DataFrame(data=self.__issues_list, columns=self.__SONAR_ISSUES_TYPE.keys())
        df = df.astype({
            "effort": "Int64",
            "debt": "Int64"
        })

        df.to_csv(file_path, index=False, header=True)

    def __check_issue_total(self, created_at=None, total_in_a_datetime=0):
        severity_types = ['INFO', 'MINOR', 'MAJOR', 'CRITICAL', 'BLOCKER']
        element_list = []
        self.__params['createdAt'] = created_at
        self.__params['createdAfter'] = None
        if total_in_a_datetime > 10000:
            for severity_type in severity_types:
                self.__params['severities'] = severity_type
                element_list = element_list + self.__do_search()
        else:
            self.__params['severities'] = None
            element_list = self.__do_search()
        return element_list

    @staticmethod
    def __get_analysis_key(date, key_date_list):
        date = np.datetime64(date)
        for i in range(len(key_date_list)):

            analysis_date = key_date_list[i][1]

            if date > analysis_date:
                return key_date_list[i - 1][0]

        return key_date_list[-1][0]

    def get_creation_analysis_key(self, issue_key, archive_file_path, key_date_list):
        if archive_file_path.exists():
            df = pd.read_csv(archive_file_path.absolute(), dtype=self.__SONAR_ISSUES_TYPE,
                             parse_dates=["creation_date", "update_date", "close_date"])
            issue_key_df = df[df['issue_key'] == issue_key]
            if not issue_key_df.empty:
                lst = issue_key_df['creation_analysis_key'].unique().tolist()
                if len(lst) > 1:
                    print(
                        "ERROR: More than 1 creation_analysis_key(s) at [{0}] - [{1}]".format(issue_key, str(
                            archive_file_path.absolute())))
                    sys.exit(1)
                return lst.values[0]

        return self.__get_analysis_key(issue_key, key_date_list)

    def __get_duration_from_str(self, input_str):
        if input_str is not None:
            idx_min = input_str.find('min')
            idx_h = input_str.find('h')
            idx_d = input_str.find('d')

            if idx_d != -1:
                days = int(input_str[:idx_d])
                if len(input_str) == idx_d + 1:
                    return 24 * 60 * days
                return 24 * 60 * days + self.__get_duration_from_str(input_str[idx_d + 1:])

            if idx_h != -1:
                hours = int(input_str[:idx_h])
                if len(input_str) == idx_h + 1:
                    return 60 * hours
                return 60 * hours + self.__get_duration_from_str(input_str[idx_h + 1:])

            if idx_min != -1:
                minutes = int(input_str[:idx_min])
                return minutes

            print("ERROR: duration string '{0}' does not contain 'min', 'h' or 'd'.".format(input_str))
            sys.exit(1)

    def __prepare_search(self):
        response = self.__call_the_api()
        if not self.__route_config.check_invalid_status_code(response=response):
            return []
        response_dict = response.json()
        project_issues = []
        first_issue_date = '1900-01-01T01:01:01+0100'
        while response_dict['paging']['total'] > 10000:
            issues = response_dict['issues']
            if issues:
                first_issue = issues[0]
                first_issue_date = first_issue['creationDate']

                project_issues += self.__check_issue_total(created_at=first_issue_date,
                                                           total_in_a_datetime=response_dict['paging']['total'])

            next_date = datetime.strptime(first_issue_date[:19], "%Y-%m-%dT%H:%M:%S") + timedelta(seconds=1)

            next_datetime = '{0}-{1}-{2}T{3}:{4}:{5}{6}'.format(next_date.strftime('%Y'), next_date.strftime('%m'),
                                                                next_date.strftime('%d'), next_date.strftime('%H'),
                                                                next_date.strftime('%M'), next_date.strftime('%S'),
                                                                first_issue_date[19:])
            self.__params['createdAfter'] = next_datetime
            self.__params['createdAt'] = None
            self.__params['severities'] = None
            response = self.__call_the_api()
            if response.status_code != 200:
                print("ERROR: HTTP Response code {0} for request {1}".format(response.status_code,
                                                                             response.request.path_url))

            response_dict = response.json()

        self.__params['createdAt'] = None
        self.__params['severities'] = None
        project_issues += self.__do_search()

        new_analysis_keys = self.__analysis['analysis_key'].values.tolist()
        new_analysis_dates = self.__analysis['date'].values
        # dates are in decreasing order
        key_date_list = list(zip(new_analysis_keys, new_analysis_dates))
        issues = []
        if project_issues:
            for project_issue in project_issues:

                update_date = None if 'updateDate' not in project_issue else self.process_datetime(project_issue['updateDate'])
                # belong to the analyses on file

                current_analysis_key = None if update_date is None else self.__get_analysis_key(update_date, key_date_list)
                creation_date = None if 'creationDate' not in project_issue else self.process_datetime(
                    project_issue['creationDate'])
                creation_analysis_key = None if creation_date is None else self.__get_analysis_key(creation_date,
                                                                                                   key_date_list)
                close_date = None if 'closeDate' not in project_issue else self.process_datetime(project_issue['closeDate'])
                issue_key = None if 'key' not in project_issue else project_issue['key']
                rule = None if 'rule' not in project_issue else project_issue['rule']
                severity = None if 'severity' not in project_issue else project_issue['severity']
                status = None if 'status' not in project_issue else project_issue['status']
                resolution = None if 'resolution' not in project_issue else project_issue['resolution']
                effort = None if 'effort' not in project_issue else self.__get_duration_from_str(project_issue['effort'])
                debt = None if 'debt' not in project_issue else self.__get_duration_from_str(project_issue['debt'])

                if 'tags' not in project_issue or len(project_issue['tags']) == 0:
                    tags = None
                else:
                    tags = ','.join(project_issue['tags'])
                issue_type = None if 'type' not in project_issue else project_issue['type']
                message = None if 'message' not in project_issue else project_issue['message']
                component = None if 'component' not in project_issue else project_issue['component']
                start_line = None if 'textRange' not in project_issue else None if 'startLine' not in project_issue[
                    'textRange'] \
                    else project_issue['textRange']['startLine']
                end_line = None if 'textRange' not in project_issue else None if 'endLine' not in project_issue[
                    'textRange'] else project_issue['textRange']['endLine']
                start_offset = None if 'textRange' not in project_issue else None if 'startOffset' not in project_issue[
                    'textRange'] else project_issue['textRange']['startOffset']
                end_offset = None if 'textRange' not in project_issue else None if 'endOffset' not in project_issue[
                    'textRange'] else project_issue['textRange']['endOffset']
                hash_value = None if 'hash' not in project_issue else project_issue['hash']
                from_hotspot = None if 'fromHotspot' not in project_issue else project_issue['fromHotspot']

                issue = (self.__project_key, current_analysis_key, creation_analysis_key, issue_key, issue_type, rule,
                         severity, status, resolution, effort, debt, tags, creation_date, update_date, close_date, message,
                         component, start_line, end_line, start_offset, end_offset, hash_value, from_hotspot)
                issues.append(issue)
            self.__issues_list = issues
            self.__write_into_csv()

    def get_issues(self):
        self.__prepare_search()
        # response = self.__call_the_api()
        # if not self.__route_config.check_invalid_status_code(response=response):
        #     return []
        # response_dict = response.json()
        # print("{0}---{1}".format(self.__project_key, response_dict['paging']['total']))
