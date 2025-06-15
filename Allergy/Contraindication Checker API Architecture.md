# Allergy/Contraindication Checker API Architecture

## Overview

The Allergy/Contraindication Checker API will provide a service to check if a given drug is contraindicated for a patient with specific allergies or medical conditions. The API will leverage multiple data sources, with openFDA as the primary source for drug information and contraindications, RxNorm for drug name normalization, and a custom database for allergen-to-ingredient mappings.

## API Endpoints

### 1. Drug-Allergy Check Endpoint

**Endpoint:** `/v1/check`

**Method:** POST

**Description:** Checks if a drug is contraindicated for a patient with specific allergies or conditions.

**Request Body:**
```json
{
  "drug": {
    "name": "string",
    "rxcui": "string (optional)",
    "ndc": "string (optional)"
  },
  "patient": {
    "allergies": [
      {
        "name": "string",
        "type": "drug|ingredient|class (optional)",
        "severity": "high|medium|low (optional)"
      }
    ],
    "conditions": [
      {
        "name": "string",
        "status": "active|inactive (optional)"
      }
    ]
  },
  "options": {
    "include_inactive_ingredients": true,
    "include_cross_reactivity": true,
    "include_evidence": true
  }
}
```

**Response Body:**
```json
{
  "drug": {
    "name": "string",
    "rxcui": "string",
    "ndc": "string (if available)",
    "ingredients": [
      {
        "name": "string",
        "type": "active|inactive",
        "rxcui": "string (if available)"
      }
    ]
  },
  "contraindications": [
    {
      "type": "allergy|condition",
      "name": "string",
      "severity": "high|medium|low",
      "description": "string",
      "evidence": {
        "source": "openFDA|custom|inferred",
        "text": "string",
        "url": "string (if available)"
      },
      "recommendation": "string"
    }
  ],
  "warnings": [
    {
      "type": "cross_reactivity|condition_interaction",
      "name": "string",
      "severity": "high|medium|low",
      "description": "string",
      "evidence": {
        "source": "openFDA|custom|inferred",
        "text": "string",
        "url": "string (if available)"
      },
      "recommendation": "string"
    }
  ],
  "safe": true|false,
  "metadata": {
    "sources_checked": ["openFDA", "RxNorm", "custom"],
    "timestamp": "ISO datetime",
    "version": "string"
  }
}
```

### 2. Drug Information Endpoint

**Endpoint:** `/v1/drug/{identifier}`

**Method:** GET

**Parameters:**
- `identifier`: Drug name, RxCUI, or NDC code
- `identifier_type`: "name" (default), "rxcui", or "ndc"

**Description:** Retrieves detailed information about a drug, including ingredients and known contraindications.

**Response Body:**
```json
{
  "drug": {
    "name": "string",
    "rxcui": "string",
    "ndc": "string (if available)",
    "brand_names": ["string"],
    "generic_name": "string",
    "ingredients": [
      {
        "name": "string",
        "type": "active|inactive",
        "rxcui": "string (if available)"
      }
    ],
    "dosage_forms": ["string"]
  },
  "contraindications": [
    {
      "type": "allergy|condition",
      "name": "string",
      "description": "string",
      "source": "openFDA|custom"
    }
  ],
  "warnings": [
    {
      "type": "general|specific",
      "text": "string",
      "source": "openFDA|custom"
    }
  ],
  "metadata": {
    "sources_checked": ["openFDA", "RxNorm", "custom"],
    "timestamp": "ISO datetime",
    "version": "string"
  }
}
```

### 3. Allergy Information Endpoint

**Endpoint:** `/v1/allergy/{name}`

**Method:** GET

**Parameters:**
- `name`: Allergy name or ingredient

**Description:** Retrieves information about an allergy, including related drugs and cross-reactivity.

**Response Body:**
```json
{
  "allergy": {
    "name": "string",
    "normalized_name": "string",
    "type": "drug|ingredient|class"
  },
  "related_ingredients": [
    {
      "name": "string",
      "rxcui": "string (if available)",
      "relationship": "exact|contains|cross_reactive"
    }
  ],
  "related_drugs": [
    {
      "name": "string",
      "rxcui": "string",
      "relationship": "contains|may_contain|cross_reactive"
    }
  ],
  "cross_reactivity": [
    {
      "name": "string",
      "type": "drug|ingredient|class",
      "evidence_level": "high|medium|low",
      "description": "string"
    }
  ],
  "metadata": {
    "sources_checked": ["openFDA", "RxNorm", "custom"],
    "timestamp": "ISO datetime",
    "version": "string"
  }
}
```

### 4. Batch Check Endpoint

**Endpoint:** `/v1/batch/check`

**Method:** POST

**Description:** Checks multiple drugs against a patient's allergies and conditions in a single request.

**Request Body:**
```json
{
  "drugs": [
    {
      "name": "string",
      "rxcui": "string (optional)",
      "ndc": "string (optional)"
    }
  ],
  "patient": {
    "allergies": [
      {
        "name": "string",
        "type": "drug|ingredient|class (optional)",
        "severity": "high|medium|low (optional)"
      }
    ],
    "conditions": [
      {
        "name": "string",
        "status": "active|inactive (optional)"
      }
    ]
  },
  "options": {
    "include_inactive_ingredients": true,
    "include_cross_reactivity": true,
    "include_evidence": true
  }
}
```

