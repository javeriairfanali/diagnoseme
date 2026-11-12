"""
The engine behaves as BOTH
  1. a DECISION-MAKING system : decision tree -> symptom matching -> diagnosis level
  2. a DECISION-SUPPORT system: safety filters on medicines, emergency alerts, lab-test
                                advice and precautions tailored to the patient.

Rule inventory (55 rules, listed in RULES below):
  B1-B6   Branch rules of the decision tree      (6)
  N1-N3   Narrowing rules (stage 3)              (3)
  C1-C5   Classification / confidence rules      (5)
  E1-E11  Emergency (red-flag) rules             (11)
  D1-D15  Disease-specific support rules         (15)
  M1-M15  Medicine safety rules                  (15)
"""
from knowledge_base import (
    SYMPTOMS, STAGE1, FEVER_Q, RESP_Q, GI_Q, URINARY_Q, HEAT_Q, DANGER_Q,
    DISEASES, BRANCH_DISEASES, BRANCH_LABEL, NO_NSAID_DISEASES,
)


# RULEs

RULES = {
    # decision-tree branch rules
    "B1": "IF fever OR chills OR tick/livestock contact THEN open FEVER branch",
    "B2": "IF cough OR sore throat OR runny nose OR breathlessness THEN open CHEST/THROAT branch",
    "B3": "IF nausea/vomiting/diarrhoea/stomach pain/appetite loss/heartburn/jaundice THEN open GUT branch",
    "B4": "IF burning urine THEN open URINARY branch",
    "B5": "IF heat/sun exposure THEN open HEAT-ILLNESS branch",
    "B6": "IF symptoms exist but no branch opened (e.g. only headache/weakness) THEN open FEVER branch as fallback",
    #  stage-3 narrowing rules 
    "N1": "Score every disease of the open branches by partial symptom match",
    "N2": "Keep only the 4 best candidate diseases",
    "N3": "Ask the remaining unanswered symptoms of those candidates only (tree gets more specific)",
    # classification rules
    "C1": "IF all criteria matched (100%) AND key symptoms present THEN CONFIRMED",
    "C2": "IF >= 80% matched AND key symptoms present THEN NOT CONFIRMED - highly probable",
    "C3": "IF >= 60% matched AND key symptoms present THEN Probable",
    "C4": "IF >= 40% matched (or key symptom missing) THEN Possible",
    "C5": "IF < 40% matched THEN disease is ruled out (Unlikely)",
    #  emergency rules 
    "E1": "IF breathlessness AND chest pain THEN EMERGENCY (heart / lung)",
    "E2": "IF confusion / fits / fainting THEN EMERGENCY",
    "E3": "IF bleeding or bruising together with fever/tick contact THEN EMERGENCY (haemorrhagic fever)",
    "E4": "IF dehydration AND age < 5 or >= 65 THEN EMERGENCY",
    "E5": "IF blood in sputum THEN urgent chest evaluation",
    "E6": "IF hot dry skin AND heat exposure/high fever THEN EMERGENCY (heatstroke)",
    "E7": "IF jaundice AND (pregnant OR confusion) THEN EMERGENCY",
    "E8": "IF rice-water stools AND dehydration THEN EMERGENCY (cholera)",
    "E9": "IF infant (< 1 year) AND fever THEN see a doctor today",
    "E10": "IF blood in stool AND fever THEN urgent evaluation (invasive infection)",
    "E11": "IF fast breathing AND (age < 5 OR breathlessness) THEN EMERGENCY (respiratory distress)",
    #  disease specific support rules
    "D1": "Dengue + bleeding/bruising -> warning signs, go to hospital now",
    "D2": "Dengue + fever >= 3 days -> advise NS1/IgM and daily platelet count",
    "D3": "Malaria + cyclic fever -> advise blood film / ICT before any antimalarial",
    "D4": "Typhoid + fever >= 3 days -> advise blood culture / Typhidot, mention XDR typhoid",
    "D5": "TB + cough > 2 weeks -> advise sputum test, free DOTS treatment, isolate",
    "D6": "Hepatitis + pregnant -> Hepatitis E is dangerous in pregnancy, hospital review",
    "D7": "Cholera + dehydration -> ORS immediately and IV fluids at hospital",
    "D8": "Gastroenteritis + blood in stool -> stool culture, no anti-diarrhoeal tablets",
    "D9": "UTI + pregnant -> urine culture same day (risk to pregnancy)",
    "D10": "UTI + flank pain + fever -> possible kidney infection, urgent doctor visit",
    "D11": "COVID-19 + breathlessness -> check SpO2, hospital if below 94%",
    "D12": "Influenza + high-risk group (age < 5, >= 65, pregnant) -> doctor visit for antiviral",
    "D13": "Tonsillitis + white patches -> do strep test before antibiotic",
    "D14": "CCHF + tick/livestock contact -> isolate patient, hospital, no self-medication",
    "D15": "Heatstroke -> immediate cooling and hospital if confusion / no sweating",
    #  medicine safety rules 
    "M1": "IF age < 12 THEN no dose is given by the system (dose depends on weight: use label/pediatrician)",
    "M2": "IF age < 2 THEN every medicine must be approved by a pediatrician",
    "M3": "IF pregnant THEN remove NSAIDs and tetracyclines; doctor must approve every medicine",
    "M4": "IF NSAID allergy OR asthma THEN remove NSAIDs (ibuprofen, aspirin, diclofenac)",
    "M5": "IF ulcer / gastritis history THEN remove NSAIDs",
    "M6": "IF kidney disease THEN remove NSAIDs",
    "M7": "IF liver disease OR hepatitis suspected THEN paracetamol only if a doctor allows",
    "M8": "IF penicillin allergy THEN remove penicillin-group antibiotics",
    "M9": "IF hypertension THEN remove decongestants (pseudoephedrine)",
    "M10": "IF diabetes THEN avoid sugary syrups/drinks, check blood sugar, ORS only as directed",
    "M11": "IF age >= 65 THEN extra caution: sedating antihistamines and all combinations need doctor advice",
    "M12": "IF age < 16 THEN never give aspirin (Reye syndrome)",
    "M13": "IF medicine is prescription-only (Rx) THEN it is shown for information; test + doctor first",
    "M14": "IF dengue / chikungunya / malaria / CCHF is a candidate THEN remove ALL NSAIDs (bleeding risk)",
    "M15": "IF loperamide AND (age < 12 OR blood in stool OR fever) THEN remove it",
}


