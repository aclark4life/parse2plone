
###############################################################################
#                                                                             #
#  ``parse2plone`` utils                                                      #
#                                                                             #
###############################################################################


def clean_path(path):
    if path.startswith('/'):
        path = path[1:]
    if path.endswith('/'):
        path = path[0:-1]
    return path
