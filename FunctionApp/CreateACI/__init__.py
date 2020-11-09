import logging
import json
import time

import os
import json


import azure.functions as func
import os.path
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import DeploymentMode


class Creator(object):
    """ Initialize the dreator class with deploymentname, subscription, resource group and ARMTemplateJSON
    :raises KeyError: If AZURE_CLIENT_ID, AZURE_CLIENT_SECRET or AZURE_TENANT_ID env
        variables or not defined
    """

    def __init__(self, deploymentname, subscription_id, resource_group, aciarmJSON):
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.aciarmJSON = aciarmJSON
        self.deploymentname = deploymentname

        self.credentials = ServicePrincipalCredentials(
            client_id=os.environ['AZURE_CLIENT_ID'],
            secret=os.environ['AZURE_CLIENT_SECRET'],
            tenant=os.environ['AZURE_TENANT_ID']
        )
        self.resource_client = ResourceManagementClient(
            self.credentials, self.subscription_id)

    def create(self):
        """Deploy the template to a resource group."""


        template = self.aciarmJSON
        deployment_properties = {
            'mode': DeploymentMode.incremental,
            'template': template,
        }
        #self.resource_client.deployments.delete

        deployment_async_operation = self.resource_client.deployments.create_or_update(
            self.resource_group,
            self.deploymentname,
            deployment_properties
        )
        deployment_async_operation.wait()

def getAccessToken():
    tenant = os.environ['tenant']
    authority_url = 'https://login.microsoftonline.com/' + tenant
    client_id = os.environ['appId']
    client_secret = os.environ['password']
    resource = 'https://management.azure.com/'
    context = adal.AuthenticationContext(authority_url)
    token = context.acquire_token_with_client_credentials(resource, client_id, client_secret)
    return token

def main(inputblob: func.InputStream,
         aciarmtemplate: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {inputblob.name}\n"
                 f"Blob Size: {inputblob.length} bytes")
    
    #Get ACI ARM Template
    aciarmBLOB = aciarmtemplate.read().decode("utf-8")
    # Convert to JSON
    aciarmJSON = json.loads(aciarmBLOB)
    # Generate a unique ACI ContainerGroupName
    # using epochtime
    aciresourcename = "solver-{}".format(time.time())
    deploymentname = aciresourcename
    aciarmJSON["variables"]["containerGroupName"] = aciresourcename

    #Apply ACR Credentials
    # resources properties array need to remove hard code of array index 1 and 0
    aciarmJSON["resources"][1]["properties"]["imageRegistryCredentials"][0]["server"] = os.environ["ACR_SERVER"]
    aciarmJSON["resources"][1]["properties"]["imageRegistryCredentials"][0]["username"] = os.environ["ACR_USERNAME"]
    aciarmJSON["resources"][1]["properties"]["imageRegistryCredentials"][0]["password"] = os.environ["ACR_PASSWORD"]

    #Apply Input & Output Configuration
    #Convert hard coded Environment Variables to dynamic assignment 
    aciarmJSON["resources"][1]["properties"]["containers"][0]["properties"]["environmentVariables"][3] = {"name": "INPUT_BLOB", "value":inputblob.name}
    aciarmJSON["resources"][1]["properties"]["containers"][0]["properties"]["environmentVariables"][4] = {"name": "OUTPUT_BLOB", "value":aciresourcename}



    # Initialize the deployer class
    creator = Creator(deploymentname, os.environ['AZURE_SUBSCRIPTION_ID'], os.environ['RESOURCE_GROUP'], aciarmJSON)
    print("Beginning the deployment... \n\n")
    # Deploy the template
    creator.create()
    # Need something to validate this...






    



    