def rule_count():
    return len(RULES)


def fire(trace, rule_id, detail=""):
    """Record that a rule fired (for the 'Why this result?' explanation)."""
    if trace is not None:
        trace.append((rule_id, RULES[rule_id] + (f"  [{detail}]" if detail else "")))



# STAGE 1 -> STAGE 2 : which branches of the decision tree to open

def active_branches(facts, trace=None):
    branches = []
    if "fever" in facts or "chills" in facts or "tick_contact" in facts:       # B1
        branches.append("FEVER")
        fire(trace, "B1")
    if ("cough" in facts or "sore_throat" in facts or "runny_nose" in facts
            or "breathless" in facts):                                          # B2
        branches.append("RESP")
        fire(trace, "B2")
    if (facts & {"nausea", "vomiting", "diarrhea", "abd_pain", "loss_appetite",
                 "heartburn", "jaundice"}):                                      # B3
        branches.append("GI")
        fire(trace, "B3")
    if "burning_urine" in facts:                                                # B4
        branches.append("URINARY")
        fire(trace, "B4")
    if "heat_exposure" in facts:                                                # B5
        branches.append("HEAT")
        fire(trace, "B5")
    if not branches and facts:                                                  # B6
        branches.append("FEVER")
        fire(trace, "B6")
    return branches


