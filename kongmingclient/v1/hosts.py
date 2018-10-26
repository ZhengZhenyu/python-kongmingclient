#   Copyright 2018 Huawei, Inc. All rights reserved.
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

from kongmingclient.common import base


class Host(base.Resource):
    pass


class HostManager(base.ManagerWithFind):
    resource_class = Host

    def get(self, host_name):
        url = '/hosts/%s' % base.getid(host_name)
        return self._get(url)

    def list(self):
        url = '/hosts'
        return self._list(url, response_key='instances')

