import sqlite3
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('database/allergy_api.db')
    conn.row_factory = sqlite3.Row
    return conn

# Helper functions
def normalize_name(name):
    """Normalize a name by converting to lowercase and removing special characters"""
    return re.sub(r'[^a-z0-9]', '', name.lower())

def find_drug_by_identifier(identifier, identifier_type='name'):
    """Find a drug by name, rxcui, or ndc"""
    conn = get_db_connection()
    
    if identifier_type == 'rxcui':
        drug = conn.execute('SELECT * FROM drugs WHERE rxcui = ?', (identifier,)).fetchone()
    elif identifier_type == 'ndc':
        drug = conn.execute('SELECT * FROM drugs WHERE ndc = ?', (identifier,)).fetchone()
    else:  # default to name
        drug = conn.execute('SELECT * FROM drugs WHERE name = ? OR generic_name = ?', 
                           (identifier, identifier)).fetchone()
        
        # If not found by exact match, try normalized name
        if drug is None:
            normalized = normalize_name(identifier)
            drug = conn.execute('''
                SELECT * FROM drugs 
                WHERE normalize_name(name) = ? OR normalize_name(generic_name) = ?
            ''', (normalized, normalized)).fetchone()
            
            # If still not found, try brand names
            if drug is None:
                brand = conn.execute('''
                    SELECT d.* FROM drugs d
                    JOIN brand_names b ON d.id = b.drug_id
                    WHERE normalize_name(b.name) = ?
                ''', (normalized,)).fetchone()
                if brand:
                    drug = brand
    
    conn.close()
    return dict(drug) if drug else None

def get_drug_ingredients(drug_id):
    """Get all ingredients for a drug"""
    conn = get_db_connection()
    ingredients = conn.execute('''
        SELECT i.*, di.is_active 
        FROM ingredients i
        JOIN drug_ingredients di ON i.id = di.ingredient_id
        WHERE di.drug_id = ?
    ''', (drug_id,)).fetchall()
    conn.close()
    return [dict(i) for i in ingredients]

def get_drug_contraindications(drug_id):
    """Get all contraindications for a drug"""
    conn = get_db_connection()
    contraindications = conn.execute('''
        SELECT dc.*, c.name as condition_name, c.normalized_name as condition_normalized_name
        FROM drug_contraindications dc
        JOIN conditions c ON dc.condition_id = c.id
        WHERE dc.drug_id = ?
    ''', (drug_id,)).fetchall()
    conn.close()
    return [dict(c) for c in contraindications]

def get_drug_warnings(drug_id):
    """Get all warnings for a drug"""
    conn = get_db_connection()
    warnings = conn.execute('SELECT * FROM drug_warnings WHERE drug_id = ?', (drug_id,)).fetchall()
    conn.close()
    return [dict(w) for w in warnings]

def find_allergies_by_names(allergy_names):
    """Find allergies by their names"""
    if not allergy_names:
        return []
        
    conn = get_db_connection()
    placeholders = ', '.join(['?'] * len(allergy_names))
    allergies = conn.execute(f'''
        SELECT * FROM allergies 
        WHERE name IN ({placeholders}) OR normalized_name IN ({placeholders})
    ''', allergy_names + allergy_names).fetchall()
    conn.close()
    return [dict(a) for a in allergies]

def find_conditions_by_names(condition_names):
    """Find conditions by their names"""
    if not condition_names:
        return []
        
    conn = get_db_connection()
    placeholders = ', '.join(['?'] * len(condition_names))
    conditions = conn.execute(f'''
        SELECT * FROM conditions 
        WHERE name IN ({placeholders}) OR normalized_name IN ({placeholders})
    ''', condition_names + condition_names).fetchall()
    conn.close()
    return [dict(c) for c in conditions]

