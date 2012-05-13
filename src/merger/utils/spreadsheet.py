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

'''
Created on May 29, 2011
'''

from merger.conf import mergeconf
from merger.conf.mergeconf import LOGGER
import gdata.spreadsheet.service
import logging
import time


def add_row(rowdict, username, apassword, aspreadsheet_key, aworksheet_id, asource):
    if not mergeconf.SPREADSHEET_ENABLED:
        LOGGER.debug("Not writing to spreadsheet as its not enabled...")
        return
    mergeconf.LOGGER.debug("spreadsheet_key: [" + aspreadsheet_key + "] worksheetid: [" + aworksheet_id + "] source: [" + asource + "]")
    password = apassword
    spreadsheet_key = aspreadsheet_key
    # All spreadsheets have worksheets. worksheet #1 by default always has a value of 'od6'
    worksheet_id = 'od6'
    
    spr_client = gdata.spreadsheet.service.SpreadsheetsService()
    spr_client.email = username
    spr_client.password = password
    spr_client.source = asource
    spr_client.ProgrammaticLogin()
    
    # Prepare the dictionary to write
    rowdict['date'] = time.strftime('%m/%d/%Y')
    logging.info(rowdict)
    
    entry = spr_client.InsertRow(rowdict, spreadsheet_key, worksheet_id)
    if isinstance(entry, gdata.spreadsheet.SpreadsheetsList):
        logging.info("Insert row succeeded.")
    else:
        logging.info("Insert row failed.")