###############################################################################
#                                                                             #
# Adds rename support to ``parse2plone``.                                     #
#                                                                             #
# This feature allows the user to specify two paths: old and new (e.g.        #
# --rename=old:new ).                                                         #
#                                                                             #
# Then if a path like this is found:                                          #
#                                                                             #
#     /old/2000/01/01/foo/index.html                                          #
#                                                                             #
# Instead of creating /old/2000/01/01/foo/index.html (in Plone),              #
# ``parse2plone`` will create:                                                #
#                                                                             #
#     /new/2000/01/01/foo/index.html                                          #
#                                                                             #
###############################################################################

from re import compile
from utils import clean_path

paths = compile('\n(\S+)\s+(\S+)')


def get_paths_to_rename(value):
    results = None
    if paths.findall(value):
        results = []
        for group in paths.findall(value):
            results.append('%s:%s' % (clean_path(group[0]),
                clean_path(group[1])))
        results = ','.join(results)
    return results


def rename_old_to_new(files, rename_map, base, rename):
    """
    Returns a rename_map which is forward/reverse mapping of old paths to
    new paths and vice versa. E.g.:

        rename_map{'forward': {'/var/www/html/old/2000/01/01/foo/index.html':
            '/var/www/html/new/2000/01/01/foo/index.html'}}

        rename_map{'reverse': {'/var/www/html/new/2000/01/01/foo/index.html':
            '/var/www/html/old/2000/01/01/foo/index.html'}}
    """
    for f in files[base]:
        for path in rename:
            parts = path.split(':')
            old = parts[0]
            new = parts[1]
            if f.find(old) >= 0:
                rename_map['forward'][f] = f.replace(old, new)
            rename_map['reverse'][f.replace(old, new)] = f
    return rename_map
