# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from datetime import datetime
import json
from msrestazure.tools import resource_id, is_valid_resource_id
from azure.cli.core.azclierror import (
    InvalidArgumentValueError,
    RequiredArgumentMissingError,
    MutuallyExclusiveArgumentError
)
from azure.cli.core.commands.client_factory import get_subscription_id

from knack.log import get_logger
logger = get_logger(__name__)


# pylint: disable=too-many-statements,line-too-long
def validate_sqlvm_group(cmd, namespace):
    '''
    Validates if name or id has been provided. If name has been provided, it assumes the group is in the same resource group.
    '''
    group = namespace.sql_virtual_machine_group_resource_id

    if group and not is_valid_resource_id(group):
        namespace.sql_virtual_machine_group_resource_id = resource_id(
            subscription=get_subscription_id(cmd.cli_ctx),
            resource_group=namespace.resource_group_name,
            namespace='Microsoft.SqlVirtualMachine', type='sqlVirtualMachineGroups',
            name=group
        )


# pylint: disable=too-many-statements,line-too-long
def validate_sqlvm_list(cmd, namespace):
    '''
    Validates if name or id has been provided. If name has been provided, it assumes the vm is in the same resource group.
    '''
    vms = namespace.sql_virtual_machine_instances

    for n, sqlvm in enumerate(vms):
        if sqlvm and not is_valid_resource_id(sqlvm):
            # add the correct resource id
            namespace.sql_virtual_machine_instances[n] = resource_id(
                subscription=get_subscription_id(cmd.cli_ctx),
                resource_group=namespace.resource_group_name,
                namespace='Microsoft.SqlVirtualMachine', type='sqlVirtualMachines',
                name=sqlvm
            )


# pylint: disable=too-many-statements,line-too-long
def validate_load_balancer(cmd, namespace):
    '''
    Validates if name or id has been provided. If name has been provided, it assumes the load balancer is in the same group.
    '''
    lb = namespace.load_balancer_resource_id

    if not is_valid_resource_id(lb):
        namespace.load_balancer_resource_id = resource_id(
            subscription=get_subscription_id(cmd.cli_ctx),
            resource_group=namespace.resource_group_name,
            namespace='Microsoft.Network', type='loadBalancers',
            name=lb
        )


# pylint: disable=too-many-statements,line-too-long
def validate_public_ip_address(cmd, namespace):
    '''
    Validates if name or id has been provided. If name has been provided, it assumes the public ip address is in the same group.
    '''
    public_ip = namespace.public_ip_address_resource_id

    if public_ip and not is_valid_resource_id(public_ip):
        namespace.public_ip_address_resource_id = resource_id(
            subscription=get_subscription_id(cmd.cli_ctx),
            resource_group=namespace.resource_group_name,
            namespace='Microsoft.Network', type='publicIPAddresses',
            name=public_ip
        )


# pylint: disable=too-many-statements,line-too-long
def validate_subnet(cmd, namespace):
    '''
    Validates if name or id has been provided. If name has been provided, it assumes the public ip address is in the same group.
    '''
    subnet = namespace.subnet_resource_id
    vnet = namespace.vnet_name

    if vnet and '/' in vnet:
        raise InvalidArgumentValueError("incorrect usage: --subnet ID | --subnet NAME --vnet-name NAME")

    subnet_is_id = is_valid_resource_id(subnet)
    if (subnet_is_id and vnet) or (not subnet_is_id and not vnet):
        raise MutuallyExclusiveArgumentError("incorrect usage: --subnet ID | --subnet NAME --vnet-name NAME")

    if not subnet_is_id and vnet:
        namespace.subnet_resource_id = resource_id(
            subscription=get_subscription_id(cmd.cli_ctx),
            resource_group=namespace.resource_group_name,
            namespace='Microsoft.Network', type='virtualNetworks',
            name=vnet, child_type_1='subnets',
            child_name_1=subnet
        )


