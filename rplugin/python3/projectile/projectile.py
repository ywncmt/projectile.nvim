import json
import datetime
from os.path import basename, isdir, normpath
from denite.util import expand, path2project


class Projectile(object):
    def __init__(self, nvim):
        self._nvim = nvim
        self._data_dir = self._nvim.eval('g:projectile#data_dir')

    def auto_add_project(self):
        data_file = expand(self._data_dir + '/projects.json')
        boofer = self._nvim.current.buffer.name
        pj_root = path2project(self._nvim, boofer, '.git,.hg,.svn')

        is_pj = (isdir("{}/.git".format(pj_root))
                 or isdir("{}/.hg".format(pj_root))
                 or isdir("{}/.svn".format(pj_root)))
        if is_pj:
            is_new_pj = True
            with open(data_file, 'r') as g:
                try:
                    json_info = json.load(g)
                except json.JSONDecodeError:
                    json_info = []

                projects = json_info[:]
                for i in range(len(projects)):
                    if projects[i]['root'] == pj_root:
                        is_new_pj = False
                        break

            if is_new_pj:
                pj_name = basename(normpath(pj_root))
                new_data = {
                    'name': pj_name,
                    'root': pj_root,
                    'timestamp': str(datetime.datetime.now().isoformat()),
                    'description': '',
                    'vcs': is_pj
                }

                projects.append(new_data)
                with open(data_file, 'w') as f:
                    json.dump(projects, f, indent=2)
