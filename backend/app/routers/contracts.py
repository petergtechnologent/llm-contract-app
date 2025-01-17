from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import openai

from ..database import get_db
from .. import models, schemas
from ..config import OPENAI_API_KEY

router = APIRouter()

@router.get("/contracts", response_model=List[schemas.ContractResponse])
def list_contracts(db: Session = Depends(get_db)):
    """
    GET /api/contracts
    Return all contracts in the database.
    """
    return db.query(models.Contract).all()

@router.post("/contracts", response_model=schemas.ContractResponse)
async def create_contract(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    POST /api/contracts
    Handle a file upload, store text in `contracts` table.
    """
    contents = await file.read()
    text_str = contents.decode("utf-8", errors="ignore")

    contract = models.Contract(
        file_name=file.filename,
        original_text=text_str,
    )
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract

@router.get("/contracts/{contract_id}", response_model=schemas.ContractDetailResponse)
def get_contract_details(contract_id: int, db: Session = Depends(get_db)):
    """
    GET /api/contracts/{contract_id}
    Retrieve a single contract and its revisions.
    """
    contract = db.query(models.Contract).filter(models.Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract

@router.post("/contracts/{contract_id}/review", response_model=schemas.ContractRevisionResponse)
def review_contract(
    contract_id: int,
    review_request: schemas.ReviewRequest,  
    db: Session = Depends(get_db)
):
    """
    POST /api/contracts/{contract_id}/review
    Generate a revised contract via OpenAI, store in `contract_revisions`.
    """
    instructions = review_request.instructions or "No additional instructions provided."

    contract = db.query(models.Contract).filter(models.Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    if not OPENAI_API_KEY:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")

    openai.api_key = OPENAI_API_KEY
    # Build a user prompt for a ChatCompletions call
    prompt = f"""
    ---INSTRUCTIONS---
    Please propose a revised version of a contract for greater clarity and to match the format of my example contract.
    Ensure the revised contract meets legal standards.

    Add the following instructions or legal guidelines:
    {instructions}

    ---CONTRACT TEXT---:
    {contract.original_text}

    ---EXAMPLE CONTRACT---
    SALES AGREEMENT

    This Sales Agreement ("Agreement") is made and entered into on this 14th day of January, 2025, by and between:

    Party A: ABC Corporation, a company organized under the laws of the State of Delaware, with its principal place of business located at 123 Business Rd., Wilmington, DE 19801 ("Seller"),

    and

    Party B: XYZ Industries, a corporation organized under the laws of the State of California, with its principal place of business located at 456 Industry Ave., San Francisco, CA 94107 ("Buyer").

    WHEREAS, Seller is engaged in the business of manufacturing and selling high-quality electronic devices, and Buyer desires to purchase such devices under the terms set forth herein.

    NOW, THEREFORE, in consideration of the mutual covenants and promises contained herein, the parties agree as follows:

    1. **Products.** Seller agrees to sell, and Buyer agrees to purchase, the electronic devices described in Exhibit A attached hereto ("Products"), subject to the terms and conditions of this Agreement.

    2. **Purchase Price.** The total purchase price for the Products shall be as set forth in Exhibit B. Payment shall be made in U.S. dollars via wire transfer within thirty (30) days of the date of invoice.

    3. **Delivery.** Seller shall deliver the Products to Buyer’s facility located at 456 Industry Ave., San Francisco, CA 94107, on or before March 31, 2025. Risk of loss shall transfer to Buyer upon delivery.

    4. **Warranties.** Seller warrants that the Products shall conform to the specifications set forth in Exhibit A and be free from defects in material and workmanship for a period of one (1) year from the date of delivery. 

    5. **Inspection and Acceptance.** Buyer shall inspect the Products upon delivery and notify Seller in writing of any non-conformity or defect within ten (10) business days. Failure to notify Seller within this period shall constitute acceptance of the Products.

    6. **Limitation of Liability.** In no event shall Seller be liable for any indirect, incidental, or consequential damages arising out of or in connection with this Agreement. Seller's total liability shall not exceed the purchase price of the Products under this Agreement.

    7. **Force Majeure.** Neither party shall be liable for any delay or failure to perform its obligations under this Agreement due to causes beyond its reasonable control, including but not limited to acts of God, war, or government regulation.

    8. **Governing Law.** This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware without regard to its conflict of law principles.

    9. **Entire Agreement.** This Agreement constitutes the entire agreement between the parties and supersedes all prior or contemporaneous understandings, representations, or agreements, whether written or oral.

    10. **Amendments.** Any amendments or modifications of this Agreement must be in writing and signed by authorized representatives of both parties.

    IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.

    ___________________________________
    ABC Corporation (Seller)
    By: _______________________________
    Name: Jane Smith
    Title: Chief Executive Officer

    ___________________________________
    XYZ Industries (Buyer)
    By: _______________________________
    Name: John Doe
    Title: President
    """
    # Build messages for a ChatCompletion call
    messages = [
        {"role": "system", "content": "You are a helpful legal assistant who specializes in contract editing."},
        {
            "role": "user",
            "content": prompt
        }
    ]
    print("DEBUG print var = ", prompt)
    try:
        print("DEBUG: Passing instructions =", instructions)
        response = openai.ChatCompletion.create(
            model="gpt-4o",  
            messages=messages,
            max_tokens=4096,
            temperature=0.2,
        )
        print("DEBUG: Raw OpenAI response:", response)
        revised_text = response.choices[0].message.content
        print("DEBUG: revised_text = ", revised_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    revision = models.ContractRevision(
        contract_id=contract.id,
        revision_text=revised_text,
        revision_notes="Auto-generated by OpenAI"
    )
    db.add(revision)
    db.commit()
    db.refresh(revision)
    return revision

@router.get("/contracts/{contract_id}/download")
def download_contract(
    contract_id: int,
    version: Optional[str] = "original",
    db: Session = Depends(get_db)
):
    """
    GET /api/contracts/{contract_id}/download?version=original|revised
    Return the selected version's text. 
    """
    contract = db.query(models.Contract).filter(models.Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    if version == "original":
        content = contract.original_text
        filename = f"{contract.file_name or 'contract'}-original.txt"
    else:
        revision = (
            db.query(models.ContractRevision)
            .filter(models.ContractRevision.contract_id == contract_id)
            .order_by(models.ContractRevision.created_at.desc())
            .first()
        )
        if not revision:
            raise HTTPException(status_code=404, detail="No revisions found for this contract")
        content = revision.revision_text
        filename = f"{contract.file_name or 'contract'}-revised.txt"

    return {
        "file_name": filename,
        "content": content
    }
