## ACI Orchestrator
An approach to managing ACI Container Group - Creation and Cleanup on completion. It is uses ARM Template for the definition of the workload template. A Python script is used too apply customizations to the ARM template at deployment time. All configurations in the ARM template for ACI Container Group creation can now be easily applied based on need. 


### Resources 
* A new subnet or subnet delegated to ACI in appropriate VNET
* If new subnet set Network Profile: Subnet delegated to ACI
* Blob Storage With Service Endpoint to ACI subnet
* 3 Containers
    * aciarmtemplates
    * datainput
    * dataoutput
* ServicePrincipal with Contributor access to RESOURCE_GROUP where ACI will be deployed
* KeyVault to store ServicePrincipal credentials and other configuration information
* MSI for Azure Functions with access to KeyVault

### Setup
* Store ARM Templates for ACI in "aciarmtemplates" Container
* The ACI Template has Network Profile pre-populated
* MSI for Azure Function With Contributor Access to Create ACI Resources
* [CreateACI]Azure Function with "datainput" Blob Trigger to Create New ACI Container Group Instance
* [TerminateACI]Azure Function on TimerTrigger at desired interval to sweep for Terminated ACI Groups and Delete ACI Container Group Instances


### Process
1. Drop "InputBlob" in "datainput"
2. Triggers "CreateACIFunc"
3. "CreateACIFunc" creates ACI Container Group Resource using ARM template blob. 
4. At 30 minute interval - Scan and Delete Container Groups with Containers in "Terminated" state



### ARM Deployment Unit Testing)
az deployment group create \
  --name aci \
  --resource-group <RESOURCE_GROUP> \
  --template-file azuredeploy.json


### Service Principal with Contributor access to RESOURCE_GROUP
az ad sp create-for-rbac -n "<SERVICEPRINCIPAL_NAME>" --role contributor \
    --scopes /subscriptions/<SUBSCRIPTIONID>/resourceGroups/<RESOURCE_GROUP>