def check_allergy_contraindications(drug_id, allergy_ids, include_cross_reactivity=True):
    """Check if a drug is contraindicated for given allergies"""
    if not allergy_ids:
        return []
        
    conn = get_db_connection()
    
    # Get all ingredients for the drug
    drug_ingredients = conn.execute('''
        SELECT i.id, i.name, di.is_active
        FROM ingredients i
        JOIN drug_ingredients di ON i.id = di.ingredient_id
        WHERE di.drug_id = ?
    ''', (drug_id,)).fetchall()
    
    contraindications = []
    
    # Check direct ingredient matches
    for allergy_id in allergy_ids:
        # Get ingredients related to this allergy
        allergy_ingredients = conn.execute('''
            SELECT i.id, i.name, ai.relationship, ai.evidence_level, a.name as allergy_name
            FROM ingredients i
            JOIN allergy_ingredients ai ON i.id = ai.ingredient_id
            JOIN allergies a ON ai.allergy_id = a.id
            WHERE ai.allergy_id = ?
        ''', (allergy_id,)).fetchall()
        
        # Check if any drug ingredient matches allergy ingredients
        for drug_ing in drug_ingredients:
            for allergy_ing in allergy_ingredients:
                if drug_ing['id'] == allergy_ing['id']:
                    contraindications.append({
                        'type': 'allergy',
                        'name': allergy_ing['allergy_name'],
                        'severity': 'high' if drug_ing['is_active'] else 'medium',
                        'description': f"Contains {allergy_ing['name']} which is related to {allergy_ing['allergy_name']} allergy",
                        'evidence': {
                            'source': 'custom',
                            'text': f"Direct match with {allergy_ing['relationship']} relationship, {allergy_ing['evidence_level']} evidence"
                        },
                        'recommendation': 'Avoid this medication'
                    })
    
    # Check cross-reactivity if enabled
    if include_cross_reactivity:
        for drug_ing in drug_ingredients:
            cross_reactions = conn.execute('''
                SELECT cr.*, i.name as target_name, 
                       (SELECT name FROM allergies WHERE id = 
                           (SELECT allergy_id FROM allergy_ingredients WHERE ingredient_id = cr.source_id LIMIT 1)
                       ) as source_allergy
                FROM cross_reactivity cr
                JOIN ingredients i ON cr.target_id = i.id
                WHERE cr.target_id = ?
            ''', (drug_ing['id'],)).fetchall()
            
            for reaction in cross_reactions:
                # Check if the source of cross-reactivity is in our allergy list
                source_allergy = conn.execute('''
                    SELECT a.* FROM allergies a
                    JOIN allergy_ingredients ai ON a.id = ai.allergy_id
                    WHERE ai.ingredient_id = ? AND a.id IN ({})
                '''.format(','.join(['?'] * len(allergy_ids))), 
                [reaction['source_id']] + allergy_ids).fetchone()
                
                if source_allergy:
                    contraindications.append({
                        'type': 'allergy',
                        'name': source_allergy['name'],
                        'severity': 'medium' if reaction['evidence_level'] == 'high' else 'low',
                        'description': f"Contains {reaction['target_name']} which may cross-react with {source_allergy['name']} allergy",
                        'evidence': {
                            'source': 'custom',
                            'text': reaction['description']
                        },
                        'recommendation': 'Use with caution' if reaction['evidence_level'] == 'low' else 'Consider alternative medication'
                    })
    
    conn.close()
    return contraindications

def check_condition_contraindications(drug_id, condition_ids):
    """Check if a drug is contraindicated for given conditions"""
    if not condition_ids:
        return []
        
    conn = get_db_connection()
    
    placeholders = ', '.join(['?'] * len(condition_ids))
    contraindications = conn.execute(f'''
        SELECT dc.*, c.name as condition_name
        FROM drug_contraindications dc
        JOIN conditions c ON dc.condition_id = c.id
        WHERE dc.drug_id = ? AND dc.condition_id IN ({placeholders})
    ''', [drug_id] + condition_ids).fetchall()
    
    conn.close()
    
    result = []
    for c in contraindications:
        result.append({
            'type': 'condition',
            'name': c['condition_name'],
            'severity': c['evidence_level'],
            'description': c['description'],
            'evidence': {
                'source': c['source'],
                'text': c['description']
            },
            'recommendation': 'Avoid this medication' if c['evidence_level'] == 'high' else 'Use with caution'
        })
    
    return result

# API Endpoints
@app.route('/v1/check', methods=['POST'])
def check_drug():
    data = request.json
    
    # Validate request
    if not data or 'drug' not in data or 'name' not in data['drug']:
        return jsonify({
            'error': 'Invalid request',
            'message': 'Request must include drug name'
        }), 400
    
    # Get drug information
    drug_name = data['drug']['name']
    rxcui = data['drug'].get('rxcui')
    ndc = data['drug'].get('ndc')
    
    # Find drug in database
    drug = None
    if rxcui:
        drug = find_drug_by_identifier(rxcui, 'rxcui')
    elif ndc:
        drug = find_drug_by_identifier(ndc, 'ndc')
    
    if not drug:
        drug = find_drug_by_identifier(drug_name)
    
    if not drug:
        return jsonify({
            'error': 'Drug not found',
            'message': f'Could not find drug with name: {drug_name}'
        }), 404
    
    # Get patient allergies and conditions
    allergies = []
    conditions = []
    
    if 'patient' in data:
        if 'allergies' in data['patient']:
            allergy_names = [a['name'] for a in data['patient']['allergies']]
            allergies = find_allergies_by_names(allergy_names)
        
        if 'conditions' in data['patient']:
            condition_names = [c['name'] for c in data['patient']['conditions']]
            conditions = find_conditions_by_names(condition_names)
    
    # Get options
    options = data.get('options', {})
    include_inactive = options.get('include_inactive_ingredients', True)
    include_cross_reactivity = options.get('include_cross_reactivity', True)
    include_evidence = options.get('include_evidence', True)
    
    # Get drug ingredients
    ingredients = get_drug_ingredients(drug['id'])
    
    # Check contraindications
    allergy_contraindications = check_allergy_contraindications(
        drug['id'], 
        [a['id'] for a in allergies],
        include_cross_reactivity
    )
    
    condition_contraindications = check_condition_contraindications(
        drug['id'],
        [c['id'] for c in conditions]
    )
    
    all_contraindications = allergy_contraindications + condition_contraindications
    
    # Get warnings
    warnings = get_drug_warnings(drug['id'])
    formatted_warnings = []
    
    for w in warnings:
        formatted_warnings.append({
            'type': w['type'],
            'name': w['type'].capitalize(),
            'severity': 'medium',
            'description': w['text'],
            'evidence': {
                'source': w['source'],
                'text': w['text']
            } if include_evidence else None,
            'recommendation': 'Follow warning instructions'
        })
    
    # Determine if drug is safe
    is_safe = not any(c['severity'] == 'high' for c in all_contraindications)
    
    # Format response
    response = {
        'drug': {
            'name': drug['name'],
            'rxcui': drug['rxcui'],
            'ndc': drug['ndc'],
            'ingredients': [
                {
                    'name': i['name'],
                    'type': 'active' if i['is_active'] else 'inactive',
                    'rxcui': i['rxcui']
                } for i in ingredients
            ]
        },
        'contraindications': all_contraindications,
        'warnings': formatted_warnings,
        'safe': is_safe,
        'metadata': {
            'sources_checked': ['custom'],
            'timestamp': 'ISO datetime',
            'version': '1.0'
        }
    }
    
    return jsonify(response)

