#from lib.network import object_sharer # YS: try to get rid of 32bit gobject from pygtk
from qkit.core.lib import temp, lockfile

qt.flow.register_exit_handler(qt.config._do_save)
qt.flow.register_exit_handler(qt.flow.close_gui)
#qt.flow.register_exit_handler(object_sharer.helper.close_sockets) # YS: try to get rid of 32bit gobject from pygtk
qt.flow.register_exit_handler(temp.File.remove_all)
qt.flow.register_exit_handler(lockfile.remove_lockfile)

# Clear "starting" status
qt.flow.finished_starting()
