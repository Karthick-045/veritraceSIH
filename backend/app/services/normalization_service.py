import re
from datetime import datetime
from dateutil import parser as date_parser

ABBREVIATION_MAP = {
    r"\binst\b\.?": "institute",
    r"\btech\b\.?": "technology",
    r"\bengg\b\.?": "engineering",
    r"\bcoll\b\.?": "college",
    r"\bdept\b\.?": "department",
    r"\buniv\b\.?": "university",
    r"\bacad\b\.?": "academy",
    r"\bltd\b\.?": "limited",
    r"\bpvt\b\.?": "private",
    r"\bmgmt\b\.?": "management",
}

class NormalizationService:
    @staticmethod
    def normalize_institution_name(name: str) -> str:
        if not name:
            return ""
        s = name.lower()
        # Replace common abbreviations
        for pattern, replacement in ABBREVIATION_MAP.items():
            s = re.sub(pattern, replacement, s, flags=re.IGNORECASE)
        # Remove punctuation except letters and numbers
        s = re.sub(r"[^\w\s]", " ", s)
        # Normalize whitespace
        s = " ".join(s.split())
        return s

    @staticmethod
    def normalize_academic_year(year_str: str) -> str:
        if not year_str:
            return ""
        s = year_str.strip()
        # Match patterns like 2025-26, 2025-2026, 2025/26, 2025/2026
        match = re.search(r"(\d{4})\s*[-/]\s*(\d{2,4})", s)
        if match:
            start_yr = int(match.group(1))
            end_val = match.group(2)
            if len(end_val) == 2:
                end_yr = int(str(start_yr)[:2] + end_val)
            else:
                end_yr = int(end_val)
            return f"{start_yr}-{end_yr}"
        return s

    @staticmethod
    def normalize_date(date_str: str) -> tuple[str | None, bool]:
        """
        Returns (normalized_iso_date, is_ambiguous).
        If ambiguous (e.g. 03/04/2025 where both part1 and part2 <= 12),
        returns (None or partial, True) so it is routed to human review without guessing.
        """
        if not date_str:
            return None, False

        s = date_str.strip()
        
        # Check for numeric pattern like DD/MM/YYYY or MM/DD/YYYY
        num_pattern = re.match(r"^(\d{1,2})[/\-\.](\d{1,2})[/\-](\d{4})$", s)
        if num_pattern:
            p1 = int(num_pattern.group(1))
            p2 = int(num_pattern.group(2))
            yr = int(num_pattern.group(3))
            
            # If both parts <= 12, ambiguous whether MM/DD or DD/MM
            if 1 <= p1 <= 12 and 1 <= p2 <= 12 and p1 != p2:
                return None, True
            
            # If p1 > 12, it must be DD/MM/YYYY
            if p1 > 12:
                day, month = p1, p2
                try:
                    dt = datetime(yr, month, day)
                    return dt.strftime("%Y-%m-%d"), False
                except ValueError:
                    return None, True
            
            # If p2 > 12, it must be MM/DD/YYYY
            if p2 > 12:
                month, day = p1, p2
                try:
                    dt = datetime(yr, month, day)
                    return dt.strftime("%Y-%m-%d"), False
                except ValueError:
                    return None, True

        # Try dateutil parser for textual dates e.g. "15 August 2025" or ISO format "2025-08-15"
        try:
            parsed = date_parser.parse(s, fuzzy=False)
            return parsed.strftime("%Y-%m-%d"), False
        except Exception:
            return None, True

    @staticmethod
    def normalize_field(field_key: str, raw_val: str) -> tuple[str | None, bool]:
        """
        Dispatches to appropriate normalizer based on field_key.
        Returns (normalized_value, is_ambiguous).
        """
        if not raw_val:
            return None, False

        if "institution_name" in field_key or "college_name" in field_key or "applicant" in field_key:
            return NormalizationService.normalize_institution_name(raw_val), False
        elif "academic_year" in field_key:
            return NormalizationService.normalize_academic_year(raw_val), False
        elif "date" in field_key or "valid_until" in field_key or "expiry" in field_key:
            return NormalizationService.normalize_date(raw_val)
        elif "area" in field_key:
            # normalize acreage / sq meters
            m = re.search(r"(\d+(?:\.\d+)?)\s*(acres?|sq(?:\.|\s*)meters?|sq(?:\.|\s*)ft)?", raw_val, re.IGNORECASE)
            if m:
                val = float(m.group(1))
                unit = (m.group(2) or "acres").lower()
                return f"{val:.2f} {unit}", False
            return raw_val.strip(), False
        else:
            return raw_val.strip(), False
