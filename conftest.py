import pytest
import requests
import ast

def openAndGive(fileName):
    responseStr = open(fileName, "r", encoding='utf-8').read()
    responseDict = ast.literal_eval(responseStr)
    return responseDict

@pytest.fixture(autouse=True)
def disable_network_calls(monkeypatch):
    def stunted_get():
        raise RuntimeError("Network access not allowed during testing!")
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: stunted_get())

@pytest.fixture
def goodOrder1Data():
    return openAndGive("dummiesFolder/dummyOrder1.txt")


