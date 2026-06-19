"""
Generate parallel bilingual (DE/EN) exam PDFs — Versions A, B, C.

Each version tests identical knowledge with the same 20 questions, but:
  - Question order is shuffled within each topic section
  - Answer options (A–D) are shuffled per question per version
This keeps exams fair and comparable while preventing copying.

Output files:
  exam-mc-questions/exam_student_A.pdf   exam_solution_A.pdf
  exam-mc-questions/exam_student_B.pdf   exam_solution_B.pdf
  exam-mc-questions/exam_student_C.pdf   exam_solution_C.pdf
"""

import os, random
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether, PageBreak,
)
from reportlab.lib.colors import HexColor, black, white

# ── colour palette ───────────────────────────────────────────────────────────
BLUE   = HexColor("#1a3a6b")
LGRAY  = HexColor("#f4f4f4")
MGRAY  = HexColor("#dddddd")
DGRAY  = HexColor("#555555")
GREEN  = HexColor("#1a7a3a")
LGREEN = HexColor("#d4edda")
RED    = HexColor("#cc0000")

VERSION_COLORS = {"A": HexColor("#1a3a6b"), "B": HexColor("#7b1a1a"), "C": HexColor("#1a5c1a")}

# ── Master question pool (4 per topic, 5 topics = 20 total) ─────────────────
# (topic, question_de, question_en, [opts_de x4], [opts_en x4], correct_index)
QUESTIONS = [
    # ── STATISTICS ───────────────────────────────────────────────────────────
    (
        "Statistik / Statistics",
        "Welche Messskala erlaubt nur die Identifikation und Klassifikation von Objekten, impliziert jedoch keine Rangordnung oder Abstände?",
        "Which measurement scale allows only the identification and classification of objects, but does not imply any ranking or distance?",
        ["Ordinalskala", "Intervallskala", "Nominalskala", "Ratioskala"],
        ["Ordinal scale", "Interval scale", "Nominal scale", "Ratio scale"],
        2,
    ),
    (
        "Statistik / Statistics",
        "Bei einem Datensatz mit Immobilienpreisen und mehreren extremen Ausreißern nach oben – welches Lagemaß ist am robustesten?",
        "In a dataset of property prices with several extreme high values, which measure of central tendency is most robust?",
        ["Mittelwert", "Median", "Modus", "Spannweite"],
        ["Mean", "Median", "Mode", "Range"],
        1,
    ),
    (
        "Statistik / Statistics",
        "Gemäß der 68-95-99,7-Regel: Wie viel Prozent der Werte einer Normalverteilung liegen innerhalb von ±2 Standardabweichungen?",
        "According to the 68-95-99.7 rule, approximately what percentage of values in a normal distribution fall within ±2 standard deviations of the mean?",
        ["68 %", "95 %", "99,7 %", "90 %"],
        ["68%", "95%", "99.7%", "90%"],
        1,
    ),
    (
        "Statistik / Statistics",
        "Welcher statistische Test ist am geeignetsten, wenn die unabhängige Variable nominal und die abhängige Variable metrisch ist?",
        "Which statistical test is most appropriate when the independent variable is nominal and the dependent variable is metric?",
        ["Chi-Quadrat-Test", "Logistische Regression", "t-Test oder ANOVA", "Spearman-Korrelation"],
        ["Chi-square test", "Logistic regression", "t-test or ANOVA", "Spearman correlation"],
        2,
    ),
    # ── REGRESSION ───────────────────────────────────────────────────────────
    (
        "Regressionsanalyse / Regression Analysis",
        "In einem einfachen linearen Regressionsmodell Y = b₀ + b₁X + ε steht der Term ε für:",
        "In a simple linear regression model Y = b₀ + b₁X + ε, the term ε represents:",
        ["Den vorhergesagten Wert von Y", "Den Achsenabschnitt (Intercept)", "Den Fehlerterm (Residuum)", "Den Steigungskoeffizienten"],
        ["The predicted value of Y", "The intercept coefficient", "The error term (residual)", "The slope coefficient"],
        2,
    ),
    (
        "Regressionsanalyse / Regression Analysis",
        "Warum wird das korrigierte R² dem R² vorgezogen, wenn Modelle mit unterschiedlicher Anzahl an Prädiktoren verglichen werden?",
        "Why is adjusted R² preferred over R² when comparing models with different numbers of predictors?",
        ["Das korrigierte R² ist immer größer als R²", "Das korrigierte R² bestraft nicht-informative Prädiktoren", "Das korrigierte R² misst Vorhersagegenauigkeit direkt", "Das korrigierte R² ist einfacher zu berechnen"],
        ["Adjusted R² is always larger than R²", "Adjusted R² penalizes for non-informative predictors", "Adjusted R² measures prediction accuracy directly", "Adjusted R² is easier to compute"],
        1,
    ),
    (
        "Regressionsanalyse / Regression Analysis",
        "Ein VIF-Wert größer als 10 weist auf Folgendes hin:",
        "A VIF value greater than 10 indicates:",
        ["Keine Multikollinearität", "Moderate Multikollinearität", "Schwerwiegende Multikollinearität – der Prädiktor sollte überdacht werden", "Perfekte Modellanpassung"],
        ["No multicollinearity", "Moderate multicollinearity", "Severe multicollinearity – the predictor should be reconsidered", "Perfect model fit"],
        2,
    ),
    (
        "Regressionsanalyse / Regression Analysis",
        "Eine Preiselastizität von −2,21 bedeutet:",
        "A price elasticity of −2.21 means:",
        ["Ein Preisanstieg von 1 % führt zu einem Rückgang der Nachfrage um 2,21 Einheiten", "Ein Preisanstieg von 1 % führt zu einem Rückgang der Nachfrage um 2,21 %", "Ein Preisanstieg von 2,21 % führt zu einem Nachfragerückgang von 1 %", "Die Nachfrage ist unelastisch"],
        ["A 1% price increase leads to a 2.21-unit decrease in demand", "A 1% price increase leads to a 2.21% decrease in demand", "A 2.21% price increase leads to a 1% decrease in demand", "Demand is inelastic"],
        1,
    ),
    # ── MEDIATION & MODERATION ────────────────────────────────────────────────
    (
        "Mediation & Moderation",
        "Gemäß Zhao, Lynch & Chen (2010): Was ist die einzige statistische Voraussetzung für den Nachweis von Mediation?",
        "According to Zhao, Lynch & Chen (2010), what is the only statistical requirement to establish mediation?",
        ["Ein signifikanter Gesamteffekt von X auf Y (Pfad c)", "Ein signifikanter direkter Effekt von X auf Y (Pfad c')", "Ein signifikanter indirekter Effekt a×b", "Gleichzeitig signifikante Pfade a, b und c"],
        ["A significant total effect of X on Y (path c)", "A significant direct effect of X on Y (path c')", "A significant indirect effect a×b", "Significant paths a, b, and c simultaneously"],
        2,
    ),
    (
        "Mediation & Moderation",
        "Welche Mediationsform ist durch einen signifikanten indirekten Effekt UND einen signifikanten direkten Effekt in DERSELBEN Richtung gekennzeichnet?",
        "Which mediation type is characterized by a significant indirect effect AND a significant direct effect in the SAME direction?",
        ["Komplementäre Mediation", "Kompetitive Mediation", "Ausschließlich indirekte Mediation", "Ausschließlich direkte Nicht-Mediation"],
        ["Complementary mediation", "Competitive mediation", "Indirect-only mediation", "Direct-only non-mediation"],
        0,
    ),
    (
        "Mediation & Moderation",
        "Warum wird die Bootstrap-Methode dem Sobel-Test für die Prüfung indirekter Effekte vorgezogen?",
        "Why is the bootstrap method preferred over the Sobel test for testing indirect effects?",
        ["Bootstrap ist einfacher zu berechnen", "Bootstrap setzt keine Normalverteilung des indirekten Effekts voraus und liefert genauere Konfidenzintervalle", "Der Sobel-Test erfordert eine wesentlich größere Stichprobe", "Bootstrap-Tests erfordern keine Signifikanz von Pfad a und Pfad b"],
        ["Bootstrap is simpler to compute", "Bootstrap does not assume normality of the indirect effect and provides more accurate confidence intervals", "The Sobel test requires a much larger sample size", "Bootstrap tests do not require path a and path b to be significant"],
        1,
    ),
    (
        "Mediation & Moderation",
        "Wenn der Interaktionsterm (X × W) in einem Moderationsmodell NICHT signifikant ist, bedeutet dies:",
        "If the interaction term (X × W) in a moderation model is NOT significant, this means:",
        ["X hat keinen Effekt auf Y", "Der Effekt von X auf Y hängt nicht vom Niveau von W ab", "W hat keinen Haupteffekt auf Y", "Das Modell ist falsch spezifiziert"],
        ["X has no effect on Y", "The effect of X on Y does not depend on the level of W", "W has no main effect on Y", "The model is misspecified"],
        1,
    ),
    # ── SURVEY RESEARCH ───────────────────────────────────────────────────────
    (
        "Survey-Forschung / Survey Research",
        "Common Method Bias (CMB) tritt am wahrscheinlichsten auf, wenn:",
        "Common Method Bias (CMB) is most likely to occur when:",
        ["Mehrere Beurteiler ein Konstrukt unabhängig voneinander bewerten", "Alle Variablen vom selben Befragten mit derselben Methode zum selben Zeitpunkt erhoben werden", "Längsschnittdaten über mehrere Zeitpunkte erhoben werden", "Eine Vollerhebung statt einer Stichprobe verwendet wird"],
        ["Multiple raters assess the same construct independently", "All variables are collected from the same respondent using the same method at the same time", "Longitudinal data are collected across multiple time points", "A census rather than a sample is used"],
        1,
    ),
    (
        "Survey-Forschung / Survey Research",
        "Der Acquiescence Response Style (ARS) beschreibt:",
        "Acquiescence Response Style (ARS) describes:",
        ["Die Tendenz, Aussagen unabhängig von ihrem Inhalt zuzustimmen", "Die Tendenz, die extremsten Antwortoptionen zu wählen", "Die Tendenz, den Mittelpunkt einer Skala zu wählen", "Die Tendenz, morgens positiver zu antworten als abends"],
        ["The tendency to agree with statements regardless of their content", "The tendency to select the most extreme response options", "The tendency to choose the midpoint of a scale", "The tendency to respond more positively in the morning than the evening"],
        0,
    ),
    (
        "Survey-Forschung / Survey Research",
        "Cronbachs Alpha ist ein Maß für:",
        "Cronbach's alpha is a measure of:",
        ["Konstruktvalidität", "Konvergenzvalidität", "Interne Konsistenz (Reliabilität)", "Diskriminanzvalidität"],
        ["Construct validity", "Convergent validity", "Internal consistency reliability", "Discriminant validity"],
        2,
    ),
    (
        "Survey-Forschung / Survey Research",
        "Die Faustregel '10 Beobachtungen pro Parameter' bezieht sich auf:",
        "The rule of thumb '10 observations per parameter' in survey research refers to:",
        ["Die Mindestanzahl an Items pro Konstrukt", "Die erforderliche Mindeststichprobengröße im Verhältnis zur Anzahl geschätzter Parameter", "Die maximale Anzahl an Konstrukten in einer Umfrage", "Die Anzahl der erforderlichen Pilottest-Teilnehmer"],
        ["The minimum number of items per construct", "The minimum sample size needed relative to the number of parameters estimated in a model", "The maximum number of constructs in a survey", "The number of pilot test participants required"],
        1,
    ),
    # ── INTERNATIONAL MARKETING ───────────────────────────────────────────────
    (
        "Internationales Marketing / International Marketing",
        "Konstruktäquivalenz in kulturvergleichender Forschung ist gegeben, wenn:",
        "Construct equivalence in cross-cultural research is established when:",
        ["Das gleiche Konstrukt eine äquivalente Bedeutung und Struktur über Kulturen hinweg aufweist", "Der Fragebogen mit identischem Wortlaut in alle Sprachen übersetzt wird", "Skalaitems in allen Ländern die gleichen Mittelwerte aufweisen", "Die gleiche Antwortskala in allen Kulturen verwendet wird"],
        ["The same construct has equivalent meaning and structure across cultures", "The questionnaire is translated with identical wording across languages", "Scale items show the same mean scores across countries", "The same response scale is used across all cultures"],
        0,
    ),
    (
        "Internationales Marketing / International Marketing",
        "Metrische Messäquivalenz (auch: schwache Äquivalenz) bedeutet:",
        "Metric measurement equivalence (also called weak equivalence) means:",
        ["Die gleiche Faktorstruktur gilt für alle Gruppen", "Faktorladungen sind über kulturelle Gruppen hinweg gleich", "Item-Intercepts sind über kulturelle Gruppen hinweg gleich", "Alle Messparameter sind über Gruppen hinweg gleich"],
        ["The same factor structure holds across groups", "Factor loadings are equal across cultural groups", "Item intercepts are equal across cultural groups", "All measurement parameters are equal across groups"],
        1,
    ),
    (
        "Internationales Marketing / International Marketing",
        "Welche Stufe der Messäquivalenz ist erforderlich, um gültige Mittelwertvergleiche zwischen Kulturen vorzunehmen?",
        "Which level of measurement equivalence is required to make valid mean comparisons across cultures?",
        ["Konfigurale Äquivalenz", "Metrische Äquivalenz", "Skalare Äquivalenz", "Kein Äquivalenztest erforderlich"],
        ["Configural equivalence", "Metric equivalence", "Scalar equivalence", "No equivalence testing is needed"],
        2,
    ),
    (
        "Internationales Marketing / International Marketing",
        "Der ökologische Fehlschluss (ecological fallacy) in kulturvergleichender Forschung bezeichnet:",
        "The ecological fallacy in cross-cultural research refers to:",
        ["Die Verwendung nationaler Kulturdimensionen zur Vorhersage individuellen Verhaltens ohne Prüfung auf Individualebene", "Schlussfolgerungen über Länder aus Daten auf Individualebene", "Rückschlüsse auf Individuen aus aggregierten (landesweiten) Zusammenhängen", "Das Messen von Kultur auf Individual- statt auf Länderebene"],
        ["Using national culture dimensions to predict individual behavior without testing individual-level relationships", "Making conclusions about countries based on individual-level data", "Making inferences about individuals based on aggregate (country-level) relationships", "Measuring culture at the individual rather than the country level"],
        2,
    ),
]

