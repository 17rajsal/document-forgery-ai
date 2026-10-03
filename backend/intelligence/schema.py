"""Stable public v1 response models. Coordinates are rendered-page pixels."""
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

Confidence = Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]
BBox = tuple[int, int, int, int]
Status = Literal['supported', 'partially_supported', 'conflicting', 'not_corroborated', 'unable_to_verify']


class Model(BaseModel):
    model_config = ConfigDict(extra='forbid')


class Located(Model):
    page: int = Field(ge=1)
    bbox: BBox | None = None
    confidence: Confidence

    @model_validator(mode='after')
    def ordered_box(self):
        if self.bbox:
            x1, y1, x2, y2 = self.bbox
            if min(self.bbox) < 0 or x2 <= x1 or y2 <= y1:
                raise ValueError('bbox must be nonnegative with positive area')
        return self


class Document(Model):
    id: str
    filename: str
    pages: int = Field(ge=1)


class Assessment(Model):
    level: Literal['LOW', 'MODERATE', 'HIGH']
    summary: str
    confidence: Confidence


class Finding(Located):
    type: str
    explanation: str


class SensitiveField(Located):
    type: str
    value: str
    concern: str = ''


class Evidence(Model):
    source_url: str
    title: str
    retrieved_at: str
    excerpt: str
    entity: str
    source_quality: Literal['authoritative', 'public', 'unassessed'] = 'unassessed'
    relation: Status


class Claim(Located):
    text: str
    category: str
    extracted_entity: str | None = None
    verification_status: Status = 'unable_to_verify'
    evidence: list[Evidence] = Field(default_factory=list)


class Destination(Located):
    value: str
    domain: str | None = None
    payment_identifier: str | None = None
    concerns: list[str] = Field(default_factory=list)


class Identity(Model):
    type: str
    value: str
    page: int = Field(ge=1)
    inconsistencies: list[str] = Field(default_factory=list)


class Explanation(Model):
    en: str
    hi: str


class Analysis(Model):
    schema_version: Literal['1.0'] = '1.0'
    document: Document
    assessment: Assessment
    forensics: list[Finding] = Field(default_factory=list)
    sensitive_fields: list[SensitiveField] = Field(default_factory=list)
    claims: list[Claim] = Field(default_factory=list)
    qr_codes: list[Destination] = Field(default_factory=list)
    urls: list[Destination] = Field(default_factory=list)
    identities: list[Identity] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    safe_actions: list[str] = Field(default_factory=list)
    simple_explanation: Explanation
    technical_details: dict = Field(default_factory=dict)
