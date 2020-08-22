from collections import OrderedDict
import pandas as pd
from pathlib import Path
from Interface import Interface
from RouteConfig import RequestsConfig
from ResponseUtils import ResponseUtils
from common import Common


class Analysis(Interface, Common):
    def __init__(self, server, output_path, project_key):
        Common.__init__(self)
        self.__server = server
        self.__endpoint = self.__server + "api/project_analyses/search"
        self.__iter = 1
        self.__page_size = 100
        self.__params = {
            'p': 1,
            'ps': self.__page_size,
            'project': project_key
        }
        self.__analysis_list = []
        self.__total_num_analysis = 0
        self.__response = {}

        self.__route_config = RequestsConfig()
        self.__session = self.__route_config.route_session()
        self.__output_path = output_path
        self.__project_key = project_key
        self.__SONAR_ANALYSES_TYPE = OrderedDict({
            "project": "object",
            "analysis_key": "object",
            "date": "object",
            "project_version": "object",
            "revision": "object"
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
            'total_num_elements': self.__total_num_analysis})
        return result

    def __do_search(self):
        response = self.__call_the_api()
        if not self.__route_config.check_invalid_status_code(response=response):
            return []
        self.__response = response
        response_dict = self.__format_response()
        self.__analysis_list = response_dict['analyses']
        self.__total_num_analysis = response_dict['paging']['total']
        if self.__check_num_of_elements():
            self.__params['p'] = self.__params['p'] + 1
            self.__analysis_list = self.__analysis_list + self.__do_search()
        return self.__analysis_list

    def __write_into_csv(self):
        analysis_list = []
        for analysis in self.__analysis_list:
            analysis_key = None if 'key' not in analysis else analysis['key']

            date = None if 'date' not in analysis else self.process_datetime(analysis['date'])

            project_version = None if 'projectVersion' not in analysis else analysis['projectVersion']
            revision = None if 'revision' not in analysis else analysis['revision']

            line = (self.__project_key, analysis_key, date, project_version, revision)
            analysis_list.append(line)

        if analysis_list:
            output_path = Path(self.__output_path).joinpath("analysis")
            output_path.mkdir(parents=True, exist_ok=True)
            file_path = output_path.joinpath("{0}.csv".format(
                self.__project_key.replace(' ', '_').replace(':', '_')))
            df = pd.DataFrame(data=analysis_list, columns=list(self.__SONAR_ANALYSES_TYPE.keys()))
            df.to_csv(file_path, index=False, header=True)
            return df
        return None

    def get_analysis(self):
        self.__do_search()
        result = self.__write_into_csv()
        return result
