from app.services.normalization_service import NormalizationService

def test_institution_normalization():
    norm1 = NormalizationService.normalize_institution_name("Delhi Institute of Technology & Management")
    norm2 = NormalizationService.normalize_institution_name("Delhi Inst. of Tech. & Mgmt.")
    assert "institute" in norm1 and "institute" in norm2
    assert "technology" in norm1 and "technology" in norm2

def test_academic_year_normalization():
    assert NormalizationService.normalize_academic_year("2025-26") == "2025-2026"
    assert NormalizationService.normalize_academic_year("2025-2026") == "2025-2026"
    assert NormalizationService.normalize_academic_year("2025/26") == "2025-2026"

def test_unambiguous_date_parsing():
    iso_date, is_ambig = NormalizationService.normalize_date("15/05/2024")
    assert iso_date == "2024-05-15"
    assert is_ambig is False

def test_ambiguous_date_flagging():
    # 03/04/2025 could be 3rd April or 4th March -> must flag ambiguous
    iso_date, is_ambig = NormalizationService.normalize_date("03/04/2025")
    assert is_ambig is True