def stage2_questions(branches, asked):
    """Questions of the opened branches + always-on danger signs, minus already asked."""
    qs = list(DANGER_Q)
    if "FEVER" in branches:
        qs += FEVER_Q
    if "RESP" in branches:
        qs += RESP_Q
    if "GI" in branches:
        qs += GI_Q
    if "URINARY" in branches:
        qs += URINARY_Q
    if "HEAT" in branches:
        qs += HEAT_Q
    seen, out = set(), []
    for q in qs:
        if q not in asked and q not in seen:
            seen.add(q)
            out.append(q)
    return out



# SCORING

def score_disease(did, facts):
    d = DISEASES[did]
    matched = [s for s in d["symptoms"] if s in facts]
    missing = [s for s in d["symptoms"] if s not in facts]
    keys_ok = all(k in facts for k in d["keys"])
    return matched, missing, keys_ok


def classify(matched_n, total, keys_ok, trace=None):
    """Confidence tiers. Returns (label, level)."""
    pct = matched_n / total
    if pct == 1.0 and keys_ok:                                  # C1
        fire(trace, "C1", f"{matched_n}/{total}")
        return "CONFIRMED", 4
    elif pct >= 0.8 and keys_ok:                                # C2
        fire(trace, "C2", f"{matched_n}/{total}")
        return "NOT CONFIRMED - Highly probable", 3
    elif pct >= 0.6 and keys_ok:                                # C3
        fire(trace, "C3", f"{matched_n}/{total}")
        return "Probable", 2
    elif pct >= 0.4:                                            # C4
        fire(trace, "C4", f"{matched_n}/{total}" + ("" if keys_ok else ", key symptom missing"))
        return "Possible", 1
    else:                                                       # C5
        fire(trace, "C5", f"{matched_n}/{total}")
        return "Unlikely", 0


def candidate_diseases(branches):
    ids = []
    for b in branches:
        for did in BRANCH_DISEASES[b]:
            if did not in ids:
                ids.append(did)
    return ids


def rank_candidates(facts, branches, trace=None, top_n=4):
    """Stage 3 narrowing: N1 score, N2 keep best 4."""
    fire(trace, "N1")
    scored = []
    for did in candidate_diseases(branches):
        matched, _, keys_ok = score_disease(did, facts)
        pct = len(matched) / len(DISEASES[did]["symptoms"])
        scored.append((pct, keys_ok, did))
    scored.sort(reverse=True)
    fire(trace, "N2")
    return [did for _, _, did in scored[:top_n]]


def stage3_questions(candidates, asked, trace=None):
    fire(trace, "N3")
    out = []
    for did in candidates:
        for s in DISEASES[did]["symptoms"]:
            if s not in asked and s not in out:
                out.append(s)
    return out


# DECISION SUPPORT 1 : emergency / red-flag rules

def emergency_check(facts, profile, trace=None):
    alerts = []
    age = profile["age"]
    if "breathless" in facts and "chest_pain" in facts:                                   # E1
        alerts.append("Shortness of breath with chest pain: go to the nearest emergency room now.")
        fire(trace, "E1")
    if "confusion" in facts:                                                              # E2
        alerts.append("Confusion, fits or fainting: this is an emergency. Go to hospital now.")
        fire(trace, "E2")
    if ("bleeding" in facts or "bruising" in facts) and ("fever" in facts or "tick_contact" in facts):  # E3
        alerts.append("Bleeding or bruising with fever can mean severe dengue or haemorrhagic fever. "
                      "Go to hospital immediately.")
        fire(trace, "E3")
    if "dehydration" in facts and (age < 5 or age >= 65):                                 # E4
        alerts.append("Dehydration in a young child or an older adult is dangerous. "
                      "Start ORS and go to hospital.")
        fire(trace, "E4")
    if "blood_sputum" in facts:                                                           # E5
        alerts.append("Coughing blood needs an urgent chest evaluation (TB, pneumonia).")
        fire(trace, "E5")
    if "hot_dry_skin" in facts and ("heat_exposure" in facts or "high_fever" in facts):   # E6
        alerts.append("Hot dry skin after heat exposure suggests heatstroke. Cool the person and call "
                      "an ambulance (Rescue 1122 where available).")
        fire(trace, "E6")
    if "jaundice" in facts and (profile["pregnant"] or "confusion" in facts):             # E7
        alerts.append("Jaundice in pregnancy or with confusion is an emergency. Go to hospital now.")
        fire(trace, "E7")
    if "rice_water" in facts and "dehydration" in facts:                                  # E8
        alerts.append("Rice-water stools with dehydration may be cholera. Take ORS and go to hospital now.")
        fire(trace, "E8")
    if age < 1 and "fever" in facts:                                                      # E9
        alerts.append("Fever in a baby under 1 year: see a pediatrician today.")
        fire(trace, "E9")
    if "blood_stool" in facts and "fever" in facts:                                       # E10
        alerts.append("Blood in stool with fever needs urgent evaluation.")
        fire(trace, "E10")
    if "fast_breath" in facts and (age < 5 or "breathless" in facts):                     # E11
        alerts.append("Fast breathing with difficulty is a danger sign. Go to hospital now.")
        fire(trace, "E11")
    return alerts



