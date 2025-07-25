#
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
"""This module contains Google Vertex AI operators."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from google.api_core.exceptions import NotFound
from google.api_core.gapic_v1.method import DEFAULT, _MethodDefault
from google.cloud.aiplatform_v1.types import Model, model_service

from airflow.providers.google.cloud.hooks.vertex_ai.model_service import ModelServiceHook
from airflow.providers.google.cloud.links.vertex_ai import (
    VertexAIModelExportLink,
    VertexAIModelLink,
    VertexAIModelListLink,
)
from airflow.providers.google.cloud.operators.cloud_base import GoogleCloudBaseOperator

if TYPE_CHECKING:
    from google.api_core.retry import Retry

    from airflow.utils.context import Context


class DeleteModelOperator(GoogleCloudBaseOperator):
    """
    Deletes a Model.

    :param project_id: Required. The ID of the Google Cloud project that the service belongs to.
    :param region: Required. The ID of the Google Cloud region that the service belongs to.
    :param model_id: Required. The ID of the Model resource to be deleted.
        Could be in format `projects/{project}/locations/{location}/models/{model_id}@{version_id}` or
        `projects/{project}/locations/{location}/models/{model_id}@{version_alias}` if model
        has several versions.
    :param retry: Designation of what errors, if any, should be retried.
    :param timeout: The timeout for this request.
    :param metadata: Strings which should be sent along with the request as metadata.
    :param gcp_conn_id: The connection ID to use connecting to Google Cloud.
    :param impersonation_chain: Optional service account to impersonate using short-term
        credentials, or chained list of accounts required to get the access_token
        of the last account in the list, which will be impersonated in the request.
        If set as a string, the account must grant the originating account
        the Service Account Token Creator IAM role.
        If set as a sequence, the identities from the list must grant
        Service Account Token Creator IAM role to the directly preceding identity, with first
        account from the list granting this role to the originating account (templated).
    """

    template_fields = ("region", "model_id", "project_id", "impersonation_chain")

    def __init__(
        self,
        *,
        region: str,
        project_id: str,
        model_id: str,
        retry: Retry | _MethodDefault = DEFAULT,
        timeout: float | None = None,
        metadata: Sequence[tuple[str, str]] = (),
        gcp_conn_id: str = "google_cloud_default",
        impersonation_chain: str | Sequence[str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.region = region
        self.project_id = project_id
        self.model_id = model_id
        self.retry = retry
        self.timeout = timeout
        self.metadata = metadata
        self.gcp_conn_id = gcp_conn_id
        self.impersonation_chain = impersonation_chain

    def execute(self, context: Context):
        hook = ModelServiceHook(
            gcp_conn_id=self.gcp_conn_id,
            impersonation_chain=self.impersonation_chain,
        )
        self.model_id = self.model_id.rpartition("@")[0] if "@" in self.model_id else self.model_id
        try:
            self.log.info("Deleting model: %s", self.model_id)
            operation = hook.delete_model(
                project_id=self.project_id,
                region=self.region,
                model=self.model_id,
                retry=self.retry,
                timeout=self.timeout,
                metadata=self.metadata,
            )
            hook.wait_for_operation(timeout=self.timeout, operation=operation)
            self.log.info("Model was deleted.")
        except NotFound:
            self.log.info("The Model ID %s does not exist.", self.model_id)


class GetModelOperator(GoogleCloudBaseOperator):
    """
    Retrieves a Model.

    :param project_id: Required. The ID of the Google Cloud project that the service belongs to.
    :param region: Required. The ID of the Google Cloud region that the service belongs to.
    :param model_id: Required. The ID of the Model resource to be retrieved.
        Could be in format `projects/{project}/locations/{location}/models/{model_id}@{version_id}` or
        `projects/{project}/locations/{location}/models/{model_id}@{version_alias}` if model has
        several versions.
    :param retry: Designation of what errors, if any, should be retried.
    :param timeout: The timeout for this request.
    :param metadata: Strings which should be sent along with the request as metadata.
    :param gcp_conn_id: The connection ID to use connecting to Google Cloud.
    :param impersonation_chain: Optional service account to impersonate using short-term
        credentials, or chained list of accounts required to get the access_token
        of the last account in the list, which will be impersonated in the request.
        If set as a string, the account must grant the originating account
        the Service Account Token Creator IAM role.
        If set as a sequence, the identities from the list must grant
        Service Account Token Creator IAM role to the directly preceding identity, with first
        account from the list granting this role to the originating account (templated).
    """

    template_fields = ("region", "model_id", "project_id", "impersonation_chain")
    operator_extra_links = (VertexAIModelLink(),)

    def __init__(
        self,
        *,
        region: str,
        project_id: str,
        model_id: str,
        retry: Retry | _MethodDefault = DEFAULT,
        timeout: float | None = None,
        metadata: Sequence[tuple[str, str]] = (),
        gcp_conn_id: str = "google_cloud_default",
        impersonation_chain: str | Sequence[str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.region = region
        self.project_id = project_id
        self.model_id = model_id
        self.retry = retry
        self.timeout = timeout
        self.metadata = metadata
        self.gcp_conn_id = gcp_conn_id
        self.impersonation_chain = impersonation_chain

    @property
    def extra_links_params(self) -> dict[str, Any]:
        return {
            "region": self.region,
            "project_id": self.project_id,
        }

    def execute(self, context: Context):
        hook = ModelServiceHook(
            gcp_conn_id=self.gcp_conn_id,
            impersonation_chain=self.impersonation_chain,
        )
        self.model_id = self.model_id.rpartition("@")[0] if "@" in self.model_id else self.model_id
        try:
            self.log.info("Retrieving model: %s", self.model_id)
            model = hook.get_model(
                project_id=self.project_id,
                region=self.region,
                model_id=self.model_id,
                retry=self.retry,
                timeout=self.timeout,
                metadata=self.metadata,
            )
            self.log.info("Model found. Model ID: %s", self.model_id)

            self.xcom_push(context, key="model_id", value=self.model_id)
            VertexAIModelLink.persist(context=context, model_id=self.model_id)
            return Model.to_dict(model)
        except NotFound:
            self.log.info("The Model ID %s does not exist.", self.model_id)


class ExportModelOperator(GoogleCloudBaseOperator):
    """
    Exports a trained, exportable Model to a location specified by the user.

    :param project_id: Required. The ID of the Google Cloud project that the service belongs to.
    :param region: Required. The ID of the Google Cloud region that the service belongs to.
    :param model_id: Required. The ID of the Model to export.
        Could be in format `projects/{project}/locations/{location}/models/{model_id}@{version_id}` or
        `projects/{project}/locations/{location}/models/{model_id}@{version_alias}` if model has
        several versions.
    :param output_config:  Required. The desired output location and configuration.
    :param retry: Designation of what errors, if any, should be retried.
    :param timeout: The timeout for this request.
    :param metadata: Strings which should be sent along with the request as metadata.
    :param gcp_conn_id: The connection ID to use connecting to Google Cloud.
    :param impersonation_chain: Optional service account to impersonate using short-term
        credentials, or chained list of accounts required to get the access_token
        of the last account in the list, which will be impersonated in the request.
        If set as a string, the account must grant the originating account
        the Service Account Token Creator IAM role.
        If set as a sequence, the identities from the list must grant
        Service Account Token Creator IAM role to the directly preceding identity, with first
        account from the list granting this role to the originating account (templated).
    """

    template_fields = ("region", "model_id", "project_id", "impersonation_chain")
    operator_extra_links = (VertexAIModelExportLink(),)

    def __init__(
        self,
        *,
        project_id: str,
        region: str,
        model_id: str,
        output_config: model_service.ExportModelRequest.OutputConfig | dict,
        retry: Retry | _MethodDefault = DEFAULT,
        timeout: float | None = None,
        metadata: Sequence[tuple[str, str]] = (),
        gcp_conn_id: str = "google_cloud_default",
        impersonation_chain: str | Sequence[str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.region = region
        self.project_id = project_id
        self.model_id = model_id
        self.output_config = output_config
        self.retry = retry
        self.timeout = timeout
        self.metadata = metadata
        self.gcp_conn_id = gcp_conn_id
        self.impersonation_chain = impersonation_chain

    def execute(self, context: Context):
        hook = ModelServiceHook(
            gcp_conn_id=self.gcp_conn_id,
            impersonation_chain=self.impersonation_chain,
        )

        try:
            self.log.info("Exporting model: %s", self.model_id)
            operation = hook.export_model(
                project_id=self.project_id,
                region=self.region,
                model=self.model_id,
                output_config=self.output_config,
                retry=self.retry,
                timeout=self.timeout,
                metadata=self.metadata,
            )
            hook.wait_for_operation(timeout=self.timeout, operation=operation)
            VertexAIModelExportLink.persist(
                context=context,
                output_config=self.output_config,
                model_id=self.model_id,
                project_id=self.project_id,
            )
            self.log.info("Model was exported.")
        except NotFound:
            self.log.info("The Model ID %s does not exist.", self.model_id)


class ListModelsOperator(GoogleCloudBaseOperator):
    r"""
    Lists Models in a Location.

    :param project_id: Required. The ID of the Google Cloud project that the service belongs to.
    :param region: Required. The ID of the Google Cloud region that the service belongs to.
    :param retry: Designation of what errors, if any, should be retried.
    :param filter: An expression for filtering the results of the request. For field names both
        snake_case and camelCase are supported.
        -  ``model`` supports = and !=. ``model`` represents the Model ID,  Could be in format the
        last segment of the Model's [resource name][google.cloud.aiplatform.v1.Model.name].
        -  ``display_name`` supports = and !=
        -  ``labels`` supports general map functions that is:
        --  ``labels.key=value`` - key:value equality
        --  \`labels.key:\* or labels:key - key existence
        --  A key including a space must be quoted. ``labels."a key"``.
    :param page_size: The standard list page size.
    :param page_token: The standard list page token. Typically obtained via
        [ListModelsResponse.next_page_token][google.cloud.aiplatform.v1.ListModelsResponse.next_page_token]
        of the previous
        [ModelService.ListModels][google.cloud.aiplatform.v1.ModelService.ListModels]
        call.
    :param read_mask: Mask specifying which fields to read.
    :param order_by: A comma-separated list of fields to order by, sorted in ascending order. Use "desc"
        after a field name for descending.
    :param timeout: The timeout for this request.
    :param metadata: Strings which should be sent along with the request as metadata.
    :param gcp_conn_id: The connection ID to use connecting to Google Cloud.
    :param impersonation_chain: Optional service account to impersonate using short-term
        credentials, or chained list of accounts required to get the access_token
        of the last account in the list, which will be impersonated in the request.
        If set as a string, the account must grant the originating account
        the Service Account Token Creator IAM role.
        If set as a sequence, the identities from the list must grant
        Service Account Token Creator IAM role to the directly preceding identity, with first
        account from the list granting this role to the originating account (templated).
    """

    template_fields = ("region", "project_id", "impersonation_chain")
    operator_extra_links = (VertexAIModelListLink(),)

    def __init__(
        self,
        *,
        region: str,
        project_id: str,
        filter: str | None = None,
        page_size: int | None = None,
        page_token: str | None = None,
        read_mask: str | None = None,
        order_by: str | None = None,
        retry: Retry | _MethodDefault = DEFAULT,
        timeout: float | None = None,
        metadata: Sequence[tuple[str, str]] = (),
        gcp_conn_id: str = "google_cloud_default",
        impersonation_chain: str | Sequence[str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.region = region
        self.project_id = project_id
        self.filter = filter
        self.page_size = page_size
        self.page_token = page_token
        self.read_mask = read_mask
        self.order_by = order_by
        self.retry = retry
        self.timeout = timeout
        self.metadata = metadata
        self.gcp_conn_id = gcp_conn_id
        self.impersonation_chain = impersonation_chain

    @property
    def extra_links_params(self) -> dict[str, Any]:
        return {
            "project_id": self.project_id,
        }

    def execute(self, context: Context):
        hook = ModelServiceHook(
            gcp_conn_id=self.gcp_conn_id,
            impersonation_chain=self.impersonation_chain,
        )
        results = hook.list_models(
            project_id=self.project_id,
            region=self.region,
            filter=self.filter,
            page_size=self.page_size,
            page_token=self.page_token,
            read_mask=self.read_mask,
            order_by=self.order_by,
            retry=self.retry,
            timeout=self.timeout,
            metadata=self.metadata,
        )
        VertexAIModelListLink.persist(context=context)
        return [Model.to_dict(result) for result in results]


class UploadModelOperator(GoogleCloudBaseOperator):
    """
    Uploads a Model artifact into Vertex AI.

    :param project_id: Required. The ID of the Google Cloud project that the service belongs to.
    :param region: Required. The ID of the Google Cloud region that the service belongs to.
    :param model: Required. The Model to create. Creating model with the name that already
        exists leads to creating new version of existing model.
    :param parent_model: The ID of the parent model to create a new version under.
    :param retry: Designation of what errors, if any, should be retried.
    :param timeout: The timeout for this request.
    :param metadata: Strings which should be sent along with the request as metadata.
    :param gcp_conn_id: The connection ID to use connecting to Google Cloud.
    :param impersonation_chain: Optional service account to impersonate using short-term
        credentials, or chained list of accounts required to get the access_token
        of the last account in the list, which will be impersonated in the request.
        If set as a string, the account must grant the originating account
        the Service Account Token Creator IAM role.
        If set as a sequence, the identities from the list must grant
        Service Account Token Creator IAM role to the directly preceding identity, with first
        account from the list granting this role to the originating account (templated).
    """

    template_fields = ("region", "project_id", "model", "parent_model", "impersonation_chain")
    operator_extra_links = (VertexAIModelLink(),)

    def __init__(
        self,
        *,
        project_id: str,
        region: str,
        model: Model | dict,
        parent_model: str | None = None,
        retry: Retry | _MethodDefault = DEFAULT,
        timeout: float | None = None,
        metadata: Sequence[tuple[str, str]] = (),
        gcp_conn_id: str = "google_cloud_default",
        impersonation_chain: str | Sequence[str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.project_id = project_id
        self.region = region
        self.model = model
        self.parent_model = parent_model
        self.retry = retry
        self.timeout = timeout
        self.metadata = metadata
        self.gcp_conn_id = gcp_conn_id
        self.impersonation_chain = impersonation_chain

    @property
    def extra_links_params(self) -> dict[str, Any]:
        return {
            "region": self.region,
            "project_id": self.project_id,
        }

    def execute(self, context: Context):
        hook = ModelServiceHook(
            gcp_conn_id=self.gcp_conn_id,
            impersonation_chain=self.impersonation_chain,
        )
        self.log.info("Upload model")
        operation = hook.upload_model(
            project_id=self.project_id,
            region=self.region,
            model=self.model,
            parent_model=self.parent_model,
            retry=self.retry,
            timeout=self.timeout,
            metadata=self.metadata,
        )
        result = hook.wait_for_operation(timeout=self.timeout, operation=operation)

        model_resp = model_service.UploadModelResponse.to_dict(result)
        model_id = hook.extract_model_id(model_resp)
        self.log.info("Model was uploaded. Model ID: %s", model_id)

        self.xcom_push(context, key="model_id", value=model_id)
        VertexAIModelLink.persist(context=context, model_id=model_id)
        return model_resp


class ListModelVersionsOperator(GoogleCloudBaseOperator):
    """
    Lists Model versions in a Location.

    :param project_id: Required. The ID of the Google Cloud project that the service belongs to.
    :param region: Required. The ID of the Google Cloud region that the service belongs to.
    :param model_id: Required. The ID of the model to list versions for.
        Could be in format `projects/{project}/locations/{location}/models/{model_id}@{version_id}` or
        `projects/{project}/locations/{location}/models/{model_id}@{version_alias}` if model has
        several versions.
    :param retry: Designation of what errors, if any, should be retried.
    :param timeout: The timeout for this request.
    :param metadata: Strings which should be sent along with the request as metadata.
    :param gcp_conn_id: The connection ID to use connecting to Google Cloud.
    :param impersonation_chain: Optional service account to impersonate using short-term
        credentials, or chained list of accounts required to get the access_token
        of the last account in the list, which will be impersonated in the request.
        If set as a string, the account must grant the originating account
        the Service Account Token Creator IAM role.
        If set as a sequence, the identities from the list must grant
        Service Account Token Creator IAM role to the directly preceding identity, with first
        account from the list granting this role to the originating account (templated).
    """

    template_fields = ("model_id", "region", "project_id", "impersonation_chain")

    def __init__(
        self,
        *,
        region: str,
        project_id: str,
        model_id: str,
        retry: Retry | _MethodDefault = DEFAULT,
        timeout: float | None = None,
        metadata: Sequence[tuple[str, str]] = (),
        gcp_conn_id: str = "google_cloud_default",
        impersonation_chain: str | Sequence[str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.region = region
        self.project_id = project_id
        self.model_id = model_id
        self.retry = retry
        self.timeout = timeout
        self.metadata = metadata
        self.gcp_conn_id = gcp_conn_id
        self.impersonation_chain = impersonation_chain

    def execute(self, context: Context):
        hook = ModelServiceHook(
            gcp_conn_id=self.gcp_conn_id,
            impersonation_chain=self.impersonation_chain,
        )
        self.log.info("Retrieving versions list from model: %s", self.model_id)
        results = hook.list_model_versions(
            project_id=self.project_id,
            region=self.region,
            model_id=self.model_id,
            retry=self.retry,
            timeout=self.timeout,
            metadata=self.metadata,
        )
        for result in results:
            model = Model.to_dict(result)
            self.log.info("Model name: %s;", model["name"])
            self.log.info("Model version: %s, model alias %s;", model["version_id"], model["version_aliases"])
        return [Model.to_dict(result) for result in results]


class SetDefaultVersionOnModelOperator(GoogleCloudBaseOperator):
    """
    Sets the desired Model version as Default.

    :param project_id: Required. The ID of the Google Cloud project that the service belongs to.
    :param region: Required. The ID of the Google Cloud region that the service belongs to.
    :param model_id: Required. The ID of the model to set as default.
        Should be in format `projects/{project}/locations/{location}/models/{model_id}@{version_id}` or
        `projects/{project}/locations/{location}/models/{model_id}@{version_alias}` if model
        has several versions.
    :param retry: Designation of what errors, if any, should be retried.
    :param timeout: The timeout for this request.
    :param metadata: Strings which should be sent along with the request as metadata.
    :param gcp_conn_id: The connection ID to use connecting to Google Cloud.
    :param impersonation_chain: Optional service account to impersonate using short-term
        credentials, or chained list of accounts required to get the access_token
        of the last account in the list, which will be impersonated in the request.
        If set as a string, the account must grant the originating account
        the Service Account Token Creator IAM role.
        If set as a sequence, the identities from the list must grant
        Service Account Token Creator IAM role to the directly preceding identity, with first
        account from the list granting this role to the originating account (templated).
    """

    template_fields = ("model_id", "project_id", "impersonation_chain")
    operator_extra_links = (VertexAIModelLink(),)

    def __init__(
        self,
        *,
        region: str,
        project_id: str,
        model_id: str,
        retry: Retry | _MethodDefault = DEFAULT,
        timeout: float | None = None,
        metadata: Sequence[tuple[str, str]] = (),
        gcp_conn_id: str = "google_cloud_default",
        impersonation_chain: str | Sequence[str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.region = region
        self.project_id = project_id
        self.model_id = model_id
        self.retry = retry
        self.timeout = timeout
        self.metadata = metadata
        self.gcp_conn_id = gcp_conn_id
        self.impersonation_chain = impersonation_chain

    @property
    def extra_links_params(self) -> dict[str, Any]:
        return {
            "region": self.region,
            "project_id": self.project_id,
        }

    def execute(self, context: Context):
        hook = ModelServiceHook(
            gcp_conn_id=self.gcp_conn_id,
            impersonation_chain=self.impersonation_chain,
        )

        self.log.info(
            "Setting version %s as default on model %s", self.model_id.rpartition("@")[0], self.model_id
        )

        updated_model = hook.set_version_as_default(
            region=self.region,
            model_id=self.model_id,
            project_id=self.project_id,
            retry=self.retry,
            timeout=self.timeout,
            metadata=self.metadata,
        )
        VertexAIModelLink.persist(context=context, model_id=self.model_id)
        return Model.to_dict(updated_model)


class AddVersionAliasesOnModelOperator(GoogleCloudBaseOperator):
    """
    Adds version aliases for the Model.

    :param project_id: Required. The ID of the Google Cloud project that the service belongs to.
    :param region: Required. The ID of the Google Cloud region that the service belongs to.
    :param model_id: Required. The ID of the model to add version aliases for.
        Should be in format `projects/{project}/locations/{location}/models/{model_id}@{version_id}` or
        `projects/{project}/locations/{location}/models/{model_id}@{version_alias}`.
    :param version_aliases: List of version aliases to be added to model version.
    :param retry: Designation of what errors, if any, should be retried.
    :param timeout: The timeout for this request.
    :param metadata: Strings which should be sent along with the request as metadata.
    :param gcp_conn_id: The connection ID to use connecting to Google Cloud.
    :param impersonation_chain: Optional service account to impersonate using short-term
        credentials, or chained list of accounts required to get the access_token
        of the last account in the list, which will be impersonated in the request.
        If set as a string, the account must grant the originating account
        the Service Account Token Creator IAM role.
        If set as a sequence, the identities from the list must grant
        Service Account Token Creator IAM role to the directly preceding identity, with first
        account from the list granting this role to the originating account (templated).
    """

    template_fields = ("model_id", "project_id", "impersonation_chain")
    operator_extra_links = (VertexAIModelLink(),)

    def __init__(
        self,
        *,
        region: str,
        project_id: str,
        model_id: str,
        version_aliases: Sequence[str],
        retry: Retry | _MethodDefault = DEFAULT,
        timeout: float | None = None,
        metadata: Sequence[tuple[str, str]] = (),
        gcp_conn_id: str = "google_cloud_default",
        impersonation_chain: str | Sequence[str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.region = region
        self.project_id = project_id
        self.model_id = model_id
        self.version_aliases = version_aliases
        self.retry = retry
        self.timeout = timeout
        self.metadata = metadata
        self.gcp_conn_id = gcp_conn_id
        self.impersonation_chain = impersonation_chain

    @property
    def extra_links_params(self) -> dict[str, Any]:
        return {
            "region": self.region,
            "project_id": self.project_id,
        }

    def execute(self, context: Context):
        hook = ModelServiceHook(
            gcp_conn_id=self.gcp_conn_id,
            impersonation_chain=self.impersonation_chain,
        )
        self.log.info(
            "Adding aliases %s to model version %s", self.version_aliases, self.model_id.rpartition("@")[0]
        )

        updated_model = hook.add_version_aliases(
            region=self.region,
            model_id=self.model_id,
            version_aliases=self.version_aliases,
            project_id=self.project_id,
            retry=self.retry,
            timeout=self.timeout,
            metadata=self.metadata,
        )
        VertexAIModelLink.persist(context=context, model_id=self.model_id)
        return Model.to_dict(updated_model)


class DeleteVersionAliasesOnModelOperator(GoogleCloudBaseOperator):
    """
    Deletes version aliases for the Model.

    :param project_id: Required. The ID of the Google Cloud project that the service belongs to.
    :param region: Required. The ID of the Google Cloud region that the service belongs to.
    :param model_id: Required. The ID of the model to delete version aliases from.
        Should be in format `projects/{project}/locations/{location}/models/{model_id}@{version_id}` or
        `projects/{project}/locations/{location}/models/{model_id}@{version_alias}`.
    :param version_aliases: List of version aliases to be deleted from model version.
    :param retry: Designation of what errors, if any, should be retried.
    :param timeout: The timeout for this request.
    :param metadata: Strings which should be sent along with the request as metadata.
    :param gcp_conn_id: The connection ID to use connecting to Google Cloud.
    :param impersonation_chain: Optional service account to impersonate using short-term
        credentials, or chained list of accounts required to get the access_token
        of the last account in the list, which will be impersonated in the request.
        If set as a string, the account must grant the originating account
        the Service Account Token Creator IAM role.
        If set as a sequence, the identities from the list must grant
        Service Account Token Creator IAM role to the directly preceding identity, with first
        account from the list granting this role to the originating account (templated).
    """

    template_fields = ("model_id", "project_id", "impersonation_chain")
    operator_extra_links = (VertexAIModelLink(),)

    def __init__(
        self,
        *,
        region: str,
        project_id: str,
        model_id: str,
        version_aliases: Sequence[str],
        retry: Retry | _MethodDefault = DEFAULT,
        timeout: float | None = None,
        metadata: Sequence[tuple[str, str]] = (),
        gcp_conn_id: str = "google_cloud_default",
        impersonation_chain: str | Sequence[str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.region = region
        self.project_id = project_id
        self.model_id = model_id
        self.version_aliases = version_aliases
        self.retry = retry
        self.timeout = timeout
        self.metadata = metadata
        self.gcp_conn_id = gcp_conn_id
        self.impersonation_chain = impersonation_chain

    @property
    def extra_links_params(self) -> dict[str, Any]:
        return {
            "region": self.region,
            "project_id": self.project_id,
        }

    def execute(self, context: Context):
        hook = ModelServiceHook(
            gcp_conn_id=self.gcp_conn_id,
            impersonation_chain=self.impersonation_chain,
        )
        self.log.info(
            "Deleting aliases %s from model version %s",
            self.version_aliases,
            self.model_id.rpartition("@")[0],
        )

        updated_model = hook.delete_version_aliases(
            region=self.region,
            model_id=self.model_id,
            version_aliases=self.version_aliases,
            project_id=self.project_id,
            retry=self.retry,
            timeout=self.timeout,
            metadata=self.metadata,
        )
        VertexAIModelLink.persist(context=context, model_id=self.model_id)
        return Model.to_dict(updated_model)


class DeleteModelVersionOperator(GoogleCloudBaseOperator):
    """
    Delete Model version in a Location.

    :param project_id: Required. The ID of the Google Cloud project that the service belongs to.
    :param region: Required. The ID of the Google Cloud region that the service belongs to.
    :param model_id: Required. The ID of the Model in which to delete version.
        Should be in format `projects/{project}/locations/{location}/models/{model_id}@{version_id}` or
        `projects/{project}/locations/{location}/models/{model_id}@{version_alias}`
        several versions.
    :param retry: Designation of what errors, if any, should be retried.
    :param timeout: The timeout for this request.
    :param metadata: Strings which should be sent along with the request as metadata.
    :param gcp_conn_id: The connection ID to use connecting to Google Cloud.
    :param impersonation_chain: Optional service account to impersonate using short-term
        credentials, or chained list of accounts required to get the access_token
        of the last account in the list, which will be impersonated in the request.
        If set as a string, the account must grant the originating account
        the Service Account Token Creator IAM role.
        If set as a sequence, the identities from the list must grant
        Service Account Token Creator IAM role to the directly preceding identity, with first
        account from the list granting this role to the originating account (templated).
    """

    template_fields = ("model_id", "project_id", "impersonation_chain")

    def __init__(
        self,
        *,
        region: str,
        project_id: str,
        model_id: str,
        retry: Retry | _MethodDefault = DEFAULT,
        timeout: float | None = None,
        metadata: Sequence[tuple[str, str]] = (),
        gcp_conn_id: str = "google_cloud_default",
        impersonation_chain: str | Sequence[str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.region = region
        self.project_id = project_id
        self.model_id = model_id
        self.retry = retry
        self.timeout = timeout
        self.metadata = metadata
        self.gcp_conn_id = gcp_conn_id
        self.impersonation_chain = impersonation_chain

    def execute(self, context: Context):
        hook = ModelServiceHook(
            gcp_conn_id=self.gcp_conn_id,
            impersonation_chain=self.impersonation_chain,
        )

        try:
            self.log.info("Deleting model version: %s", self.model_id)
            operation = hook.delete_model_version(
                project_id=self.project_id,
                region=self.region,
                model_id=self.model_id,
                retry=self.retry,
                timeout=self.timeout,
                metadata=self.metadata,
            )
            hook.wait_for_operation(timeout=self.timeout, operation=operation)
            self.log.info("Model version was deleted.")
        except NotFound:
            self.log.info("The Model ID %s does not exist.", self.model_id)