@app.route('/v1/drug/<identifier>', methods=['GET'])
def get_drug(identifier):
    identifier_type = request.args.get('identifier_type', 'name')
    
    # Find drug in database
    drug = find_drug_by_identifier(identifier, identifier_type)
    
    if not drug:
        return jsonify({
            'error': 'Drug not found',
            'message': f'Could not find drug with {identifier_type}: {identifier}'
        }), 404
    
    # Get drug details
    ingredients = get_drug_ingredients(drug['id'])
    contraindications = get_drug_contraindications(drug['id'])
    warnings = get_drug_warnings(drug['id'])
    
    # Get brand names
    conn = get_db_connection()
    brand_names = conn.execute('SELECT name FROM brand_names WHERE drug_id = ?', (drug['id'],)).fetchall()
    conn.close()
    
    # Format response
    response = {
        'drug': {
            'name': drug['name'],
            'rxcui': drug['rxcui'],
            'ndc': drug['ndc'],
            'brand_names': [b['name'] for b in brand_names],
            'generic_name': drug['generic_name'],
            'ingredients': [
                {
                    'name': i['name'],
                    'type': 'active' if i['is_active'] else 'inactive',
                    'rxcui': i['rxcui']
                } for i in ingredients
            ],
            'dosage_forms': [drug['dosage_form']] if drug['dosage_form'] else []
        },
        'contraindications': [
            {
                'type': 'condition',
                'name': c['condition_name'],
                'description': c['description'],
                'source': c['source']
            } for c in contraindications
        ],
        'warnings': [
            {
                'type': w['type'],
                'text': w['text'],
                'source': w['source']
            } for w in warnings
        ],
        'metadata': {
            'sources_checked': ['custom'],
            'timestamp': 'ISO datetime',
            'version': '1.0'
        }
    }
    
    return jsonify(response)

@app.route('/v1/allergy/<name>', methods=['GET'])
def get_allergy(name):
    conn = get_db_connection()
    
    # Find allergy
    allergy = conn.execute('SELECT * FROM allergies WHERE name = ? OR normalized_name = ?', 
                          (name, normalize_name(name))).fetchone()
    
    if not allergy:
        conn.close()
        return jsonify({
            'error': 'Allergy not found',
            'message': f'Could not find allergy with name: {name}'
        }), 404
    
    allergy = dict(allergy)
    
    # Get related ingredients
    related_ingredients = conn.execute('''
        SELECT i.*, ai.relationship
        FROM ingredients i
        JOIN allergy_ingredients ai ON i.id = ai.ingredient_id
        WHERE ai.allergy_id = ?
    ''', (allergy['id'],)).fetchall()
    
    # Get cross-reactivity
    cross_reactivity = conn.execute('''
        SELECT cr.*, i1.name as source_name, i2.name as target_name
        FROM cross_reactivity cr
        JOIN ingredients i1 ON cr.source_id = i1.id
        JOIN ingredients i2 ON cr.target_id = i2.id
        WHERE cr.source_id IN (
            SELECT ingredient_id FROM allergy_ingredients WHERE allergy_id = ?
        )
    ''', (allergy['id'],)).fetchall()
    
    # Get related drugs
    related_drugs = conn.execute('''
        SELECT d.*, 
               ai.relationship,
               i.name AS ingredient_name
        FROM drugs d
        JOIN drug_ingredients di ON d.id = di.drug_id
        JOIN ingredients i ON di.ingredient_id = i.id
        JOIN allergy_ingredients ai ON ai.ingredient_id = i.id
        WHERE ai.allergy_id = ?
    ''', (allergy['id'],)).fetchall()

    conn.close()

    return jsonify({
        'allergy': allergy,
        'related_ingredients': [dict(row) for row in related_ingredients],
        'cross_reactivity': [dict(row) for row in cross_reactivity],
        'related_drugs': [dict(row) for row in related_drugs]
    }), 200
