from fastapi import FastAPI, HTTPException, status, UploadFile, File
from models import Molecule
from rdkit import Chem
import json


app = FastAPI()

mol_db = []

@app.get("/")
def home_page():
    return "Here you can get, create, update, delete, search molecules and upload a molecule file"

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
            mol_db[index] = updated_mol.dict()
            return updated_mol.dict()
        raise HTTPException(status_code=404, detail="Mol is not found")
    if not Chem.MolFromSmiles(molecule.name):
            raise HTTPException(status_code=400, detail=f"Invalid SMILES: {molecule.name}")
    

@app.delete("/molecules/{mol_id}", status_code=status.HTTP_200_OK, tags=["Molecules"], response_description="Delete molecule by ID")
def delete_mol(mol_id: int):
    for index, molecule in enumerate(mol_db):
        if molecule["mol_id"] == mol_id:
            deleted_mol = mol_db.pop(index)
            return deleted_mol
    raise HTTPException(status_code=404, detail="Mol is not found")

@app.get("/substructure_search/", tags=["Molecules"], status_code=status.HTTP_200_OK, response_description="Search for molecules with a specific substructure")
def substructure_search(substructure_name: str):
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
def create_upload_file(file: UploadFile = File(...)):
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