# pylint: disable=too-many-statements,line-too-long
def validate_sqlmanagement(namespace):
    '''
    Validates if sql management mode provided, the offer type and sku type has to be provided.
    '''
    sql_mgmt_mode = namespace.sql_management_mode

    if (sql_mgmt_mode == "NoAgent" and (namespace.sql_image_sku is None or namespace.sql_image_offer is None)):
        raise RequiredArgumentMissingError("usage error: --sql-mgmt-type NoAgent --image-sku NAME --image-offer NAME")


# pylint: disable=too-many-statements,line-too-long
def validate_least_privilege_mode(namespace):
    '''
    Validates if least privilege mode provided, management mode is Full
    '''
    least_privilege_mode = namespace.least_privilege_mode

    if (least_privilege_mode == "Enabled" and (namespace.sql_management_mode is None or namespace.sql_management_mode != "Full")):
        raise RequiredArgumentMissingError("usage error: --least-privilege-mode Enabled --sql-mgmt-type Full")


# pylint: disable=too-many-statements,line-too-long
def validate_expand(namespace):
    '''
    Concatenates expand parameters
    '''
    if namespace.expand is not None:
        namespace.expand = ",".join(namespace.expand)


# pylint: disable=too-many-statements,line-too-long
def validate_assessment(namespace):
    '''
    Validates assessment settings
    '''
    enable_assessment = namespace.enable_assessment
    enable_assessment_schedule = namespace.enable_assessment_schedule
    assessment_weekly_interval = namespace.assessment_weekly_interval
    assessment_monthly_occurrence = namespace.assessment_monthly_occurrence
    assessment_day_of_week = namespace.assessment_day_of_week
    assessment_start_time_local = namespace.assessment_start_time_local

    is_assessment_schedule_provided = False
    if (assessment_weekly_interval is not None or
            assessment_weekly_interval is not None or assessment_monthly_occurrence is not None or
            assessment_day_of_week is not None or assessment_start_time_local is not None):
        is_assessment_schedule_provided = True

    # Validate conflicting settings
    if (enable_assessment_schedule is False and is_assessment_schedule_provided):
        raise InvalidArgumentValueError("Assessment schedule settings cannot be provided while enable-assessment-schedule is False")

    # Validate conflicting settings
    if (enable_assessment is False and is_assessment_schedule_provided):
        raise InvalidArgumentValueError("Assessment schedule settings cannot be provided while enable-assessment is False")

    # Validate necessary fields for Assessment schedule
    if is_assessment_schedule_provided:
        if (assessment_weekly_interval is not None and assessment_monthly_occurrence is not None):
            raise MutuallyExclusiveArgumentError("Both assessment-weekly-interval and assessment-montly-occurrence cannot be provided at the same time for Assessment schedule")
        if (assessment_weekly_interval is None and assessment_monthly_occurrence is None):
            raise RequiredArgumentMissingError("Either assessment-weekly-interval or assessment-montly-occurrence must be provided for Assessment schedule")
        if assessment_day_of_week is None:
            raise RequiredArgumentMissingError("assessment-day-of-week must be provided for Assessment schedule")
        if assessment_start_time_local is None:
            raise RequiredArgumentMissingError("assessment-start-time-local must be provided for Assessment schedule")


# pylint: disable=too-many-statements,line-too-long
def validate_assessment_start_time_local(namespace):
    '''
    Validates assessment start time format
    '''
    assessment_start_time_local = namespace.assessment_start_time_local

    TIME_FORMAT = '%H:%M'
    if assessment_start_time_local:
        try:
            datetime.strptime(assessment_start_time_local, TIME_FORMAT)
        except ValueError:
            raise InvalidArgumentValueError("assessment-start-time-local input '{}' is not valid time. Valid example: 19:30".format(assessment_start_time_local))


