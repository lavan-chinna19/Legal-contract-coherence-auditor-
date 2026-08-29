import pytest
from src.segmentation.factory import get_segmenter
from src.segmentation.rule_based import RuleBasedSegmenter
from src.segmentation.bio_tagger import BIOTaggerSegmenter
from src.config import ClauseRecord

def test_factory_v1():
    seg = get_segmenter("v1")
    assert isinstance(seg, RuleBasedSegmenter)

def test_factory_v2():
    seg = get_segmenter("v2")
    assert isinstance(seg, BIOTaggerSegmenter)

def test_factory_invalid():
    with pytest.raises(ValueError):
        get_segmenter("invalid_type")

def test_rule_based_numbered_clauses():
    text = "1. First clause.\n2. Second clause."
    seg = get_segmenter("v1")
    clauses = seg.segment(text, "doc1")
    
    assert len(clauses) == 2
    assert clauses[0].text == "1. First clause."
    assert clauses[1].text == "2. Second clause."
    assert clauses[0].char_start == 0
    assert clauses[1].char_start == 17

def test_rule_based_nested_numbering():
    text = "1.1 First nested.\n1.2 Second nested."
    seg = get_segmenter("v1")
    clauses = seg.segment(text, "doc1")
    
    assert len(clauses) == 2
    assert clauses[0].text == "1.1 First nested."
    assert clauses[1].text == "1.2 Second nested."

def test_rule_based_headings():
    text = "ARTICLE I\nThis is the first article.\nARTICLE II\nThis is the second."
    seg = get_segmenter("v1")
    clauses = seg.segment(text, "doc1")
    
    assert len(clauses) == 2
    assert "ARTICLE I" in clauses[0].text
    assert "ARTICLE II" in clauses[1].text

def test_rule_based_preamble():
    text = "This contract is made between A and B.\n1. Definitions."
    seg = get_segmenter("v1")
    clauses = seg.segment(text, "doc1")
    
    assert len(clauses) == 2
    assert clauses[0].text == "This contract is made between A and B."
    assert clauses[1].text == "1. Definitions."
    
def test_bio_tagger_fallback():
    # V2 might have different logic, but shouldn't crash
    text = "This is a sentence. 1. This is a clause."
    seg = get_segmenter("v2")
    clauses = seg.segment(text, "doc1")
    assert isinstance(clauses, list)
    if clauses:
        assert isinstance(clauses[0], ClauseRecord)