**Response Body:**
```json
{
  "results": [
    {
      "drug": {
        "name": "string",
        "rxcui": "string",
        "ndc": "string (if available)"
      },
      "contraindications": [
        {
          "type": "allergy|condition",
          "name": "string",
          "severity": "high|medium|low",
          "description": "string",
          "evidence": {
            "source": "openFDA|custom|inferred",
            "text": "string"
          },
          "recommendation": "string"
        }
      ],
      "warnings": [
        {
          "type": "cross_reactivity|condition_interaction",
          "name": "string",
          "severity": "high|medium|low",
          "description": "string"
        }
      ],
      "safe": true|false
    }
  ],
  "metadata": {
    "sources_checked": ["openFDA", "RxNorm", "custom"],
    "timestamp": "ISO datetime",
    "version": "string"
  }
}
```

## Data Models

### Drug Model

```json
{
  "id": "string (internal)",
  "name": "string",
  "rxcui": "string",
  "ndc": "string (optional)",
  "brand_names": ["string"],
  "generic_name": "string",
  "ingredients": [
    {
      "id": "string (internal)",
      "name": "string",
      "type": "active|inactive",
      "rxcui": "string (optional)"
    }
  ],
  "dosage_forms": ["string"],
  "contraindications": [
    {
      "id": "string (internal)",
      "type": "allergy|condition",
      "name": "string",
      "description": "string",
      "source": "openFDA|custom"
    }
  ],
  "warnings": [
    {
      "id": "string (internal)",
      "type": "general|specific",
      "text": "string",
      "source": "openFDA|custom"
    }
  ],
  "metadata": {
    "last_updated": "ISO datetime",
    "source": "openFDA|custom"
  }
}
```

### Allergy Model

```json
{
  "id": "string (internal)",
  "name": "string",
  "normalized_name": "string",
  "type": "drug|ingredient|class",
  "related_ingredients": [
    {
      "id": "string (internal)",
      "name": "string",
      "rxcui": "string (optional)",
      "relationship": "exact|contains|cross_reactive"
    }
  ],
  "cross_reactivity": [
    {
      "id": "string (internal)",
      "name": "string",
      "type": "drug|ingredient|class",
      "evidence_level": "high|medium|low",
      "description": "string"
    }
  ],
  "metadata": {
    "last_updated": "ISO datetime",
    "source": "custom"
  }
}
```

### Condition Model

```json
{
  "id": "string (internal)",
  "name": "string",
  "normalized_name": "string",
  "contraindicated_drugs": [
    {
      "id": "string (internal)",
      "name": "string",
      "rxcui": "string",
      "evidence_level": "high|medium|low",
      "description": "string"
    }
  ],
  "metadata": {
    "last_updated": "ISO datetime",
    "source": "openFDA|custom"
  }
}
```

## Integration Strategy

### Data Flow

1. **Drug Normalization**:
   - Input drug name is normalized using RxNorm API
   - RxCUI is retrieved for standardized identification
   - Ingredients are extracted from RxNorm relationships

2. **Allergy Matching**:
   - Patient allergies are normalized and matched against:
     - Direct drug matches
     - Active ingredient matches
     - Inactive ingredient matches
     - Cross-reactivity matches

3. **Condition Matching**:
   - Patient conditions are normalized and matched against:
     - Direct contraindication mentions in openFDA
     - Custom condition-drug contraindication database

4. **Response Generation**:
   - Contraindications are compiled with severity levels
   - Evidence is attached from source data
   - Recommendations are generated based on severity
   - Safe/unsafe determination is made based on contraindication severity

### Data Sources Integration

1. **openFDA Integration**:
   - Query drug labels for contraindications and warnings
   - Extract structured information from text using NLP
   - Map to standardized terminology

2. **RxNorm Integration**:
   - Normalize drug names to RxCUI
   - Extract ingredient information
   - Map between brand and generic names

3. **Custom Database**:
   - Map allergens to ingredients
   - Store cross-reactivity information
   - Maintain condition contraindications

## Authentication and Rate Limiting

- API key authentication for all endpoints
- Rate limiting based on subscription tier
- HTTPS required for all communications

## Error Handling

- Standard HTTP status codes
- Detailed error messages with error codes
- Fallback mechanisms when primary data sources are unavailable

## Future Extensions

1. **Enhanced NLP**:
   - Improved extraction of contraindications from unstructured text
   - Better matching of patient conditions to contraindication descriptions

2. **Additional Data Sources**:
   - Integration with DrugBank for more detailed drug information
   - Integration with MedlinePlus for consumer-friendly explanations

3. **Machine Learning**:
   - Prediction of potential allergic reactions based on similar drug structures
   - Severity scoring based on historical data

4. **Personalization**:
   - Patient-specific risk scoring
   - Demographic-based risk adjustments
