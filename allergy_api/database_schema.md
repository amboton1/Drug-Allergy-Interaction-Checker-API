# Database Schema for Allergy/Contraindication Checker API

## Overview

This document outlines the database schema for the Allergy/Contraindication Checker API. The schema is designed to support the MVP functionality while allowing for future expansion.

## Tables

### 1. Drugs

```sql
CREATE TABLE drugs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    rxcui VARCHAR(50),
    ndc VARCHAR(50),
    generic_name VARCHAR(255),
    is_otc BOOLEAN DEFAULT FALSE,
    dosage_form VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_drugs_name ON drugs(name);
CREATE INDEX idx_drugs_rxcui ON drugs(rxcui);
CREATE INDEX idx_drugs_ndc ON drugs(ndc);
```

### 2. Brand Names

```sql
CREATE TABLE brand_names (
    id SERIAL PRIMARY KEY,
    drug_id INTEGER REFERENCES drugs(id),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_brand_names_drug_id ON brand_names(drug_id);
CREATE INDEX idx_brand_names_name ON brand_names(name);
```

### 3. Ingredients

```sql
CREATE TABLE ingredients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    rxcui VARCHAR(50),
    normalized_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ingredients_name ON ingredients(name);
CREATE INDEX idx_ingredients_rxcui ON ingredients(rxcui);
CREATE INDEX idx_ingredients_normalized_name ON ingredients(normalized_name);
```

### 4. Drug Ingredients

```sql
CREATE TABLE drug_ingredients (
    id SERIAL PRIMARY KEY,
    drug_id INTEGER REFERENCES drugs(id),
    ingredient_id INTEGER REFERENCES ingredients(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(drug_id, ingredient_id)
);

CREATE INDEX idx_drug_ingredients_drug_id ON drug_ingredients(drug_id);
CREATE INDEX idx_drug_ingredients_ingredient_id ON drug_ingredients(ingredient_id);
```

### 5. Allergies

```sql
CREATE TABLE allergies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    normalized_name VARCHAR(255),
    type VARCHAR(50) CHECK (type IN ('drug', 'ingredient', 'class')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_allergies_name ON allergies(name);
CREATE INDEX idx_allergies_normalized_name ON allergies(normalized_name);
```

### 6. Allergy Ingredients

```sql
CREATE TABLE allergy_ingredients (
    id SERIAL PRIMARY KEY,
    allergy_id INTEGER REFERENCES allergies(id),
    ingredient_id INTEGER REFERENCES ingredients(id),
    relationship VARCHAR(50) CHECK (relationship IN ('exact', 'contains', 'cross_reactive')),
    evidence_level VARCHAR(50) CHECK (evidence_level IN ('high', 'medium', 'low')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(allergy_id, ingredient_id)
);

CREATE INDEX idx_allergy_ingredients_allergy_id ON allergy_ingredients(allergy_id);
CREATE INDEX idx_allergy_ingredients_ingredient_id ON allergy_ingredients(ingredient_id);
```

### 7. Conditions

```sql
CREATE TABLE conditions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    normalized_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conditions_name ON conditions(name);
CREATE INDEX idx_conditions_normalized_name ON conditions(normalized_name);
```

### 8. Drug Contraindications

```sql
CREATE TABLE drug_contraindications (
    id SERIAL PRIMARY KEY,
    drug_id INTEGER REFERENCES drugs(id),
    condition_id INTEGER REFERENCES conditions(id),
    evidence_level VARCHAR(50) CHECK (evidence_level IN ('high', 'medium', 'low')),
    description TEXT,
    source VARCHAR(50) CHECK (source IN ('openFDA', 'custom')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(drug_id, condition_id)
);

CREATE INDEX idx_drug_contraindications_drug_id ON drug_contraindications(drug_id);
CREATE INDEX idx_drug_contraindications_condition_id ON drug_contraindications(condition_id);
```

### 9. Drug Warnings

```sql
CREATE TABLE drug_warnings (
    id SERIAL PRIMARY KEY,
    drug_id INTEGER REFERENCES drugs(id),
    type VARCHAR(50) CHECK (type IN ('general', 'specific')),
    text TEXT NOT NULL,
    source VARCHAR(50) CHECK (source IN ('openFDA', 'custom')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_drug_warnings_drug_id ON drug_warnings(drug_id);
```

### 10. Cross Reactivity

```sql
CREATE TABLE cross_reactivity (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES ingredients(id),
    target_id INTEGER REFERENCES ingredients(id),
    evidence_level VARCHAR(50) CHECK (evidence_level IN ('high', 'medium', 'low')),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_id, target_id)
);

CREATE INDEX idx_cross_reactivity_source_id ON cross_reactivity(source_id);
CREATE INDEX idx_cross_reactivity_target_id ON cross_reactivity(target_id);
```

## Initial Data Population

For the MVP, we will populate the database with:

1. **Common Drugs**: Top 100 prescribed medications in the US
2. **Common Allergies**: Major drug allergies (penicillin, sulfa, etc.)
3. **Common Conditions**: Pregnancy, renal impairment, hepatic impairment, etc.
4. **Known Cross-Reactivity**: Well-established cross-reactivity patterns

### Sample Initial Data

#### Common Drug Allergies
- Penicillin
- Cephalosporins
- Sulfonamides
- NSAIDs (Aspirin, Ibuprofen)
- Tetracyclines
- Fluoroquinolones
- Macrolides
- Local anesthetics
- ACE inhibitors
- Anticonvulsants

#### Common Conditions with Contraindications
- Pregnancy
- Breastfeeding
- Renal impairment
- Hepatic impairment
- Cardiovascular disease
- Diabetes
- Asthma
- Glaucoma
- Myasthenia gravis
- Thyroid disorders

#### Well-Known Cross-Reactivity Patterns
- Penicillin → Cephalosporins (5-10% cross-reactivity)
- Sulfonamide antibiotics → Other sulfonamide antibiotics
- Aspirin → Other NSAIDs
- Codeine → Other opioids
- Erythromycin → Other macrolides

## Data Sources for Population

1. **OpenFDA API**: For drug information, contraindications, and warnings
2. **RxNorm API**: For drug normalization and ingredient information
3. **Manual Entry**: For well-established cross-reactivity patterns and allergen-ingredient mappings

## Database Update Strategy

1. **Regular Updates**: Weekly updates from openFDA for new drug information
2. **Versioning**: Track database versions for API responses
3. **Audit Trail**: Log all changes to contraindication data
