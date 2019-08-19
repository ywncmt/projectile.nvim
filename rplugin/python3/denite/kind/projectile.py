"""Kind using JSON to persist data for projects."""
#  =============================================================================
#  FILE: projectile.py
#  AUTHOR: Clay Dunston <dunstontc@gmail.com>, Ywncmt <ywncmt@gmail.com>
#  License: MIT
#  Last Modified: 2019-08-19
#  =============================================================================

# import snake
import json
import datetime
import re
import os
from os.path import abspath, join, dirname, basename, expanduser, exists
from os.path import isdir, normpath, abspath

from ..kind.directory import Kind as Directory
from denite.util import expand, input, path2project

import platform
import sys
import re

def get_os():
    ''' Get the current OS
    But the real linux and the linux in VMM will be treated as the same. '''
    patt = re.compile(r'(.*win.*)|(.*nt.*)')
    if patt.match(sys.platform):
        if 'darwin' in sys.platform:
            return 'mac'
        return "win"
    elif re.match(r'.*Micro.*', platform.release(), re.IGNORECASE):
        return "wsl"
    elif re.match(r'.*linux.*', sys.platform, re.IGNORECASE):
        return "linux"
    else:
        return "mac"

def IsWin():
    return get_os() == 'win'   

def neopath2project(filepath, roots=['.git', '.projectile'], nearest=True, MAX_DEPTH = 20):
    DEPTH = 0

    folderpath = abspath(dirname(filepath))
    curfolder = folderpath

    FOUND = False

    while DEPTH < MAX_DEPTH:
        FOUND = FOUND or ( 
            any(map(lambda x: exists(join(curfolder, x)), roots))
        )

        if FOUND:
            return curfolder
        else:
            DEPTH += 1
            curfolder = abspath(join(curfolder, '..'))

    return folderpath
    

class Kind(Directory):
    """Kind using JSON to persist data for projects."""

    def __init__(self, vim):
        """Initialize thyself."""
        super().__init__(vim)
        self.name             = 'projectile'
        self.default_action   = 'open'
        self.persist_actions += ['delete']
        self.redraw_actions  += ['delete']
        self.vars = {
            'exclude_filetypes': ['denite'],
            'date_format':       '%d %b %Y %H:%M:%S',
            'data_dir':          vim.vars.get('projectile#data_dir', '~/.cache/projectile'),
            'user_cmd':          vim.vars.get('projectile#directory_command'),
        }

    def action_add(self, context):
        """Add a project to ``projectile#data_dir``/projects.json."""
        data_file = expand(self.vars['data_dir'] + '/projects.json')
        root_dir  = self.vim.call('getcwd')
        boofer    = self.vim.current.buffer.name
        pj_root   = neopath2project(boofer, ['.git', '.svn', '.hg', '.projectile'])
        pj_name   = basename(normpath(pj_root))
        new_data  = {}

        project_root = input(self.vim, context, 'Project Root: ', pj_root)
        if not len(project_root):
            project_root = pj_root

        project_name = input(self.vim, context, 'Project Name: ', pj_name)
        if not len(project_name):
            project_name = pj_name

        new_data = {
            'name':        project_name,
            'root':        project_root,
            'timestamp':   str(datetime.datetime.now().isoformat()),
            'description': '',
            'vcs':         isdir("{}/.git".format(root_dir))  # TODO: Also check for .hg/ and .svn
        }

        with open(data_file, 'r') as g:
            try:
                json_info = json.load(g)
            except json.JSONDecodeError:
                json_info = []
            json_info.append(new_data)

        # learn from another fork: remove old project information   
        projects = json_info[:]
        for i in range(len(projects)):
            if projects[i]['root'] == project_root and projects[i]['name'] == project_name:
                projects.pop(i)
                break

        projects.append(new_data)

        with open(data_file, 'w') as f:
            json.dump(projects, f, indent=4)

    def action_delete(self, context):
        """Remove a project from *projects.json*."""
        target       = context['targets'][0]
        target_date  = target['timestamp']
        target_name  = target['name']
        data_file    = expand(self.vars['data_dir'] + '/projects.json')
        confirmation = self.vim.call('confirm', "Remove {}?".format(target_name), "&Yes\n&No")
        if confirmation == 2:
            return
        else:
            with open(data_file, 'r') as g:
                content  = json.load(g)
                projects = content[:]
                for i in range(len(projects)):
                    if projects[i]['timestamp'] == target_date:
                        projects.pop(i)
                        break

                with open(data_file, 'w') as f:
                    json.dump(projects, f, indent=2)


    def action_custom(self, context):
        """Execute a custom action defined by ``g:projectile#directory_command``."""
        target   = context['targets'][0]
        user_cmd = self.vim.vars.get('projectile#directory_command')
        if not isdir(target['action__path']):
            return
        destination = expand(target['action__path'])
        self.vim.call('execute', '{} {}'.format(user_cmd, destination))


    def action_open(self, context):
        '''
            Activate FZF when open.
        '''
        target = context['targets'][0]
        if not isdir(target['action__path']):
            return
        self.vim.command('cd {}'.format(target['action__path']))
        self.vim.command('lcd {}'.format(target['action__path']))
        self.vim.command('FZF')
        
    def action_jumptags(self, context):
        '''
            Activate Leaderf Tags when open, not work.
        '''
        target = context['targets'][0]
        if not isdir(target['action__path']):
            return
        self.vim.command('cd {}'.format(target['action__path']))  
        self.vim.command('lcd {}'.format(target['action__path']))  
        self.vim.command('Denite tag -path={folder}'.format(folder=target['action__path']))     

    def action_term(self, context):
        '''
            Not work   
        '''
        target = context['targets'][0]
        if not isdir(target['action__path']):
            return
        self.vim.command('cd {}'.format(target['action__path']))  
        self.vim.command('lcd {}'.format(target['action__path']))  
        self.vim.command('terminal {term}'.format(term='powershell' if IsWin() else 'zsh'))        

    def action_rg(self, context):
        '''
            Use Rg to search the whole project, depends on `fzf.vim`.
        '''
        target = context['targets'][0]
        if not isdir(target['action__path']):
            return
        self.vim.command('cd {}'.format(target['action__path']))  
        self.vim.command('lcd {}'.format(target['action__path']))  
        self.vim.command('Ag')        


