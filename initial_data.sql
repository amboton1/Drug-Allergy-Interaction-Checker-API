-- Initial data population for Allergy/Contraindication Checker API

-- Common Allergies
INSERT INTO allergies (name, normalized_name, type) VALUES
('Penicillin', 'penicillin', 'class'),
('Cephalosporins', 'cephalosporins', 'class'),
('Sulfonamides', 'sulfonamides', 'class'),
('NSAIDs', 'nsaids', 'class'),
('Aspirin', 'aspirin', 'drug'),
('Ibuprofen', 'ibuprofen', 'drug'),
('Tetracyclines', 'tetracyclines', 'class'),
('Fluoroquinolones', 'fluoroquinolones', 'class'),
('Macrolides', 'macrolides', 'class'),
('Local anesthetics', 'local anesthetics', 'class'),
('ACE inhibitors', 'ace inhibitors', 'class'),
('Anticonvulsants', 'anticonvulsants', 'class'),
('Codeine', 'codeine', 'ingredient'),
('Sulfites', 'sulfites', 'ingredient'),
('Latex', 'latex', 'ingredient');

-- Common Conditions
INSERT INTO conditions (name, normalized_name) VALUES
('Pregnancy', 'pregnancy'),
('Breastfeeding', 'breastfeeding'),
('Renal impairment', 'renal impairment'),
('Hepatic impairment', 'hepatic impairment'),
('Cardiovascular disease', 'cardiovascular disease'),
('Diabetes', 'diabetes'),
('Asthma', 'asthma'),
('Glaucoma', 'glaucoma'),
('Myasthenia gravis', 'myasthenia gravis'),
('Thyroid disorders', 'thyroid disorders');

-- Common Ingredients
INSERT INTO ingredients (name, normalized_name) VALUES
('Penicillin G', 'penicillin g'),
('Amoxicillin', 'amoxicillin'),
('Ampicillin', 'ampicillin'),
('Cephalexin', 'cephalexin'),
('Cefazolin', 'cefazolin'),
('Sulfamethoxazole', 'sulfamethoxazole'),
('Trimethoprim', 'trimethoprim'),
('Acetylsalicylic acid', 'acetylsalicylic acid'),
('Ibuprofen', 'ibuprofen'),
('Naproxen', 'naproxen'),
('Tetracycline', 'tetracycline'),
('Doxycycline', 'doxycycline'),
('Ciprofloxacin', 'ciprofloxacin'),
('Levofloxacin', 'levofloxacin'),
('Erythromycin', 'erythromycin'),
('Azithromycin', 'azithromycin'),
('Lidocaine', 'lidocaine'),
('Benzocaine', 'benzocaine'),
('Lisinopril', 'lisinopril'),
('Enalapril', 'enalapril'),
('Phenytoin', 'phenytoin'),
('Carbamazepine', 'carbamazepine'),
('Codeine', 'codeine'),
('Morphine', 'morphine'),
('Sodium metabisulfite', 'sodium metabisulfite');

-- Sample Drugs
INSERT INTO drugs (name, rxcui, generic_name, is_otc, dosage_form) VALUES
('Amoxil', '723', 'Amoxicillin', FALSE, 'Oral Capsule'),
('Augmentin', '105904', 'Amoxicillin/Clavulanate', FALSE, 'Oral Tablet'),
('Keflex', '203542', 'Cephalexin', FALSE, 'Oral Capsule'),
('Bactrim', '209459', 'Sulfamethoxazole/Trimethoprim', FALSE, 'Oral Tablet'),
('Aspirin', '1191', 'Acetylsalicylic acid', TRUE, 'Oral Tablet'),
('Advil', '153010', 'Ibuprofen', TRUE, 'Oral Tablet'),
('Aleve', '849574', 'Naproxen', TRUE, 'Oral Tablet'),
('Tetracycline', '10395', 'Tetracycline', FALSE, 'Oral Capsule'),
('Vibramycin', '1650286', 'Doxycycline', FALSE, 'Oral Capsule'),
('Cipro', '203563', 'Ciprofloxacin', FALSE, 'Oral Tablet'),
('Levaquin', '311296', 'Levofloxacin', FALSE, 'Oral Tablet'),
('Erythrocin', '141962', 'Erythromycin', FALSE, 'Oral Tablet'),
('Zithromax', '141963', 'Azithromycin', FALSE, 'Oral Tablet'),
('Xylocaine', '6387', 'Lidocaine', FALSE, 'Topical Solution'),
('Prinivil', '29046', 'Lisinopril', FALSE, 'Oral Tablet'),
('Dilantin', '202741', 'Phenytoin', FALSE, 'Oral Capsule'),
('Tegretol', '2002', 'Carbamazepine', FALSE, 'Oral Tablet'),
('Tylenol with Codeine', '993837', 'Acetaminophen/Codeine', FALSE, 'Oral Tablet');

