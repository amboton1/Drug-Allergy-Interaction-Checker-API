# Allergy/Contraindication Checker API Documentation

## Overview

The Allergy/Contraindication Checker API provides a service to check if a given drug is contraindicated for a patient with specific allergies or medical conditions. This documentation covers the API endpoints, request/response formats, and deployment instructions.

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

## Deployment Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. Clone or download the API code repository
2. Navigate to the project directory
3. Install required dependencies:

```bash
pip install flask flask-cors
```

### Database Setup

The API uses SQLite for data storage. To set up the database:

1. Navigate to the project directory
2. Run the database setup script:

```bash
python database/setup_database.py
```

This will create the database schema and populate it with initial data.

### Running the API

To start the API server:

```bash
python api/app.py
```

By default, the server will run on `http://localhost:5000`.

### Production Deployment

For production deployment, it's recommended to use a WSGI server such as Gunicorn:

1. Install Gunicorn:

```bash
pip install gunicorn
```

2. Run the API with Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 api.app:app
```

## Data Sources

The API uses the following data sources:

1. **Custom Database**: The primary source for drug-allergy relationships and contraindications
2. **openFDA** (future enhancement): For additional drug information and FDA-approved contraindications
3. **RxNorm** (future enhancement): For drug name normalization and ingredient mapping

## Error Handling

The API uses standard HTTP status codes:

- 200: Success
- 400: Bad Request (invalid input)
- 404: Not Found (drug or allergy not found)
- 500: Server Error

Error responses include a JSON body with error details:

```json
{
  "error": "string",
  "message": "string"
}
```

## Rate Limiting

The API implements rate limiting based on API keys. Contact the API provider for key issuance and rate limit details.

## Security Considerations

- All API requests should use HTTPS
- API keys should be kept secure and not shared
- Patient data should be anonymized when possible
- The API does not store patient data beyond the request lifetime

## Future Enhancements

1. Integration with additional data sources:
   - DrugBank for more detailed drug information
   - MedlinePlus for consumer-friendly explanations

2. Enhanced NLP capabilities:
   - Improved extraction of contraindications from unstructured text
   - Better matching of patient conditions to contraindication descriptions

3. Machine learning features:
   - Prediction of potential allergic reactions based on similar drug structures
   - Severity scoring based on historical data

4. Personalization:
   - Patient-specific risk scoring
   - Demographic-based risk adjustments
