# Copyright (c) 2012 Liveperson. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#   * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#   * Neither the name of Liveperson. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Internal LOGGER initialized with common logging requirements and log file path.
"""


import logging
def initlogger(loggername, logfilepath, tomask):
    """Facade to make logging in this small project more straight forward.
       Nothing special here, just having the defaults.

    Args:
      loggername: str Specifies the LOGGER name to be used.
      logfilepath: str Where to write the logs into.

    Returns:
      A LOGGER which prints to a file at specified location.
    """
    logging.basicConfig(format='%(asctime)s %(levelname)s' + 
        ' %(module)s %(lineno)d %(message)s', level=logging.DEBUG)
    LOGGER = logging.getLogger(loggername)
    hdlr = logging.FileHandler(logfilepath)
    formatter = MaskFormatter('%(asctime)s %(levelname)s' + 
        ' %(module)s %(lineno)d %(message)s', mask=tomask)
    hdlr.setLevel(logging.DEBUG)
    LOGGER.setLevel(logging.DEBUG)
    hdlr.setFormatter(formatter)
    LOGGER.addHandler(hdlr)
    return LOGGER

def log(LOGGER, message):
    """Log a message using the specified LOGGER.

    Args:
      LOGGER: str Specifies the LOGGER name to be used.
      logfilepath: str Where to write the logs into.
      mas: str to mask when printing to log

    Returns:
      A LOGGER which prints to a file at specified location.
    """
    if LOGGER is not None:
        LOGGER.debug(message)
    else:
        logging.info(message)

class MaskFormatter(logging.Formatter):

    def __init__(self, fmt, mask):
        logging.Formatter.__init__(self, fmt)
        self.mask = mask

    def format(self, record):
        result = logging.Formatter.format(self, record)
        if result is not None and result.find(self.mask) != -1:
            result = result.replace(self.mask, '*' * len(self.mask))
        return result    

