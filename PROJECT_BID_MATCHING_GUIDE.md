# Project and Bid Matching Guide

## Overview
This guide shows which project description file matches with which bid JSON file for testing the bid evaluation system.

---

## **MATCHING PAIRS**

### **Pair 1: Commercial Renovation (Occupied Building)**
- **Project File**: `projects/project_1_commercial_renovation.txt`
- **Bid File**: `bids/bids_project_1_commercial.json`
- **Test Focus**: Risk vs cost trade-offs, occupied building operations, scope completeness
- **Expected Outcome**: Tutor Perini should win (full scope, balanced risk)

---

### **Pair 2: Residential Apartment Complex**
- **Project File**: `projects/project_2_residential_complex.txt`
- **Bid File**: `bids/bids_project_2_residential.json`
- **Test Focus**: LEED certification, cost control, quality vs budget
- **Expected Outcome**: Webcor Builders likely winner (LEED experience, reasonable cost)

---

### **Pair 3: Industrial Warehouse Expansion**
- **Project File**: `projects/project_3_industrial_warehouse.txt`
- **Bid File**: `bids/bids_project_3_industrial.json`
- **Test Focus**: Timeline criticality, fast-track construction, operational continuity
- **Expected Outcome**: TIC Industrial or FastTrack (timeline is CRITICAL)

---

### **Pair 4: Healthcare Facility Renovation**
- **Project File**: `projects/project_4_healthcare_facility.txt`
- **Bid File**: `bids/bids_project_4_healthcare.json`
- **Test Focus**: Regulatory compliance, patient safety, healthcare-specific requirements
- **Expected Outcome**: Turner Construction (full compliance, healthcare experience)

---

### **Pair 5: Retail Chain Renovation**
- **Project File**: `projects/project_5_retail_renovation.txt`
- **Bid File**: `bids/bids_project_5_retail.json`
- **Test Focus**: Multi-location coordination, cost control, standardization
- **Expected Outcome**: Moss Construction (multi-location experience, consistency)

---

## How to Use

### Step 1: Copy Project Description
1. Open the project description file (`.txt` file from `projects/` folder)
2. Copy the entire content

### Step 2: Prepare Bid JSON
1. Open the matching bid JSON file (from `bids/` folder)
2. The JSON already has the project description embedded, OR
3. Replace the `project.description` field with the content from Step 1

### Step 3: Test in Streamlit
1. Run `streamlit run app.py`
2. Upload the bid JSON file
3. Click "Evaluate Bids"
4. Review results

---

## Quick Reference Table

| Project # | Project Type | Project File | Bid File | Key Test Aspect |
|----------|-------------|--------------|----------|-----------------|
| 1 | Commercial Renovation | `project_1_commercial_renovation.txt` | `bids_project_1_commercial.json` | Risk vs cost, occupied building |
| 2 | Residential Complex | `project_2_residential_complex.txt` | `bids_project_2_residential.json` | LEED, cost control |
| 3 | Industrial Warehouse | `project_3_industrial_warehouse.txt` | `bids_project_3_industrial.json` | Timeline criticality |
| 4 | Healthcare Facility | `project_4_healthcare_facility.txt` | `bids_project_4_healthcare.json` | Compliance, patient safety |
| 5 | Retail Chain | `project_5_retail_renovation.txt` | `bids_project_5_retail.json` | Multi-location, cost control |

---

## Notes

- Each bid JSON file already contains the project description in the correct format
- You can modify the project description in the JSON if you want to test variations
- The system will search for contractor information online (Serper API)
- Real contractor names are used for realistic web search results
- Each project tests different evaluation priorities and constraints

