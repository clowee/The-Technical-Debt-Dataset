class ResponseUtils:
    @staticmethod
    def check_num_of_elements(params):
        if params['iter'] * params['page_size'] < params['total_num_elements']:
            return True
        return False
