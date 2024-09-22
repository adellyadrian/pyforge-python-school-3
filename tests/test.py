import requests

ENDPOINT = "http://localhost:8000"
SUBSTRUCTURE_NAME = "C"
LIMIT = 100


def upload_molecules_json(filename='molecules.json'):
    """Helper function to upload a molecules JSON file."""
    with open(filename, 'rb') as file:
        files = {'file': ('molecules.json', file, 'application/json')}
        response = requests.post(ENDPOINT + "/upload_file/", files=files)
    return response


def test_upload_file_invalid_json():
    """Test uploading an invalid JSON file."""
    files = {
        'file': (
            'molecules.json',
            '{"mol_id": 5, "name": "C1=CC=CC=C1"',
            'application/json'
        )
    }
    response = requests.post(ENDPOINT + "/upload_file/", files=files)
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid JSON file"}


def test_upload_file_success():
    """Test successful file upload."""
    response = upload_molecules_json()
    assert response.status_code == 201
    assert response.json() == {
        "message": "File uploaded and molecules parsed successfully",
        "num_molecules": 10
    }


def test_get_server():
    """Test to check if the server is up and running."""
    response = requests.get(ENDPOINT)
    assert response.status_code == 200
    assert "server_id" in response.json()


def test_get_molecule_by_id():
    response = requests.get(ENDPOINT + "/molecules/4")
    assert response.status_code == 200
    assert response.json() == {"id": 4, "name": "CNC"}


def test_update_molecule():
    response = requests.put(
        ENDPOINT + "/molecules/2",
        params={"name": "CNO"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Molecule updated successfully"}


def test_delete_molecule():
    response = requests.delete(ENDPOINT + "/molecules/7")
    assert response.status_code == 200
    assert response.json() == {"message": "The molecule with id 7 is deleted!"}