# DECISION SUPPORT 2 : disease-specific advice

def disease_rules(did, facts, profile, trace=None):
    notes = []
    age = profile["age"]
    preg = profile["pregnant"]
    if did == "dengue":
        if "bleeding" in facts or "bruising" in facts:                                    # D1
            notes.append("WARNING SIGNS present (bleeding). Go to hospital now for platelet monitoring.")
            fire(trace, "D1")
        elif "fever_3d" in facts:                                                         # D2
            notes.append("Fever for 3+ days: get CBC with platelets and NS1/IgM test; repeat platelets daily.")
            fire(trace, "D2")
    elif did == "malaria":
        if "cyclic_fever" in facts:                                                       # D3
            notes.append("Cyclic fever is typical of malaria. Get a blood film / ICT BEFORE taking antimalarials.")
            fire(trace, "D3")
    elif did == "typhoid":
        if "fever_3d" in facts:                                                           # D4
            notes.append("Fever 3+ days with stomach symptoms: get blood culture / Typhidot. "
                         "XDR (resistant) typhoid is reported in Sindh, so antibiotic choice is for the doctor.")
            fire(trace, "D4")
    elif did == "tb":
        if "cough_2w" in facts:                                                           # D5
            notes.append("Cough over 2 weeks: sputum AFB / GeneXpert test. Treatment is free at DOTS centres. "
                         "Cover your mouth and keep the room ventilated.")
            fire(trace, "D5")
    elif did == "hepatitis":
        if preg:                                                                          # D6
            notes.append("Hepatitis E can be severe in pregnancy: hospital review is needed.")
            fire(trace, "D6")
    elif did == "cholera":
        if "dehydration" in facts:                                                        # D7
            notes.append("Start ORS now and go to hospital for IV fluids.")
            fire(trace, "D7")
    elif did == "gastro":
        if "blood_stool" in facts:                                                        # D8
            notes.append("Blood in stool: do a stool culture and do NOT take anti-diarrhoeal tablets.")
            fire(trace, "D8")
    elif did == "uti":
        if preg:                                                                          # D9
            notes.append("UTI in pregnancy: urine culture the same day.")
            fire(trace, "D9")
        if "flank_pain" in facts and "fever" in facts:                                    # D10
            notes.append("Back/side pain with fever suggests a kidney infection. See a doctor today.")
            fire(trace, "D10")
    elif did == "covid":
        if "breathless" in facts:                                                         # D11
            notes.append("Check oxygen (SpO2). If below 94%, go to hospital.")
            fire(trace, "D11")
    elif did == "influenza":
        if age < 5 or age >= 65 or preg:                                                  # D12
            notes.append("You are in a high-risk group for flu: see a doctor early (antiviral may be needed).")
            fire(trace, "D12")
    elif did == "tonsillitis":
        if "white_patches" in facts:                                                      # D13
            notes.append("White patches on tonsils: strep throat is possible. Do a throat swab before antibiotics.")
            fire(trace, "D13")
    elif did == "cchf":
        if "tick_contact" in facts:                                                       # D14
            notes.append("Tick/livestock contact + fever: isolate, wear gloves, go to hospital. Do NOT self-medicate.")
            fire(trace, "D14")
    elif did == "heatstroke":                                                             # D15
        if "confusion" in facts or "hot_dry_skin" in facts:
            notes.append("Cool the body immediately (shade, wet cloths, fan) and go to hospital.")
        else:
            notes.append("Move to shade, drink ORS and rest; if symptoms worsen go to hospital.")
        fire(trace, "D15")
    return notes

