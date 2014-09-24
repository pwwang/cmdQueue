
import os, imp, re



class cqPlugin:
    
    def __init__(self):
        self.dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'plugins'
        )
        self.plugins = []
        ps = self.get()

        for p in ps:
            plugin = imp.load_module('cqp-%s-%s' % (p[1], p[0]), *p[2])
            self.plugins.append(plugin)

    def get(self):
        plugins = []
        pps = os.listdir(self.dir) # possible plugins

        pfn0 = re.compile(r"^cqp-(?P<name>.+)\.py$")

        pfn = re.compile(r"^cqp-(?P<name>.+)-(?P<priority>\d+)\.py$")
        for fn in pps:
            
            m = pfn.match(fn)

            if m:
                name = m.group('name')
                priority = int(m.group('priority'))
            else:
                m = pfn0.match(fn)
                if m:
                    name = m.group('name')
                    priority = 0
                else:
                    continue

            info = imp.find_module('cqp-%s-%s' % (name, priority), [self.dir])

            plugins.append([priority, name, info])
            plugins = sorted(plugins, key=lambda plugins: plugins[0])
        return plugins

    def __getattr__(self, name, *args):
        def nomethod():
            pass
        def call(*args):
            for plugin in self.plugins:
                func = getattr(plugin, name, nomethod)
                func(*args)

        return call

