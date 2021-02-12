from collections import OrderedDict
import pandas as pd
import os
import sys
import csv
from datetime import datetime
from pathlib import Path
from Interface import Interface
from RouteConfig import RequestsConfig
from ResponseUtils import ResponseUtils
from common import Common


class Measures(Interface, Common):
    def __init__(self, server, output_path, project_key, analyses, measures_type):
        Common.__init__(self)
        self.__server = server
        self.__endpoint = self.__server + "api/measures/search_history"
        self.__page_size = 1000
        self.__metrics_params = []
        self.__params = {
            'p': 1,
            'ps': self.__page_size,
            'component': project_key
        }
        self.__measures_list = []
        self.__headers = []
        self.__total_num_measures = 0
        self.__response = {}

        self.__route_config = RequestsConfig()
        self.__session = self.__route_config.route_session()
        self.__output_path = output_path
        self.__project_key = project_key
        self.__analysis = analyses
        self.measures_type = measures_type

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
            'total_num_elements': self.__total_num_measures})
        return result

    @staticmethod
    def __get_metrics():
        current_file_path = os.path.realpath(__file__)
        parent_path = '/'.join(current_file_path.split("/")[:-1])
        path = '{0}/sonar_data/metrics/metrics.csv'.format(parent_path)
        p = Path(path)
        if not p.exists():
            print("ERROR: Path for metrics {0} does not exists.".format(p.resolve()))
            sys.exit(1)
        try:
            metrics_order = {}
            with open(p, 'r') as f:
                csv_reader = csv.reader(f)
                next(csv_reader)
                order = 0
                for line in csv_reader:
                    metric = line[1]
                    metric_type = line[2]
                    metrics_order[metric] = (order, metric_type)
                    order += 1
            return metrics_order
        except Exception as e:
            print("ERROR: Reading metrics file", e)
            sys.exit(1)

    @staticmethod
    def __concat_measures(measures_1, measures_2):
        for measure_1, measure_2 in zip(measures_1, measures_2):
            if measure_2['history']:
                measure_1['history'] = measure_1['history'] + measure_2['history']
        return measures_1

    def __do_search(self):
        response = self.__call_the_api()
        if not self.__route_config.check_invalid_status_code(response=response):
            return []

        response_dict = response.json()
        measures = response_dict['measures']
        self.__total_num_measures = response_dict['paging']['total']
        if self.__check_num_of_elements():
            self.__params['p'] = self.__params['p'] + 1
            measures = self.__concat_measures(measures, self.__do_search())
        return measures

    def __write_into_csv(self):
        output_path = Path(self.__output_path).joinpath("measures")
        output_path.mkdir(parents=True, exist_ok=True)
        file_path = output_path.joinpath("{0}.csv".format(
            self.__project_key.replace(' ', '_').replace(':', '_')))

        df = pd.DataFrame(data=self.__measures_list, columns=self.__headers)
        df.to_csv(file_path, index=False, header=True)

    @staticmethod
    def __safe_cast(val, to_type, contain_comma=False, list_with_semicolon=False):
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

    def __extract_measures_value(self, measures, metrics_order_type, columns, data):
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
                (map(lambda x: None if 'value' not in x else self.__safe_cast(x['value'], metric_type, contain_comma,
                                                                              list_with_semicolon),
                     'None' if not history else history)))

            values.reverse()

            values = values[:len(data['analysis_key'])]
            if len(values) < length_of_history:
                for i in range(length_of_history - len(values)):
                    values.append(None)

            if self.measures_type[metric] == "Int64":
                values = pd.array(values, dtype=pd.Int64Dtype())

            data[metric] = values
        return columns, data

    def __metric_wise_search(self):
        metrics = self.__get_metrics()
        metrics_list = list(metrics.keys())
        measures = []

        for i in range(0, len(metrics_list), 10):
            self.__params['metrics'] = ','.join(metrics_list[i:i + 10])
            self.__params['p'] = 1
            measures = measures + self.__do_search()

        measures.sort(key=lambda x: metrics[x['metric']][0])
        data = OrderedDict()
        data['analysis_key'] = self.__analysis['analysis_key'].values.tolist()

        columns = ['analysis_key']
        self.__headers, self.__measures_list = self.__extract_measures_value(measures, metrics, columns, data)
        self.__write_into_csv()

    def get_measures(self):
        self.__metric_wise_search()
