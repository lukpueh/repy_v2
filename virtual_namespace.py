"""
<Author>
  Armon Dadgar

<Start Date>
  October 21st, 2009

<Description>
  This module provides the VirtualNamespace object. This object allows
  arbitrary code to be checked for safety, and evaluated within a
  specified global context.
"""

# encoding_header contains a multi-line ENCODING_DECLARATION that is to be
# prepended to user code loaded into an instantiated VirtualNamespace.
# It has the effect of treating user code as having UTF-8 encoding, preventing
# certain bugs. As a side effect, prepending this header to code also results
# in traceback line numbers being off. To remedy this, we import the code
# header in several modules so as to subtract the number of lines it contains
# from such line counts. We place it in its own file so that it can be imported
# by multiple files with interdependencies, to avoid import loops.
# For more info, see SeattleTestbed/repy_v2#95 and #96.
import encoding_header

# Used for safety checking
import safe

# Get the errors
from exception_hierarchy import *

# This is to work around safe...
safe_compile = compile

# Functional constructor for VirtualNamespace
def createvirtualnamespace(code, name):
  return VirtualNamespace(code,name)

# This class is used to represent a namespace
class VirtualNamespace(object):
  """
  The VirtualNamespace class is used as a wrapper around an arbitrary
  code string that has been verified for safety. The namespace provides
  a method of evaluating the code with an arbitrary global context.
  """

  # Constructor
  def __init__(self, code, name):
    """
    <Purpose>
      Initializes the VirtualNamespace class.

    <Arguments>
      
      code:
          (String) The code to run in the namespace

      name:
          (String, optional) The name to use for the code. When the module is
          being executed, if there is an exception, this name will appear in
          the traceback.

    <Exceptions>
      A safety check is performed on the code, and a CodeUnsafeError exception will be raised
      if the code fails the safety check. 

      If code or name are not string types, a RepyArgumentError exception will be raised.
    """
    # Check for the code
    # Do a type check
    if type(code) is not str:
      raise RepyArgumentError, "Code must be a string!"

    if type(name) is not str:
      raise RepyArgumentError, "Name must be a string!"

    # Remove any windows carriage returns
    code = code.replace('\r\n','\n')

    # Prepend an encoding string to protect against bugs in that code (#982).
    # Without further fixes, prepending the encoding string causes tracebacks 
    # to have an inaccurate line number, see SeattleTestbed/repy_v2#95.
    # Note that we work around this in tracebackrepy.py, safe.py, and
    # safe_check.py by retrieving the length of
    # virtual_namespace.ENCODING_DECLARATION and subtracting it from reported
    # line numbers.
    code = encoding_header.ENCODING_DECLARATION + code 


    # Do a safety check
    try:
      safe.serial_safe_check(code)
    except Exception, e:
      raise CodeUnsafeError, "Code failed safety check! Error: "+str(e)

    # All good, store the compiled byte code
    self.code = safe_compile(code,name,"exec")


  # Evaluates the virtual namespace
  def evaluate(self,context):
    """
    <Purpose>
      Evaluates the wrapped code within a context.

    <Arguments>
      context: A global context to use when executing the code.
      This should be a SafeDict object, but if a dict object is provided
      it will automatically be converted to a SafeDict object.

    <Exceptions>
      Any that may be raised by the code that is being evaluated.
      A RepyArgumentError exception will be raised if the provided context is not
      a safe dictionary object or a ContextUnsafeError if the
      context is a dict but cannot be converted into a SafeDict.

    <Returns>
      The context dictionary that was used during evaluation.
      If the context was a dict object, this will be a new
      SafeDict object. If the context was a SafeDict object,
      then this will return the same context object.
    """
    # Try to convert a normal dict into a SafeDict
    if type(context) is dict:
      try:
        context = safe.SafeDict(context)
      except Exception, e:
        raise ContextUnsafeError, "Provided context is not safe! Exception: "+str(e)

    # Type check
    if not isinstance(context, safe.SafeDict):
      raise RepyArgumentError, "Provided context is not a safe dictionary!"

    # Call safe_run with the underlying dictionary
    safe.safe_run(self.code, context.__under__)

    # Return the dictionary we used
    return context