# DECISION SUPPORT 3 : medicine safety filter

def filter_medicines(did, facts, profile, nsaid_ban, hepatitis_possible, trace=None):
    kept, removed = [], []
    age = profile["age"]
    for m in DISEASES[did]["meds"]:
        tags = m["tags"]
        reason = None
        note = ""

        #  reasons to REMOVE a medicine 
        if "nsaid" in tags:
            if nsaid_ban:                                                                 # M14
                reason = "NSAIDs are banned when dengue/chikungunya/malaria/CCHF is possible (bleeding risk)"
                fire(trace, "M14", m["generic"])
            elif profile["pregnant"]:                                                     # M3
                reason = "NSAIDs are unsafe in pregnancy"
                fire(trace, "M3", m["generic"])
            elif profile["allergy_nsaid"] or profile["asthma"]:                           # M4
                reason = "NSAID allergy / asthma"
                fire(trace, "M4", m["generic"])
            elif profile["ulcer"]:                                                        # M5
                reason = "Ulcer / gastritis history"
                fire(trace, "M5", m["generic"])
            elif profile["kidney"]:                                                       # M6
                reason = "Kidney disease"
                fire(trace, "M6", m["generic"])
        if reason is None and "tetracycline" in tags and (profile["pregnant"] or age < 8):  # M3
            reason = "Tetracyclines are unsafe in pregnancy and young children"
            fire(trace, "M3", m["generic"])
        if reason is None and "antibiotic_pen" in tags and profile["allergy_penicillin"]:  # M8
            reason = "Penicillin allergy"
            fire(trace, "M8", m["generic"])
        if reason is None and "decongestant" in tags and profile["hypertension"]:          # M9
            reason = "High blood pressure"
            fire(trace, "M9", m["generic"])
        if reason is None and "antimotility" in tags and (
                age < 12 or "blood_stool" in facts or "fever" in facts):                   # M15
            reason = "Loperamide is unsafe for children, bloody stool or fever"
            fire(trace, "M15", m["generic"])

        if reason:
            removed.append((m["generic"], reason))
            continue

        #  reasons to ADD A WARNING to a medicine that stays 
        if "paracetamol" in tags and (profile["liver"] or hepatitis_possible):             # M7
            note = "Use only if your doctor allows (liver)."
            fire(trace, "M7", m["generic"])
        elif "antihistamine" in tags and age >= 65:                                        # M11
            note = "May cause drowsiness/confusion at your age: ask a doctor first."
            fire(trace, "M11", m["generic"])
        elif m["kind"] == "Rx":                                                            # M13
            note = "Prescription only: get tested and consult a doctor first."
            fire(trace, "M13", m["generic"])
        if age < 2:                                                                        # M2
            note = (note + " " if note else "") + "Pediatrician must approve."
            fire(trace, "M2", m["generic"])
        kept.append(dict(m, note=note))
    return kept, removed


def general_safety_notes(profile, facts, trace=None):
    notes = []
    age = profile["age"]
    if age < 12:                                                                           # M1
        notes.append("Child under 12: dose depends on weight. Follow the product label or ask a "
                     "pediatrician/pharmacist. This system does not give doses.")
        fire(trace, "M1")
    if age < 16:                                                                           # M12
        notes.append("Never give aspirin to anyone under 16 (risk of Reye syndrome).")
        fire(trace, "M12")
    if profile["diabetes"]:                                                                # M10
        notes.append("Diabetes: avoid sugary syrups and drinks, monitor blood sugar during illness, "
                     "use ORS as directed.")
        fire(trace, "M10")
    if profile["pregnant"]:
        notes.append("Pregnancy: every medicine, even OTC, must be approved by your doctor.")
    return notes

