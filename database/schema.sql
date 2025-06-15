-- Create database tables for Allergy/Contraindication Checker API

-- Drugs table
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

-- Brand Names table
CREATE TABLE brand_names (
    id SERIAL PRIMARY KEY,
    drug_id INTEGER REFERENCES drugs(id),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_brand_names_drug_id ON brand_names(drug_id);
CREATE INDEX idx_brand_names_name ON brand_names(name);

-- Ingredients table
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

-- Drug Ingredients table
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

-- Allergies table
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

-- Allergy Ingredients table
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

-- Conditions table
CREATE TABLE conditions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    normalized_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conditions_name ON conditions(name);
CREATE INDEX idx_conditions_normalized_name ON conditions(normalized_name);

-- Drug Contraindications table
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

-- Drug Warnings table
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

-- Cross Reactivity table
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
