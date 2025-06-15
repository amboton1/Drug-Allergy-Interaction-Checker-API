import sqlite3
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import re
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Database connection
def get_db_connection():
    try:
        conn = sqlite3.connect('../database/allergy_api.db')
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise

# Helper functions
def normalize_name(name):
    """Normalize a name by converting to lowercase and removing special characters"""
    return re.sub(r'[^a-z0-9]', '', name.lower())

def find_drug_by_identifier(identifier, identifier_type='name'):
    """Find a drug by name, rxcui, or ndc"""
    logger.debug(f"Finding drug with {identifier_type}: {identifier}")
    conn = get_db_connection()
    
    try:
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
                    WHERE LOWER(name) = ? OR LOWER(generic_name) = ?
                ''', (identifier.lower(), identifier.lower())).fetchone()
                
                # If still not found, try brand names
                if drug is None:
                    brand = conn.execute('''
                        SELECT d.* FROM drugs d
                        JOIN brand_names b ON d.id = b.drug_id
                        WHERE LOWER(b.name) = ?
                    ''', (identifier.lower(),)).fetchone()
                    if brand:
                        drug = brand
        
        result = dict(drug) if drug else None
        logger.debug(f"Found drug: {result}")
        return result
    except Exception as e:
        logger.error(f"Error finding drug: {e}")
        return None
    finally:
        conn.close()

def get_drug_ingredients(drug_id):
    """Get all ingredients for a drug"""
    logger.debug(f"Getting ingredients for drug_id: {drug_id}")
    conn = get_db_connection()
    try:
        ingredients = conn.execute('''
            SELECT i.*, di.is_active 
            FROM ingredients i
            JOIN drug_ingredients di ON i.id = di.ingredient_id
            WHERE di.drug_id = ?
        ''', (drug_id,)).fetchall()
        return [dict(i) for i in ingredients]
    except Exception as e:
        logger.error(f"Error getting drug ingredients: {e}")
        return []
    finally:
        conn.close()

def get_drug_contraindications(drug_id):
    """Get all contraindications for a drug"""
    logger.debug(f"Getting contraindications for drug_id: {drug_id}")
    conn = get_db_connection()
    try:
        contraindications = conn.execute('''
            SELECT dc.*, c.name as condition_name, c.normalized_name as condition_normalized_name
            FROM drug_contraindications dc
            JOIN conditions c ON dc.condition_id = c.id
            WHERE dc.drug_id = ?
        ''', (drug_id,)).fetchall()
        return [dict(c) for c in contraindications]
    except Exception as e:
        logger.error(f"Error getting drug contraindications: {e}")
        return []
    finally:
        conn.close()

def get_drug_warnings(drug_id):
    """Get all warnings for a drug"""
    logger.debug(f"Getting warnings for drug_id: {drug_id}")
    conn = get_db_connection()
    try:
        warnings = conn.execute('SELECT * FROM drug_warnings WHERE drug_id = ?', (drug_id,)).fetchall()
        return [dict(w) for w in warnings]
    except Exception as e:
        logger.error(f"Error getting drug warnings: {e}")
        return []
    finally:
        conn.close()

def find_allergies_by_names(allergy_names):
    """Find allergies by their names"""
    if not allergy_names:
        return []
    
    logger.debug(f"Finding allergies by names: {allergy_names}")
    conn = get_db_connection()
    try:
        placeholders = ', '.join(['?'] * len(allergy_names))
        allergies = conn.execute(f'''
            SELECT * FROM allergies 
            WHERE name IN ({placeholders}) OR normalized_name IN ({placeholders})
        ''', allergy_names + allergy_names).fetchall()
        return [dict(a) for a in allergies]
    except Exception as e:
        logger.error(f"Error finding allergies: {e}")
        return []
    finally:
        conn.close()

def find_conditions_by_names(condition_names):
    """Find conditions by their names"""
    if not condition_names:
        return []
    
    logger.debug(f"Finding conditions by names: {condition_names}")
    conn = get_db_connection()
    try:
        placeholders = ', '.join(['?'] * len(condition_names))
        conditions = conn.execute(f'''
            SELECT * FROM conditions 
            WHERE name IN ({placeholders}) OR normalized_name IN ({placeholders})
        ''', condition_names + condition_names).fetchall()
        return [dict(c) for c in conditions]
    except Exception as e:
        logger.error(f"Error finding conditions: {e}")
        return []
    finally:
        conn.close()

def check_allergy_contraindications(drug_id, allergy_ids, include_cross_reactivity=True):
    """Check if a drug is contraindicated for given allergies"""
    if not allergy_ids:
        return []
    
    logger.debug(f"Checking allergy contraindications for drug_id: {drug_id}, allergy_ids: {allergy_ids}")
    conn = get_db_connection()
    
    try:
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
                    allergy_placeholders = ','.join(['?'] * len(allergy_ids))
                    source_allergy = conn.execute(f'''
                        SELECT a.* FROM allergies a
                        JOIN allergy_ingredients ai ON a.id = ai.allergy_id
                        WHERE ai.ingredient_id = ? AND a.id IN ({allergy_placeholders})
                    ''', [reaction['source_id']] + allergy_ids).fetchone()
                    
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
        
        return contraindications
    except Exception as e:
        logger.error(f"Error checking allergy contraindications: {e}")
        return []
    finally:
        conn.close()

def check_condition_contraindications(drug_id, condition_ids):
    """Check if a drug is contraindicated for given conditions"""
    if not condition_ids:
        return []
    
    logger.debug(f"Checking condition contraindications for drug_id: {drug_id}, condition_ids: {condition_ids}")
    conn = get_db_connection()
    
    try:
        placeholders = ', '.join(['?'] * len(condition_ids))
        contraindications = conn.execute(f'''
            SELECT dc.*, c.name as condition_name
            FROM drug_contraindications dc
            JOIN conditions c ON dc.condition_id = c.id
            WHERE dc.drug_id = ? AND dc.condition_id IN ({placeholders})
        ''', [drug_id] + condition_ids).fetchall()
        
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
    except Exception as e:
        logger.error(f"Error checking condition contraindications: {e}")
        return []
    finally:
        conn.close()

# API Endpoints
@app.route('/v1/check', methods=['POST'])
def check_drug():
    try:
        data = request.json
        logger.debug(f"Received check request: {data}")
        
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
        
        logger.debug(f"Returning response for drug check: {drug['name']}")
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in check_drug endpoint: {e}")
        return jsonify({
            'error': 'Server error',
            'message': str(e)
        }), 500

@app.route('/v1/drug/<identifier>', methods=['GET'])
def get_drug(identifier):
    try:
        identifier_type = request.args.get('identifier_type', 'name')
        logger.debug(f"Getting drug info for {identifier_type}: {identifier}")
        
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
    except Exception as e:
        logger.error(f"Error in get_drug endpoint: {e}")
        return jsonify({
            'error': 'Server error',
            'message': str(e)
        }), 500

@app.route('/v1/allergy/<name>', methods=['GET'])
def get_allergy(name):
    try:
        logger.debug(f"Getting allergy info for: {name}")
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
                CASE 
                    WHEN ai.relationship = 'exact' THEN 'contains'
                    WHEN ai.relationship = 'cross_reactive' THEN 'may_contain'
                    ELSE ai.relationship
                END as relationship
            FROM drugs d
            JOIN drug_ingredients di ON d.id = di.drug_id
            JOIN allergy_ingredients ai ON di.ingredient_id = ai.ingredient_id
            WHERE ai.allergy_id = ?
        ''', (allergy['id'],)).fetchall()
        
        conn.close()
        
        # Format response
        response = {
            'allergy': {
                'name': allergy['name'],
                'normalized_name': allergy['normalized_name'],
                'type': allergy['type']
            },
            'related_ingredients': [
                {
                    'name': i['name'],
                    'rxcui': i['rxcui'],
                    'relationship': i['relationship']
                } for i in related_ingredients
            ],
            'related_drugs': [
                {
                    'name': d['name'],
                    'rxcui': d['rxcui'],
                    'relationship': d['relationship']
                } for d in related_drugs
            ],
            'cross_reactivity': [
                {
                    'name': cr['target_name'],
                    'type': 'ingredient',
                    'evidence_level': cr['evidence_level'],
                    'description': cr['description']
                } for cr in cross_reactivity
            ],
            'metadata': {
                'sources_checked': ['custom'],
                'timestamp': 'ISO datetime',
                'version': '1.0'
            }
        }
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in get_allergy endpoint: {e}")
        return jsonify({
            'error': 'Server error',
            'message': str(e)
        }), 500