LETTERS = ["A", "B", "C", "D"]

# Fixed seeds per version — guarantees identical PDFs on every regeneration
VERSION_SEEDS = {"A": 101, "B": 202, "C": 303}


# ── Version shuffling ─────────────────────────────────────────────────────────
def make_version(questions, seed):
    """
    Return a shuffled copy of questions:
      - Question order shuffled within each topic group
      - Answer options reshuffled per question (correct index updated accordingly)
    """
    rng = random.Random(seed)

    # Group by topic (preserving topic order)
    topics_seen = []
    grouped = {}
    for q in questions:
        t = q[0]
        if t not in grouped:
            grouped[t] = []
            topics_seen.append(t)
        grouped[t].append(q)

    result = []
    for t in topics_seen:
        qs = list(grouped[t])
        rng.shuffle(qs)
        for q in qs:
            topic, qde, qen, opts_de, opts_en, correct = q
            order = list(range(4))
            rng.shuffle(order)
            new_opts_de  = [opts_de[i]  for i in order]
            new_opts_en  = [opts_en[i]  for i in order]
            new_correct  = order.index(correct)
            result.append((topic, qde, qen, new_opts_de, new_opts_en, new_correct))
    return result


# ── Styles ────────────────────────────────────────────────────────────────────
def make_styles(ver_color):
    return {
        "title": ParagraphStyle("title", fontSize=17, fontName="Helvetica-Bold",
                                textColor=ver_color, alignment=TA_CENTER, spaceAfter=3),
        "version_badge": ParagraphStyle("version_badge", fontSize=28, fontName="Helvetica-Bold",
                                        textColor=ver_color, alignment=TA_CENTER, spaceAfter=0),
        "subtitle": ParagraphStyle("subtitle", fontSize=10, fontName="Helvetica",
                                   textColor=DGRAY, alignment=TA_CENTER, spaceAfter=2),
        "section": ParagraphStyle("section", fontSize=9, fontName="Helvetica-Bold",
                                  textColor=white, leading=12),
        "qnum": ParagraphStyle("qnum", fontSize=10, fontName="Helvetica-Bold",
                               textColor=ver_color, spaceBefore=3, spaceAfter=1),
        "qde": ParagraphStyle("qde", fontSize=10, fontName="Helvetica-Bold",
                              textColor=black, leading=13, spaceAfter=2),
        "qen": ParagraphStyle("qen", fontSize=8.5, fontName="Helvetica-Oblique",
                              textColor=DGRAY, leading=11, spaceAfter=3),
        "opt_de": ParagraphStyle("opt_de", fontSize=9.5, fontName="Helvetica",
                                 textColor=black, leading=12),
        "opt_en": ParagraphStyle("opt_en", fontSize=8, fontName="Helvetica-Oblique",
                                 textColor=DGRAY, leading=10),
        "opt_de_c": ParagraphStyle("opt_de_c", fontSize=9.5, fontName="Helvetica-Bold",
                                   textColor=GREEN, leading=12),
        "opt_en_c": ParagraphStyle("opt_en_c", fontSize=8, fontName="Helvetica-BoldOblique",
                                   textColor=GREEN, leading=10),
        "header_label": ParagraphStyle("header_label", fontSize=9, fontName="Helvetica-Bold",
                                       textColor=DGRAY),
        "header_line": ParagraphStyle("header_line", fontSize=9, fontName="Helvetica",
                                      textColor=DGRAY),
        "footer": ParagraphStyle("footer", fontSize=7.5, fontName="Helvetica",
                                 textColor=DGRAY, alignment=TA_CENTER),
        "sol_warn": ParagraphStyle("sol_warn", fontSize=10, fontName="Helvetica-Bold",
                                   textColor=RED, alignment=TA_CENTER,
                                   spaceBefore=4, spaceAfter=6),
        "sheet_title": ParagraphStyle("sheet_title", fontSize=12, fontName="Helvetica-Bold",
                                      textColor=ver_color, alignment=TA_CENTER,
                                      spaceBefore=0, spaceAfter=5),
        "sheet_hdr": ParagraphStyle("sheet_hdr", fontSize=9, fontName="Helvetica-Bold",
                                    textColor=white, alignment=TA_CENTER, leading=11),
        "sheet_cell": ParagraphStyle("sheet_cell", fontSize=9, fontName="Helvetica",
                                     textColor=black, alignment=TA_CENTER, leading=11),
        "sheet_cell_c": ParagraphStyle("sheet_cell_c", fontSize=10, fontName="Helvetica-Bold",
                                       textColor=white, alignment=TA_CENTER, leading=11),
        "sheet_q": ParagraphStyle("sheet_q", fontSize=9, fontName="Helvetica-Bold",
                                  textColor=ver_color, alignment=TA_CENTER, leading=11),
    }


