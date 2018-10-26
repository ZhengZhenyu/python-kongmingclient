#   Copyright 2016 Huawei, Inc. All rights reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#


"""Kongming v1 Instance CPU mapping action implementations"""

import logging

from osc_lib.cli import parseractions
from osc_lib.command import command
from osc_lib import exceptions
from osc_lib import utils
from oslo_utils import strutils

from kongmingclient.common.i18n import _
from kongmingclient.common import utils as cli_utils

LOG = logging.getLogger(__name__)


class ShowHost(command.ShowOne):
    """Display host details"""

    def get_parser(self, prog_name):
        parser = super(ShowHost, self).get_parser(prog_name)
        parser.add_argument(
            'host_name',
            metavar='<host_name>',
            help=_("Host to display (Host_name)")
        )
        return parser

    def take_action(self, parsed_args):
        kongmingclient = self.app.client_manager.resource_pin
        data = utils.find_resource(
            kongmingclient.hosts, parsed_args.host_name)

        info = {}
        info.update(data._info)
        return zip(*sorted(info.items()))