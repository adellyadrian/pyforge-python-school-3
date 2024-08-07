from fastapi import FastAPI, HTTPException, status, UploadFile, File
from models import Molecule
from rdkit import Chem
import json
from os import getenv


app = FastAPI()

mol_db = []

@app.get("/")
def get_server():
    return {"server_id": getenv("SERVER_ID", "1")}

@app.post("/molecules", status_code=status.HTTP_201_CREATED, tags=["Molecules"], response_description="Molecule added successfully")
def add_molecule(molecule: Molecule):
    for mol in mol_db:
        if mol["mol_id"] == molecule.mol_id:
            raise HTTPException(status_code=400, detail="Molecule with this ID already exists")
    if not Chem.MolFromSmiles(molecule.name):
            raise HTTPException(status_code=400, detail=f"Invalid SMILES: {molecule.name}")
    mol_db.append(molecule)
    return molecule

@app.get("/molecules", tags=["Molecules"], status_code=status.HTTP_200_OK, response_description="List of all molecules")
def retrieve_molecules():
    return mol_db

@app.get("/molecules/{item_id}", tags=["Molecules"], status_code=status.HTTP_200_OK, response_description="Get molecule by ID")
def get_mol_by_id(item_id: int):
    for molecule in mol_db:
        if molecule["mol_id"] == item_id:
            return molecule
    raise HTTPException(status_code=404, detail="Molecule not found")

@app.put("/molecules/{mol_id}", status_code=status.HTTP_200_OK, tags=["Molecules"], response_description="Update molecule by ID")
def update_mol(mol_id: int, updated_mol: Molecule):
    for index, molecule in enumerate(mol_db):
        if molecule["mol_id"] == mol_id:
            if not Chem.MolFromSmiles(updated_mol.name):
                raise HTTPException(status_code=400, detail=f"Invalid SMILES: {updated_mol.name}")
            mol_db[index] = updated_mol.dict()
            return updated_mol.dict()
    raise HTTPException(status_code=404, detail="Mol is not found")

@app.delete("/molecules/{mol_id}", status_code=status.HTTP_200_OK, tags=["Molecules"], response_description="Delete molecule by ID")
def delete_mol(mol_id: int):
    for index, molecule in enumerate(mol_db):
        if molecule["mol_id"] == mol_id:
            deleted_mol = mol_db.pop(index)
            return deleted_mol
    raise HTTPException(status_code=404, detail="Mol is not found")

@app.get("/substructure_search/", tags=["Molecules"], status_code=status.HTTP_200_OK, response_description="Search for molecules with a specific substructure")
def substructure_search(substructure_name: str):
    if not substructure_name:
        raise HTTPException(status_code=400, detail="Invalid substructure SMILES")
    substructure_mol = Chem.MolFromSmiles(substructure_name)
    if substructure_mol is None:
        raise HTTPException(status_code=400, detail="Invalid substructure SMILES")
    matches = []
    for molecule in mol_db:
        each_mol = Chem.MolFromSmiles(molecule["name"])
        if each_mol is None:
            print(f"Invalid SMILES: {molecule['name']}")
            continue
        if each_mol and each_mol.HasSubstructMatch(substructure_mol):
            matches.append(molecule)
    return {"molecules": matches}

# In this function, it is assumed to attach a json file, which should include a list of moleculesn with the mol_id and name fields
@app.post("/upload_file/", status_code=status.HTTP_201_CREATED, tags=["File Upload"], response_description="File uploaded and molecules parsed successfully")
async def create_upload_file(file: UploadFile = File(...)):
    content = file.file.read().decode("utf-8")
    try:
        molecules = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")

    for molecule in molecules:
        if not {"mol_id", "name"} <= molecule.keys():
            raise HTTPException(status_code=400, detail="Invalid molecule format")
        if not Chem.MolFromSmiles(molecule["name"]):
            raise HTTPException(status_code=400, detail=f"Invalid SMILES: {molecule['name']}")
        mol_db.append(molecule)

    return {"message": "File uploaded and molecules parsed successfully", "num_molecules": len(molecules)}


if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)