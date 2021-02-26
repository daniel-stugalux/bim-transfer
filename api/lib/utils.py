import re

from lib.autodeskConnector import get_folder_info, upload_file, update_file_version, is_file_already_in_folder, \
    create_folder_in_bim_360, get_subfolder_id


def is_folder_known(folder_id, known_paths):
    for i in known_paths:
        element = next((item for item in i if item["id"] == folder_id), None)
        if element:
            return element, i
    return False, None


def get_path_to_item(token, project_id, folder_id, known_paths=None):
    path = []
    if known_paths is None:
        known_paths = []
    parent_folder_id = folder_id
    # Check if we already know the parent folder
    known_element, known_path = is_folder_known(folder_id, known_paths)
    while parent_folder_id and not known_element:
        response, folder_info = get_folder_info(token, project_id, parent_folder_id)
        if response != 200:
            return response, folder_info
        parent_folder_id = folder_info['parent_id']
        # Check if we already know the parent folder
        known_element, known_path = is_folder_known(parent_folder_id, known_paths)
        path = [folder_info] + path
    # In case we found a known folder
    if parent_folder_id is not None:
        path = known_path[:known_path.index(known_element) + 1] + path
    return 200, path


def extract_variables_from_link(url):
    try:
        search = re.search('^https://docs.b360.autodesk.com/projects/([^/]+)/folders/([^/]+)/documents/([^/]+)', url)
        return (200, (search.group(1), search.group(2), search.group(3))) if search else (405, "Bad URL input.")
    except (IndexError, AttributeError):
        return 405, "Bad URL input."


def get_mirror_folder_id_in_plans(token, project_id, path_to_file):
    """
    Gets the folder's ID in the Plans subfolders. The path is mirrored from the one
    on the Project files side. If we get the file from "01 WIP", we publish it on
    "02 SHARED".
    """
    project_files = path_to_file[2]
    # Get plans folder id
    response, parent_folder_id = get_subfolder_id(token, project_id, project_files['parent_id'], "Plans")
    if response != 200:
        return response, parent_folder_id
    for folder in path_to_file[3:]:
        # We want to post files in shared folder, not wip
        if folder['name'] == '01 WIP':
            name = '02 SHARED'
        else:
            name = folder['name']
        # Get folder f it exist
        response, next_parent_folder_id = get_subfolder_id(token, project_id, parent_folder_id, name)
        # Create folder if it does not exist yet
        if response == 404:
            response_create, plans_side_folder = create_folder_in_bim_360(token, project_id, parent_folder_id, name)
            if response_create != 200:
                return response_create, plans_side_folder
            parent_folder_id = plans_side_folder['data']['id']
        elif response == 200:
            parent_folder_id = next_parent_folder_id
        else:
            return response, next_parent_folder_id
    return 200, parent_folder_id


def upload_or_update_to_mirror_folder(access_token, project_id, path_to_file, item_name, filepath, filename):
    response, target_folder_id = get_mirror_folder_id_in_plans(access_token, project_id, path_to_file)
    if response != 200:
        return response, target_folder_id
    print("\n" + filename + " is being uploaded to " + target_folder_id + "\n")

    response, target_item_id = is_file_already_in_folder(access_token, project_id, target_folder_id, item_name)
    if response == 200:
        # Update version
        return update_file_version(access_token, project_id, target_folder_id, filepath + filename, item_name,
                                   target_item_id)
    elif response == 404:
        # Upload version
        return upload_file(access_token, project_id, target_folder_id, filepath + filename, item_name)
    else:
        return response, target_item_id