def _sp(h=0.2): return Spacer(1, h * cm)
def _hr(thick=1.0, col=MGRAY): return HRFlowable(width="100%", thickness=thick, color=col)


# ── Page 1 header ─────────────────────────────────────────────────────────────
def header_block(version, S, ver_color):
    # Title + version badge side by side
    title_cell = [
        Paragraph("Quantitative Methods — Exam / Prüfung", S["title"]),
        _sp(0.25),
        Paragraph("WU Vienna &nbsp;·&nbsp; Dr. Arne Floh", S["subtitle"]),
    ]
    badge_cell = Paragraph(f"Version&nbsp;{version}", S["version_badge"])

    top = Table(
        [[title_cell, badge_cell]],
        colWidths=[15.5*cm, 3.7*cm],
    )
    top.setStyle(TableStyle([
        ("VALIGN", (0,0),(-1,-1), "MIDDLE"),
        ("LEFTPADDING",  (0,0),(-1,-1), 0),
        ("RIGHTPADDING", (0,0),(-1,-1), 0),
        ("LINERIGHT", (0,0),(0,0), 1, MGRAY),
    ]))

    elems = [top, _sp(0.3), _hr(2.0, ver_color), _sp(0.25)]

    name_row = Table(
        [[Paragraph("Name:", S["header_label"]),
          Paragraph(" ", S["header_line"]),
          Paragraph("Student ID:", S["header_label"]),
          Paragraph(" ", S["header_line"])]],
        colWidths=[2.0*cm, 10.5*cm, 2.5*cm, 4.2*cm],
    )
    name_row.setStyle(TableStyle([
        ("VALIGN",        (0,0),(-1,-1), "BOTTOM"),
        ("LEFTPADDING",   (0,0),(-1,-1), 0),
        ("RIGHTPADDING",  (0,0),(-1,-1), 6),
        ("BOTTOMPADDING", (0,0),(-1,-1), 3),
        ("LINEBELOW",     (1,0),(1,0), 0.8, DGRAY),
        ("LINEBELOW",     (3,0),(3,0), 0.8, DGRAY),
    ]))
    elems.append(name_row)
    elems.append(_sp(0.12))

    instr = Table(
        [[Paragraph("Instructions / Anweisungen:", S["header_label"]),
          Paragraph(
              "Select exactly ONE answer per question. &nbsp;|&nbsp; "
              "Bitte genau EINE Antwort pro Frage ankreuzen.",
              S["header_line"])]],
        colWidths=[4.8*cm, 14.4*cm],
    )
    instr.setStyle(TableStyle([
        ("VALIGN", (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0),(-1,-1), 0),
        ("RIGHTPADDING", (0,0),(-1,-1), 0),
    ]))
    elems.append(instr)
    elems.append(_hr(1.0, MGRAY))
    elems.append(_sp(0.15))
    return elems


