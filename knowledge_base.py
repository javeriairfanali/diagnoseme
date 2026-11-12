# 1. SYMPTOM / FACT DICTIONARY 

SYMPTOMS = {
    # common symptoms
    "fever": "Fever",
    "chills": "Chills / shivering",
    "headache": "Headache",
    "body_ache": "Severe body ache / muscle pain",
    "fatigue": "Weakness / tiredness",
    "cough": "Cough",
    "sore_throat": "Sore throat",
    "runny_nose": "Runny / blocked nose",
    "breathless": "Shortness of breath",
    "nausea": "Nausea",
    "vomiting": "Vomiting",
    "diarrhea": "Loose motions",
    "abd_pain": "Stomach pain",
    "loss_appetite": "Loss of appetite",
    "heartburn": "Burning in chest / stomach",
    "jaundice": "Yellow eyes or skin",
    "burning_urine": "Burning while passing urine",
    "rash": "Skin rash / red spots",
    "dizziness": "Dizziness",
    "heat_exposure": "Long exposure to heat / sun",
    "tick_contact": "Tick bite or handling livestock / slaughtering animals",
    #  fever branch 
    "high_fever": "High fever above 102 F / 39 C",
    "fever_3d": "Fever lasting 3 days or more",
    "cyclic_fever": "Fever comes in cycles: chills, then fever, then sweating (every 1-3 days)",
    "stepladder": "Fever rising step by step each day",
    "sweating_episodes": "Heavy sweating after fever episodes",
    "retro_orbital": "Pain behind the eyes",
    "joint_pain": "Joint pain",
    "joint_swelling": "Swollen / stiff joints",
    "bleeding": "Bleeding from gums / nose / in vomit",
    "bruising": "Unexplained bruises or purple spots on skin",
    "mosquito_exp": "Mosquito bites / stagnant water near home",
    #  respiratory branch
    "dry_cough": "Dry cough",
    "productive_cough": "Cough with phlegm",
    "cough_2w": "Cough lasting more than 2 weeks",
    "blood_sputum": "Blood in sputum (Khansi mein khoon)",
    "night_sweats": "Night sweats",
    "weight_loss": "Unexplained weight loss",
    "loss_smell": "Loss of smell or taste",
    "sneezing": "Frequent sneezing",
    "painful_swallow": "Pain while swallowing",
    "white_patches": "White patches / pus on tonsils",
    "neck_glands": "Swollen glands in the neck",
    "chest_pain": "Chest pain",
    "fast_breath": "Fast breathing (rapid breaths)",
    "tb_contact": "Close contact with a TB patient",
    #  gastro-intestinal branch 
    "watery_stool": "Watery stools (many times a day)",
    "rice_water": "Rice-water like stools (pale, milky)",
    "blood_stool": "Blood in stool",
    "dehydration": "Dehydration: dry mouth, sunken eyes, very little urine",
    "dirty_water": "Drank untreated water / ate street food recently",
    "constipation": "Constipation",
    "bloating": "Bloating / gas",
    "sour_belch": "Sour belching / acid coming up",
    "dark_urine": "Dark tea-coloured urine",
    "pale_stool": "Pale / clay-coloured stool",
    "ruq_pain": "Pain in upper right abdomen (liver area)",
    "cramps": "Muscle cramps",
    #  urinary branch 
    "freq_urine": "Frequent urge to urinate",
    "cloudy_urine": "Cloudy or foul-smelling urine",
    "lower_abd_pain": "Pain in lower abdomen",
    "flank_pain": "Pain in the back / side (kidney area)",
    # heat branch 
    "hot_dry_skin": "Hot, dry skin with no sweating",
    "confusion": "Confusion, fits or fainting",
}

# 2. DECISION-TREE QUESTION SETS

# Stage 1: common symptoms
STAGE1 = [
    "fever", "chills", "headache", "body_ache", "fatigue", "cough", "sore_throat",
    "runny_nose", "breathless", "nausea", "vomiting", "diarrhea", "abd_pain",
    "loss_appetite", "heartburn", "jaundice", "burning_urine", "rash", "dizziness",
    "heat_exposure", "tick_contact",
]

# Stage 2 (branch level): discriminating questions for each branch
FEVER_Q = ["high_fever", "fever_3d", "cyclic_fever", "retro_orbital",
           "joint_pain", "bleeding", "mosquito_exp"]
