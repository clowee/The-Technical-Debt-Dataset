# import os
# from typing import re

from datetime import datetime
from collections import OrderedDict

from pydriller import RepositoryMining
import pandas as pd
import argparse
from collections import OrderedDict
import git
from pathlib import Path
from ast import literal_eval
import os


def format_array_to_string(array_to_convert):
    if array_to_convert:
        result = "["
        for x in array_to_convert:
            result += "'"+str(x) + "', "
        result = result[:-1]
        result += "]"
        return result
    return "[]"


def check_value_exists(value):
    return 'None' if value == '' else value


def modify_string(value):
    value = value.replace('\n', ' ')
    value = value.replace(',', ' ')
    value = value.replace(';', ' ')
    return value


def get_commits():
    project_name = 'ambari'
    projectDirAbsPath = '/home/sazzad/'+project_name
    currentProjectCsv = '/home/sazzad/Git_Logs/' + project_name + '_logs.csv'
    commits = []
    headers = OrderedDict({
        "HASH": "object",
        "AUTHOR_NAME": "object",
        "AUTHOR_EMAIL": "object",
        "AUTHOR_DATE": "object",
        "AUTHOR_TIMEZONE": "object",
        "COMMITTER_NAME": "object",
        "COMMITTER_EMAIL": "object",
        "COMMITTER_DATE": "object",
        "COMMITTER_TIMEZONE": "object",
        "BRANCHES": "object",
        "IN_MAIN_BRANCH": "object",
        "IS_MERGE_COMMIT": "object",
        "MODIFIED_FILES": "object",
        "NUM_LINES_ADDED": "object",
        "NUM_LINES_REMOVED": "object",
        "COMMIT_PARENTS": "object",
        "PROJECT_NAME": "object",
        "DMM_UNIT_SIZE": "object",
        "DMM_UNIT_COMPLEXITY": "object",
        "DMM_UNIT_INTERFACING": "object"
    })

    i = 0
    for commit in RepositoryMining(projectDirAbsPath).traverse_commits():

        hash = check_value_exists(commit.hash)
        # msg = check_value_exists(modify_string(commit.msg))
        author_name = check_value_exists(commit.author.name)
        author_email = check_value_exists(commit.author.email)
        author_date = check_value_exists(commit.author_date.strftime("%Y-%m-%d %H:%M:%S"))
        author_timezone = check_value_exists(str(commit.author_timezone))
        committer_name = check_value_exists(commit.committer.name)
        committer_email = check_value_exists(commit.committer.email)
        committer_date = check_value_exists(str(commit.committer_date.strftime("%Y-%m-%d %H:%M:%S")))
        committer_timezone = check_value_exists(str(commit.committer_timezone))
        branches = format_array_to_string(commit.branches)  # format
        in_main_branch = check_value_exists(str(commit.in_main_branch))
        merge = check_value_exists(str(commit.merge))
        parents = None if len(commit.parents) == 0 else format_array_to_string(commit.parents)  # format
        project_name = check_value_exists(commit.project_name)
        dmm_unit_size = check_value_exists(str(commit.dmm_unit_size))
        dmm_unit_complexity = check_value_exists(str(commit.dmm_unit_complexity))
        dmm_unit_interfacing = check_value_exists(str(commit.dmm_unit_interfacing))

        modified_files = []
        num_lines_added = []
        num_lines_removed = []
        for mod in commit.modifications:
           modified_file = mod.filename
           num_added = mod.added
           num_removed = mod.removed

           modified_files.append(modified_file)
           num_lines_added.append(num_added)
           num_lines_removed.append(num_removed)
        # print(modified_files)
        # modified_files = check_value_exists(format_array_to_string(modified_files))
        num_lines_added = check_value_exists(format_array_to_string(num_lines_added))
        num_lines_removed = check_value_exists(format_array_to_string(num_lines_removed))

        line = (hash, author_name, author_email, author_date, author_timezone, committer_name, committer_email,
                committer_date, committer_timezone, branches, in_main_branch, merge, modified_files, num_lines_added,
                num_lines_removed, parents, project_name, dmm_unit_size, dmm_unit_complexity, dmm_unit_interfacing)
        commits.append(line)

    df = pd.DataFrame(data=commits, columns=headers)
    df.to_csv(currentProjectCsv, index=False, header=True)


def clone_repo(path_to_save, repositories_list):
    for repo in repositories_list:
        print(repo)
        git.Git(Path(path_to_save).joinpath("repositories")).clone(repo)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output-path", default='./sonar_data', help="Path to output file directory.")
    args = vars(ap.parse_args())
    output_path = args['output_path']
    projects = pd.read_csv(output_path + "/projects_list.csv")
    repositories = projects.gitLink
    clone_repo(path_to_save=output_path, repositories_list=repositories)

    # get_commits()
