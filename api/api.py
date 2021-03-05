#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from time import time
from zipfile import is_zipfile, ZipFile

import connexion
import configparser
import os
from flask_cors import CORS

from lib.autodeskConnector import create_relationship, search_parent_folder_id_by_name, get_item_display_name, \
    get_2_legged_authentification_token, download_file
from lib.utils import upload_or_update_to_mirror_folder, get_path_to_item, extract_variables_from_link, \
    beautify_folders_string

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
        return 'Bad Request.', 400
    known_paths = []
    start_time = str(int(time() * 1000))
    filepath = os.getcwd() + '/data/' + start_time + '/'
    filename = 'model_data'

    # create a folder ro store the data
    try:
        os.mkdir(filepath)
    except OSError:
        return "Folder creation on the server failed", 514

    # Get 2-legged authentification token
    response, access_token_2_legged = get_2_legged_authentification_token(config['FORGE']['client_id'],
                                                                          config['FORGE']['client_secret'])
    if response != 200:
        return access_token_2_legged, response

    # Extract variables from the model's URL
    response, response_data = extract_variables_from_link(model_url)
    if response != 200:
        return response_data, response
    else:
        project_id = response_data[0]
        folder_id = response_data[1]
        item_id = response_data[2]

    # Download file
    response, message = download_file(access_token_2_legged, project_id, item_id, filepath + filename)
    if response != 200:
        return message, response

    # Getting the path to the item...
    response, path_to_file = get_path_to_item(access_token_2_legged, project_id, folder_id)
    if response != 200:
        return path_to_file, response

    # Saving item(s) and related paths...
    response, display_name = get_item_display_name(access_token_2_legged, project_id, item_id)
    if response != 200:
        return display_name, response

    known_paths.append(path_to_file)
    files_to_upload = {display_name: 0}

    # Get WIP folder id
    wip_folder_id = path_to_file[4]['id']

    success_message = []
    is_model_linked = is_zipfile(filepath + filename)

    if is_model_linked:
        with ZipFile(filepath + filename) as my_file:
            files = my_file.namelist()
            my_file.extractall(filepath)
        for i in files:
            if i not in files_to_upload:
                # search item's parent folder to known the upload path
                response, parent_folder_id = search_parent_folder_id_by_name(access_token, project_id, wip_folder_id, i)
                if response != 200:
                    return parent_folder_id, response
                # Get the path to the file
                response, path_to_file = get_path_to_item(access_token_2_legged, project_id, parent_folder_id,
                                                          known_paths)
                if response != 200:
                    return path_to_file, response
                known_paths.append(path_to_file)
                files_to_upload[i] = len(known_paths) - 1
        # Upload files to mirror directories
        uploaded_version_ids_set = set()
        uploaded_ids = {}
        for name, index in files_to_upload.items():
            response, response_data = upload_or_update_to_mirror_folder(access_token_2_legged, project_id,
                                                                        known_paths[index], name, filepath, name)
            if response != 200:
                return response_data, response
            else:
                item_id = response_data[0]
                version_id = response_data[1]
            uploaded_version_ids_set = uploaded_version_ids_set.union({version_id})
            uploaded_ids[name] = {'version': version_id, 'item': item_id}
            # complete success message
            response, folders_string = beautify_folders_string(known_paths[index])
            if response != 200:
                return folders_string, response
            success_message.append(name + ' was uploaded to ' + folders_string + '.')

        # Create links between all the files
        for name, ids in uploaded_ids.items():
            versions_to_link = list(uploaded_version_ids_set.difference({ids['version']}))
            response, message = create_relationship(access_token_2_legged, project_id, ids['version'], versions_to_link)
            if response != 200:
                return message, response
    else:
        # upload unique file
        os.rename(filepath + filename, filepath + display_name)
        response, response_data = upload_or_update_to_mirror_folder(access_token_2_legged, project_id, path_to_file,
                                                                    display_name, filepath, display_name)
        # complete success message
        response, folders_string = beautify_folders_string(path_to_file)
        if response != 200:
            return folders_string, response
        success_message = ['WARNING : File was uploaded with no links.', display_name + ' was uploaded to '
                           + folders_string + '.']
        if response != 200:
            return response_data, response
    return success_message, 200 if is_model_linked else 201


app = connexion.App(__name__, specification_dir='./specification/')
app.add_api('specification.yaml')

if __name__ == "__main__":
    application = app.app
    CORS(app.app)
    # noinspection PyTypeChecker
    app.run(port=config['API']['port'])