# ── Topic banner ──────────────────────────────────────────────────────────────
def topic_banner(topic, ver_color, S):
    t = Table([[Paragraph(topic, S["section"])]], colWidths=[19.2*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), ver_color),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
    ]))
    return t


# ── Question block (KeepTogether) ─────────────────────────────────────────────
def question_block(idx, q, S, ver_color, solution=False, first_in_topic=False):
    topic, qde, qen, opts_de, opts_en, correct = q
    inner = []

    if first_in_topic:
        inner.append(topic_banner(topic, ver_color, S))
        inner.append(_sp(0.12))

    inner.append(Paragraph(f"Frage / Question {idx}", S["qnum"]))
    inner.append(Paragraph(qde, S["qde"]))
    inner.append(Paragraph(qen, S["qen"]))

    for i, (ode, oen) in enumerate(zip(opts_de, opts_en)):
        is_c = solution and (i == correct)
        ds = "opt_de_c" if is_c else "opt_de"
        es = "opt_en_c" if is_c else "opt_en"

        row = Table(
            [[Paragraph(f"<b>{LETTERS[i]})</b>", S[ds]),
              [Paragraph(ode, S[ds]), Paragraph(oen, S[es])]]],
            colWidths=[0.85*cm, 18.35*cm],
        )
        row.setStyle(TableStyle([
            ("VALIGN",        (0,0),(-1,-1), "TOP"),
            ("LEFTPADDING",   (0,0),(-1,-1), 1),
            ("RIGHTPADDING",  (0,0),(-1,-1), 1),
            ("TOPPADDING",    (0,0),(-1,-1), 2),
            ("BOTTOMPADDING", (0,0),(-1,-1), 2),
            ("BACKGROUND",    (0,0),(-1,-1), LGREEN if is_c else (LGRAY if i%2==0 else white)),
        ]))
        inner.append(row)

    inner.append(_sp(0.25))
    return KeepTogether(inner)


