# -*- coding: utf-8 -*-
"""The compoennts

"""

__license__ = """
    This file is part of Janitoo.

    Janitoo is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Janitoo is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Janitoo. If not, see <http://www.gnu.org/licenses/>.

"""
__author__ = 'Sébastien GALLET aka bibi21000'
__email__ = 'bibi21000@gmail.com'
__copyright__ = "Copyright © 2013-2014-2015-2016 Sébastien GALLET aka bibi21000"

# Set default logging handler to avoid "No handler found" warnings.
import logging
logger = logging.getLogger(__name__)

import os
import time
import datetime
import urllib2 as urllib
from urllib2 import Request as request

from janitoo.bus import JNTBus
from janitoo.value import JNTValue, value_config_poll
from janitoo.node import JNTNode
from janitoo.component import JNTComponent

##############################################################
#Check that we are in sync with the official command classes
#Must be implemented for non-regression
from janitoo.classes import COMMAND_DESC

COMMAND_NOTIFY = 0x3010

assert(COMMAND_DESC[COMMAND_NOTIFY] == 'COMMAND_NOTIFY')
##############################################################

from janitoo_sms import OID

def make_freemobile(**kwargs):
    return FreemobileComponent(**kwargs)

class SMSComponent(JNTComponent):
    """ A SMS component"""

    def __init__(self, bus=None, **kwargs):
        """
        """
        oid = kwargs.pop('oid', '%s.genericsms'%OID)
        name = kwargs.pop('name', "Generic sms")
        product_name = kwargs.pop('product_name', "Generic sms")
        hearbeat = kwargs.pop('hearbeat', 900)
        default_notify = kwargs.pop('default_notify', "That's all folks")
        default_userid = kwargs.pop('default_userid', "")
        default_passwd = kwargs.pop('default_passwd', "")
        default_url = kwargs.pop('default_url', 'https://smsapi.free-mobile.fr/sendmsg')
        bus = kwargs.pop('bus', bus)
        JNTComponent.__init__(self, oid=oid, bus=bus, name=name, hearbeat=hearbeat,
                product_name=product_name, **kwargs)
        logger.debug("[%s] - __init__ node uuid:%s", self.__class__.__name__, self.uuid)
        uuid="notify"
        self.values[uuid] = self.value_factory['action_string'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='Notify the user',
            label='Notify',
            default=default_notify,
            set_data_cb=self.set_notify,
            cmd_class=COMMAND_NOTIFY,
        )
        uuid="userid"
        self.values[uuid] = self.value_factory['config_string'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='The userid from your provider',
            label='Userid',
            default=default_userid,
        )
        uuid="passwd"
        self.values[uuid] = self.value_factory['config_string'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='The passwd from your provider',
            label='Pwd',
            default=default_passwd,
        )
        uuid="url"
        self.values[uuid] = self.value_factory['config_string'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='The API url of your provider',
            label='Url',
            default=default_url,
        )

    def check_heartbeat(self):
        """Check that the component is 'available'
        """
        return True

    def set_notify(self, node_uuid, index, data):
        """Send the notification
        """
        pass

class FreemobileComponent(SMSComponent):
    """ A Free mobile component"""

    def __init__(self, bus=None, **kwargs):
        """
        """
        oid = kwargs.pop('oid', '%s.freemobile'%OID)
        name = kwargs.pop('name', "Fee mobile sms")
        product_name = kwargs.pop('product_name', "Free mobile sms")
        SMSComponent.__init__(self, oid=oid, bus=bus, name=name,
                product_name=product_name, default_url='https://smsapi.free-mobile.fr/sendmsg', **kwargs)

    def set_notify(self, node_uuid, index, data, **kwargs):
        """Send the notification
        """
        params = {
            'url' : self.values['url'].get_data_index(index=index),
            'userid' : kwargs.pop('userid', self.values['userid'].get_data_index(index=index)),
            'passwd' : kwargs.pop('passwd', self.values['passwd'].get_data_index(index=index)),
            'msg' : urllib.quote(data),
            }
        urlst = "{url}?user={userid}&pass={passwd}&msg={msg}".format(**params)
        try:
            req = request(urlst)
            response = urllib.urlopen(req)
            the_page = response.read()
        except Exception:
            logger.exception('[%s] - Exception when sending sms to freemobile')

    def check_heartbeat(self):
        """Check that the component is 'available'
        """
        try:
            req = request(self.values['url'].data)
            response = urllib.urlopen(req)
            the_page = response.read()
            return True
        except urllib.HTTPError as e:
            if e.code == 400:
                return True
            else:
                logger.exception('[%s] - Exception when checking heartbeat')
                return False
        except Exception:
            logger.exception('[%s] - Exception when checking heartbeat')
            return False
