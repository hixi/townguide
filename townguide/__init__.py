# Usage would be: townguide.bookRenderer
# from plugins.bookRenderer import *

# Usage would be: townguide.bookRenderer.bookRenderer
# Usage would be:
# from plugins import bookRenderer

# Usage would be: townguide.plugins.bookRenderer

# Does not work
# from townguide import plugins

# Usage could be: import townguide; import townguide.plugins...

# Usage is: import townguide; townguide.townguide.townguide(); townguide.plugins.bookRenderer()
# import townguide
# import plugins

# Usage is: import townguide; townguide.townguide(); townguide.plugins.bookRenderer()
from townguide import townguide
import plugins
import defaults
from prefs import prefs

# Maybe someday there should be a way to register a plugin...
# but first things first!

