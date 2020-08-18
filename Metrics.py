from collections import OrderedDict
import pandas as pd
from pathlib import Path
from Interface import Interface
from RouteConfig import RequestsConfig
from ResponseUtils import ResponseUtils
from common import Common


class Metrics(Interface, Common):
    def __init__(self, server, organization, output_path):
        Common.__init__(self)
        self.__server = server
        self.__endpoint = self.__server + "api/metrics/search"
        self.__organization = organization
        self.__iter = 1
        self.__page_size = 100
        self.__params = {
            'p': self.__iter,
            'ps': self.__page_size,
        }
        self.__metrics_list = []
        self.__total_num_metrics = 0
        self.__response = {}

        self.__route_config = RequestsConfig()
        self.__session = self.__route_config.route_session()
        self.__SONAR_MEASURES_TYPE = OrderedDict({
            'project': 'object',
            'analysis_key': 'object',
        })
        self.__output_path = output_path

    def __format_response(self):
        r_dict = self.__response.json()
        return r_dict

    def __call_the_api(self):
        return self.__route_config.call_api_route(session=self.__session, endpoint=self.__endpoint,
                                                  params=self.__params)

    def __check_num_of_elements(self):
        result = ResponseUtils.check_num_of_elements({
            'iter': self.__iter,
            'page_size': self.__page_size,
            'total_num_elements': self.__total_num_metrics})
        return result

    def __do_search(self):
        response = self.__call_the_api()
        if not self.__route_config.check_invalid_status_code(response=response):
            return []
        self.__response = response
        response_dict = self.__format_response()
        self.__metrics_list = response_dict['metrics']
        self.__total_num_metrics = response_dict['total']
        if self.__check_num_of_elements():
            self.__iter = self.__iter + 1
            self.__params['p'] = self.__iter
            self.__metrics_list = self.__metrics_list + self.__do_search()
        return self.__metrics_list

    def __write_into_csv(self):
        metrics = []
        for metric in self.__metrics_list:
            self.__SONAR_MEASURES_TYPE[metric['key']] = self.TYPE_CONVERSION[metric['type']]
            metric = ('No Domain' if 'domain' not in metric else metric['domain'],
                      'No Key' if 'key' not in metric else metric['key'],
                      'No Type' if 'type' not in metric else metric['type'],
                      'No Description' if 'description' not in metric else metric['description'])

            metrics.append(metric)

        if metrics:
            headers = ['domain', 'key', 'type', 'description']
            output_path = Path(self.__output_path).joinpath("metrics")
            output_path.mkdir(parents=True, exist_ok=True)
            file_path = output_path.joinpath("metrics.csv")
            df = pd.DataFrame(data=metrics, columns=headers)
            df.to_csv(file_path, index=False, header=True)

    def get_metrics(self):
        self.__do_search()
        self.__write_into_csv()
