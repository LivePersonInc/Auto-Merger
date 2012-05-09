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
Simple facade for sending emails, takes the host,port from configuration.
"""

from merger.conf import mergeconf
import smtplib
from merger.conf.mergeconf import LOGGER



def mail(recipients, subject, text, mailenabled=True):
    """Send an email to recipients with specified subject,text.

    Args:
      to: Array of recipients.
      subject: str subject of email to be sent.
      text: str The body text of the email.

    Returns:
      Nothing, just sends an email.
    """
    if not mailenabled:
        LOGGER.debug('Not sending mail, not enabled...')
    else:
        smtp_server = mergeconf.SMTP_HOST
        smtp_port = mergeconf.SMTP_PORT
        login = mergeconf.MAIL_USERNAME
        sender = mergeconf.MAIL_FROM_NAME
        password = mergeconf.MAIL_PASSWORD
        recipient = recipients
        subject = subject
        body = text
        
        body = "" + body + ""
        
        headers = ["From: " + sender,
                   "Subject: " + subject,
                   "To: " + ';'.join(recipient),
                   "MIME-Version: 1.0",
                   "Content-Type: text/plain"]
        headers = "\r\n".join(headers)
        
        mergeconf.LOGGER.debug(headers + '\n' + body)
    
        session = smtplib.SMTP(smtp_server, smtp_port)
        
        session.ehlo()
        session.starttls()
        session.ehlo()
        
        session.login(login, password)
        session.sendmail(sender, recipient, headers + "\r\n\r\n" + body)
        session.quit()
