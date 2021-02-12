import pandas as pd
from pathlib import Path
from Interface import Interface
from RouteConfig import RequestsConfig
from ResponseUtils import ResponseUtils


class Projects(Interface):
    def __init__(self, server, organization, output_path):
        self.__server = server
        self.__endpoint = self.__server + "api/components/search"
        self.__organization = organization
        self.__qualifiers = 'TRK'
        self.__iter = 1
        self.__page_size = 100
        self.__params = {
            'p': self.__iter,
            'ps': self.__page_size,
            'organization': self.__organization,
            'qualifiers': self.__qualifiers
        }
        self.__project_list = []
        self.__total_num_projects = 0
        self.__response = {}

        self.__route_config = RequestsConfig()
        self.__session = self.__route_config.route_session()
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
            'total_num_elements': self.__total_num_projects})
        return result

    def __do_search(self):
        response = self.__call_the_api()
        if not self.__route_config.check_invalid_status_code(response=response):
            return []
        self.__response = response
        response_dict = self.__format_response()
        self.__project_list = response_dict['components']
        self.__total_num_projects = response_dict['paging']['total']
        if self.__check_num_of_elements():
            self.__iter += self.__iter
            self.__params['p'] = self.__iter
            self.__project_list = self.__project_list + self.__do_search()
        return self.__project_list

    def __write_into_csv(self):
        projects = []
        for project in self.__project_list:
            project_var = (project.values())
            projects.append(project_var)

        if projects:
            headers = list(self.__project_list[0].keys())
            output_path = Path(self.__output_path).joinpath("projects")
            output_path.mkdir(parents=True, exist_ok=True)
            file_path = output_path.joinpath("projects.csv")
            df = pd.DataFrame(data=projects, columns=headers)
            df.to_csv(file_path, index=False, header=True)

    def get_projects(self):
        self.__do_search()
        self.__write_into_csv()
        return self.__project_list