# ── Answer sheet (last page) ──────────────────────────────────────────────────
def answer_sheet(version, questions, S, ver_color, solution=False):
    elems = [PageBreak()]

    title = (f"Version {version} — Lösungsschlüssel / Solution Key"
             if solution else
             f"Version {version} — Antwortbogen / Answer Sheet")
    elems.append(Paragraph(title, S["sheet_title"]))
    elems.append(_hr(1.5, ver_color))
    elems.append(_sp(0.2))

    if not solution:
        name_row = Table(
            [[Paragraph("Name:", S["header_label"]),
              Paragraph(" ", S["header_line"]),
              Paragraph("Student ID:", S["header_label"]),
              Paragraph(" ", S["header_line"])]],
            colWidths=[2.0*cm, 10.5*cm, 2.5*cm, 4.2*cm],
        )
        name_row.setStyle(TableStyle([
            ("VALIGN",        (0,0),(-1,-1), "BOTTOM"),
            ("LEFTPADDING",   (0,0),(-1,-1), 0),
            ("RIGHTPADDING",  (0,0),(-1,-1), 6),
            ("BOTTOMPADDING", (0,0),(-1,-1), 3),
            ("LINEBELOW",     (1,0),(1,0), 0.8, DGRAY),
            ("LINEBELOW",     (3,0),(3,0), 0.8, DGRAY),
        ]))
        elems.append(name_row)
    else:
        elems.append(Paragraph(
            "<b>LÖSUNG / SOLUTION — Nur für Lehrende / For instructors only</b>",
            S["sol_warn"],
        ))

    elems.append(_hr(0.8, MGRAY))
    elems.append(_sp(0.3))

    def half_table(qs_slice):
        hdr = [Paragraph(h, S["sheet_hdr"]) for h in ["Frage/Q", "A", "B", "C", "D"]]
        rows = [hdr]
        for q_num, q in qs_slice:
            c = q[5]
            row = [Paragraph(str(q_num), S["sheet_q"])]
            for i in range(4):
                row.append(Paragraph(LETTERS[i] if (solution and i == c) else " ", S["sheet_cell_c"] if (solution and i == c) else S["sheet_cell"]))
            rows.append(row)

        col_w = [1.6*cm, 1.4*cm, 1.4*cm, 1.4*cm, 1.4*cm]
        t = Table(rows, colWidths=col_w, repeatRows=1)
        cmds = [
            ("BACKGROUND",    (0,0),(-1,0), ver_color),
            ("TEXTCOLOR",     (0,0),(-1,0), white),
            ("FONTNAME",      (0,0),(-1,0), "Helvetica-Bold"),
            ("FONTSIZE",      (0,0),(-1,-1), 9),
            ("ALIGN",         (0,0),(-1,-1), "CENTER"),
            ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
            ("ROWBACKGROUNDS",(0,1),(-1,-1), [LGRAY, white]),
            ("GRID",          (0,0),(-1,-1), 0.5, MGRAY),
            ("TOPPADDING",    (0,0),(-1,-1), 6),
            ("BOTTOMPADDING", (0,0),(-1,-1), 6),
        ]
        if solution:
            for row_i, (_, q) in enumerate(qs_slice, 1):
                c = q[5]
                cmds += [
                    ("BACKGROUND", (c+1, row_i),(c+1, row_i), GREEN),
                    ("TEXTCOLOR",  (c+1, row_i),(c+1, row_i), white),
                ]
        t.setStyle(TableStyle(cmds))
        return t

    indexed = list(enumerate(questions, 1))
    left_t  = half_table(indexed[:10])
    right_t = half_table(indexed[10:])

    combined = Table(
        [[left_t, Spacer(1, 1*cm), right_t]],
        colWidths=[7.2*cm, 1.2*cm, 7.2*cm],
    )
    combined.setStyle(TableStyle([
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
        ("LEFTPADDING",  (0,0),(-1,-1), 0),
        ("RIGHTPADDING", (0,0),(-1,-1), 0),
    ]))
    elems.append(combined)

    if not solution:
        elems += [_sp(0.5), _hr(0.8, MGRAY), _sp(0.15),
                  Paragraph("Bitte nur EINE Antwort pro Zeile ankreuzen. &nbsp;|&nbsp; "
                            "Please tick exactly ONE box per row.", S["footer"])]
    return elems


