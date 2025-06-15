# Data Sources Research for Allergy/Contraindication Checker API

## OpenFDA

### Overview
OpenFDA provides structured data from FDA drug labels, including contraindications and warnings sections. The API allows querying by drug name, ingredients, and other parameters.

### Key Endpoints
- `/drug/label.json` - Main endpoint for drug labeling information
- Search parameters: `search=_exists_:contraindications` to find drugs with contraindication data
- Search parameters: `search=_exists_:warnings` to find drugs with warnings data

### Relevant Fields
- `contraindications` - Contains text describing situations where the drug should not be used
- `warnings` - Contains text describing potential risks and precautions
- `active_ingredient` - Lists active ingredients in the drug
- `inactive_ingredient` - Lists inactive ingredients that could be allergens
- `openfda.brand_name` - Brand name of the drug
- `openfda.generic_name` - Generic name of the drug
- `openfda.substance_name` - Substance names related to the drug

### Advantages
- Official FDA data source
- Structured JSON format
- Regular updates (weekly)
- No authentication required for basic usage
- Contains both prescription and OTC drugs

### Limitations
- Text-based contraindications (not coded)
- Varying levels of detail across different drugs
- No direct mapping between allergens and drugs
- Rate limits on API usage

## MedlinePlus

### Overview
MedlinePlus provides consumer-friendly drug information, including sections on allergies, precautions, and contraindications.

### Relevant Sections
- "Before taking [drug]" section includes allergy information
- "What special precautions should I follow?" section includes contraindications
- Information about drug interactions and conditions that require caution

### Advantages
- Consumer-friendly language
- Comprehensive coverage of common drugs
- Structured format with consistent sections
- Maintained by the National Library of Medicine

### Limitations
- No direct API for programmatic access
- Would require web scraping or manual data extraction
- Text-based information requires NLP processing

## RxNorm

### Overview
RxNorm provides standardized names for clinical drugs and links to many drug vocabularies used in pharmacy management.

### Key APIs
- RxNorm API - Access to RxNorm dataset
- Functions for finding related drugs, ingredients, and brand names

### Relevant Functions
- `findRxcuiByString` - Find RxNorm concept unique identifier by drug name
- `getRxcuiProperties` - Get properties of a drug by its RxCUI
- `findRelatedByType` - Find related drugs by relationship type

### Advantages
- Standardized drug naming
- Hierarchical relationships between drugs
- Links between brand names and generic ingredients
- Maintained by the National Library of Medicine

### Limitations
- Focuses on drug naming and relationships, not contraindications
- No direct allergy information
- Would need to be combined with other data sources

## SNOMED CT

### Overview
SNOMED CT is a comprehensive clinical terminology that includes concepts for allergies, adverse reactions, and contraindications.

### Relevant Concept Hierarchies
- Allergy concepts
- Substance concepts that can be mapped to drugs
- Condition concepts that can be mapped to contraindications

### Advantages
- Structured, coded terminology
- Hierarchical relationships
- International standard

### Limitations
- Requires license for full access
- Complex structure requires significant implementation effort
- No direct API; requires local implementation

## Integration Strategy

The most feasible approach for the MVP is to:

1. Use openFDA as the primary data source for drug information and contraindications
2. Use RxNorm for drug name normalization and ingredient mapping
3. Build a custom database mapping common allergens to drug ingredients
4. Implement logic to check if a patient's allergies match any ingredients in a drug
5. Return structured warnings with severity levels based on the match type

For future enhancements:
- Incorporate SNOMED CT for more structured allergy coding
- Add MedlinePlus data for more consumer-friendly explanations
- Expand the custom mapping database with more allergen-drug relationships
