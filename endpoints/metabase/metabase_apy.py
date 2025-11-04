import httpx
import os
import asyncio
from typing import Dict, Any, List
from dotenv import load_dotenv
from sqlalchemy.future import select
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from endpoints.metabase.schemas import RequestionParamers
from sqlalchemy.ext.asyncio import AsyncSession
from endpoints.user_api import get_current_active_user

from manage.database import SessionLocal

router = APIRouter()
load_dotenv()

METABASE_API_URL = os.getenv("METABASE_API_URL")
METABASE_API_KEY = os.getenv("METABASE_API_KEY")



async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session




# Connection pool for reuse
_client: httpx.AsyncClient = None
async def get_async_client() -> httpx.AsyncClient:
    """Get or create async client with connection pool"""
    global _client
    if _client is None:
        # Reuse connections with proper limits
        limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
        _client = httpx.AsyncClient(timeout=300.0, limits=limits)
    return _client

async def close_async_client():
    """Close the async client on shutdown"""
    global _client
    if _client:
        await _client.aclose()
        _client = None

async def make_metabase_request(
    method: str,
    url: str,
    headers: Dict[str, str],
    json_data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Make async HTTP request to Metabase API with connection reuse"""
    client = await get_async_client()
    
    if method.upper() == "GET":
        response = await client.get(url, headers=headers)
    elif method.upper() == "POST":
        response = await client.post(url, headers=headers, json=json_data)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")
    
    response.raise_for_status()
    return response.json()

async def build_request_parameters(id: int, data: List[RequestionParamers]) -> List[Dict[str, Any]]:
    """Build request parameters from filter data"""
    description_url = f"{METABASE_API_URL}/card/{id}"
    headers = {"x-api-key": METABASE_API_KEY}
    
    client = await get_async_client()
    details_response = await client.get(description_url, headers=headers)
    details_response.raise_for_status()
    details_result = details_response.json()
    
    # Build parameters efficiently
    param_map = {param['slug'].upper(): param for param in details_result['parameters']}
    request_queries = []
    
    for query in data:
        param = param_map.get(query.name.upper())
        if param:
            request_queries.append({
                "id": param['id'],
                "type": param['type'],
                "value": [query.value],
                "target": [
                    "dimension",
                    ["template-tag", param['slug']]
                ]
            })
    
    return request_queries

@router.get('/mb_dashbord_details/{id}')
async def get_dashbord_details(id: int):
    """Get dashboard details - fully async, client waits for result"""
    api_url = f"{METABASE_API_URL}/dashboard/{id}"
    headers = {"x-api-key": METABASE_API_KEY}

    try:
        # This runs in background but client waits for result
        result = await make_metabase_request("GET", api_url, headers)
        return result

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Metabase API request timed out")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Metabase API request failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get('/mb_report_question_details/{id}')
async def get_question_details(id: int):
    """Get question details - fully async, client waits for result"""
    api_url = f"{METABASE_API_URL}/card/{id}"
    headers = {"x-api-key": METABASE_API_KEY}

    try:
        result = await make_metabase_request("GET", api_url, headers)
        return { 
            'id': result['id'], 
            'name': result['name'],  
            'parameters': result['parameters'] 
        }

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Metabase API request timed out")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Metabase API request failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post('/mb_report_question_data/{id}')
async def get_question_data(data: List[RequestionParamers], id: int):
    """Get question data with parameters - optimized async version"""
    api_url = f"{METABASE_API_URL}/card/{id}/query"
    description_url = f"{METABASE_API_URL}/card/{id}"
    headers = {"x-api-key": METABASE_API_KEY}

    try:
        client = await get_async_client()
        
        # Run both requests concurrently using asyncio.gather
        details_future = client.get(description_url, headers=headers)
        # Prepare the data request but don't execute yet
        data_future = None
        
        details_response = await details_future
        details_response.raise_for_status()
        details_result = details_response.json()
        
        # Build parameters efficiently
        param_map = {param['slug'].upper(): param for param in details_result['parameters']}
        request_queries = []
        
        for query in data:
            param = param_map.get(query.name.upper())
            if param:
                request_queries.append({
                    "id": param['id'],
                    "type": param['type'],
                    "value": [query.value],
                    "target": [
                        "dimension",
                        ["template-tag", param['slug']]
                    ]
                })
        
        # Execute the data request
        data_response = await client.post(api_url, headers=headers, json={
            "ignore_cache": False,
            "collection_preview": False,
            "parameters": request_queries
        })
        data_response.raise_for_status()
        result = data_response.json()
        
        # Format response
        data_result = result['data']
        data_result['native_form'] = None
        data_result['question'] = { 
            'id': details_result['id'], 
            'name': details_result['name'], 
            'parameters': details_result['parameters'],
            'display': details_result['display'],
            'visualization_settings': details_result['visualization_settings'],
        }

        return data_result
    
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Metabase API request timed out")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Metabase API request failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/mb_report_question_data/{id}/csv")
async def get_question_data_as_csv(data: List[RequestionParamers], id: int):
    """Stream CSV data with filter parameters applied"""
    api_url = f"{METABASE_API_URL}/card/{id}/query/csv"
    headers = {
        "x-api-key": METABASE_API_KEY,
        "Accept": "text/csv",
    }

    try:
        client = await get_async_client()
        
        # Build request parameters from filter data
        request_queries = await build_request_parameters(id, data)
        
        # Make POST request with parameters to get filtered CSV
        response = await client.post(api_url, headers=headers, json={
            "ignore_cache": False,
            "collection_preview": False,
            "parameters": request_queries
        })
        response.raise_for_status()

        # Get question details for filename
        question_details = await get_question_details(id)
        question_name = question_details['name'].replace(' ', '_').lower()
        
        # Use async streaming for large files
        async def async_file_generator():
            yield response.text

        return StreamingResponse(
            async_file_generator(),
            media_type="text/csv; charset=utf-8",
            headers={
                "Content-Disposition": f'attachment; filename="{question_name}_{id}.csv"'
            },
        )

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Metabase API request timed out")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Metabase API request failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/mb_report_question_data/{id}/xlsx")
async def get_question_data_as_xlsx(data: List[RequestionParamers], id: int):
    """Stream XLSX data with filter parameters applied"""
    api_url = f"{METABASE_API_URL}/card/{id}/query/xlsx"
    headers = {
        "x-api-key": METABASE_API_KEY,
        "Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }

    try:
        client = await get_async_client()
        
        # Build request parameters from filter data
        request_queries = await build_request_parameters(id, data)
        
        # Make POST request with parameters to get filtered XLSX
        response = await client.post(api_url, headers=headers, json={
            "ignore_cache": False,
            "collection_preview": False,
            "parameters": request_queries
        })
        response.raise_for_status()

        # Get question details for filename
        question_details = await get_question_details(id)
        question_name = question_details['name'].replace(' ', '_').lower()

        # Use async streaming for binary data
        async def async_binary_generator():
            yield response.content

        return StreamingResponse(
            async_binary_generator(),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={
                "Content-Disposition": f'attachment; filename="{question_name}_{id}.xlsx"'
            },
        )

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Metabase API request timed out")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Metabase API request failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# Add JSON download endpoint
@router.post("/mb_report_question_data/{id}/json")
async def get_question_data_as_json(data: List[RequestionParamers], id: int):
    """Get filtered data as JSON"""
    api_url = f"{METABASE_API_URL}/card/{id}/query"
    headers = {
        "x-api-key": METABASE_API_KEY,
        "Accept": "application/json",
    }

    try:
        client = await get_async_client()
        
        # Build request parameters from filter data
        request_queries = await build_request_parameters(id, data)
        
        # Make POST request with parameters to get filtered JSON
        response = await client.post(api_url, headers=headers, json={
            "ignore_cache": False,
            "collection_preview": False,
            "parameters": request_queries
        })
        response.raise_for_status()
        
        result = response.json()
        
        # Get question details for response
        question_details = await get_question_details(id)
        
        return {
            "question": question_details,
            "filters_applied": data,
            "data": result['data'],
            "row_count": len(result['data']['rows']) if result.get('data') and result['data'].get('rows') else 0
        }

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Metabase API request timed out")
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Metabase API request failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# Add shutdown event to close client
@router.on_event("shutdown")
async def shutdown_event():
    await close_async_client()