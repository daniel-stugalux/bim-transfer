#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from zipfile import is_zipfile, ZipFile

import connexion
import configparser
import os
from flask_cors import CORS

from lib.autodeskConnector import create_relationship, search_parent_folder_id_by_name, get_item_display_name, \
    get_2_legged_authentification_token, download_file
from lib.utils import upload_or_update_to_mirror_folder, get_path_to_item, extract_variables_from_link

path = os.path.dirname(os.path.abspath(__file__))
config = configparser.ConfigParser()
config.read(path + '''/config/configuration.cfg''')


def transfer(data):
    """
    Function transfering files in BIM 360 from the 'project files WIP' directory to the 'plans Shared' directory.
      
    :param data: Object containing 'access_token', a 3-legged access token and 'model_url', the model's URL.
    :return: A status code, and a message.
    """

    access_token = data.get('access_token', None)
    model_url = data.get('model_url', None)
    if not access_token or not model_url:
        return 400, 'Bad Request'
    known_paths = []
    filepath = os.getcwd() + '/data/'
    filename = 'model_data'

    # Get 2-legged authentification token
    access_token_2_legged, cookies = get_2_legged_authentification_token(config['FORGE']['client_id'],
                                                                         config['FORGE']['client_secret'])

    # Extract variables from the model's URL
    project_id, folder_id, item_id = extract_variables_from_link(model_url)

    # Download file
    download_file(access_token_2_legged, project_id, item_id, filepath + filename)

    # Getting the path to the item...
    path_to_file = get_path_to_item(access_token_2_legged, project_id, folder_id)

    # Saving item(s) and related paths...
    display_name = get_item_display_name(access_token_2_legged, project_id, item_id)
    known_paths.append(path_to_file)
    files_to_upload = {display_name: 0}

    # Get WIP folder id
    wip_folder_id = path_to_file[4]['id']

    if is_zipfile(filepath + filename):
        with ZipFile(filepath + filename) as my_file:
            files = my_file.namelist()
            my_file.extractall(filepath)
        for i in files:
            if i not in files_to_upload:
                # search item's parent folder to known the upload path
                parent_folder_id = search_parent_folder_id_by_name(access_token, project_id, wip_folder_id, i)
                # Get the path to the file
                path_to_file = get_path_to_item(access_token_2_legged, project_id, parent_folder_id, known_paths)
                known_paths.append(path_to_file)
                files_to_upload[i] = len(known_paths) - 1
        # Upload files to mirror directories
        uploaded_version_ids_set = set()
        uploaded_ids = {}
        for name, index in files_to_upload.items():
            item_id, version_id = upload_or_update_to_mirror_folder(access_token_2_legged, project_id,
                                                                    known_paths[index], name, filepath, name)
            uploaded_version_ids_set = uploaded_version_ids_set.union({version_id})
            uploaded_ids[name] = {'version': version_id, 'item': item_id}

        # Create links between all the files
        for name, ids in uploaded_ids.items():
            versions_to_link = list(uploaded_version_ids_set.difference({ids['version']}))
            create_relationship(access_token_2_legged, project_id, ids['version'], versions_to_link)
    else:
        # upload unique file
        os.rename(filepath + filename, filepath + display_name)
        upload_or_update_to_mirror_folder(access_token_2_legged, project_id, path_to_file, display_name, filepath,
                                          display_name)


app = connexion.App(__name__, specification_dir='./specification/')
app.add_api('specification.yaml')

if __name__ == "__main__":
    application = app.app
    CORS(app.app)
    # noinspection PyTypeChecker
    app.run(port=config['API']['port'])