-- Link Ingredients to Drugs
-- Amoxil
INSERT INTO drug_ingredients (drug_id, ingredient_id, is_active) 
SELECT d.id, i.id, TRUE FROM drugs d, ingredients i 
WHERE d.name = 'Amoxil' AND i.name = 'Amoxicillin';

-- Augmentin
INSERT INTO drug_ingredients (drug_id, ingredient_id, is_active) 
SELECT d.id, i.id, TRUE FROM drugs d, ingredients i 
WHERE d.name = 'Augmentin' AND i.name = 'Amoxicillin';

-- Keflex
INSERT INTO drug_ingredients (drug_id, ingredient_id, is_active) 
SELECT d.id, i.id, TRUE FROM drugs d, ingredients i 
WHERE d.name = 'Keflex' AND i.name = 'Cephalexin';

-- Bactrim
INSERT INTO drug_ingredients (drug_id, ingredient_id, is_active) 
SELECT d.id, i.id, TRUE FROM drugs d, ingredients i 
WHERE d.name = 'Bactrim' AND i.name = 'Sulfamethoxazole';
INSERT INTO drug_ingredients (drug_id, ingredient_id, is_active) 
SELECT d.id, i.id, TRUE FROM drugs d, ingredients i 
WHERE d.name = 'Bactrim' AND i.name = 'Trimethoprim';

-- Aspirin
INSERT INTO drug_ingredients (drug_id, ingredient_id, is_active) 
SELECT d.id, i.id, TRUE FROM drugs d, ingredients i 
WHERE d.name = 'Aspirin' AND i.name = 'Acetylsalicylic acid';

-- Advil
INSERT INTO drug_ingredients (drug_id, ingredient_id, is_active) 
SELECT d.id, i.id, TRUE FROM drugs d, ingredients i 
WHERE d.name = 'Advil' AND i.name = 'Ibuprofen';

-- Aleve
INSERT INTO drug_ingredients (drug_id, ingredient_id, is_active) 
SELECT d.id, i.id, TRUE FROM drugs d, ingredients i 
WHERE d.name = 'Aleve' AND i.name = 'Naproxen';

-- Tetracycline
INSERT INTO drug_ingredients (drug_id, ingredient_id, is_active) 
SELECT d.id, i.id, TRUE FROM drugs d, ingredients i 
WHERE d.name = 'Tetracycline' AND i.name = 'Tetracycline';

-- Vibramycin
INSERT INTO drug_ingredients (drug_id, ingredient_id, is_active) 
SELECT d.id, i.id, TRUE FROM drugs d, ingredients i 
WHERE d.name = 'Vibramycin' AND i.name = 'Doxycycline';

-- Cipro
INSERT INTO drug_ingredients (drug_id, ingredient_id, is_active) 
SELECT d.id, i.id, TRUE FROM drugs d, ingredients i 
WHERE d.name = 'Cipro' AND i.name = 'Ciprofloxacin';

-- Levaquin
INSERT INTO drug_ingredients (drug_id, ingredient_id, is_active) 
SELECT d.id, i.id, TRUE FROM drugs d, ingredients i 
WHERE d.name = 'Levaquin' AND i.name = 'Levofloxacin';

-- Erythrocin
INSERT INTO drug_ingredients (drug_id, ingredient_id, is_active) 
SELECT d.id, i.id, TRUE FROM drugs d, ingredients i 
WHERE d.name = 'Erythrocin' AND i.name = 'Erythromycin';

-- Zithromax
INSERT INTO drug_ingredients (drug_id, ingredient_id, is_active) 
SELECT d.id, i.id, TRUE FROM drugs d, ingredients i 
WHERE d.name = 'Zithromax' AND i.name = 'Azithromycin';

-- Xylocaine
INSERT INTO drug_ingredients (drug_id, ingredient_id, is_active) 
SELECT d.id, i.id, TRUE FROM drugs d, ingredients i 
WHERE d.name = 'Xylocaine' AND i.name = 'Lidocaine';

-- Prinivil
INSERT INTO drug_ingredients (drug_id, ingredient_id, is_active) 
SELECT d.id, i.id, TRUE FROM drugs d, ingredients i 
WHERE d.name = 'Prinivil' AND i.name = 'Lisinopril';

-- Dilantin
INSERT INTO drug_ingredients (drug_id, ingredient_id, is_active) 
SELECT d.id, i.id, TRUE FROM drugs d, ingredients i 
WHERE d.name = 'Dilantin' AND i.name = 'Phenytoin';

