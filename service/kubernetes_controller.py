from kubernetes import client
# Import the logging library and the custom formatter
from loguru import logger
from fastapi import Depends
from dependencies import get_kubernetes_api_client, get_kube_namespace
from errors import AgentError
from fastapi.encoders import jsonable_encoder
import json

class KubernetesControllerService:
    CHARACTERS = {
        "ABREPARENTESIS" : "c-.-",
        "CIERRAPARENTESIS" : "-.-c",
        "DOSPUNTOS" : "-..-",
        "COMMA" : "-.-"
    }
    
    def __init__(self, api_client : client.ApiClient=Depends(get_kubernetes_api_client), namespace : str=Depends(get_kube_namespace)) -> None:
        self.api_client = api_client
        self.api_instance = client.CoreV1Api(api_client)
        self.k8s_apps_v1 = client.AppsV1Api(api_client)
        self.batch_api = client.BatchV1Api(api_client)
        self.namespace = namespace
        self.CHARACTERS = {
            "ABREPARENTESIS" : "c-.-",
            "CIERRAPARENTESIS" : "-.-c",
            "DOSPUNTOS" : "-..-",
            "COMMA" : "-.-"
        }
      
    def get_agent_twin_list(self, context: str, agentId: str, kind: str):
        if kind == "Deployment":
            list_of_twins = self.k8s_apps_v1.list_namespaced_deployment(self.namespace, label_selector="opentwins.agents/kind=ot-agent, opentwins.agents/context={}, opentwins.agents/id={}".format(context, agentId)).items[0].metadata.labels["opentwins.agents/twins"]
        else:
            list_of_twins = self.batch_api.list_namespaced_cron_job(self.namespace, label_selector="opentwins.agents/kind=ot-agent, opentwins.agents/context={}, opentwins.agents/id={}".format(context, agentId)).items[0].metadata.labels["opentwins.agents/twins"]

        list_of_twins = self.convert_twin_list(list_of_twins)
        return list_of_twins
    
    # TODO: Sustituir por las annotations 
    def convert_twin_list(self, twin_list):
        print(type(twin_list))
        if type(twin_list) == str:
            logger.info("Converting from string")
            if twin_list == self.CHARACTERS["ABREPARENTESIS"] + self.CHARACTERS["CIERRAPARENTESIS"]:
                return []
            new_twin_list = twin_list
            new_twin_list = new_twin_list.replace(self.CHARACTERS["ABREPARENTESIS"], "[\"")
            new_twin_list = new_twin_list.replace(self.CHARACTERS["CIERRAPARENTESIS"], "\"]")
            new_twin_list = new_twin_list.replace(self.CHARACTERS["DOSPUNTOS"], ":")
            new_twin_list = new_twin_list.replace(self.CHARACTERS["COMMA"], "\",\"")
            return json.loads(new_twin_list)
        elif type(twin_list) == list:
            logger.info("Converting from list")
            
            new_twin_list = self.CHARACTERS["ABREPARENTESIS"]
                            
            for twin in twin_list:
                twin_name = str(twin)
                new_twin_list+=twin_name.replace(":", self.CHARACTERS["DOSPUNTOS"])
                new_twin_list+= self.CHARACTERS["COMMA"]
            if len(twin_list) > 0:
                new_twin_list = new_twin_list[:-3]
            new_twin_list += self.CHARACTERS["CIERRAPARENTESIS"]
            
            return new_twin_list
        
    def check_if_exists(self, context: str, agentId: str):
        logger.info("Searching in deployment list")
        list_of_deployments = self.k8s_apps_v1.list_namespaced_deployment(self.namespace, label_selector="opentwins.agents/kind=ot-agent, opentwins.agents/context={}, opentwins.agents/id={}".format(context, agentId))
        if list_of_deployments.items:
            return "Deployment"
        
        logger.info("Searching in cronjob list")
        list_of_cronjobs = self.batch_api.list_namespaced_cron_job(self.namespace, label_selector="opentwins.agents/kind=ot-agent, opentwins.agents/context={}, opentwins.agents/id={}".format(context, agentId))
        
        if list_of_cronjobs.items:
            return "CronJob"
        
        return False

    def get_running_agents(self, context: str = None, twinId: str= None):
        logger.info("Listing pods with their IPs:")
        
        tries = 0
        while(tries < 3):
            try:
                #pod_list = self.api_instance.list_namespaced_pod(context, watch=False)
                label_selector = "opentwins.agents/kind=ot-agent"
                if context != None:
                    label_selector += ", opentwins.agents/context={}".format(context)
                print(label_selector)
                deployment_list = self.k8s_apps_v1.list_namespaced_deployment(self.namespace, label_selector=label_selector)   
                cronjob_list = self.batch_api.list_namespaced_cron_job(self.namespace, label_selector=label_selector) 



                list_of_deployments = []
                for deployment in deployment_list.items:
                    if twinId != None and not twinId in self.convert_twin_list(deployment.metadata.labels["opentwins.agents/twins"]):
                        continue
                    
                    
                    pod_list = self.api_instance.list_namespaced_pod(self.namespace, label_selector="opentwins.agents/kind=ot-agent, opentwins.agents/type=deployment, opentwins.agents/context={}, opentwins.agents/id={}".format(deployment.metadata.labels["opentwins.agents/context"], deployment.metadata.labels["opentwins.agents/id"]),watch=False)

                    list_of_pods = [
                        {
                            "id": pod.metadata.labels["opentwins.agents/id"],
                            "name": pod.metadata.labels["opentwins.agents/name"],
                            "phase": pod.status.phase,
                            "status": pod.status.container_statuses[0].ready,
                            "creation_timestamp": pod.metadata.creation_timestamp.strftime("%Y/%m/%d, %H:%M:%S%z"),
                        } for pod in pod_list.items
                    ]
                    
                    deployment_info = {
                        "id": deployment.metadata.labels["opentwins.agents/id"],
                        "name": deployment.metadata.labels["opentwins.agents/name"],
                        "namespace":deployment.metadata.labels["opentwins.agents/context"],
                        "status": "Paused" if deployment.spec.replicas == 0 else "Active",
                        "type": "deployment",
                        "twins": self.convert_twin_list(deployment.metadata.labels["opentwins.agents/twins"]),
                        "pods": list_of_pods
                    }
                    list_of_deployments.append(deployment_info)


                list_of_cronjobs = []
                for cronjob in cronjob_list.items:
                    if twinId != None and not twinId in self.convert_twin_list(cronjob.metadata.labels["opentwins.agents/twins"]):
                        continue
                    pod_list = self.api_instance.list_namespaced_pod(self.namespace, label_selector="opentwins.agents/kind=ot-agent, opentwins.agents/type=cronjob, opentwins.agents/context={}, opentwins.agents/id={}".format(cronjob.metadata.labels["opentwins.agents/context"], cronjob.metadata.labels["opentwins.agents/id"]),watch=False)
                    
                    list_of_pods = [
                        {
                            "id": pod.metadata.labels["opentwins.agents/id"],
                            "phase": pod.status.phase,
                            "status": pod.status.container_statuses[0].ready,
                            "creation_timestamp": pod.metadata.creation_timestamp.strftime("%Y/%m/%d, %H:%M:%S%z"),
                        } for pod in pod_list.items
                    ]
                    
                    cronjob_info = {
                        "id": cronjob.metadata.labels["opentwins.agents/id"],
                        "name": cronjob.metadata.labels["opentwins.agents/name"],
                        "namespace":cronjob.metadata.labels["opentwins.agents/context"],
                        "type": "cronjob",
                        "schedule": cronjob.spec.schedule,
                        "twins": self.convert_twin_list(cronjob.metadata.labels["opentwins.agents/twins"]),
                        "status": "Active" if not cronjob.spec.suspend else "Paused",
                        "last_scheduled" : cronjob.status.last_schedule_time.strftime("%Y/%m/%d, %H:%M:%S+%z") if cronjob.status.last_schedule_time is not None else None,
                        "last_scheduled_successful" : cronjob.status.last_successful_time.strftime("%Y/%m/%d, %H:%M:%S%z") if cronjob.status.last_successful_time is not None else None,
                        "pods" : list_of_pods
                        } 
                    list_of_cronjobs.append(cronjob_info)
                
                
                
                return list_of_deployments + list_of_cronjobs
            except Exception as e:
                logger.error(e)
                logger.warning("Retrying to get the pods")
                tries +=1
        raise AgentError("Failed to get the pods")
        
    def deploy_agent(self, manifest: str, context: str, agentId: str):
        tries = 0
        while(tries < 3):
            try:                
                # If doesnt exists it just create it.
                if not self.check_if_exists(context, agentId):
                    logger.info("Exists, deploying agent...")
                    
                    manifest["metadata"]["name"] = "opentwins-agent-"+agentId
                    manifest["metadata"]["labels"]["opentwins.agents/id"] = agentId
                    manifest["metadata"]["labels"]["opentwins.agents/context"] = context
                    manifest["metadata"]["labels"]["opentwins.agents/kind"] = "ot-agent"
                    
                    if "opentwins.agents/twins" in manifest["metadata"]["labels"]:
                        twin_list = json.loads(manifest["metadata"]["labels"]["opentwins.agents/twins"])
                        
                        new_twin_list = self.convert_twin_list(twin_list)                        
                        
                        manifest["metadata"]["labels"]["opentwins.agents/twins"] = new_twin_list
                    else:
                        manifest["metadata"]["labels"]["opentwins.agents/twins"] = self.convert_twin_list([])
                        
                        
                        
                                        
                    if manifest["kind"] == "Deployment":
                        logger.info("Creating new deployment")
                        
                        manifest["spec"]["template"]["metadata"]["labels"]["opentwins.agents/kind"] = "ot-agent"
                        manifest["spec"]["template"]["metadata"]["labels"]["opentwins.agents/id"] = agentId
                        manifest["spec"]["template"]["metadata"]["labels"]["opentwins.agents/context"] = context
                        manifest["spec"]["template"]["metadata"]["labels"]["opentwins.agents/type"] = "deployment"
                        manifest["spec"]["template"]["metadata"]["labels"]["opentwins.agents/name"] = manifest["metadata"]["labels"]["opentwins.agents/name"] if "opentwins.agents/name" in manifest["metadata"]["labels"] else agentId
                        
                        resp = self.k8s_apps_v1.create_namespaced_deployment(body=manifest, namespace=self.namespace)
                    else:
                        manifest["spec"]["jobTemplate"]["spec"]["template"]["metadata"] = {
                            "labels": {
                                "opentwins.agents/kind" : "ot-agent",
                                "opentwins.agents/id" : agentId,
                                "opentwins.agents/context" : context,
                                "opentwins.agents/type" :"cronjob",
                                "opentwins.agents/name" : manifest["metadata"]["labels"]["opentwins.agents/name"] if "opentwins.agents/name" in manifest["metadata"]["labels"] else agentId
                            }
                        }

                        logger.info("Creating new cronjob")
                        resp = self.batch_api.create_namespaced_cron_job(body=manifest, namespace=self.namespace)
                    return False
                # If it does, return true to raise the error
                logger.info("Already exists...")
                return True
            except Exception as e:
                logger.error(e)
                logger.warning("Retrying to create deploy")
                tries +=1
        raise AgentError("Failed creating deployment or cronjob")
    
    def delete_agent(self, context: str, agentId: str):
        logger.info("Deleting agent %s", agentId)
        tries = 0
        while(tries < 3):        
            try:
                kind = self.check_if_exists(context, agentId)
                if not kind:
                    raise AgentError("There is not any agent with that characteristics")
                
                logger.info("Found agent, deleting...")
                
                if kind == "Deployment":
                    self.k8s_apps_v1.delete_namespaced_deployment("opentwins-agent-"+agentId, self.namespace)
                else:
                    self.batch_api.delete_namespaced_cron_job("opentwins-agent-"+agentId, self.namespace)
                    
                return True
            except Exception as e:
                logger.error(e)
                logger.error("Failed to delete agent %s", agentId)
                tries +=1
        raise AgentError("Failed deleting deployment or cronjob")
    
    def stop_resume_agent(self, context: str, agentId: str, nreplicas = 0):
        tries = 0
        while(tries < 3):   
            try: 
                kind = self.check_if_exists(context, agentId)
                if not kind:
                    raise AgentError("There is not any agent with that characteristics")
                logger.info("Found, patching the process...")
                
                if kind == "Deployment":
                    self.k8s_apps_v1.patch_namespaced_deployment("opentwins-agent-"+agentId, self.namespace ,{'spec': {'replicas': nreplicas}})
                else:
                    nreplicas = False if nreplicas else True
                    self.batch_api.patch_namespaced_cron_job("opentwins-agent-"+agentId, self.namespace, {'spec': {'suspend' : nreplicas}})
                
                return True
            except Exception as e:
                logger.error(e)
                logger.error("Failed to patch agent %s", agentId)
                tries+=1
        raise AgentError("Failed to patch agent")
                
    def get_agent_info(self, context: str, agentId: str):
        logger.info("Getting deployment %s info", agentId)
        
        tries = 0
        while(tries < 3): 
            try: 
                kind = self.check_if_exists(context, agentId)
                if not kind:
                    raise AgentError("There is not any agent with that characteristics")
                logger.info("Found, retrieving info...")
                
                if kind == "Deployment":
                    data = self.k8s_apps_v1.read_namespaced_deployment("opentwins-agent-"+agentId, self.namespace)
                else:
                    data = self.batch_api.read_namespaced_cron_job("opentwins-agent-"+agentId, self.namespace)
                    
                data_dict = data.to_dict()
                data_dict["metadata"]["labels"]["opentwins.agents/twins"] = self.convert_twin_list(data_dict["metadata"]["labels"]["opentwins.agents/twins"])
                
                
                
                # sendBackData = {
                #     'name' : data_dict['metadata']['name'],
                #     'start_time' : data.status.start_time.isoformat(),
                #     'status' : jsonable_encoder(data_dict['status']['container_statuses'][0]['state']),
                #     'env_variables' : data_dict['spec']['containers'][0]['env']
                # }
                
                #return sendBackData
                data_dict = json.dumps(data_dict, default=str)
                return data_dict
            except Exception as e:
                logger.error(e)
                logger.error("Failed to get deployment %s info", agentId)
                tries+=1
        raise AgentError("Failed to patch agent")
    
    def link_unlink_agent_twin(self, context: str, agentId: str, twinId:str, link: bool):
        tries = 0
        while(tries < 3):   
            try: 
                kind = self.check_if_exists(context, agentId)
                if not kind:
                    raise AgentError("There is not any agent with that characteristics")
                logger.info("Found, patching the agent...")
                
                twin_list = self.get_agent_twin_list(context, agentId, kind)
                
                if link:
                    if twinId in twin_list:
                        raise AgentError("Link already exists")
                    else:
                        new_twin_list = twin_list
                        new_twin_list.append(twinId)
                        new_twin_list = self.convert_twin_list(new_twin_list)
                    
                    if kind == "Deployment":
                        self.k8s_apps_v1.patch_namespaced_deployment("opentwins-agent-"+agentId, self.namespace, {'metadata': {'labels': {'opentwins.agents/twins': new_twin_list}}})
                    else:
                        self.batch_api.patch_namespaced_cron_job("opentwins-agent-"+agentId, self.namespace, {'metadata': {'labels': {'opentwins.agents/twins': new_twin_list}}})
                else:
                    if not twinId in twin_list:
                        raise AgentError("Link doesn't exists")
                    else:
                        new_twin_list = twin_list
                        new_twin_list.remove(twinId)
                        new_twin_list = self.convert_twin_list(new_twin_list)

                    if kind == "Deployment":
                        self.k8s_apps_v1.patch_namespaced_deployment("opentwins-agent-"+agentId, self.namespace, {'metadata': {'labels': {'opentwins.agents/twins': new_twin_list}}})
                    else:
                        self.batch_api.patch_namespaced_cron_job("opentwins-agent-"+agentId, self.namespace, {'metadata': {'labels': {'opentwins.agents/twins': new_twin_list}}})
                
                return True
            except Exception as e:
                logger.error(e)
                logger.error("Failed to patch agent %s", agentId)
                tries+=1
        raise AgentError("Failed to patch agent")
    
    
    