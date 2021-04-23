#!/usr/bin/python3
import os
import requests
from typing import Optional
from fastapi import FastAPI, Response, Request

import util
import deploy

app = FastAPI()

gb_env = util.get_env([
    'CS_DB_INFO_API_SERVICE_HOST',
    'CS_DB_INFO_API_SERVICE_PORT'
    ])

dest = (f"http://{gb_env['CS_DB_INFO_API_SERVICE_HOST']}:" +
               f"{gb_env['CS_DB_INFO_API_SERVICE_PORT']}")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/v1/cs/info/manage/{db_path:path}")
async def api_get(db_path:str, request: Request):
    params = str(request.query_params)
    if len(params) > 0: params = '?' + params
    url = f'{dest}{request.url.path}{params}'
    ret = requests.get(url)
    util.debug(f"GET {url} ret_status: {ret.status_code} text: {ret.text}")
    return ret.text

@app.put("/v1/cs/info/manage/{db_path:path}")
async def api_put(db_path:str, request: Request):
    params = str(request.query_params)
    if len(params) > 0: params = '?' + params
    url = f'{dest}{request.url.path}{params}'
    body = await request.body()
    ret = requests.put(url, data=body)
    util.debug(f"PUT {url} body: {body} ret_status: {ret.status_code} text: {ret.text}")

    if ret.status_code >= 200 and ret.status_code <= 300 and len(body) > 1:
        deploy.kube_create(db_path, body)

    return ret.text

@app.post("/v1/cs/info/manage/{db_path:path}")
async def api_post(db_path:str, request: Request):
    params = str(request.query_params)
    if len(params) > 0: params = '?' + params
    url = f'{dest}{request.url.path}{params}'
    body = await request.body()
    ret = requests.post(url, data=body)
    util.debug(f"POST {url} body: {body} ret_status: {ret.status_code} text: {ret.text}")

    if ret.status_code >= 200 and ret.status_code <= 300 and len(body) > 1:
        deploy.kube_create(db_path, body)
            
    return ret.text

@app.delete("/v1/cs/info/manage/{db_path:path}")
async def api_delete(db_path:str, request: Request):
    params = str(request.query_params)
    if len(params) > 0: params = '?' + params
    url = f'{dest}{request.url.path}{params}'
    body = await request.body()
    ret = requests.delete(url, data=body)
    util.debug(f"DELETE {url} body: {body} ret_status: {ret.status_code} text: {ret.text}")

    if ret.status_code >= 200 and ret.status_code <= 300:
        deploy.kube_delete(db_path, body)
 
    return ret.text

@app.patch("/v1/cs/info/manage/{db_path:path}")
async def api_patch(db_path:str, request: Request):
    params = str(request.query_params)
    if len(params) > 0: params = '?' + params
    url = f'{dest}{request.url.path}{params}'
    body = await request.body()
    ret = requests.patch(url, data=body)
    util.debug(f"PATCH {url} body: {body} ret_status: {ret.status_code} text: {ret.text}")

    if ret.status_code >= 200 and ret.status_code <= 300 and len(body) > 1:
        deploy.kube_create(db_path, body)

    return ret.text
