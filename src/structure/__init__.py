"""Source-backed structural parsing independent of frozen neural input segmentation."""
from .parser import parse_contract
from .resolver import resolve_references

__all__ = ['parse_contract', 'resolve_references']
