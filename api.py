"""Nitro api
Usage:
    api.py add <img-file>
    api.py checkout <img-uuid> <out_file>
    api.py show <img-uuid>
    api.py delete <img-uuid>
    api.py network
    api.py info
    api.py reset
    api.py (-h | --help)
    api.py --version

Arguments:
    <img-file> image file
    <img-uuid> image UUID

Options:
    -h, --help         Show this screen.
    -v, --version      Print the version.
"""

import sys

from docopt import docopt
import requests


class BackendStorageWSClient(object):

    def __init__(self, endpoint):
        self.session = requests.Session()
        self.endpoint = endpoint

    def _issue_get_request(self, path, req_params=None):
        req = self.session.get("http://" + self.endpoint + '/' + path, params=req_params)
        return req.status_code == 200, req.text

    def add_image(self, image_file, image_metadata):
        return self._issue_get_request('add', {'path': image_file})
    def checkout_image(self, image_uuid, out_file):
        return self._issue_get_request('checkout', {'uuid': image_uuid, 'path': out_file})
    def is_image_available_locally(self, image_uuid):
        return self._issue_get_request('is_available', {'uuid': image_uuid})
    def delete_image(self, image_uuid):
        return self._issue_get_request('del', {'uuid': image_uuid})
    def network(self):
        return self._issue_get_request('network')
    def info(self):
        return self._issue_get_request('info')
    def reset(self):
        return self._issue_get_request('reset')


def run():

    arguments = docopt(__doc__, version='0.1.0')

    config_file = "/etc/nitro/nitro.yaml"
    from global_configuration import NitroConfiguration
    cfg = NitroConfiguration(config_file)
    #ws_address_connect
    storage_ws = BackendStorageWSClient(cfg.get_nitro_endpoint()) 

    if arguments["add"]:
        img_file = arguments["<img-file>"]
        ok, uuid = storage_ws.add_image(img_file, [])
        if ok:
            print '###', uuid.strip()
        else:
            print >> sys.stderr, uuid
            return 1

    if arguments["checkout"]:
        img_uuid = arguments["<img-uuid>"]
        out_file = arguments["<out_file>"]
        ok, err_msg = storage_ws.checkout_image(img_uuid, out_file)
        if ok:
            print 'Image checkout done.'
        else:
            print >> sys.stderr, err_msg
            return 1

    if arguments["network"]:
        ok, info = storage_ws.network()
        print info

    if arguments["info"]:
        ok, info = storage_ws.info()
        print info

    if arguments["reset"]:
        ok, info = storage_ws.reset()
        print info

    return 0


if __name__ == "__main__":
    sys.exit(run())
