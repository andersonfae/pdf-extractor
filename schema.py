from pydantic import BaseModel

class InvoiceData(BaseModel):
    invoice_number: str
    date: str
    total_amount: float