# MAIN INFERENCE:  

def evaluate(facts, profile):
    trace = []
    facts = set(facts)
    branches = active_branches(facts, trace)
    result = {"branches": branches, "diseases": [], "emergencies": [], "general_notes": [],
              "nsaid_ban": False, "trace": trace, "message": ""}

    if not branches:
        result["message"] = "No symptoms selected. Please go back and select at least one symptom."
        return result

    # 1. score all diseases of opened branches
    rows = []
    for did in candidate_diseases(branches):
        matched, missing, keys_ok = score_disease(did, facts)
        total = len(DISEASES[did]["symptoms"])
        label, level = classify(len(matched), total, keys_ok)      # (no trace yet)
        rows.append({"id": did, "matched": matched, "missing": missing, "keys_ok": keys_ok,
                     "total": total, "pct": len(matched) / total, "label": label, "level": level})
    rows.sort(key=lambda r: (r["level"], r["pct"], len(r["matched"])), reverse=True)
    shown = [r for r in rows if r["level"] >= 1][:4]

    # 2. record classification rules only for the diseases we show
    for r in shown:
        classify(len(r["matched"]), r["total"], r["keys_ok"], trace)
    if not shown:
        fire(trace, "C5", "no disease reached 40%")
        result["message"] = ("No disease matched strongly enough (below 40% of criteria). "
                             "Your symptoms are non-specific. Please consult a general physician.")

    # 3. decision support
    shown_ids = {r["id"] for r in shown}
    nsaid_ban = bool(shown_ids & NO_NSAID_DISEASES)
    hepatitis_possible = "hepatitis" in shown_ids
    result["nsaid_ban"] = nsaid_ban
    result["emergencies"] = emergency_check(facts, profile, trace)
    result["general_notes"] = general_safety_notes(profile, facts, trace)

    for r in shown:
        d = DISEASES[r["id"]]
        meds, removed = filter_medicines(r["id"], facts, profile, nsaid_ban, hepatitis_possible, trace)
        r.update({
            "name": d["name"],
            "matched_labels": [SYMPTOMS[s] for s in r["matched"]],
            "missing_labels": [SYMPTOMS[s] for s in r["missing"]],
            "tests": d["tests"], "precautions": d["precautions"], "avoid": d["avoid"],
            "meds": meds, "removed": removed,
            "notes": disease_rules(r["id"], facts, profile, trace),
        })
        result["diseases"].append(r)
    return result



# REPORT 

def build_report(profile, facts, result):
    L = ["DIAGNOSEME - CONSULTATION REPORT", "=" * 40,
                  f"Age: {profile['age']}  Gender: {profile['gender']}"
         + (f"  Pregnant: {'Yes' if profile['pregnant'] else 'No'}" if profile["gender"] == "Female" else ""),
         "Symptoms reported: " + ", ".join(SYMPTOMS[s] for s in sorted(facts)), ""]
    for a in result["emergencies"]:
        L.append("!! EMERGENCY: " + a)
    for r in result["diseases"]:
        L += ["", f"{r['name']} - {r['label']} ({len(r['matched'])}/{r['total']} criteria)",
              "  Tests: " + r["tests"], "  Precautions: " + r["precautions"]]
        for n in r["notes"]:
            L.append("  Note: " + n)
        for m in r["meds"]:
            L.append(f"  Medicine [{m['kind']}]: {m['generic']} ({m['brands']}) - {m['purpose']} {m['note']}")
        for g, why in r["removed"]:
            L.append(f"  Removed for safety: {g} ({why})")
    for n in result["general_notes"]:
        L.append("Safety: " + n)
    L += ["", "DISCLAIMER: Educational decision-support tool, not a replacement for a doctor."]
    return "\n".join(L)
