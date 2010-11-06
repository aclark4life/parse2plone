
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

