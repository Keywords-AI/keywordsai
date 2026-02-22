import pytest
from dify_client import Client, AsyncClient
from respan_exporter_dify import create_client, create_async_client

def test_create_client():
    client = Client(api_key="test-dify-key")
    respan_client = create_client(client=client, api_key="test-respan-key")
    assert respan_client.api_key == "test-respan-key"
    assert respan_client._client == client

def test_create_async_client():
    client = AsyncClient(api_key="test-dify-key")
    respan_client = create_async_client(client=client, api_key="test-respan-key")
    assert respan_client.api_key == "test-respan-key"
    assert respan_client._client == client

def test_create_client_with_dify_key():
    respan_client = create_client(dify_api_key="test-dify-key", api_key="test-respan-key")
    assert respan_client.api_key == "test-respan-key"
    assert respan_client._client.api_key == "test-dify-key"
