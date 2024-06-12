import os
import sys

sys.path.insert(1, '../utils')
sys.path.insert(1, '../service')

from loguru import logger
from errors import AgentError
import json
#import dotenv
import tempfile
import shutil
from loguru import logger
from fastapi import FastAPI, UploadFile, File, Response, Request, Depends, APIRouter
from fastapi.responses import JSONResponse
from urllib3 import HTTPResponse
from service import KubernetesControllerService

import zipfile

#BaseRouter = APIRouter(prefix='/agents')
BaseRouter = APIRouter()

@BaseRouter.get('/agents/')
async def get_agent_list(request: Request, context:str = None, twin:str = None, kubernetesController: KubernetesControllerService = Depends(KubernetesControllerService)):
    #context = request.headers.get('namespace')
    try:
        data = kubernetesController.get_running_agents(context = context, twinId = twin)
        return JSONResponse(data, 200)
    except AgentError as e:
        return JSONResponse([], 404)

# @BaseRouter.get('/agents/{context}')
# async def get_agent_list_by_context(request: Request, context: str, kubernetesController: KubernetesControllerService = Depends(KubernetesControllerService)):
#     #context = request.headers.get('namespace')
#     try:
#         data = kubernetesController.get_running_agents(context = context)
#         print(data)
#         return JSONResponse(data, 200)
#     except AgentError as e:
#         return JSONResponse([], 404)

# @BaseRouter.get('/agents/{context}/{twinId}')
# async def get_agent_list_by_context_twin(request: Request, context: str, twinId: str, kubernetesController: KubernetesControllerService = Depends(KubernetesControllerService)):
#     logger.info("Entro por el que no es")
#     try:
#         data = kubernetesController.get_running_agents(context = context, twinId = twinId)
#         return JSONResponse(data, 200)
#     except AgentError as e:
#         return JSONResponse([], 404)

# @BaseRouter.get('/agents/twins/{twinId}')
# async def get_agent_list_by_twin(request: Request, twinId: str, kubernetesController: KubernetesControllerService = Depends(KubernetesControllerService)):
#     logger.info("Entro por el que es")
#     try:
#         data = kubernetesController.get_running_agents(twinId = twinId)
#         return JSONResponse(data, 200)
#     except AgentError as e:
#         return JSONResponse([], 404)

# COSAS CONCRETAS DE AGENTE       
@BaseRouter.post('/agent/{context}/{agentId}')
async def create_agent(request: Request, context:str, agentId:str, kubernetesController: KubernetesControllerService = Depends(KubernetesControllerService)):
    payload = await request.json()
    
    try:
        exists = kubernetesController.deploy_agent(payload, context, agentId)
        if exists: return JSONResponse("Already exists", 422)
        return JSONResponse("Agent deployed correctly", 200)
    except AgentError as e:
        return JSONResponse("Failed creating resource", 500)

@BaseRouter.delete('/agent/{context}/{agentId}')
async def delete_agent(request: Request, context: str, agentId: str, kubernetesController: KubernetesControllerService = Depends(KubernetesControllerService)):
    try:
        kubernetesController.delete_agent(context, agentId)
        return JSONResponse(200)
    except AgentError as e:
        return JSONResponse("Failed deleting agent {} in context {}".format(agentId, context))
     
@BaseRouter.post('/agent/{context}/{agentId}/pause')
async def stop_agent(request: Request, context :str, agentId: str, kubernetesController: KubernetesControllerService = Depends(KubernetesControllerService)):
    try:
        kubernetesController.stop_resume_agent(context, agentId, nreplicas = 0)
        return JSONResponse(200)
    except AgentError as e:
        return JSONResponse("Failed stopping agent {} in context {}".format(agentId, context), 404)
    
@BaseRouter.post('/agent/{context}/{agentId}/resume')
async def resume_agent(request: Request, context :str, agentId: str, kubernetesController: KubernetesControllerService = Depends(KubernetesControllerService)):
    try:
        kubernetesController.stop_resume_agent(context, agentId, nreplicas = 1)
        return JSONResponse(200)
    except AgentError as e:
        return JSONResponse("Failed resuming agent {} in context {}".format(agentId, context), 404)
    
@BaseRouter.get('/agent/{context}/{agentId}')
async def get_agent_info(request: Request, context :str, agentId: str, kubernetesController:KubernetesControllerService = Depends(KubernetesControllerService)):
    try:
        result = kubernetesController.get_agent_info(context, agentId)
        return JSONResponse(result, 200)
    except AgentError as e:
        return JSONResponse("Failed retrieving agent {} in context {}".format(agentId, context))
    
@BaseRouter.put('/agent/{context}/{agentId}/twin/{twinId}/link')
async def link_agent_twin(request: Request, context: str, agentId: str, twinId: str, kubernetesController: KubernetesControllerService = Depends(KubernetesControllerService)):
    try:
        kubernetesController.link_unlink_agent_twin(context, agentId, twinId, True)
        return JSONResponse(200)
    except AgentError as e:
        return JSONResponse("Failed linking agent {} in context {} to twin".format(agentId, context, twinId), 404)

@BaseRouter.put('/agent/{context}/{agentId}/twin/{twinId}/unlink')
async def unlink_agent_twin(request: Request, context: str, agentId: str, twinId: str, kubernetesController: KubernetesControllerService = Depends(KubernetesControllerService)):
    try:
        kubernetesController.link_unlink_agent_twin(context, agentId, twinId, False)
        return JSONResponse(200)
    except AgentError as e:
        return JSONResponse("Failed unlinking agent {} in context {} from twin".format(agentId, context, twinId), 404)