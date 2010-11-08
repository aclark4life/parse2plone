###############################################################################
#                                                                             #
#  Adds match feature to ``parse2plone``.                                     #
#                                                                             #
#  The user may specify a string to match file names against; only content    #
#  from files that match the string will be imported. E.g.                    #
#                                                                             #
#      $ bin/plone run bin/import /var/www/html --match=2000                  #
#                                                                             #
#  Will import:                                                               #
#                                                                             #
#      /var/www/html/2000/01/01/foo/index.html                                #
#                                                                             #
#  But not:                                                                   #
#                                                                             #
#      /var/www/html/2001/01/01/foo/index.html                                #
#                                                                             #
###############################################################################


def match_files(files):
    return files

