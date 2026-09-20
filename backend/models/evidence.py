from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional


class SourceType(str, Enum):
    OFFICIAL = "OFFICIAL"                
    FEDERAL_REGULATOR = "FEDERAL_REGULATOR"  
    STATE_GOVERNMENT = "STATE_GOVERNMENT"    
    OPERATOR = "OPERATOR"               
    COMMUNITY = "COMMUNITY"              
    NEWS = "NEWS"                       
    RESEARCH = "RESEARCH"             
    SATELLITE_CONTEXT = "SATELLITE_CONTEXT"  


class ClaimField(str, Enum):
    OCCURRENCE = "OCCURRENCE"
    LOCATION = "LOCATION"
    DATE = "DATE"
    CAUSE = "CAUSE"
    VOLUME = "VOLUME"


class FieldStatus(str, Enum):
    CORROBORATED = "CORROBORATED"         
    SUPPORTED = "SUPPORTED"               
    CONTESTED = "CONTESTED"                
    CONFLICTING = "CONFLICTING"            
    UNRESOLVED = "UNRESOLVED"              
    NOT_ESTABLISHED = "NOT_ESTABLISHED"   
    NOT_ENOUGH_EVIDENCE = "NOT_ENOUGH_EVIDENCE"


@dataclass(frozen=True)
class Source:
    id: str
    name: str
    type: SourceType
    url: Optional[str] = None
    attributed_to: Optional[str] = None


@dataclass(frozen=True)
class Claim:
    id: str
    incident_id: str
    field: ClaimField
    raw_value: str
    source_id: str
    event_date: Optional[date] = None       
    publication_date: Optional[date] = None  
    excerpt: Optional[str] = None            
    derived_from_claim_id: Optional[str] = None


@dataclass
class ValueGroup:
    """One cluster of claims that agree with each other after normalization."""
    normalized_value: str
    display_value: str
    claim_ids: list[str] = field(default_factory=list)
    source_ids: set[str] = field(default_factory=set)  
    independent_source_ids: set[str] = field(default_factory=set)


@dataclass
class FieldAssessment:
    field: ClaimField
    status: FieldStatus
    groups: list[ValueGroup] = field(default_factory=list)
    contributing_claim_ids: list[str] = field(default_factory=list)
    note: str = ""
    reason: str = ""


@dataclass
class IncidentAssessment:
    incident_id: str
    fields: dict[ClaimField, FieldAssessment]
    summary: str
