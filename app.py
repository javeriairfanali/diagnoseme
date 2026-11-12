import pandas as pd
import streamlit as st

import engine
from knowledge_base import SYMPTOMS, STAGE1, DISEASES, BRANCH_LABEL

st.set_page_config(page_title="DiagnoseMe - Pakistan Health Expert System",
                   page_icon="🩺", layout="wide")

# toolbar clutter and centre the three dashboard boxes
st.markdown(
    """
    <style>
    #MainMenu {display: none !important;}
    [data-testid="stMetric"] {text-align: center; align-items: center;}
    [data-testid="stMetricLabel"] {justify-content: center;}
    </style>
    """,
    unsafe_allow_html=True,
)

# State

DEFAULT_PROFILE = dict(age=25, gender="Male", pregnant=False, allergy_nsaid=False,
                       allergy_penicillin=False, asthma=False, ulcer=False, kidney=False,
                       liver=False, hypertension=False, diabetes=False)

CONDITIONS = {
    "Allergy to painkillers (aspirin / ibuprofen)": "allergy_nsaid",
    "Allergy to penicillin / amoxicillin": "allergy_penicillin",
    "Asthma": "asthma",
    "Stomach ulcer / chronic gastritis": "ulcer",
    "Kidney disease": "kidney",
    "Liver disease": "liver",
    "High blood pressure": "hypertension",
    "Diabetes": "diabetes",
}

PAGES = ["Dashboard", "Health Check", "Conditions", "How it works", "Quick demo cases"]

DEMO_INFO = {
    "Dengue": "Fever, headache, pain behind the eyes, body and joint pain, rash and nausea.",
    "Heatwave": "Long sun exposure in extreme heat with high fever, hot dry skin, dizziness and "
                "confusion (age 60).",
}

STEP_NAMES = ["Patient profile", "Common symptoms", "Branch questions",
              "Narrowing down", "Result"]

DEMOS = {
    "Dengue": (set(DISEASES["dengue"]["symptoms"][:8]), {}),
    "Heatwave": (
        {"heat_exposure", "high_fever", "hot_dry_skin", "confusion", "dizziness", "headache"},
        {"age": 60}),
}

RULE_GROUPS = {"B": "Decision-tree branch", "N": "Narrowing", "C": "Classification",
               "E": "Emergency", "D": "Disease support", "M": "Medicine safety"}


def count(prefix):
    return sum(1 for r in engine.RULES if r.startswith(prefix))


ss = st.session_state
ss.setdefault("page", "Dashboard")
ss.setdefault("step", 0)
ss.setdefault("facts", set())
ss.setdefault("asked", set())
ss.setdefault("profile", dict(DEFAULT_PROFILE))
ss.setdefault("candidates", [])


def restart():
    ss.page = "Health Check"
    ss.step = 0
    ss.facts = set()
    ss.asked = set()
    ss.profile = dict(DEFAULT_PROFILE)
    ss.candidates = []


def load_demo(name):
    facts, prof = DEMOS[name]
    ss.page = "Health Check"
    ss.facts = set(facts)
    ss.asked = set(SYMPTOMS)
    ss.profile = dict(DEFAULT_PROFILE, **prof)
    ss.step = 4


def save_answers(answers):
    """answers = {symptom_id: bool}. Store yes-answers in facts, remember what was asked."""
    for sid, yes in answers.items():
        if yes:
            ss.facts.add(sid)
        else:
            ss.facts.discard(sid)
        ss.asked.add(sid)


def ask_block(symptom_ids, columns=3):
    """Render yes/no checkboxes; returns dict of answers."""
    answers = {}
    cols = st.columns(columns)
    for i, sid in enumerate(symptom_ids):
        answers[sid] = cols[i % columns].checkbox(
            SYMPTOMS[sid], value=(sid in ss.facts), key=f"cb_{sid}")
    return answers


def stage2_list():
    return engine.stage2_questions(engine.active_branches(ss.facts), set(STAGE1))


def stage3_list():
    asked_before = set(STAGE1) | set(stage2_list())
    return engine.stage3_questions(ss.candidates, asked_before)


def nav(back_to=None, next_label="Next", next_enabled=True):
    """Back / Next buttons. Returns True when Next is pressed."""
    c1, c2, _ = st.columns([1, 1, 4])
    if back_to is not None and c1.button("Back"):
        ss.step = back_to
        st.rerun()
    return c2.button(next_label, type="primary", disabled=not next_enabled)



# Sidebar

with st.sidebar:
    st.header("🩺 DiagnoseMe")
    st.caption("Pakistan's disease detection and medicine advice expert system.")
    st.button("Start a new consultation", on_click=restart, type="primary")
    st.radio("Menu", PAGES, key="page", label_visibility="collapsed")


    st.markdown(
        """
        <div style="
            color: #A0A8B8;
            font-size: 12px;
            line-height: 1.6;
            padding: 12px 5px;
        ">
            Educational decision-support tool.<br>
            Not a substitute for medical advice.
        </div>
        """,
        unsafe_allow_html=True
    )


# PAGE 1 : Dashboard

