"""
Comprehensive HSN (Harmonized System of Nomenclature) & SAC (Services Accounting Code) Directory
Enables instant natural language matching for goods and services to exact tariff codes and GST slab rates.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class HSNCodeEntry:
    code: str
    code_type: str  # "HSN" for Goods, "SAC" for Services
    description: str
    category: str
    gst_rate: float
    itc_eligible: bool
    blocked_reason: Optional[str] = None
    keywords: List[str] = None


HSN_SAC_MASTER: List[HSNCodeEntry] = [
    # ---------------- ELECTRONICS & COMPUTERS ----------------
    HSNCodeEntry(
        code="8471",
        code_type="HSN",
        description="Automatic data processing machines, computers, laptops, microcomputers, CPU, optical readers",
        category="Computers & Hardware",
        gst_rate=18.0,
        itc_eligible=True,
        keywords=["laptop", "computer", "pc", "desktop", "server", "macbook", "hard drive", "ssd", "ram", "processor"]
    ),
    HSNCodeEntry(
        code="84716040",
        code_type="HSN",
        description="Keyboard, mouse, graphic tablets and computer input peripherals",
        category="Computer Peripherals",
        gst_rate=18.0,
        itc_eligible=True,
        keywords=["keyboard", "mouse", "wireless mouse", "trackpad", "webcam", "stylus", "input device"]
    ),
    HSNCodeEntry(
        code="8528",
        code_type="HSN",
        description="Monitors, projectors, television receivers, gaming screens",
        category="Monitors & Displays",
        gst_rate=18.0,
        itc_eligible=True,
        keywords=["monitor", "screen", "display", "gaming monitor", "projector", "led screen"]
    ),
    HSNCodeEntry(
        code="8517",
        code_type="HSN",
        description="Telephone sets, smartphones, cellular networks, routers, modems, networking switches",
        category="Telecommunications",
        gst_rate=18.0,
        itc_eligible=True,
        keywords=["mobile", "phone", "smartphone", "iphone", "android", "router", "modem", "wifi", "switch"]
    ),
    HSNCodeEntry(
        code="8443",
        code_type="HSN",
        description="Printing machinery, multi-function printers, laser printers, copiers and fax machines",
        category="Office Machinery",
        gst_rate=18.0,
        itc_eligible=True,
        keywords=["printer", "photocopier", "laser printer", "scanner", "xerox machine", "cartridge"]
    ),
    HSNCodeEntry(
        code="8525",
        code_type="HSN",
        description="Transmission apparatus, digital cameras, CCTV cameras, video recording apparatus",
        category="Cameras & Surveillance",
        gst_rate=18.0,
        itc_eligible=True,
        keywords=["cctv", "camera", "security camera", "dslr", "web camera", "surveillance"]
    ),

    # ---------------- SERVICES (SAC CODES) ----------------
    HSNCodeEntry(
        code="998313",
        code_type="SAC",
        description="Information technology (IT) systems design, architecture and development services",
        category="IT & Software",
        gst_rate=18.0,
        itc_eligible=True,
        keywords=["software", "it consulting", "coding", "system design", "app development", "backend", "cloud"]
    ),
    HSNCodeEntry(
        code="998314",
        code_type="SAC",
        description="Internet telecommunication and website hosting, maintenance and UI/UX design services",
        category="Web & Digital Services",
        gst_rate=18.0,
        itc_eligible=True,
        keywords=["website", "web design", "hosting", "domain", "seo", "ui", "ux", "frontend", "portal development"]
    ),
    HSNCodeEntry(
        code="998221",
        code_type="SAC",
        description="Accounting, financial auditing, tax compliance and bookkeeping services by professionals",
        category="Accounting & Tax",
        gst_rate=18.0,
        itc_eligible=True,
        keywords=["accounting", "audit", "tax filing", "ca fees", "bookkeeping", "gst return", "financial consultancy"]
    ),
    HSNCodeEntry(
        code="998211",
        code_type="SAC",
        description="Legal advisory, representation and litigation services provided by advocates or law firms (RCM Sec 9(3))",
        category="Legal Services",
        gst_rate=18.0,
        itc_eligible=True,
        blocked_reason="Payable under Reverse Charge Mechanism (RCM) by business recipient.",
        keywords=["legal", "lawyer", "advocate", "court", "attorney", "arbitration", "legal consulting"]
    ),
    HSNCodeEntry(
        code="996511",
        code_type="SAC",
        description="Road transport services of goods by Goods Transport Agency (GTA) with consignment note",
        category="Logistics & Freight",
        gst_rate=5.0,
        itc_eligible=True,
        keywords=["transport", "gta", "freight", "trucking", "courier", "logistics", "cargo", "delivery"]
    ),
    HSNCodeEntry(
        code="997212",
        code_type="SAC",
        description="Renting or leasing of commercial immovable property (office spaces, warehouses, retail shops)",
        category="Commercial Rent",
        gst_rate=18.0,
        itc_eligible=True,
        keywords=["office rent", "commercial rent", "warehouse lease", "coworking", "shop rent", "premises"]
    ),
    HSNCodeEntry(
        code="996331",
        code_type="SAC",
        description="Restaurant, food and beverage services (Non-hotel / Standalone or hotel with room tariff < ₹7,500)",
        category="Food & Hospitality",
        gst_rate=5.0,
        itc_eligible=False,
        blocked_reason="Blocked under Section 17(5)(b)(i): Food and beverages, restaurant dining.",
        keywords=["restaurant", "food", "dining", "meal", "cafe", "coffee", "lunch", "dinner", "swiggy", "zomato"]
    ),
    HSNCodeEntry(
        code="996332",
        code_type="SAC",
        description="Outdoor catering, event banquet and party catering services",
        category="Outdoor Catering",
        gst_rate=18.0,
        itc_eligible=False,
        blocked_reason="Blocked under Section 17(5)(b)(i): Outdoor catering services.",
        keywords=["catering", "outdoor catering", "event buffet", "banquet dinner", "party food"]
    ),
    HSNCodeEntry(
        code="996311",
        code_type="SAC",
        description="Room accommodation in hotels, guest houses, clubs (Declared room tariff ₹1,000 to ₹7,500)",
        category="Hotel Accommodation",
        gst_rate=12.0,
        itc_eligible=True,
        keywords=["hotel", "room", "stay", "guest house", "resort", "lodging", "oyo"]
    ),

    # ---------------- FURNITURE, FIXTURES & OFFICE GOODS ----------------
    HSNCodeEntry(
        code="9403",
        code_type="HSN",
        description="Office furniture, wooden desks, workstations, metal cabinets, ergonomic office chairs",
        category="Office Furniture",
        gst_rate=18.0,
        itc_eligible=True,
        keywords=["furniture", "desk", "table", "chair", "office chair", "workstation", "cabinet", "shelf"]
    ),
    HSNCodeEntry(
        code="4820",
        code_type="HSN",
        description="Registers, account books, notebooks, receipt books, order books, stationery pads",
        category="Stationery",
        gst_rate=12.0,
        itc_eligible=True,
        keywords=["notebook", "diary", "register", "stationery", "paper pad", "folder"]
    ),
    HSNCodeEntry(
        code="4802",
        code_type="HSN",
        description="Uncoated printing and writing paper, A4 copier paper reams, office stationery paper",
        category="Paper Products",
        gst_rate=12.0,
        itc_eligible=True,
        keywords=["a4 paper", "copier paper", "printing paper", "xerox paper", "ream"]
    ),

    # ---------------- AUTOMOBILES & MOTOR VEHICLES ----------------
    HSNCodeEntry(
        code="8703",
        code_type="HSN",
        description="Motor cars and other motor vehicles principally designed for the transport of persons (<= 13 seats)",
        category="Motor Vehicles",
        gst_rate=28.0,
        itc_eligible=False,
        blocked_reason="Blocked under Section 17(5)(a): Passenger motor vehicles with seating capacity <= 13 seats.",
        keywords=["car", "motor car", "suv", "sedan", "automobile", "executive vehicle"]
    ),
    HSNCodeEntry(
        code="8704",
        code_type="HSN",
        description="Commercial motor vehicles for the transport of goods (Trucks, Lorries, Delivery Vans)",
        category="Commercial Cargo Vehicles",
        gst_rate=28.0,
        itc_eligible=True,
        keywords=["truck", "lorry", "delivery van", "cargo vehicle", "goods vehicle", "tempo"]
    ),

    # ---------------- INDUSTRIAL & CONSTRUCTION ----------------
    HSNCodeEntry(
        code="2523",
        code_type="HSN",
        description="Portland cement, aluminous cement, slag cement and similar hydraulic cements",
        category="Building Materials",
        gst_rate=28.0,
        itc_eligible=True,
        keywords=["cement", "portland cement", "clinker", "building cement", "concrete mix"]
    ),
    HSNCodeEntry(
        code="7214",
        code_type="HSN",
        description="TMT steel bars, rods of iron or non-alloy steel, construction rebar",
        category="Steel & Metals",
        gst_rate=18.0,
        itc_eligible=True,
        keywords=["steel", "tmt bar", "iron rod", "rebar", "metal beam", "steel rod"]
    ),

    # ---------------- APPAREL & TEXTILES ----------------
    HSNCodeEntry(
        code="6109",
        code_type="HSN",
        description="T-shirts, singlets and other vests, knitted or crocheted (Value > ₹1,000)",
        category="Apparel",
        gst_rate=12.0,
        itc_eligible=True,
        keywords=["t-shirt", "shirt", "clothing", "apparel", "garment", "uniform"]
    ),
    HSNCodeEntry(
        code="6403",
        code_type="HSN",
        description="Footwear with outer soles of rubber, plastics, leather (Value > ₹1,000)",
        category="Footwear",
        gst_rate=18.0,
        itc_eligible=True,
        keywords=["shoes", "footwear", "boots", "sneakers", "leather shoes", "safety shoes"]
    ),
]


def find_hsn_or_sac(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """
    Searches the HSN/SAC master directory using natural language query matching.
    Returns matched entries with code, GST rate, description, and ITC eligibility.
    """
    q_tokens = [t.lower().strip() for t in query.split() if len(t.strip()) > 1]
    if not q_tokens:
        return []

    scored_results = []
    for entry in HSN_SAC_MASTER:
        score = 0
        search_blob = f"{entry.code} {entry.description} {entry.category} {' '.join(entry.keywords or [])}".lower()
        
        # Exact code match
        if any(t == entry.code.lower() for t in q_tokens):
            score += 15.0
            
        # Keyword matches
        for kw in (entry.keywords or []):
            if any(t in kw or kw in t for t in q_tokens):
                score += 5.0

        # General text overlap
        for token in q_tokens:
            if token in search_blob:
                score += 2.0

        if score > 0:
            scored_results.append((entry, score))

    scored_results.sort(key=lambda x: x[1], reverse=True)
    
    output = []
    for entry, sc in scored_results[:top_k]:
        output.append({
            "code": entry.code,
            "code_type": entry.code_type,
            "description": entry.description,
            "category": entry.category,
            "gst_rate": entry.gst_rate,
            "itc_eligible": entry.itc_eligible,
            "blocked_reason": entry.blocked_reason,
            "score": round(sc, 2)
        })

    return output