# pylint: disable=too-many-statements,line-too-long
def validate_azure_ad_authentication(cmd, namespace):
    '''
    Validates Azure AD authentication
    '''
    enable_azure_ad_authentication = namespace.enable_azure_ad_auth
    if enable_azure_ad_authentication is False:
        raise InvalidArgumentValueError("Disable Azure AD authentication is not supported")

    skip_msi_validation = namespace.skip_msi_validation
    if skip_msi_validation is True:
        return

    # SQL VM Azure AD authentication is currently only supported on Azure Public Cloud
    from azure.cli.core.cloud import AZURE_PUBLIC_CLOUD
    if cmd.ctx_cli.cloud.name != AZURE_PUBLIC_CLOUD.name:
        raise InvalidArgumentValueError("Azure AD authentication is not supported in {}".format(cmd.ctx_cli.cloud.name))

    # validate the SQL VM supports Azure AD authentication, i.e. it is on Windows platform and is SQL 2022 or later
    _validate_azure_ad_authentication_supported_on_sqlvm(cmd.cli_ctx, namespace)

    # validate the MSI is valid on the Azure virtual machine
    _validate_msi_valid_on_vm(cmd.cli_ctx, namespace)

    # validate the MSI has appropriate permission to query Microsoft Graph API
    _validate_msi_with_enough_permission(cmd.cli_ctx, namespace)


# validate the SQL VM supports Azure AD authentication, i.e. it is on Windows platform and is SQL 2022 or later
def _validate_azure_ad_authentication_supported_on_sqlvm(cli_ctx, namespace):
    # retrieve SQL VM client
    from ._util import get_sqlvirtualmachine_management_client
    sqlvm_ops = get_sqlvirtualmachine_management_client(cli_ctx).sql_virtual_machines

    # get the sqlvm instance, this is a rest call to the server and deserialization afterwards
    # therefore there is a greater chance to encouter an exception. Instead of poping the exception
    # to the caller directly, we will throw our own InvalidArgumentValueError with more context
    # information
    try:
        sqlvm = sqlvm_ops.get(namespace.resource_group_name, namespace.sql_virtual_machine_name)
    except Exception as e:
        raise InvalidArgumentValueError("Unable to validate Azure AD authentication due to retrieving SQL VM instance encountering an error") from e

    # construct error message for unsupported SQL server version or OS platform
    unsupported_error = "Azure AD authentication requires SQL Server 2022 on Windows platform but the SQL Image Offer of this SQL VM is {}".format(sqlvm.sql_image_offer)

    if sqlvm.sql_image_offer is None:
        raise InvalidArgumentValueError(unsupported_error)

    # an example sqlImageOffer is SQL2022-WS2022
    version_platform = sqlvm.sql_image_offer.split('-')
    if len(version_platform) < 2:
        raise InvalidArgumentValueError(unsupported_error)

    version = version_platform[0]
    platform = version_platform[1]

    try:
        int_version = int(version[3:])
    except ValueError:
        raise InvalidArgumentValueError(unsupported_error)

    if int_version < 2022 or not platform.startswith("WS"):
        raise InvalidArgumentValueError(unsupported_error)