# ── Build one PDF ─────────────────────────────────────────────────────────────
def build_pdf(path, version, questions, solution=False):
    ver_color = VERSION_COLORS[version]
    S = make_styles(ver_color)

    doc = SimpleDocTemplate(
        path, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=1.5*cm,  bottomMargin=1.8*cm,
    )
    story = header_block(version, S, ver_color)

    if solution:
        story.append(Paragraph(
            f"<b>LÖSUNG / SOLUTION Version {version} — Nur für Lehrende / For instructors only</b>",
            S["sol_warn"],
        ))

    current_topic = None
    for idx, q in enumerate(questions, 1):
        first = (q[0] != current_topic)
        story.append(question_block(idx, q, S, ver_color,
                                    solution=solution, first_in_topic=first))
        current_topic = q[0]

    story += answer_sheet(version, questions, S, ver_color, solution=solution)

    label = "Lösungsschlüssel" if solution else "Prüfungsbogen"

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(DGRAY)
        w, _ = A4
        canvas.drawCentredString(
            w/2, 1.0*cm,
            f"WU Vienna · Quantitative Methods · Version {version} · {label} · 20 Fragen/Questions  —  Seite/Page {doc.page}",
        )
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"  Written: {path}")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    out = "/home/user/quantmethods/exam/exam-mc-questions"
    os.makedirs(out, exist_ok=True)

    for ver, seed in VERSION_SEEDS.items():
        print(f"\nGenerating Version {ver} (seed={seed}) …")
        qs = make_version(QUESTIONS, seed)
        build_pdf(f"{out}/exam_student_{ver}.pdf", ver, qs, solution=False)
        build_pdf(f"{out}/exam_solution_{ver}.pdf", ver, qs, solution=True)

    print("\nDone. 6 files written.")
