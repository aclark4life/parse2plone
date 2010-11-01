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


def get_paths_to_rename():
    return '/foo/bar:/foo/baz'

def rename_old_to_new():
    pass
