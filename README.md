````markdown
# 💊 Drug-Allergy Interaction Checker API

This is a Flask-based REST API designed to check potential drug contraindications and cross-reactive allergies for patients. It also provides detailed information about drugs and allergies using a custom SQLite database.

⚠️ **Disclaimer**  
> This project is for **educational and testing purposes only**.  
> The data provided by this API is not intended for medical use. Do **not** use this application to make medical decisions.  
> The author assumes **no responsibility or liability** for any misuse or misunderstanding of the code or data.

---

## 🚀 Features

- Check drug interactions based on patient allergies and conditions
- Get detailed drug information by name, RxCUI, or NDC
- Lookup known allergy information and cross-reactivity data
- Built with Flask and SQLite

---

## 📦 API Endpoints

### 1. **Check Drug Safety**
`POST /v1/check`

**Request Body:**
```json
{
  "drug": { "name": "ibuprofen" },
  "patient": {
    "allergies": ["aspirin"],
    "conditions": ["asthma"]
  },
  "options": {
    "check_cross_reactivity": true
  }
}
````

**Response:** Contraindication results or empty array.

---

### 2. **Get Drug Info**

`GET /v1/drug/<identifier>?identifier_type=name|rxcui|ndc`

Example:

```
GET /v1/drug/ibuprofen?identifier_type=name
```

**Response:** Drug details, ingredients, brand names, contraindications, warnings.

---

### 3. **Get Allergy Info**

`GET /v1/allergy/<name>`

Example:

```
GET /v1/allergy/penicillin
```

**Response:** Related ingredients, related drugs, and cross-reactivity info.

---

## 🛠️ Installation

1. Clone the repo:

```bash
git clone https://github.com/your-username/drug-allergy-checker-api.git
cd drug-allergy-checker-api
```

2. Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Run the server:

```bash
flask run
```

---

## 🧪 Testing with Postman

Use Postman or cURL to hit endpoints at:

```
http://localhost:5000/v1/...
```

---

## 🧱 Tech Stack

* **Python** + **Flask**
* **SQLite** (for local drug/allergy database)
* **SQLAlchemy** (optional if you're planning ORM support)
* JSON-based APIs

---

## ✨ Future Plans

* Add Swagger/OpenAPI support
* External RxNorm or FDA data integration
* Admin UI for managing the drug database

## ☕ Support This Project
If you find this project useful or it helped you in any way, consider supporting me by buying me a coffee.
Your support helps me keep building and maintaining open-source tools like this. Thank you! 🙏

[![Buy Me a Coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-%E2%98%95%EF%B8%8F-yellow?style=flat&logo=buy-me-a-coffee)](https://www.buymeacoffee.com/botarius)
