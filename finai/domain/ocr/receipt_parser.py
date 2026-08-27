import re
from typing import List, Optional, Tuple
from finai.domain.models.financial_models import ParsedReceipt, ReceiptLineItem


def is_valid_gstin(gstin: str) -> bool:
    """
    Validates 15-character Indian GSTIN format:
    2 digits state code + 5 chars PAN alpha + 4 digits PAN num + 1 char PAN alpha + 1 entity num + 'Z' + 1 checksum char.
    """
    if not gstin or len(gstin) != 15:
        return False
    pattern = r"^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z0-9]{1}Z[A-Z0-9]{1}$"
    return bool(re.match(pattern, gstin.upper()))


def parse_ocr_text(raw_text: str, word_confidences: Optional[List[float]] = None) -> ParsedReceipt:
    """
    Pure domain parser that converts raw Tesseract OCR text into a structured ParsedReceipt.
    Strict implementation of Section 5.1 of FinAI Specification.
    Unit-testable without any image files.
    """
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    if not lines:
        return ParsedReceipt(
            vendor_name="Unknown Vendor",
            total_amount=0.0,
            confidence_score=0.0,
            is_low_confidence=True,
        )

    # Calculate base OCR confidence from Tesseract word confidence scores
    base_confidence = (
        sum(word_confidences) / len(word_confidences) / 100.0 if word_confidences else 0.85
    )

    # 1. Vendor Name Heuristic (first non-empty line)
    vendor_name = lines[0]
    vendor_name = re.sub(r"^[^\w]+|[^\w]+$", "", vendor_name)
    if len(vendor_name) < 2:
        vendor_name = lines[1] if len(lines) > 1 else "Unknown Vendor"

    # 2. Date Regex (Indian formats: DD/MM/YYYY, DD-MM-YY, DD Mon YYYY, YYYY-MM-DD, YYYY/MM/DD)
    date_pattern = r"\b(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}|\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2})\b"
    receipt_date = None
    date_match = re.search(date_pattern, raw_text, re.IGNORECASE)
    if date_match:
        receipt_date = date_match.group(1)

    # 3. GSTIN Regex (15-character Indian GSTIN pattern)
    gstin_pattern = r"\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z0-9]{1}Z[A-Z0-9]{1}\b"
    gstin_match = re.search(gstin_pattern, raw_text)
    gstin = gstin_match.group(0) if gstin_match else None

    # 4. GST Amount & Rate Regex
    gst_amount = None
    gst_match = re.search(
        r"(?:GST|CGST|SGST|IGST|TAX)\s*[\:\=]?\s*(?:Rs\.?|INR|₹)?\s*([\d\.\,]+)",
        raw_text,
        re.IGNORECASE,
    )
    if gst_match:
        try:
            clean_gst = gst_match.group(1).replace(",", "")
            gst_amount = float(clean_gst)
        except ValueError:
            pass

    # 5. Total Amount Regex (Strict Priority: GRAND TOTAL / TOTAL / NET PAYABLE > PAID)
    total_amount = 0.0
    
    # Priority 1: High confidence total keywords
    strict_matches = re.findall(
        r"(?:GRAND TOTAL|NET PAYABLE|TOTAL AMOUNT|TOTAL PAYABLE|FINAL TOTAL)\s*[\:\=]?\s*(?:Rs\.?|INR|₹)?\s*([\d\.\,]+)",
        raw_text,
        re.IGNORECASE,
    )
    
    if not strict_matches:
        # Priority 2: General total keywords
        strict_matches = re.findall(
            r"(?:TOTAL|AMOUNT PAID|PAYABLE)\s*[\:\=]?\s*(?:Rs\.?|INR|₹)?\s*([\d\.\,]+)",
            raw_text,
            re.IGNORECASE,
        )

    if strict_matches:
        try:
            amounts = [float(m.replace(",", "")) for m in strict_matches if m.replace(",", "").replace(".", "").isdigit()]
            if amounts:
                total_amount = amounts[-1]  # Pick last match under header
        except ValueError:
            pass

    # Fallback for Total Amount: look for currency amounts in text
    if total_amount == 0.0:
        currency_matches = re.findall(r"(?:Rs\.?|INR|₹)\s*([\d\.\,]+)", raw_text, re.IGNORECASE)
        if not currency_matches:
            currency_matches = re.findall(r"\b\d+\.\d{2}\b", raw_text)
        
        parsed_nums = []
        for m in currency_matches:
            try:
                val = float(m.replace(",", ""))
                parsed_nums.append(val)
            except ValueError:
                pass
        if parsed_nums:
            total_amount = max(parsed_nums)

    # 6. Line Items Extraction
    line_items: List[ReceiptLineItem] = []
    for line in lines[1:]:
        if re.search(r"(?:TOTAL|TAX|GSTIN|DATE|THANK YOU|WELCOME|INVOICE|SUBTOTAL|CHANGE)", line, re.IGNORECASE):
            continue
        
        item_match = re.match(r"^(.+?)\s+(?:Rs\.?|INR|₹)?\s*([\d\.\,]+)$", line)
        if item_match:
            desc = item_match.group(1).strip()
            try:
                amt = float(item_match.group(2).replace(",", ""))
                if amt > 0 and amt != total_amount:
                    line_items.append(
                        ReceiptLineItem(description=desc, amount=amt, confidence=base_confidence)
                    )
            except ValueError:
                pass

    # Calculate overall confidence score
    confidence_score = base_confidence
    if total_amount == 0.0:
        confidence_score *= 0.5
    if not receipt_date:
        confidence_score *= 0.8
    if not gstin and "gst" in raw_text.lower():
        confidence_score *= 0.9

    confidence_score = round(max(0.1, min(1.0, confidence_score)), 2)
    is_low_confidence = confidence_score < 0.7

    return ParsedReceipt(
        vendor_name=vendor_name,
        receipt_date=receipt_date,
        total_amount=round(total_amount, 2),
        gstin=gstin,
        gst_amount=round(gst_amount, 2) if gst_amount else None,
        line_items=line_items,
        confidence_score=confidence_score,
        is_low_confidence=is_low_confidence,
    )
