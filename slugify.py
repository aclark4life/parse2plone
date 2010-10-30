###############################################################################
#                                                                             #
# Adds "slugify" support to parse2plone, which means that if a path like this #
# is discovered:                                                              #
#                                                                             #
#     /2000/01/01/foo/index.html                                              #
#                                                                             #
# And --slugify is called, then instead of creating /2000/01/01/foo/index.html#
# (in Plone), parse2plone will create:                                        #
#                                                                             #
#     /foo-20000101.html                                                      #
#                                                                             #
# thereby "slugifying" the content, if you will.                              #
#                                                                             #
###############################################################################

from re import compile

slug = compile('(\d\d\d\d)/(\d\d)/(\d\d)/(.+)/index.html')

def path_to_slug(files):
    """
    Returns a slug_ref which is mapping of paths to slugified paths. E.g.
    slug_ref{'/var/www/html/2000/01/01/foo/index.html':
             '/var/www/html/foo-20000101.html'}
    """
    pass