RESP_Q = ["dry_cough", "productive_cough", "cough_2w", "loss_smell",
          "painful_swallow", "sneezing", "chest_pain"]
GI_Q = ["watery_stool", "rice_water", "blood_stool", "dehydration",
        "dirty_water", "constipation", "bloating"]
URINARY_Q = ["freq_urine", "cloudy_urine", "lower_abd_pain", "flank_pain"]
HEAT_Q = ["high_fever", "hot_dry_skin", "confusion", "cramps"]
# Danger signs are always asked (safety first)
DANGER_Q = ["confusion", "bleeding", "fast_breath", "chest_pain", "dehydration"]

# 3. DISEASES  (17)   symptoms = defining criteria

def med(generic, brands, kind, purpose, tags=()):
    """Helper that builds a medicine record. kind = 'OTC' or 'Rx'."""
    return {"generic": generic, "brands": brands, "kind": kind,
            "purpose": purpose, "tags": set(tags)}


DISEASES = {
    "dengue": {
        "name": "Dengue Fever",
        "symptoms": ["fever", "high_fever", "headache", "retro_orbital", "body_ache",
                     "joint_pain", "rash", "nausea", "fatigue", "mosquito_exp"],
        "keys": ["fever"],
        "tests": "CBC with platelet count, NS1 antigen (days 1-5) or Dengue IgM/IgG.",
        "precautions": "Drink plenty of fluids, complete rest, use mosquito nets / repellent, "
                       "remove stagnant water. Platelets must be monitored daily.",
        "avoid": ["Aspirin, ibuprofen, diclofenac and other NSAIDs (risk of bleeding)"],
        "meds": [
            med("Paracetamol", "Panadol, Calpol", "OTC", "Reduces fever and pain", {"paracetamol"}),
            med("ORS (WHO formula) + fluids", "ORS sachets, coconut water, soups", "OTC",
                "Prevents dehydration"),
        ],
    },
    "chikungunya": {
        "name": "Chikungunya",
        "symptoms": ["fever", "high_fever", "joint_pain", "joint_swelling", "rash",
                     "headache", "body_ache", "fatigue", "mosquito_exp"],
        "keys": ["fever", "joint_pain"],
        "tests": "Chikungunya IgM / RT-PCR; CBC to rule out dengue.",
        "precautions": "Rest, fluids, mosquito protection. Joint pain can last weeks.",
        "avoid": ["NSAIDs until dengue is ruled out by a doctor"],
        "meds": [
            med("Paracetamol", "Panadol, Calpol", "OTC", "Fever and joint pain", {"paracetamol"}),
            med("ORS + fluids", "ORS sachets", "OTC", "Hydration"),
        ],
    },
    "malaria": {
        "name": "Malaria",
        "symptoms": ["fever", "chills", "cyclic_fever", "sweating_episodes", "headache",
                     "body_ache", "nausea", "vomiting", "fatigue", "mosquito_exp"],
        "keys": ["fever", "chills"],
        "tests": "Blood film (thick and thin smear) or Malaria rapid ICT test.",
        "precautions": "Sleep under a treated net, remove stagnant water. "
                       "Treatment depends on the parasite type, so test BEFORE taking medicine.",
        "avoid": ["Taking antimalarials without a positive test"],
        "meds": [
            med("Paracetamol", "Panadol, Calpol", "OTC", "Fever control", {"paracetamol"}),
            med("Antimalarial (chloroquine / artemether-lumefantrine / primaquine)", "As prescribed",
                "Rx", "Kills the parasite, doctor chooses after test", {"antimalarial"}),
        ],
    },
    "typhoid": {
        "name": "Typhoid (Enteric) Fever",
        "symptoms": ["fever", "fever_3d", "stepladder", "headache", "abd_pain",
                     "constipation", "loss_appetite", "fatigue", "dirty_water", "nausea"],
        "keys": ["fever", "fever_3d"],
        "tests": "Blood culture (best), Typhidot IgM or Widal (less reliable).",
        "precautions": "Drink boiled / filtered water, avoid street food, wash hands. "
                       "Note: drug-resistant (XDR) typhoid exists in Sindh, so antibiotic must be chosen by a doctor.",
        "avoid": ["Self-medicating with random antibiotics"],
        "meds": [
            med("Paracetamol", "Panadol, Calpol", "OTC", "Fever control", {"paracetamol"}),
            med("ORS + soft diet", "ORS sachets", "OTC", "Hydration and nutrition"),
            med("Antibiotic (azithromycin / cefixime / ceftriaxone)", "As prescribed", "Rx",
                "Treats the infection, chosen by doctor from culture", {"antibiotic"}),
        ],
    },
    "influenza": {
        "name": "Seasonal Influenza (Flu)",
        "symptoms": ["fever", "high_fever", "chills", "body_ache", "headache",
                     "fatigue", "dry_cough", "sore_throat", "runny_nose"],
        "keys": ["fever", "body_ache"],
        "tests": "Usually clinical; rapid flu test if needed.",
        "precautions": "Rest, warm fluids, steam inhalation, cover cough, stay home 3-5 days.",
        "avoid": ["Antibiotics (flu is a virus)"],
        "meds": [
            med("Paracetamol", "Panadol, Calpol", "OTC", "Fever and body ache", {"paracetamol"}),
            med("Ibuprofen", "Brufen", "OTC", "Body ache (alternative)", {"nsaid"}),
            med("Ibuprofen + pseudoephedrine (cold-flu combination)", "Arinac", "OTC",
                "Blocked nose and ache", {"nsaid", "decongestant"}),
            med("Oseltamivir", "As prescribed", "Rx", "Antiviral for high-risk patients", {"antiviral"}),
        ],
    },
    "covid": {
        "name": "COVID-19",
        "symptoms": ["fever", "dry_cough", "fatigue", "loss_smell", "sore_throat",
                     "body_ache", "headache", "breathless"],
        "keys": ["dry_cough"],
        "tests": "COVID-19 rapid antigen or PCR test; check oxygen level (SpO2).",
        "precautions": "Isolate, wear a mask, monitor SpO2. Go to hospital if SpO2 is below 94%.",
        "avoid": ["Antibiotics unless a doctor finds a bacterial infection"],
        "meds": [
            med("Paracetamol", "Panadol, Calpol", "OTC", "Fever and body ache", {"paracetamol"}),
            med("ORS + fluids", "ORS sachets", "OTC", "Hydration"),
            med("Antiviral for high-risk patients", "As prescribed", "Rx", "Doctor decision", {"antiviral"}),
        ],
    },
    "cold": {
        "name": "Common Cold",
        "symptoms": ["runny_nose", "sneezing", "sore_throat", "cough", "headache",
                     "fatigue", "body_ache"],
        "keys": ["runny_nose"],
        "tests": "No test needed.",
        "precautions": "Rest, warm fluids, saline nasal drops, steam, gargle with warm salt water.",
        "avoid": ["Antibiotics (they do not work on colds)"],
        "meds": [
            med("Paracetamol", "Panadol, Calpol", "OTC", "Headache and mild fever", {"paracetamol"}),
            med("Cetirizine / chlorpheniramine", "Zyrtec, Piriton", "OTC",
                "Runny nose and sneezing", {"antihistamine"}),
            med("Saline nasal drops / spray", "Saline drops", "OTC", "Clears blocked nose"),
            med("Pseudoephedrine decongestant", "Sudafed", "OTC", "Blocked nose", {"decongestant"}),
        ],
    },
    "gastro": {
        "name": "Acute Gastroenteritis / Food Poisoning",
        "symptoms": ["diarrhea", "watery_stool", "vomiting", "nausea", "abd_pain",
                     "fever", "loss_appetite", "dehydration", "dirty_water"],
        "keys": ["diarrhea"],
        "tests": "Stool R/E and culture if severe, bloody, or lasting over 3 days.",
        "precautions": "Small frequent sips of ORS, eat light food (banana, rice, toast), wash hands.",
        "avoid": ["Anti-diarrhoeal tablets (loperamide) if there is blood in stool or fever"],
        "meds": [
            med("ORS (WHO formula)", "ORS sachets", "OTC", "Replaces lost water and salts"),
            med("Zinc supplement", "Zinc syrup / tablets", "OTC", "Shortens diarrhoea (esp. children)"),
            med("Probiotic", "Probiotic sachets", "OTC", "Restores gut bacteria"),
            med("Paracetamol", "Panadol, Calpol", "OTC", "Fever and cramps", {"paracetamol"}),
            med("Loperamide", "Imodium", "OTC", "Slows loose motions (adults only)", {"antimotility"}),
        ],
    },
    "cholera": {
        "name": "Cholera (Severe Watery Diarrhoea)",
        "symptoms": ["diarrhea", "watery_stool", "rice_water", "vomiting",
                     "dehydration", "cramps", "dizziness", "dirty_water"],
        "keys": ["rice_water"],
        "tests": "Stool culture / rapid cholera test. Report to the health department.",
        "precautions": "This is an emergency: start ORS immediately and go to hospital for IV fluids.",
        "avoid": ["Waiting at home when dehydrated"],
        "meds": [
            med("ORS (WHO formula)", "ORS sachets", "OTC", "Start at once, sip continuously"),
            med("IV fluids (Ringer lactate)", "Hospital only", "Rx", "Corrects severe dehydration"),
            med("Antibiotic (azithromycin / doxycycline)", "As prescribed", "Rx",
                "Shortens illness", {"antibiotic", "tetracycline"}),
        ],
    },
    "hepatitis": {
        "name": "Viral Hepatitis (A / E)",
        "symptoms": ["jaundice", "dark_urine", "pale_stool", "fatigue", "nausea",
                     "loss_appetite", "ruq_pain", "fever", "dirty_water"],
        "keys": ["jaundice"],
        "tests": "LFT (ALT, bilirubin), Hepatitis A IgM, Hepatitis E IgM, HBsAg and Anti-HCV.",
        "precautions": "Complete rest, clean boiled water, no alcohol, no herbal or 'desi' liver remedies. "
                       "Hepatitis A vaccine is available for prevention.",
        "avoid": ["Alcohol, herbal remedies and unnecessary medicines (liver is inflamed)"],
        "meds": [
            med("Oral fluids + high-calorie light diet", "Glucose water, soups", "OTC", "Supportive care"),
            med("Paracetamol (restricted)", "Panadol", "OTC", "Only if a doctor allows", {"paracetamol"}),
        ],
    },
    "tb": {
        "name": "Pulmonary Tuberculosis (TB)",
        "symptoms": ["cough_2w", "productive_cough", "blood_sputum", "night_sweats",
                     "weight_loss", "fever", "fatigue", "loss_appetite", "chest_pain", "tb_contact"],
        "keys": ["cough_2w"],
        "tests": "Sputum AFB smear, GeneXpert, chest X-ray.",
        "precautions": "Cover mouth when coughing, ventilate room. Free DOTS treatment is available "
                       "through the National TB Control Programme centres.",
        "avoid": ["Stopping or skipping TB treatment once started"],
        "meds": [
            med("Anti-TB regimen (HRZE)", "Free at DOTS centres", "Rx",
                "6-month supervised treatment, never self-start", {"antitb"}),
        ],
    },
    "tonsillitis": {
        "name": "Tonsillitis / Strep Throat",
        "symptoms": ["sore_throat", "painful_swallow", "fever", "white_patches",
                     "neck_glands", "headache", "fatigue", "loss_appetite"],
        "keys": ["sore_throat"],
        "tests": "Rapid strep test or throat swab culture.",
        "precautions": "Warm salt-water gargles, warm fluids, rest, avoid cold drinks.",
        "avoid": ["Antibiotics unless the infection is bacterial"],
        "meds": [
            med("Paracetamol", "Panadol, Calpol", "OTC", "Pain and fever", {"paracetamol"}),
            med("Ibuprofen", "Brufen", "OTC", "Throat pain", {"nsaid"}),
            med("Throat lozenges", "Strepsils", "OTC", "Soothes throat"),
            med("Amoxicillin / penicillin", "As prescribed", "Rx",
                "Only if strep is confirmed", {"antibiotic", "antibiotic_pen"}),
        ],
    },
    "uti": {
        "name": "Urinary Tract Infection (UTI)",
        "symptoms": ["burning_urine", "freq_urine", "cloudy_urine", "lower_abd_pain",
                     "flank_pain", "fever", "nausea"],
        "keys": ["burning_urine"],
        "tests": "Urine R/E and urine culture and sensitivity.",
        "precautions": "Drink 2-3 litres of water daily, do not hold urine, maintain hygiene.",
        "avoid": ["Stopping antibiotics early"],
        "meds": [
            med("Plenty of water", "Water, barley water", "OTC", "Flushes bacteria"),
            med("Paracetamol", "Panadol", "OTC", "Pain and fever", {"paracetamol"}),
            med("Antibiotic (e.g. nitrofurantoin / cefixime)", "As prescribed", "Rx",
                "Chosen from urine culture", {"antibiotic"}),
        ],
    },
    "heatstroke": {
        "name": "Heat Exhaustion / Heatstroke",
        "symptoms": ["heat_exposure", "high_fever", "hot_dry_skin", "confusion",
                     "headache", "dizziness", "nausea", "cramps"],
        "keys": ["heat_exposure"],
        "tests": "Body temperature, blood tests in hospital.",
        "precautions": "Move to shade, remove extra clothes, cool body with wet cloths and fan, sip ORS.",
        "avoid": ["Giving fluids by mouth to an unconscious person"],
        "meds": [
            med("ORS / salt-sugar water", "ORS sachets", "OTC", "Replaces salts and water"),
        ],
    },
    "cchf": {
        "name": "Crimean-Congo Haemorrhagic Fever (CCHF)",
        "symptoms": ["fever", "high_fever", "headache", "body_ache", "bleeding",
                     "bruising", "vomiting", "abd_pain", "tick_contact"],
        "keys": ["tick_contact"],
        "tests": "CCHF PCR / IgM at a designated lab (e.g. NIH Islamabad, hospital lab).",
        "precautions": "Seen around Eid-ul-Adha: avoid direct contact with animal blood, wear gloves, "
                       "use tick repellent. Isolate the patient and go to hospital immediately.",
        "avoid": ["All NSAIDs and aspirin; touching the patient's blood without gloves"],
        "meds": [
            med("Ribavirin (hospital supervised)", "Hospital only", "Rx", "Antiviral", {"antiviral"}),
        ],
    },
    "gastritis": {
        "name": "Gastritis / Acidity (GERD)",
        "symptoms": ["heartburn", "sour_belch", "bloating", "abd_pain", "nausea",
                     "loss_appetite", "vomiting"],
        "keys": ["heartburn"],
        "tests": "Usually clinical; H. pylori test or endoscopy if persistent.",
        "precautions": "Small meals, avoid spicy / oily food, tea and smoking, do not lie down after eating.",
        "avoid": ["Painkillers like ibuprofen / aspirin on an empty stomach"],
        "meds": [
            med("Antacid (aluminium + magnesium hydroxide)", "Gaviscon, Mylanta", "OTC",
                "Quick relief from acidity", {"antacid"}),
            med("Omeprazole / esomeprazole", "Risek, Nexum", "OTC",
                "Reduces stomach acid (short course)", {"ppi"}),
        ],
    },
    "pneumonia": {
        "name": "Pneumonia (Chest Infection)",
        "symptoms": ["fever", "high_fever", "productive_cough", "breathless",
                     "fast_breath", "chest_pain", "chills", "fatigue", "loss_appetite"],
        "keys": ["breathless"],
        "tests": "Chest X-ray, CBC, oxygen saturation, sputum culture.",
        "precautions": "Needs a doctor the same day. Rest, fluids, sit upright, monitor breathing.",
        "avoid": ["Cough suppressants without a doctor's advice"],
        "meds": [
            med("Paracetamol", "Panadol, Calpol", "OTC", "Fever and chest pain", {"paracetamol"}),
            med("Antibiotic (amoxicillin-clavulanate / azithromycin)", "As prescribed", "Rx",
                "Treats bacterial pneumonia", {"antibiotic", "antibiotic_pen"}),
        ],
    },
}


# 4. TREE BRANCHES  ->  diseases that belong to each branch

BRANCH_DISEASES = {
    "FEVER": ["dengue", "chikungunya", "malaria", "typhoid", "influenza",
              "covid", "cchf", "pneumonia", "hepatitis"],
    "RESP": ["influenza", "covid", "cold", "tb", "tonsillitis", "pneumonia"],
    "GI": ["gastro", "cholera", "hepatitis", "typhoid", "gastritis"],
    "URINARY": ["uti"],
    "HEAT": ["heatstroke"],
}

BRANCH_LABEL = {
    "FEVER": "Fever branch",
    "RESP": "Chest / throat branch",
    "GI": "Stomach / gut branch",
    "URINARY": "Urinary branch",
    "HEAT": "Heat-illness branch",
}

# Diseases for which NSAIDs must never be suggested 
NO_NSAID_DISEASES = {"dengue", "chikungunya", "cchf", "malaria"}
