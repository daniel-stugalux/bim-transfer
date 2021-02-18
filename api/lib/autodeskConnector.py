import json
import re
import requests
from pprint import pprint


def extract_object_id(response_string):
    search = re.search('^[^/]+/(.+)$', response_string)
    return search.group(1)


def get_2_legged_authentification_token(forge_client_id, forge_client_secret):
    url = "https://developer.api.autodesk.com/authentication/v1/authenticate"

    payload = 'client_id=' + forge_client_id + '&client_secret=' + forge_client_secret \
              + '&grant_type=client_credentials&scope=data%3Aread%20data%3Acreate%20data%3Awrite%20account%3Aread'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json()["access_token"], response.cookies.get_dict()


def get_folder_info(token, project_id, folder_id):
    url = 'https://developer.api.autodesk.com/data/v1/projects/b.' + \
          project_id + '/folders/' + folder_id

    headers = {
        'Authorization': 'Bearer ' + token,
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        pprint("\nError in get item info\n")
        pprint(response.json())
        return None
    else:
        return {
            'id': response.json()['data']['id'],
            'name': response.json()['data']['attributes']['displayName'],
            'parent_id': response.json()['data']['relationships'].get('parent', {}).get('data', {}).get('id', None)
        }


def get_item_storage_location(token, project_id, item_id):
    url = "https://developer.api.autodesk.com/data/v1/projects/b." + \
          project_id + "/items/" + item_id

    headers = {
        'Authorization': 'Bearer ' + token
    }

    response = requests.request("GET", url, headers=headers)
    return response.json()['included'][0]['relationships']['storage']['meta']['link']['href']


def download_file(token, project_id, item_id, path_to_storage_folder):
    url = get_item_storage_location(token, project_id, item_id)

    headers = {
        'Authorization': 'Bearer ' + token
    }

    response = requests.request("GET", url, headers=headers)
    if response.status_code == 200:
        open(path_to_storage_folder, 'wb').write(response.content)
        print("Download done\n")
    else:
        print("Download failed\n")


def get_item_display_name(token, project_id, item_id):
    url = "https://developer.api.autodesk.com/data/v1/projects/b." + \
          project_id + "/items/" + item_id + '/versions'

    headers = {
        'Authorization': 'Bearer ' + token
    }

    response = requests.request("GET", url, headers=headers)
    return response.json()['data'][0]['attributes']['displayName']


def search_parent_folder_id_by_name(token, project_id, root_folder_id, item_name):
    url = "https://developer.api.autodesk.com/data/v1/projects/b." + \
          project_id + "/folders/" + root_folder_id + '/search'

    headers = {
        'Authorization': 'Bearer ' + token
    }
    parameters = {
        'filter[attributes.displayName]': item_name
    }

    response = requests.request("GET", url, headers=headers, params=parameters)
    return response.json()['included'][0]['relationships']['parent']['data']['id']


def get_subfolder_id(token, project_id, folder_id, subfolder_name):
    url = 'https://developer.api.autodesk.com/data/v1/projects/b.' + \
          project_id + '/folders/' + folder_id + '/contents'

    headers = {
        'Authorization': 'Bearer ' + token,
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        for i in response.json()['data']:
            if i['attributes']['displayName'] == subfolder_name:
                return i['id']
    return None


def create_folder_in_bim_360(token, project_id, parent_folder_id, name):
    print("\n" + parent_folder_id + "\n")
    url = "https://developer.api.autodesk.com/data/v1/projects/b." + project_id + "/folders"
    payload = {
        "jsonapi": {
            "version": "1.0"
        },
        "data": {
            "type": "folders",
            "attributes": {
                "name": name,
                "extension": {
                    "type": "folders:autodesk.bim360:Folder",
                    "version": "1.0"
                }
            },
            "relationships": {
                "parent": {
                    "data": {
                        "type": "folders",
                        "id": parent_folder_id
                    }
                }
            }
        }
    }
    headers = {
        'Content-Type': 'application/vnd.api+json',
        'Authorization': 'Bearer ' + token
    }

    response = requests.request(
        "POST", url, headers=headers, data=json.dumps(payload))
    return response.json()


def is_file_already_in_folder(token, project_id, folder_id, filename):
    url = 'https://developer.api.autodesk.com/data/v1/projects/b.' + \
          project_id + '/folders/' + folder_id + '/contents'

    headers = {
        'Authorization': 'Bearer ' + token,
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        for i in response.json()['data']:
            if i['attributes']['displayName'] == filename:
                return i['id']
    return None


def prepare_file_storage(token, project_id, traget_folder_id, filepath, filename):
    url = 'https://developer.api.autodesk.com/data/v1/projects/b.' + project_id + '/storage'
    headers = {
        'Authorization': 'Bearer ' + token,
    }

    data = {
        "jsonapi": {
            "version": "1.0"
        },
        "data": {
            "type": "objects",
            "attributes": {
                "name": filename
            },
            "relationships": {
                "target": {
                    "data": {
                        "type": "folders",
                        "id": traget_folder_id
                    }
                }
            }
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 201:
        object_id_raw = response.json()['data']['id']
        object_id = extract_object_id(object_id_raw)
    else:
        pprint(response.json())
        print("\nResponse status code : " + str(response.status_code) + '\n')
        return None

    url = 'https://developer.api.autodesk.com/oss/v2/buckets/wip.dm.prod/objects/' + object_id
    data = open(filepath, 'rb').read()

    response = requests.put(url, headers=headers, data=data)
    if response.status_code != 200:
        pprint(response.json())
        return None
    object_id_raw = response.json()['objectId']
    return object_id, object_id_raw


def upload_file(token, project_id, target_folder_id, filepath, filename):
    _, object_id_raw = prepare_file_storage(token, project_id, target_folder_id, filepath, filename)

    url = 'https://developer.api.autodesk.com/data/v1/projects/b.' + project_id + '/items'
    headers = {
        'Authorization': 'Bearer ' + token,
        'Content-Type': 'application/vnd.api+json'
    }

    data = {
        "jsonapi": {
            "version": "1.0"
        },
        "data": {
            "type": "items",
            "attributes": {
                "displayName": filename,
                "extension": {
                    "type": "items:autodesk.bim360:File",
                    "version": "1.0"
                }
            },
            "relationships": {
                "tip": {
                    "data": {
                        "type": "versions",
                        "id": "1"
                    }
                },
                "parent": {
                    "data": {
                        "type": "folders",
                        "id": target_folder_id
                    }
                }
            }
        },
        "included": [
            {
                "type": "versions",
                "id": "1",
                "attributes": {
                    "name": filename,
                    "extension": {
                        "type": "versions:autodesk.bim360:File",
                        "version": "1.0"
                    }
                },
                "relationships": {
                    "storage": {
                        "data": {
                            "type": "objects",
                            "id": object_id_raw
                        }
                    }
                }
            }
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code != 201:
        pprint(response.json())
        return None
    else:
        item_id = response.json()['data']['id']
        try:
            version_id = response.json()['included']['id']
        except TypeError:
            version_id = response.json()['included'][0]['id']
        return item_id, version_id


def update_file_version(token, project_id, target_folder_id, filepath, filename, item_id):
    _, object_id_raw = prepare_file_storage(token, project_id, target_folder_id, filepath, filename)

    url = 'https://developer.api.autodesk.com/data/v1/projects/b.' + project_id + '/versions'

    headers = {
        'Authorization': 'Bearer ' + token,
    }

    data = {
        "jsonapi": {
            "version": "1.0"
        },
        "data": {
            "type": "versions",
            "attributes": {
                "name": filename,
                "extension": {
                    "type": "versions:autodesk.bim360:File",
                    "version": "1.0"
                }
            },
            "relationships": {
                "item": {
                    "data": {
                        "type": "items",
                        "id": item_id
                    }
                },
                "storage": {
                    "data": {
                        "type": "objects",
                        "id": object_id_raw
                    }
                }
            }
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))
    return item_id, response.json()['data']['id']


def create_relationship(token, project_id, version_id, linked_versions):
    url = "https://developer.api.autodesk.com/data/v1/projects/b." + project_id + "/versions"

    headers = {
        'Authorization': 'Bearer ' + token,
    }
    parameters = {
        'copyFrom': version_id
    }
    data = {
        "jsonapi": {
            "version": "1.0"
        },
        "data": {
            "type": "versions",
            "relationships": {
                "refs": {
                    "data": []
                }
            }
        }
    }
    for i in linked_versions:
        # noinspection PyTypeChecker
        data["data"]["relationships"]["refs"]["data"].append({
            "type": "versions",
            "id": i,
            "meta": {
                "refType": "xrefs",
                "direction": "from",
                "extension": {
                    "type": "xrefs:autodesk.core:Xref",
                    "version": "1.1",
                    "data": {
                        "nestedType": "overlay"
                    }
                }
            }
        })

    response = requests.post(url, headers=headers, params=parameters, data=json.dumps(data))
    if response.status_code != 201:
        pprint(response.json())
        return None
    else:
        return 201