# validate the MSI is valid on the Azure virtual machine
# return the principal ID of the MSI
def _validate_msi_valid_on_vm(cli_ctx, namespace):
    from azure.cli.core.commands.client_factory import get_mgmt_service_client
    from azure.cli.core.profiles import ResourceType
    compute_client = get_mgmt_service_client(cli_ctx, ResourceType.MGMT_COMPUTE)

    # get the vm instance, this is a rest call to the server and deserialization afterwards
    # therefore there is a greater chance to encouter an exception. Instead of poping the exception
    # to the caller directly, we will throw our own InvalidArgumentValueError with more context
    # information
    try:
        # Azure VM has the same name as the SQL VM
        vm = compute_client.virtual_machines.get(namespace.resource_group_name, namespace.sql_virtual_machine_name)
    except Exception as e:
        raise InvalidArgumentValueError("Unable to validate Azure AD authentication due to retrieving the Azure VM instance encountering an error") from e

    # system-assigned MSI
    if namespace.msi_client_id is None:
        if vm.identity is None or not hasattr(vm.identity, 'principal_id') or getattr(vm.identity, 'principal_id') is None:
            raise InvalidArgumentValueError("Enable Azure AD authentication with system-assigned managed identity but the system-assgined managed identity is not enabled on this Azure VM")
        return vm.identity.principal_id

    # user-assigned MSI
    if vm.identity is None or not hasattr(vm.identity, 'user_assigned_identities'):
        raise InvalidArgumentValueError("Enable Azure AD authentication with user-assigned managed identity {}, but the managed identity is not attached to this Azure VM".format(namespace.msi_client_id))

    for umi in vm.identity.user_assigned_identities:
        if umi.client_id == namespace.msi_client_id:
            return umi.principal_id

    raise InvalidArgumentValueError("Enable Azure AD authentication with user-assigned managed identity {}, but the managed identity is not attached to this Azure VM".format(namespace.msi_client_id))


# Validate the MSI has appropriate permission to query Microsoft Graph API
USER_READ_ALL = "User.Read.All"
APPLICATION_READ_ALL = "Application.Read.All"
GROUP_MEMBER_READ_ALL = "GroupMember.Read.All"


def _validate_msi_with_enough_permission(cli_ctx, principal_id):
    directory_roles = _directory_role_list(cli_ctx, principal_id)

    # If the MSI is assigned "Directory Readers" role, it has enough permission
    if any(role["displayName"] == "Directory Readers" for role in directory_roles):
        return

    # The hardcode appRoleId for the required app roles. most likely they won't change overtime.
    # For safety, we will try to find these appRoleId programatically and only use the hardcode
    # values if we fail to find them
    USER_READ_ALL_ROLE_ID = "a154be20-db9c-4678-8ab7-66f6cc099a59"
    APPLICATION_READ_ALL_ROLE_ID = "9a5d68dd-52b0-4cc2-bd40-abcf44ac3a30"
    GROUP_MEMBER_READ_ALL_ROLE_ID = "98830695-27a2-44f7-8c18-0c3ebc9698f6"

    app_role_id_map = _find_role_id(cli_ctx)
    app_role_id_map.setdefault(USER_READ_ALL, USER_READ_ALL_ROLE_ID)
    app_role_id_map.setdefault(APPLICATION_READ_ALL, APPLICATION_READ_ALL_ROLE_ID)
    app_role_id_map.setdefault(GROUP_MEMBER_READ_ALL, GROUP_MEMBER_READ_ALL_ROLE_ID)

    missing_roles = [USER_READ_ALL, APPLICATION_READ_ALL, GROUP_MEMBER_READ_ALL]
    app_role_assignments = _app_role_assignment_list(cli_ctx, principal_id)
    for assignment in app_role_assignments:
        if assignment["appRoleId"] == app_role_id_map[USER_READ_ALL]:
            missing_roles.remove(USER_READ_ALL)
        elif assignment["appRoleId"] == app_role_id_map[APPLICATION_READ_ALL]:
            missing_roles.remove(APPLICATION_READ_ALL)
        elif assignment["appRoleId"] == app_role_id_map[GROUP_MEMBER_READ_ALL]:
            missing_roles.remove(GROUP_MEMBER_READ_ALL)

        # if we find all the app roles, we can break from here
        if len(missing_roles) == 0:
            break

    if len(missing_roles) > 0:
        raise InvalidArgumentValueError("The managed identity is lack of the following roles for Azure AD authentication: " + ", ".join(missing_roles))