-- Tegretol
INSERT INTO drug_ingredients (drug_id, ingredient_id, is_active) 
SELECT d.id, i.id, TRUE FROM drugs d, ingredients i 
WHERE d.name = 'Tegretol' AND i.name = 'Carbamazepine';

-- Tylenol with Codeine
INSERT INTO drug_ingredients (drug_id, ingredient_id, is_active) 
SELECT d.id, i.id, TRUE FROM drugs d, ingredients i 
WHERE d.name = 'Tylenol with Codeine' AND i.name = 'Codeine';

-- Link Allergies to Ingredients
-- Penicillin allergy
INSERT INTO allergy_ingredients (allergy_id, ingredient_id, relationship, evidence_level)
SELECT a.id, i.id, 'exact', 'high' FROM allergies a, ingredients i
WHERE a.name = 'Penicillin' AND i.name IN ('Penicillin G', 'Amoxicillin', 'Ampicillin');

-- Cephalosporins allergy
INSERT INTO allergy_ingredients (allergy_id, ingredient_id, relationship, evidence_level)
SELECT a.id, i.id, 'exact', 'high' FROM allergies a, ingredients i
WHERE a.name = 'Cephalosporins' AND i.name IN ('Cephalexin', 'Cefazolin');

-- Sulfonamides allergy
INSERT INTO allergy_ingredients (allergy_id, ingredient_id, relationship, evidence_level)
SELECT a.id, i.id, 'exact', 'high' FROM allergies a, ingredients i
WHERE a.name = 'Sulfonamides' AND i.name = 'Sulfamethoxazole';

-- NSAIDs allergy
INSERT INTO allergy_ingredients (allergy_id, ingredient_id, relationship, evidence_level)
SELECT a.id, i.id, 'exact', 'high' FROM allergies a, ingredients i
WHERE a.name = 'NSAIDs' AND i.name IN ('Acetylsalicylic acid', 'Ibuprofen', 'Naproxen');

-- Aspirin allergy
INSERT INTO allergy_ingredients (allergy_id, ingredient_id, relationship, evidence_level)
SELECT a.id, i.id, 'exact', 'high' FROM allergies a, ingredients i
WHERE a.name = 'Aspirin' AND i.name = 'Acetylsalicylic acid';

-- Ibuprofen allergy
INSERT INTO allergy_ingredients (allergy_id, ingredient_id, relationship, evidence_level)
SELECT a.id, i.id, 'exact', 'high' FROM allergies a, ingredients i
WHERE a.name = 'Ibuprofen' AND i.name = 'Ibuprofen';

-- Tetracyclines allergy
INSERT INTO allergy_ingredients (allergy_id, ingredient_id, relationship, evidence_level)
SELECT a.id, i.id, 'exact', 'high' FROM allergies a, ingredients i
WHERE a.name = 'Tetracyclines' AND i.name IN ('Tetracycline', 'Doxycycline');

-- Fluoroquinolones allergy
INSERT INTO allergy_ingredients (allergy_id, ingredient_id, relationship, evidence_level)
SELECT a.id, i.id, 'exact', 'high' FROM allergies a, ingredients i
WHERE a.name = 'Fluoroquinolones' AND i.name IN ('Ciprofloxacin', 'Levofloxacin');

-- Macrolides allergy
INSERT INTO allergy_ingredients (allergy_id, ingredient_id, relationship, evidence_level)
SELECT a.id, i.id, 'exact', 'high' FROM allergies a, ingredients i
WHERE a.name = 'Macrolides' AND i.name IN ('Erythromycin', 'Azithromycin');

-- Local anesthetics allergy
INSERT INTO allergy_ingredients (allergy_id, ingredient_id, relationship, evidence_level)
SELECT a.id, i.id, 'exact', 'high' FROM allergies a, ingredients i
WHERE a.name = 'Local anesthetics' AND i.name IN ('Lidocaine', 'Benzocaine');

-- ACE inhibitors allergy
INSERT INTO allergy_ingredients (allergy_id, ingredient_id, relationship, evidence_level)
SELECT a.id, i.id, 'exact', 'high' FROM allergies a, ingredients i
WHERE a.name = 'ACE inhibitors' AND i.name IN ('Lisinopril', 'Enalapril');

-- Anticonvulsants allergy
INSERT INTO allergy_ingredients (allergy_id, ingredient_id, relationship, evidence_level)
SELECT a.id, i.id, 'exact', 'high' FROM allergies a, ingredients i
WHERE a.name = 'Anticonvulsants' AND i.name IN ('Phenytoin', 'Carbamazepine');

