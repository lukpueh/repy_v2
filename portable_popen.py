# Split out Popen into its own library to reduce circular imports with
# nonportable.

# This may fail on Windows CE
try:
  import subprocess
  mobile_no_subprocess = False
except ImportError:
  # Set flag to avoid using subprocess
  mobile_no_subprocess = True 

# Detect windows.
import os

def Popen(args):
  # Defined in Winbase.h, CREATE_NO_WINDOW is a CreationFlag meaning "don't
  # create a console window for the started process." For more info, see:
  #   http://msdn.microsoft.com/en-us/library/ms684863%28VS.85%29.aspx
  CREATE_NO_WINDOW = 0x08000000

  if mobile_no_subprocess:
    raise Exception("No subprocess available on this platform!")

  # On android we use a custom 
  # fork-and-run C-Python extension,
  # because we don't have a Python binary 
  try: 
    import android

    # Other commands (ps, wc, ifconfig, ...) don't use this extension
    if len(args) >= 2 and "python" in str(args[0]):
      # Todo: Add args
      return android.run(args[1])
  except Exception, e:
    pass      

  if os.name == 'nt':
    # Windows
    return subprocess.Popen(args, creationflags=CREATE_NO_WINDOW,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  else:
    # Everything else
    return subprocess.Popen(args, close_fds=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
