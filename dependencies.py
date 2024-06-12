from kubernetes import client, config
import os
from loguru import logger
import boto3
from dotenv import load_dotenv

load_dotenv()


def get_kubernetes_api_client():
    """ Get Kubernetes configuration.
        You can provide a token and the external host IP 
        to access a external Kubernetes cluster. If one
        of them is not provided the configuration returned
        will be for your local machine.
        Parameters:
            str: token 
            str: external_host
        Return:
            Kubernetes API client
    """
    # KUBERNETES code goes here
    aConfiguration = client.Configuration()
    if os.getenv("INSIDE_CLUSTER"):
        logger.info("RUNNING INSIDE CLUSTER")
        config.load_incluster_config(aConfiguration) # To run inside the container
    else:
        external_host = os.getenv('KUBE_HOST')
        token = os.getenv('TOKEN_KUBERNETES')

        config.load_kube_config() # To run externally
        
        aConfiguration.host = external_host 
        aConfiguration.verify_ssl = False
        aConfiguration.api_key = { "authorization": "Bearer " + token }
        
    api_client = client.ApiClient(aConfiguration)
    
    return api_client

def get_kube_namespace():
    """ Get the namespace from the environment variables
        Return:
            str: namespace
    """
    return os.getenv('KUBE_NAMESPACE')