# copied from src/azure-cli/azure/cli/command_modules/role/_msgrpah/_graph_client.py with minor modification
def _send(cli_ctx, method, url, param=None, body=None):
    from azure.cli.core.util import send_raw_request

    # Get the Microsoft Graph API endpoint from CLI metadata
    # https://graph.microsoft.com/ (AzureCloud)
    graph_endpoint = cli_ctx.cloud.endpoints.microsoft_graph_resource_id.rstrip('/')
    graph_resource = cli_ctx.cloud.endpoints.microsoft_graph_resource_id

    # Microsoft Graph API version to use
    MICROSOFT_GRAPH_API_VERSION = "v1.0"
    url = f'{graph_endpoint}/{MICROSOFT_GRAPH_API_VERSION}{url}'

    if body:
        body = json.dumps(body)

        list_result = []
        is_list_result = False

        while True:
            try:
                r = send_raw_request(cli_ctx, method, url, resource=graph_resource, uri_parameters=param, body=body)
            except Exception as ex:
                raise InvalidArgumentValueError("Unable to validate the permission of MSI due to querying Microsoft Graph API encountered error") from ex

            if r.text:
                dic = r.json()

                # The result is a list. Add value to list_result.
                if 'value' in dic:
                    is_list_result = True
                    list_result.extend(dic['value'])

                # Follow nextLink if available
                if '@odata.nextLink' in dic:
                    url = dic['@odata.nextLink']
                    continue

                # Result a list
                if is_list_result:
                    # 'value' can be empty list [], so we can't determine if the result is a list only by
                    # bool(list_result)
                    return list_result

                # Return a single object
                return r.json()
            return None


# https://graph.microsoft.com/v1.0/servicePrincipals/{principalId}/transitiveMemberOf/microsoft.graph.directoryRole
# retrieve all directory role assigned to a service principal
def _directory_role_list(cli_ctx, principal_id):
    DIRECTORY_ROLE_URL = "/servicePrincipals/{}/transitiveMemberOf/microsoft.graph.directoryRole"
    return _send(cli_ctx, "GET", DIRECTORY_ROLE_URL.format(principal_id))


# https://graph.microsoft.com/v1.0/servicePrincipals/{principalId}/appRoleAssignments
# retrieve all app role assignments to a service principal
def _app_role_assignment_list(cli_ctx, principal_id):
    APP_ROLE_ASSIGNMENT_URL = "/servicePrincipals/{}/appRoleAssignments"
    return _send(cli_ctx, "GET", APP_ROLE_ASSIGNMENT_URL.format(principal_id))


# https://graph.microsoft.com/v1.0/servicePrincipals?$filter=displayName%20eq%20'Microsoft%20Graph'
# this is a best effor retrieval
def _find_role_id(cli_ctx):
    app_role_id_map = {}

    MICROSOFT_GRAPH_URL = "/servicePrincipals?$filter=displayName%20eq%20'Microsoft%20Graph'"
    try:
        service_principals = _send(cli_ctx, "GET", MICROSOFT_GRAPH_URL)
    except Exception as ex:  # pylint: disable=broad-except
        logger.warning("Unable to query Microsoft Graph service principal, exception: %s", ex)
        return app_role_id_map

    # this in fact shoud not happen
    if service_principals is None or len(service_principals) == 0:
        logger.warning("Failed to find Microsoft Graph service principal")
        return app_role_id_map

    app_roles = service_principals[0]['appRoles']
    for app_role in app_roles:
        if app_role["value"] == USER_READ_ALL:
            app_role_id_map[USER_READ_ALL] = app_role["id"]
        elif app_role["value"] == APPLICATION_READ_ALL:
            app_role_id_map[APPLICATION_READ_ALL] = app_role["id"]
        elif app_role["value"] == GROUP_MEMBER_READ_ALL:
            app_role_id_map[GROUP_MEMBER_READ_ALL] = app_role["id"]

    if len(app_role_id_map) < 3:
        logger.warning("Failed to find all app role id, using the hardcoded app role id")

    return app_role_id_map
