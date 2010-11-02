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


def get_paths_to_rename(value):
    results = []
    for group in paths.findall(value):
        results.append('%s:%s' % (group[0], group[1]))
    return ','.join(results)


def rename_old_to_new(files, slug_ref, base):
    """
    Returns a rename_ref which is forward/reverse mapping of old paths to
    new paths and vice versa. E.g.:

        rename_ref{'forward': {'/var/www/html/old/2000/01/01/foo/index.html':
            '/var/www/html/new/2000/01/01/foo/index.html'}}

        rename_ref{'reverse': {'/var/www/html/new/2000/01/01/foo/index.html':
            '/var/www/html/old/2000/01/01/foo/index.html'}}
    """

    for f in files[base]:
        result = slug.match(f)
        if result:
            groups = result.groups()
            slug_ref['forward'][f] = '%s%s-%s%s%s.html' % (groups[0],
                groups[4], groups[1], groups[2], groups[3])
            slug_ref['reverse']['%s%s-%s%s%s.html' % (groups[0], groups[4],
                groups[1], groups[2], groups[3])] = f

    return slug_ref
