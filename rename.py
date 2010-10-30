###############################################################################
#                                                                             #
# Adds rename support to ``parse2plone``.                                     #
#                                                                             #
# This feature allows the user to specify two paths, old and new (e.g.        #
# --rename=old:new ).                                                         #
#                                                                             #
# Then when a path like this is discovered:                                   #
#                                                                             #
#     /2000/01/01/old/index.html                                              #
#                                                                             #
# Instead of creating /2000/01/01/foo/index.html                              #
# (in Plone), parse2plone will create:                                        #
#                                                                             #
#     /2000/01/01/new/index.html                                              #
#                                                                             #
###############################################################################



