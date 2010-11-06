
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


def swap_types(typeswap, _CONTENT, logger):
    """
    Update _CONTENT
    """
    for swap in typeswap:
        types = swap.split(':')
        old = types[0]
        new = types[1]
        if old in _CONTENT:
            _CONTENT[old] = new
        else:
            logger.error("Can't swap '%s' with unknown type: '%s'" % (new,
                old))
            exit(1)

    return _CONTENT
