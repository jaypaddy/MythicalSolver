import logging
import json
import datetime

import os
import json


import azure.functions as func
import os.path
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode
from azure.mgmt.containerinstance import ContainerInstanceManagementClient
from azure.mgmt.containerinstance.models import (ContainerGroup, Container, ContainerPort, Port, IpAddress,
                                                 ResourceRequirements, ResourceRequests, ContainerGroupNetworkProtocol, OperatingSystemTypes)

class Terminator(object):
    """ Initialize the terminator class with deploymentname, subscription, resource group 
    :raises KeyError: If AZURE_CLIENT_ID, AZURE_CLIENT_SECRET or AZURE_TENANT_ID env
        variables or not defined
    """

    def __init__(self, subscription_id, resource_group):
        self.subscription_id = subscription_id
        self.resource_group = resource_group

        self.credentials = ServicePrincipalCredentials(
            client_id=os.environ['AZURE_CLIENT_ID'],
            secret=os.environ['AZURE_CLIENT_SECRET'],
            tenant=os.environ['AZURE_TENANT_ID']
        )
        self.resource_client = ResourceManagementClient(
            self.credentials, self.subscription_id)
        self.acigroup_client = ContainerInstanceManagementClient(
            self.credentials, self.subscription_id)

    def terminate(self):
        """List all ACI Resources that have Stopped and Delete Them"""
        container_groups = self.acigroup_client.container_groups.list_by_resource_group(self.resource_group)

        for container_group in container_groups:
            to_be_deleted=False
            cgroup = self.acigroup_client.container_groups.get(self.resource_group,container_group.name)
            print("\t{0}: {{ name: '{0}', location: '{1}', containers: {2} }}".format(
                container_group.name,
                container_group.location,
                len(container_group.containers))
                )
            print('\n{0}\t\t\t{1}'.format('restart_count', 'current_state'))
            print('---------------------------------------------------')
            for container in cgroup.containers:
                instance = container.instance_view
                print('{0}\t\t{1}'.format(instance.restart_count,instance.current_state.state))
                if instance.current_state.state == "Terminated":
                    to_be_deleted = True
                else:
                    to_be_deleted = False
            if to_be_deleted == True:
                    self.acigroup_client.container_groups.delete(self.resource_group,container_group.name)



def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    # Initialize the terminator class
    terminator = Terminator(os.environ['AZURE_SUBSCRIPTION_ID'], "MythicalSolver_RG")
    terminator.terminate()
