"""
Generate bilingual (DE/EN) exam PDFs:
  - exam_student.pdf  : student version with tick boxes and name field
  - exam_solution.pdf : instructor solution key with correct answers marked
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib import colors
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import random

# ── colour palette ──────────────────────────────────────────────────────────
BLUE  = HexColor("#1a3a6b")
LGRAY = HexColor("#f4f4f4")
MGRAY = HexColor("#dddddd")
DGRAY = HexColor("#555555")
GREEN = HexColor("#1a7a3a")

# ── 20 questions (4 per topic) – bilingual DE / EN ───────────────────────────
# Each entry: (topic, question_de, question_en, [option_de, ...], [option_en, ...], correct_index 0-3)
QUESTIONS = [
    # ── STATISTICS ──────────────────────────────────────────────────────────
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
    # ── REGRESSION ──────────────────────────────────────────────────────────
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
    # ── MEDIATION & MODERATION ───────────────────────────────────────────────
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
    # ── SURVEY RESEARCH ──────────────────────────────────────────────────────
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
    # ── INTERNATIONAL MARKETING ──────────────────────────────────────────────
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

OPTION_LETTERS = ["A", "B", "C", "D"]

# ── Styles ────────────────────────────────────────────────────────────────────
def make_styles():
    base = dict(fontName="Helvetica", leading=13)
    return {
        "title": ParagraphStyle("title", fontSize=18, fontName="Helvetica-Bold",
                                 textColor=BLUE, alignment=TA_CENTER, spaceAfter=4),
        "subtitle": ParagraphStyle("subtitle", fontSize=11, fontName="Helvetica",
                                    textColor=DGRAY, alignment=TA_CENTER, spaceAfter=2),
        "section": ParagraphStyle("section", fontSize=9, fontName="Helvetica-Bold",
                                   textColor=white, leading=12),
        "qnum": ParagraphStyle("qnum", fontSize=11, fontName="Helvetica-Bold",
                                textColor=BLUE, spaceBefore=2, spaceAfter=1),
        "qde": ParagraphStyle("qde", fontSize=10, fontName="Helvetica-Bold",
                               textColor=black, leading=14, spaceAfter=2),
        "qen": ParagraphStyle("qen", fontSize=9, fontName="Helvetica-Oblique",
                               textColor=DGRAY, leading=12, spaceAfter=4),
        "opt_de": ParagraphStyle("opt_de", fontSize=10, fontName="Helvetica",
                                  textColor=black, leading=13),
        "opt_en": ParagraphStyle("opt_en", fontSize=8.5, fontName="Helvetica-Oblique",
                                  textColor=DGRAY, leading=11),
        "opt_de_correct": ParagraphStyle("opt_de_correct", fontSize=10,
                                          fontName="Helvetica-Bold", textColor=GREEN, leading=13),
        "opt_en_correct": ParagraphStyle("opt_en_correct", fontSize=8.5,
                                          fontName="Helvetica-BoldOblique", textColor=GREEN, leading=11),
        "header_label": ParagraphStyle("header_label", fontSize=9, fontName="Helvetica-Bold",
                                        textColor=DGRAY),
        "header_line": ParagraphStyle("header_line", fontSize=9, fontName="Helvetica",
                                       textColor=DGRAY),
        "footer": ParagraphStyle("footer", fontSize=8, fontName="Helvetica",
                                  textColor=DGRAY, alignment=TA_CENTER),
        "topic_label": ParagraphStyle("topic_label", fontSize=7.5, fontName="Helvetica-Bold",
                                       textColor=BLUE),
    }

S = make_styles()

# ── Header block (name field etc.) ────────────────────────────────────────────
def header_block():
    elems = []
    elems.append(Paragraph("Quantitative Methods — Exam / Prüfung", S["title"]))
    elems.append(Paragraph("WU Vienna &nbsp;·&nbsp; Dr. Arne Floh", S["subtitle"]))
    elems.append(Spacer(1, 0.3 * cm))
    elems.append(HRFlowable(width="100%", thickness=1.5, color=BLUE))
    elems.append(Spacer(1, 0.25 * cm))

    field_data = [
        [Paragraph("Name:", S["header_label"]),
         Paragraph("_" * 55, S["header_line"]),
         Paragraph("Matrikelnummer / Student ID:", S["header_label"]),
         Paragraph("_" * 22, S["header_line"])],
    ]
    t = Table(field_data, colWidths=[2.0 * cm, 8.5 * cm, 5.2 * cm, 3.5 * cm])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "BOTTOM"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 0),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
    elems.append(t)
    elems.append(Spacer(1, 0.15 * cm))

    instr_data = [
        [Paragraph("Instructions / Anweisungen:", S["header_label"]),
         Paragraph(
             "Select exactly ONE answer per question by ticking the corresponding box. &nbsp;|&nbsp; "
             "Bitte genau EINE Antwort pro Frage ankreuzen.",
             S["header_line"])],
    ]
    t2 = Table(instr_data, colWidths=[4.5 * cm, 14.7 * cm])
    t2.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                             ("LEFTPADDING", (0, 0), (-1, -1), 0),
                             ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    elems.append(t2)
    elems.append(HRFlowable(width="100%", thickness=1, color=MGRAY))
    elems.append(Spacer(1, 0.2 * cm))
    return elems


# ── Topic banner ──────────────────────────────────────────────────────────────
def topic_banner(topic):
    t = Table([[Paragraph(topic, S["section"])]],
              colWidths=[19.2 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BLUE),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


# ── Single question block ─────────────────────────────────────────────────────
def question_block(idx, q, solution=False):
    topic, qde, qen, opts_de, opts_en, correct = q
    elems = []

    elems.append(Paragraph(f"Frage / Question {idx}", S["qnum"]))
    elems.append(Paragraph(qde, S["qde"]))
    elems.append(Paragraph(qen, S["qen"]))

    for i, (ode, oen) in enumerate(zip(opts_de, opts_en)):
        letter = OPTION_LETTERS[i]
        is_correct = (i == correct)

        if solution and is_correct:
            tick = "✔"
            box_col = GREEN
            de_style = S["opt_de_correct"]
            en_style = S["opt_en_correct"]
        else:
            tick = "☐"
            box_col = DGRAY
            de_style = S["opt_de"]
            en_style = S["opt_en"]

        box_cell = Paragraph(f'<font color="{box_col.hexval()}">{tick}</font>', S["opt_de"])
        letter_cell = Paragraph(f"<b>{letter})</b>", S["opt_de"] if not (solution and is_correct) else S["opt_de_correct"])
        text_cell_content = [Paragraph(ode, de_style), Paragraph(oen, en_style)]

        row = Table(
            [[box_cell, letter_cell, text_cell_content]],
            colWidths=[0.6 * cm, 0.9 * cm, 17.7 * cm],
        )
        row.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 1),
            ("RIGHTPADDING", (0, 0), (-1, -1), 1),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
            ("BACKGROUND", (0, 0), (-1, -1), LGRAY if i % 2 == 0 else white),
        ]))
        elems.append(row)

    elems.append(Spacer(1, 0.3 * cm))
    return elems


# ── Build one PDF ─────────────────────────────────────────────────────────────
def build_pdf(path, questions, solution=False):
    doc = SimpleDocTemplate(
        path,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )
    story = []
    story += header_block()

    if solution:
        story.append(Paragraph(
            "<b>LÖSUNG / SOLUTION — Nur für Lehrende / For instructors only</b>",
            ParagraphStyle("sol_warn", fontSize=10, fontName="Helvetica-Bold",
                           textColor=HexColor("#cc0000"), alignment=TA_CENTER,
                           spaceBefore=4, spaceAfter=8)
        ))

    current_topic = None
    for idx, q in enumerate(questions, 1):
        topic = q[0]
        if topic != current_topic:
            story.append(topic_banner(topic))
            story.append(Spacer(1, 0.15 * cm))
            current_topic = topic
        story += question_block(idx, q, solution=solution)

    # footer note
    story.append(HRFlowable(width="100%", thickness=0.8, color=MGRAY))
    story.append(Spacer(1, 0.1 * cm))
    label = "Lösungsschlüssel" if solution else "Prüfungsbogen"
    story.append(Paragraph(
        f"WU Vienna · Quantitative Methods · {label} · 20 Fragen / Questions",
        S["footer"]
    ))

    doc.build(story)
    print(f"Written: {path}")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import os
    out_dir = "/home/user/quantmethods/exam/exam-mc-questions"
    os.makedirs(out_dir, exist_ok=True)

    build_pdf(f"{out_dir}/exam_student.pdf",  QUESTIONS, solution=False)
    build_pdf(f"{out_dir}/exam_solution.pdf", QUESTIONS, solution=True)
    print("Done.")