-- Codeine allergy
INSERT INTO allergy_ingredients (allergy_id, ingredient_id, relationship, evidence_level)
SELECT a.id, i.id, 'exact', 'high' FROM allergies a, ingredients i
WHERE a.name = 'Codeine' AND i.name = 'Codeine';

-- Sulfites allergy
INSERT INTO allergy_ingredients (allergy_id, ingredient_id, relationship, evidence_level)
SELECT a.id, i.id, 'exact', 'high' FROM allergies a, ingredients i
WHERE a.name = 'Sulfites' AND i.name = 'Sodium metabisulfite';

-- Cross-reactivity patterns
-- Penicillin → Cephalosporins
INSERT INTO cross_reactivity (source_id, target_id, evidence_level, description)
SELECT i1.id, i2.id, 'medium', 'Approximately 5-10% of patients with penicillin allergy may have cross-reactivity with cephalosporins'
FROM ingredients i1, ingredients i2
WHERE i1.name = 'Penicillin G' AND i2.name = 'Cephalexin';

INSERT INTO cross_reactivity (source_id, target_id, evidence_level, description)
SELECT i1.id, i2.id, 'medium', 'Approximately 5-10% of patients with penicillin allergy may have cross-reactivity with cephalosporins'
FROM ingredients i1, ingredients i2
WHERE i1.name = 'Amoxicillin' AND i2.name = 'Cephalexin';

-- Aspirin → Other NSAIDs
INSERT INTO cross_reactivity (source_id, target_id, evidence_level, description)
SELECT i1.id, i2.id, 'high', 'High cross-reactivity between aspirin and other NSAIDs'
FROM ingredients i1, ingredients i2
WHERE i1.name = 'Acetylsalicylic acid' AND i2.name = 'Ibuprofen';

INSERT INTO cross_reactivity (source_id, target_id, evidence_level, description)
SELECT i1.id, i2.id, 'high', 'High cross-reactivity between aspirin and other NSAIDs'
FROM ingredients i1, ingredients i2
WHERE i1.name = 'Acetylsalicylic acid' AND i2.name = 'Naproxen';

-- Codeine → Morphine
INSERT INTO cross_reactivity (source_id, target_id, evidence_level, description)
SELECT i1.id, i2.id, 'high', 'High cross-reactivity between codeine and other opioids'
FROM ingredients i1, ingredients i2
WHERE i1.name = 'Codeine' AND i2.name = 'Morphine';

-- Sample Drug Contraindications
-- Tetracycline contraindicated in pregnancy
INSERT INTO drug_contraindications (drug_id, condition_id, evidence_level, description, source)
SELECT d.id, c.id, 'high', 'Tetracyclines may cause permanent discoloration of teeth and enamel hypoplasia in the fetus. They can also inhibit bone growth.', 'openFDA'
FROM drugs d, conditions c
WHERE d.name = 'Tetracycline' AND c.name = 'Pregnancy';

-- ACE inhibitors contraindicated in pregnancy
INSERT INTO drug_contraindications (drug_id, condition_id, evidence_level, description, source)
SELECT d.id, c.id, 'high', 'ACE inhibitors can cause injury and death to the developing fetus when used during the second and third trimesters.', 'openFDA'
FROM drugs d, conditions c
WHERE d.name = 'Prinivil' AND c.name = 'Pregnancy';

-- NSAIDs contraindicated in severe renal impairment
INSERT INTO drug_contraindications (drug_id, condition_id, evidence_level, description, source)
SELECT d.id, c.id, 'high', 'NSAIDs can cause further kidney damage in patients with severe renal impairment.', 'openFDA'
FROM drugs d, conditions c
WHERE d.name IN ('Advil', 'Aleve') AND c.name = 'Renal impairment';

-- Sample Drug Warnings
INSERT INTO drug_warnings (drug_id, type, text, source)
SELECT d.id, 'general', 'May cause drowsiness. Alcohol may intensify this effect. Use care when operating a car or dangerous machinery.', 'openFDA'
FROM drugs d
WHERE d.name = 'Tylenol with Codeine';

INSERT INTO drug_warnings (drug_id, type, text, source)
SELECT d.id, 'specific', 'May cause photosensitivity. Avoid prolonged exposure to sunlight and use sun protection.', 'openFDA'
FROM drugs d
WHERE d.name IN ('Tetracycline', 'Vibramycin', 'Cipro', 'Levaquin');

INSERT INTO drug_warnings (drug_id, type, text, source)
SELECT d.id, 'specific', 'May cause gastrointestinal bleeding. Take with food to minimize risk.', 'openFDA'
FROM drugs d
WHERE d.name IN ('Aspirin', 'Advil', 'Aleve');