def page_dashboard():
    st.title("🩺 DiagnoseMe: Pakistan Health Expert System")
    st.caption("Tell us your symptoms. The system asks smart follow-up questions (decision tree), "
               "detects the most likely diseases and suggests safe medicines for YOU.")
    box1, box2, box3 = st.columns(3)
    for box, label, value in [(box1, "Conditions (IF-ELSE rules)", engine.rule_count()),
                              (box2, "Diseases covered", len(DISEASES)),
                              (box3, "Symptoms / facts", len(SYMPTOMS))]:
        with box.container(border=True):
            st.metric(label, value)
    st.subheader("Conditions by group")
    chart_df = pd.DataFrame({"Conditions": [count(k) for k in RULE_GROUPS]},
                            index=list(RULE_GROUPS.values()))
    st.bar_chart(chart_df)
    st.info("Open **Health Check** from the left menu to start a consultation, or try "
            "**Quick demo cases**.")


# PAGE 2 : Health Check (the consultation wizard)

def page_health_check():
    st.title("Health Check")
    st.progress(ss.step / (len(STEP_NAMES) - 1))
    st.markdown(f"**Step {ss.step + 1} of {len(STEP_NAMES)}: {STEP_NAMES[ss.step]}**")

    
    # STEP 0 : profile
    
    if ss.step == 0:
        p = ss.profile
        c1, c2, c3 = st.columns(3)
        age = c1.number_input("Patient age (years, 0 = under 1 year)", 0, 110, int(p["age"]))
        gender = c2.selectbox("Gender", ["Male", "Female"],
                              index=["Male", "Female"].index(p["gender"]))
        pregnant = False
        if gender == "Female" and 12 <= age <= 55:
            pregnant = c3.checkbox("Pregnant?", value=p["pregnant"])
        st.markdown("**Existing conditions / allergies** (important for medicine safety)")
        cond_cols = st.columns(2)
        chosen = [label for i, label in enumerate(CONDITIONS)
                  if cond_cols[i % 2].checkbox(label, value=bool(p[CONDITIONS[label]]),
                                               key=f"cond_{CONDITIONS[label]}")]
        if nav(back_to=None):
            ss.profile = dict(DEFAULT_PROFILE, age=int(age), gender=gender, pregnant=pregnant,
                              **{v: (k in chosen) for k, v in CONDITIONS.items()})
            ss.step = 1
            st.rerun()

    
    # STEP 1 : common symptoms (root of tree)
    
    elif ss.step == 1:
        st.write("Tick **every symptom you have right now**. Do not worry if you are unsure; "
                 "more specific questions come next.")
        answers = ask_block(STAGE1, columns=3)
        if not any(answers.values()):
            st.info("Select at least one symptom to continue.")
        if nav(back_to=0, next_enabled=any(answers.values())):
            save_answers(answers)
            ss.step = 2
            st.rerun()

    
    # STEP 2 : branch questions
    
    elif ss.step == 2:
        branches = engine.active_branches(ss.facts)
        st.success("Decision tree opened: " + ", ".join(BRANCH_LABEL[b] for b in branches))
        questions = stage2_list()
        st.write("Now some more specific questions. Tick the ones that apply.")
        answers = ask_block(questions, columns=2)
        if nav(back_to=1):
            save_answers(answers)
            ss.candidates = engine.rank_candidates(ss.facts, branches)
            ss.step = 3 if stage3_list() else 4
            st.rerun()

    
    # STEP 3 : narrowing to the 4 best candidates
    
    elif ss.step == 3:
        names = [DISEASES[d]["name"] for d in ss.candidates]
        st.info("The tree has narrowed down to: **" + "  |  ".join(names) + "**")
        remaining = stage3_list()
        st.write("A few final questions to separate these diseases:")
        answers = ask_block(remaining, columns=2)
        if nav(back_to=2, next_label="Show result"):
            save_answers(answers)
            ss.step = 4
            st.rerun()


    # STEP 4 : result
    else:
        result = engine.evaluate(ss.facts, ss.profile)
        st.caption("Reported: " + ", ".join(SYMPTOMS[s] for s in sorted(ss.facts)))

        for alert in result["emergencies"]:
            st.error("🚨 EMERGENCY: " + alert)

        if result["message"]:
            st.warning(result["message"])

        for r in result["diseases"]:
            with st.container(border=True):
                st.subheader(f"{r['name']}")
                text = f"**{r['label']}**: {len(r['matched'])} of {r['total']} criteria matched"
                if r["level"] == 4:
                    st.success(text + ". All clinical criteria are met. A lab test is still needed to prove it.")
                elif r["level"] == 3:
                    st.warning(text + ". Not confirmed yet: some criteria are missing.")
                else:
                    st.info(text)
                st.progress(r["pct"])

                m1, m2 = st.columns(2)
                m1.markdown("**Matched symptoms**")
                m1.write("\n".join("- " + x for x in r["matched_labels"]) or "-")
                m2.markdown("**Not present / not reported**")
                m2.write("\n".join("- " + x for x in r["missing_labels"]) or "-")

                for n in r["notes"]:
                    st.warning("Support note: " + n)

                st.markdown("**Suggested medicines (safe for your profile)**")
                if r["meds"]:
                    rows = ["| Medicine | Brands in Pakistan | Type | Purpose | Note |",
                            "|---|---|---|---|---|"]
                    for m in r["meds"]:
                        rows.append(f"| {m['generic']} | {m['brands']} | {m['kind']} | {m['purpose']} | {m['note']} |")
                    st.markdown("\n".join(rows))
                else:
                    st.write("No safe medicine can be suggested by this system. Please see a doctor.")
                for generic, why in r["removed"]:
                    st.error(f"Removed for your safety: {generic} ({why})")

                st.markdown("**Recommended tests:** " + r["tests"])
                st.markdown("**Precautions:** " + r["precautions"])
                st.markdown("**Avoid:** " + "; ".join(r["avoid"]))

        if result["nsaid_ban"]:
            st.error("Do NOT take aspirin, ibuprofen (Brufen), diclofenac or combination cold-flu tablets "
                     "containing them while dengue / malaria / CCHF is possible.")
        for n in result["general_notes"]:
            st.info(n)

        with st.expander("Why this result? (rules that fired)"):
            for rid, text in result["trace"]:
                st.markdown(f"- **{rid}**: {text}")

        st.download_button("Download report (.txt)",
                           engine.build_report(ss.profile, ss.facts, result),
                           file_name="diagnoseme_report.txt")
        c1, c2, _ = st.columns([1, 1, 4])
        if c1.button("Back"):
            if ss.candidates:
                ss.step = 3 if stage3_list() else 2
            else:
                ss.step = 1
            st.rerun()
        c2.button("New consultation", on_click=restart, type="primary")

        st.caption("Disclaimer: DiagnoseMe is an educational decision-support system built for a university "
                   "project. It cannot replace a licensed doctor. The system does not give doses.")


