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


class CreateInstanceCPUMappings(command.ShowOne):
    """Create a new baremetal flavor"""

    def get_parser(self, prog_name):
        parser = super(CreateInstanceCPUMappings, self).get_parser(prog_name)
        parser.add_argument(
            "instance_uuid",
            metavar="<instance_uuid>",
            help=_("The instance uuid you want to create mapping for.")
        )
        parser.add_argument(
            "cpu_mappings",
            metavar="<cpu_mappings>",
            help=_("The mappings you want to assign for the given instance.")
        )
        parser.add_argument(
            "--wait-until-active",
            metavar='<wait_until_active|True>',
            default=False,
            help=_("Whether to perform this action now or do it "
                   "automatically once the instance turn into ACTIVE status.")
        )
        return parser

    def take_action(self, parsed_args):
        kongmingclient = self.app.client_manager.resource_pin

        info = {}

        data = kongmingclient.instance_cpu_mappings.create(
            instance_uuid=parsed_args.instance_uuid,
            cpu_mappings=parsed_args.cpu_mappings,
            wait_until_active=parsed_args.wait_until_active,
        )

        info.update(data._info)

        return zip(*sorted(info.items()))


class DeleteInstanceCPUMappings(command.Command):
    """Delete existing baremetal flavor(s)"""

    def get_parser(self, prog_name):
        parser = super(DeleteInstanceCPUMappings, self).get_parser(prog_name)
        parser.add_argument(
            'instance_uuid',
            metavar='<instance_uuid>',
            nargs='+',
            help=_("instance_cpu_mapping(s) to delete (instance UUID)")
        )
        return parser

    def take_action(self, parsed_args):
        kongmingclient = self.app.client_manager.resource_pin
        result = 0
        for one_mapping in parsed_args.instance_uuid:
            try:
                data = utils.find_resource(
                    kongmingclient.instance_cpu_mappings, one_mapping)
                kongmingclient.instance_cpu_mappings.delete(
                    data.instance_uuid)
            except Exception as e:
                result += 1
                LOG.error("Failed to delete cpu mapping with instance UUID "
                          "'%(uuid)s': %(e)s",
                          {'uuid': one_mapping, 'e': e})

        if result > 0:
            total = len(parsed_args.flavor)
            msg = (_("%(result)s of %(total)s mapping failed "
                     "to delete.") % {'result': result, 'total': total})
            raise exceptions.CommandError(msg)


class ListInstanceCPUMappings(command.Lister):
    """List all baremetal flavors"""

    def get_parser(self, prog_name):
        parser = super(ListInstanceCPUMappings, self).get_parser(prog_name)
        parser.add_argument(
            '--long',
            action='store_true',
            default=False,
            help=_("List additional fields in output")
        )
        return parser

    def take_action(self, parsed_args):
        kongmingclient = self.app.client_manager.resource_pin

        column_headers = (
            "Instance UUID",
            "CPU Mappings",
            "Host",
            "Status",
            "Project ID",
            "User ID",
        )
        columns = (
            "instance_uuid",
            "cpu_mappings",
            "host",
            "status",
            "project_id",
            "user_id",
        )

        data = kongmingclient.instance_cpu_mappings.list()
        if not data:
            return (), ()
        column_headers, columns = cli_utils.clean_listing_columns(
            column_headers, columns, data[0])

        return (column_headers,
                (utils.get_item_properties(
                    s, columns) for s in data))


class ShowFlavor(command.ShowOne):
    """Display baremetal flavor details"""

    def get_parser(self, prog_name):
        parser = super(ShowFlavor, self).get_parser(prog_name)
        parser.add_argument(
            'flavor',
            metavar='<flavor>',
            help=_("Flavor to display (name or UUID)")
        )
        return parser

    def take_action(self, parsed_args):
        bc_client = self.app.client_manager.baremetal_compute
        data = utils.find_resource(
            bc_client.flavor,
            parsed_args.flavor,
        )

        if 'resources' in data._info:
            data._info.update({'resources': utils.format_dict(
                data._info.get('resources', {}))})
        if 'resource_aggregates' in data._info:
            data._info.update({'resource_aggregates': utils.format_dict(
                data._info.get('resource_aggregates', {}))})
        info = {}
        info.update(data._info)
        return zip(*sorted(info.items()))


class SetFlavor(command.Command):
    """Set baremetal flavor properties"""

    def get_parser(self, prog_name):
        parser = super(SetFlavor, self).get_parser(prog_name)
        parser.add_argument(
            'flavor',
            metavar='<flavor>',
            help=_("Flavor to modify (name or UUID)")
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Set flavor access to project (name or ID) '
                   '(admin only)'),
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help=_('Set a new name to a flavor (admin only)')
        )
        parser.add_argument(
            '--is-public',
            metavar='<is-public>',
            type=strutils.bool_from_string,
            help=_('Set a flavor to be public or private '
                   '(admin only)'),
        )
        parser.add_argument(
            '--disabled',
            metavar='<disabled>',
            type=strutils.bool_from_string,
            help=_('Set a flavor to be disabled or enabled '
                   '(admin only)'),
        )
        return parser

    def take_action(self, parsed_args):

        bc_client = self.app.client_manager.baremetal_compute
        data = utils.find_resource(
            bc_client.flavor,
            parsed_args.flavor,
        )
        updates = []
        if parsed_args.name:
            updates.append({"op": "replace",
                            "path": "/name",
                            "value": parsed_args.name})
        if parsed_args.is_public is not None:
            updates.append({"op": "replace",
                            "path": "/is_public",
                            "value": parsed_args.is_public})
        if parsed_args.disabled is not None:
            updates.append({"op": "replace",
                            "path": "/disabled",
                            "value": parsed_args.disabled})
        if updates:
            bc_client.flavor.update(data, updates)
        if parsed_args.project:
            if data.is_public:
                msg = _("Cannot set access for a public flavor")
                raise exceptions.CommandError(msg)
            else:
                bc_client.flavor.add_tenant_access(
                    data, parsed_args.project)


class UnsetFlavor(command.Command):
    """Unset baremetal flavor properties"""

    def get_parser(self, prog_name):
        parser = super(UnsetFlavor, self).get_parser(prog_name)
        parser.add_argument(
            'flavor',
            metavar='<flavor>',
            help=_("Flavor to modify (name or UUID)")
        )
        parser.add_argument(
            '--project',
            metavar='<project>',
            help=_('Remove flavor access from project (name or ID) '
                   '(admin only)'),
        )
        return parser

    def take_action(self, parsed_args):

        bc_client = self.app.client_manager.baremetal_compute
        data = utils.find_resource(
            bc_client.flavor,
            parsed_args.flavor,
        )
        if parsed_args.project:
            if data.is_public:
                msg = _("Cannot remove access for a public flavor")
                raise exceptions.CommandError(msg)
            else:
                bc_client.flavor.remove_tenant_access(
                    data, parsed_args.project)