@app.route('/v1/batch/check', methods=['POST'])
def batch_check():
    try:
        data = request.json
        logger.debug(f"Received batch check request with {len(data.get('drugs', []))} drugs")
        
        # Validate request
        if not data or 'drugs' not in data or not isinstance(data['drugs'], list):
            return jsonify({
                'error': 'Invalid request',
                'message': 'Request must include a list of drugs'
            }), 400
        
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
        
        results = []
        
        # Process each drug
        for drug_data in data['drugs']:
            # Get drug information
            drug_name = drug_data.get('name')
            rxcui = drug_data.get('rxcui')
            ndc = drug_data.get('ndc')
            
            if not drug_name and not rxcui and not ndc:
                continue
            
            # Find drug in database
            drug = None
            if rxcui:
                drug = find_drug_by_identifier(rxcui, 'rxcui')
            elif ndc:
                drug = find_drug_by_identifier(ndc, 'ndc')
            
            if not drug and drug_name:
                drug = find_drug_by_identifier(drug_name)
            
            if not drug:
                results.append({
                    'drug': {
                        'name': drug_name,
                        'rxcui': rxcui,
                        'ndc': ndc
                    },
                    'error': 'Drug not found'
                })
                continue
            
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
                    'description': w['text']
                })
            
            # Determine if drug is safe
            is_safe = not any(c['severity'] == 'high' for c in all_contraindications)
            
            # Add to results
            results.append({
                'drug': {
                    'name': drug['name'],
                    'rxcui': drug['rxcui'],
                    'ndc': drug['ndc']
                },
                'contraindications': all_contraindications,
                'warnings': formatted_warnings,
                'safe': is_safe
            })
        
        # Format response
        response = {
            'results': results,
            'metadata': {
                'sources_checked': ['custom'],
                'timestamp': 'ISO datetime',
                'version': '1.0'
            }
        }
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error in batch_check endpoint: {e}")
        return jsonify({
            'error': 'Server error',
            'message': str(e)
        }), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Test database connection
        conn = get_db_connection()
        conn.execute('SELECT 1').fetchone()
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'version': '1.0'
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    logger.info("Starting Allergy/Contraindication Checker API")
    app.run(debug=True, host='0.0.0.0', port=5000)