# PAGE 3 : Conditions 

def page_conditions():
    st.title("Conditions")
    st.write("All %d IF-ELSE conditions of the expert system. Every condition is an explicit "
             "if / elif / else block in the code." % engine.rule_count())
    rows = ["| ID | Group | Condition |", "|---|---|---|"]
    for rid, text in engine.RULES.items():
        rows.append(f"| {rid} | {RULE_GROUPS[rid[0]]} | {text} |")
    st.markdown("\n".join(rows))



# PAGE 4 : How it works

def page_how_it_works():
    st.title("How it works")
    st.markdown(
        "1. **Profile**: age, gender, allergies and conditions (keeps medicines safe).\n"
        "2. **Common symptoms**: you tick what you feel (root of the decision tree).\n"
        "3. **Branch questions**: only the relevant branches open (fever, chest, gut, urinary, heat).\n"
        "4. **Narrowing**: the 4 likeliest diseases stay; only their remaining symptoms are asked.\n"
        "5. **Result**: diagnosis level, safe medicines, tests, precautions and emergency alerts.")
    st.subheader("Decision tree")
    st.code(
        "Common symptoms (root)\n"
        " |-- fever / chills / tick contact  -> FEVER branch\n"
        " |-- cough / sore throat / nose     -> CHEST branch\n"
        " |-- vomiting / diarrhoea / pain    -> GUT branch\n"
        " |-- burning urine                  -> URINARY branch\n"
        " |-- heat exposure                  -> HEAT branch\n"
        " |\n"
        "Branch questions + danger signs -> keep best 4 diseases -> ask their remaining symptoms -> result",
        language=None)
    st.subheader("Confidence levels")
    st.markdown(
        "| Matched criteria | Result |\n|---|---|\n"
        "| All, e.g. 10 of 10, with key symptoms | **CONFIRMED** |\n"
        "| 80% or more, e.g. 8 of 10 | **NOT CONFIRMED - Highly probable** |\n"
        "| 60% or more | Probable |\n"
        "| 40% or more | Possible |\n"
        "| Below 40% | Ruled out |")
    st.subheader("Two jobs in one system")
    st.markdown(
        "- **Decision making**: decision tree and symptom matching decide the disease and its confidence.\n"
        "- **Decision support**: emergency alerts, lab-test advice, precautions and a medicine safety "
        "filter that removes unsafe medicines (for example ibuprofen in dengue or pregnancy).")

# PAGE 5 : Quick demo cases

def page_demos():
    st.title("Quick demo cases")
    st.write("Pick a case. The system loads sample symptoms and shows the full result.")
    cols = st.columns(len(DEMO_INFO))
    for col, (name, text) in zip(cols, DEMO_INFO.items()):
        with col.container(border=True):
            st.subheader(name)
            st.write(text)
            st.button(f"Run {name} demo", key=f"demo_{name}", on_click=load_demo, args=(name,))



# show the page chosen in the left menu

if ss.page == "Dashboard":
    page_dashboard()
elif ss.page == "Health Check":
    page_health_check()
elif ss.page == "Conditions":
    page_conditions()
elif ss.page == "How it works":
    page_how_it_works()
else:
    page_demos()
