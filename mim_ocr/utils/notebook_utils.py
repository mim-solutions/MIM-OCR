import os
import requests
import ipykernel
import re
from notebook.notebookapp import list_running_servers
from pathlib import Path


def get_current_notebook_path() -> Path:
    """
    Code was copied (and slightly modified) from: https://github.com/jupyterhub/jupyterhub/issues/1718
    Popular (and much simplier_ solutions (from StackOverflow or github) fail when:
      * code was moved to python libs (from notebooks) e.g. solutions based on "__file__",
      * notebook cells were run without break (changing kernel status to idle) e.g. solutions based on javascript.
    This solution is a hack and can stop working on newer versions of used libraries.
    This solution works only on jupyter with token based authorization (e.g. in jupyterhub).

    It also does not work when running jupyter notebooks from command line e.g. via jupyter nbconvert.
    TODO detect running from command line (unfortunatelly it sounds as difficult as writing this function
    all SO answers does not support all cases):
    https://stackoverflow.com/questions/15411967/how-can-i-check-if-code-is-executed-in-the-ipython-notebook
    """

    # proper way of getting token in jupyterhub
    TOKEN = os.environ.get('JUPYTERHUB_API_TOKEN', '')

    # proper way of getting token in (single user) jupyter notebooks with token authorization
    running_server_props = next(list_running_servers())
    if not TOKEN:
        TOKEN = running_server_props['token']
    if not TOKEN:
        raise NotImplementedError('Jupyter token not found. Getting current notebook path is not supported '
                                  'for jupyter instances without token authorization')

    base_url = running_server_props['url']
    r = requests.get(
        url=base_url + 'api/sessions',
        headers={'Authorization': 'token {}'.format(TOKEN)})

    r.raise_for_status()
    response = r.json()

    kernel_id = re.search('kernel-(.*).json', ipykernel.connect.get_connection_file()).group(1)
    notebook_path = {r['kernel']['id']: r['notebook']['path'] for r in response}[kernel_id]

    return Path(notebook_path)


def get_directory_for_notebook_images(initial_cwd: Path, makedirs: bool = True) -> Path:
    """
       Get directory path for storing images from current jupyter notebook.
       Args:
           makedirs (bool): if true directory will be created
    """
    dirname = get_current_notebook_path().name + ".images"
    dirpath = Path(initial_cwd) / dirname
    if makedirs:
        os.makedirs(dirpath, exist_ok=True)
    return dirpath
