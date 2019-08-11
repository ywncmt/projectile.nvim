import pynvim
from projectile.projectile import Projectile


@pynvim.plugin
class ProjectileHandlers(object):
    def __init__(self, nvim):
        self._nvim = nvim
        self._projectile = Projectile(self._nvim)

    @pynvim.autocmd('BufRead', pattern='*', sync=False)
    def on_bufread(self):
        self._projectile.auto_add_project()
