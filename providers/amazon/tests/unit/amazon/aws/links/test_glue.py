# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import annotations

from airflow.providers.amazon.aws.links.glue import GlueJobRunDetailsLink
from airflow.providers.amazon.version_compat import AIRFLOW_V_3_0_PLUS

from unit.amazon.aws.links.test_base_aws import BaseAwsLinksTestCase

if AIRFLOW_V_3_0_PLUS:
    from airflow.sdk.execution_time.comms import XComResult

import pytest

pytestmark = pytest.mark.db_test


class TestGlueJobRunDetailsLink(BaseAwsLinksTestCase):
    link_class = GlueJobRunDetailsLink

    def test_extra_link(self, mock_supervisor_comms):
        if AIRFLOW_V_3_0_PLUS and mock_supervisor_comms:
            mock_supervisor_comms.send.return_value = XComResult(
                key=self.link_class.key,
                value={
                    "region_name": "ap-southeast-2",
                    "aws_domain": self.link_class.get_aws_domain("aws"),
                    "aws_partition": "aws",
                    "job_run_id": "11111",
                    "job_name": "test_job_name",
                },
            )
        self.assert_extra_link_url(
            expected_url=(
                "https://console.aws.amazon.com/gluestudio/home"
                "?region=ap-southeast-2#/job/test_job_name/run/11111"
            ),
            region_name="ap-southeast-2",
            aws_partition="aws",
            job_run_id="11111",
            job_name="test_job_name",
        )
