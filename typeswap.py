
###############################################################################
#                                                                             #
# Adds "typeswap" feature to ``parse2plone``.                                 #
#                                                                             #
# This feature allows the user to specify customize content types for use     #
# when importing content by specifying a "default" content type followed by   #
# its replacement "custom" content type (e.g.                                 #
# --typeswap=Document:MyCustomPageType).                                      #
#                                                                             #
# That means that instead of calling:                                         #
#   parent.invokeFactory('Document','foo')                                    #
#                                                                             #
# ``parse2plone`` will call:                                                  #
#   parent.invokeFactory('MyCustomPageType','foo')                            #
#                                                                             #
###############################################################################

from re import compile
from utils import clean_path

paths = compile('\n(\S+)\s+(\S+)')


def get_types_to_swap(value):
    results = None
    if paths.findall(value):
        results = []
        for group in paths.findall(value):
            results.append('%s:%s' % (clean_path(group[0]),
                clean_path(group[1])))
        results = ','.join(results)
    return results


def swap_types(files, types_map, base, typeswap):
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
