import requests
import pytest
import json

ENDPOINT = "http://localhost:8011"  

def upload_molecules_json():
    files = {'file': ('molecules.json', open('src/molecules.json', 'rb'), 'application/json')}
    response = requests.post(ENDPOINT + "/upload_file/", files=files)
    assert response.status_code == 201
    assert response.json() == {"message": "File uploaded and molecules parsed successfully", "num_molecules": 10}

def test_get_server():
    response = requests.get(ENDPOINT)
    assert response.status_code == 200
    assert "server_id" in response.json()

def test_upload_file_success():
    upload_molecules_json()

def test_get_molecule_by_id():
    response = requests.get(ENDPOINT + "/molecules/4")
    assert response.status_code == 200
    assert response.json() == {"mol_id": 4, "name": "CNC"}

def test_update_molecule():
    response = requests.put(ENDPOINT + "/molecules/2", json={"mol_id": 2, "name": "CNO"})
    assert response.status_code == 200
    assert response.json() == {"mol_id": 2, "name": "CNO"}

def test_delete_molecule():
    response = requests.delete(ENDPOINT + "/molecules/5")
    assert response.status_code == 200
    assert response.json() == {"mol_id": 5, "name": "NNN"}

def test_substructure_search_valid_smiles():
    upload_molecules_json()
    response = requests.get(ENDPOINT + "/substructure_search/", params={"substructure_name": "C"})
    assert response.status_code == 200
    data = response.json()
    assert "molecules" in data
    assert len(data["molecules"]) > 0

def test_substructure_search_invalid_smiles():
    upload_molecules_json()
    response = requests.get(ENDPOINT + "/substructure_search/", params={"substructure_name": "INVALID"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid substructure SMILES"}

def test_substructure_search_empty_smiles():
    upload_molecules_json()
    response = requests.get(ENDPOINT + "/substructure_search/", params={"substructure_name": ""})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid substructure SMILES"}

def test_substructure_search_special_characters():
    upload_molecules_json()
    response = requests.get(ENDPOINT + "/substructure_search/", params={"substructure_name": "CCO$"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid substructure SMILES"}

def test_substructure_search_large_data():
    large_molecule_list = [{"mol_id": i, "name": "CC" * (i % 10)} for i in range(1000)]
    with open('src/large_molecules.json', 'w') as file:
        json.dump(large_molecule_list, file)
    
    with open('src/large_molecules.json', 'rb') as file:
        files = {'file': ('large_molecules.json', file, 'application/json')}
        response = requests.post(ENDPOINT + "/upload_file/", files=files)
        assert response.status_code == 201

    response = requests.get(ENDPOINT + "/substructure_search/", params={"substructure_name": "CC"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["molecules"]) > 0

def test_upload_file_invalid_json():
    files = {'file': ('molecules.json', '{"mol_id": 5, "name": "C1=CC=CC=C1"', 'application/json')}
    response = requests.post(ENDPOINT + "/upload_file/", files=files)
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid JSON file"}


def test_upload_file_invalid_json():
    files = {'file': ('molecules.json', '{"mol_id": 5, "name": "C1=CC=CC=C1"', 'application/json')}
    response = requests.post(ENDPOINT + "/upload_file/", files=files)
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid JSON file"}
