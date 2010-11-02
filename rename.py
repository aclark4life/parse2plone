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

paths = compile('\n(\S+)\s+(\S+)')

# XXX Factor me out of both parse2plone and rename modules
def clean_path(path):
    if path.startswith('/'):
        return path[1:]

def get_paths_to_rename(value):
    results = []
    for group in paths.findall(value):
        results.append('%s:%s' % (clean_path(group[0]), clean_path(group[1])))
    return ','.join(results)

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
        import pdb; pdb.set_trace()
#        if result:
#            groups = result.groups()
#            slug_ref['forward'][f] = '%s%s-%s%s%s.html' % (groups[0],
#                groups[4], groups[1], groups[2], groups[3])
#            slug_ref['reverse']['%s%s-%s%s%s.html' % (groups[0], groups[4],
#                groups[1], groups[2], groups[3])] = f
#
#    return slug_ref
