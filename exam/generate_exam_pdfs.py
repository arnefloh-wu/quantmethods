"""
Generate 3 parallel bilingual (DE/EN) exam PDFs — Versions A, B, C.

Master pool: 12 questions per topic × 5 topics = 60 bilingual questions.
Each version draws 4 non-overlapping questions per topic (fixed group seed),
then shuffles question order and answer options within the version (version seed).
Result: identical difficulty/topic coverage, zero question overlap across versions.
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

# ── Colours ──────────────────────────────────────────────────────────────────
BLUE   = HexColor("#1a3a6b")
LGRAY  = HexColor("#f4f4f4")
MGRAY  = HexColor("#dddddd")
DGRAY  = HexColor("#555555")
GREEN  = HexColor("#1a7a3a")
LGREEN = HexColor("#d4edda")
RED    = HexColor("#cc0000")
VERSION_COLORS = {"A": HexColor("#1a3a6b"), "B": HexColor("#7b1a1a"), "C": HexColor("#1a5c1a")}

LETTERS = ["A", "B", "C", "D"]

# Seeds — fixed for full reproducibility
GROUP_SEED   = 999   # determines which 4 questions per topic go to each version
VERSION_SEEDS = {"A": 101, "B": 202, "C": 303}  # shuffle order + answers within version

# ── Master bilingual question pool (12 per topic × 5 topics) ─────────────────
# Format: (topic, question_de, question_en, [opts_de×4], [opts_en×4], correct_idx)

MASTER_POOL = {

# ════════════════════════════════════════════════════════════════════════════════
"Statistik / Statistics": [
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
    (
        "Statistik / Statistics",
        "Ein Forscher ordnet Marathonläufer auf die Plätze 1., 2. und 3. ein. Welche Messskala wird dabei verwendet?",
        "A researcher ranks marathon runners as 1st, 2nd, and 3rd place. Which measurement scale is being used?",
        ["Nominalskala", "Ordinalskala", "Intervallskala", "Ratioskala"],
        ["Nominal scale", "Ordinal scale", "Interval scale", "Ratio scale"],
        1,
    ),
    (
        "Statistik / Statistics",
        "Das Alter einer befragten Person in Jahren ist ein Beispiel für welche Messskala?",
        "A respondent's age in years is an example of which measurement scale?",
        ["Nominalskala", "Ordinalskala", "Intervallskala", "Ratioskala"],
        ["Nominal scale", "Ordinal scale", "Interval scale", "Ratio scale"],
        3,
    ),
    (
        "Statistik / Statistics",
        "Warum ist die Summe der Abweichungen vom Mittelwert stets gleich null?",
        "Why is the sum of deviations from the mean always equal to zero?",
        ["Weil alle Werte gleich sind", "Weil der Mittelwert der größte Wert ist", "Weil sich positive und negative Abweichungen gegenseitig aufheben", "Weil die Standardabweichung gleich eins ist"],
        ["Because all values are equal", "Because the mean is the largest value", "Because positive and negative deviations cancel each other out", "Because the standard deviation equals one"],
        2,
    ),
    (
        "Statistik / Statistics",
        "Die Normalverteilung wird vollständig durch folgende Parameter beschrieben:",
        "The normal distribution is fully defined by:",
        ["Modus und Spannweite", "Median und Varianz", "Mittelwert und Standardabweichung", "Perzentile und Kurtosis"],
        ["Mode and range", "Median and variance", "Mean and standard deviation", "Percentiles and kurtosis"],
        2,
    ),
    (
        "Statistik / Statistics",
        "Die Nullhypothese (H₀) in der Hypothesenprüfung repräsentiert:",
        "The null hypothesis (H₀) in hypothesis testing represents:",
        ["Die Vorhersage des Forschers", "Den erwarteten Effekt oder Unterschied", "Den Status quo – keinen Effekt oder Unterschied", "Die Alternative, die bewiesen werden soll"],
        ["The researcher's prediction", "The expected effect or difference", "The status quo — no effect or no difference", "The alternative to be proven"],
        2,
    ),
    (
        "Statistik / Statistics",
        "Ein Fehler 1. Art (Alpha-Fehler) tritt auf, wenn:",
        "A Type I error (alpha error) occurs when:",
        ["Die Nullhypothese wahr ist und korrekt beibehalten wird", "Die Nullhypothese falsch ist und korrekt abgelehnt wird", "Die Nullhypothese wahr ist, aber fälschlicherweise abgelehnt wird", "Die Nullhypothese falsch ist, aber fälschlicherweise beibehalten wird"],
        ["The null hypothesis is true and correctly retained", "The null hypothesis is false and correctly rejected", "The null hypothesis is true but incorrectly rejected", "The null hypothesis is false but incorrectly retained"],
        2,
    ),
    (
        "Statistik / Statistics",
        "Statistische Power (Teststärke) ist definiert als:",
        "Statistical power is defined as:",
        ["1 − Alpha", "Alpha + Beta", "1 − Beta", "Alpha / Beta"],
        ["1 − alpha", "Alpha + beta", "1 − beta", "Alpha / beta"],
        2,
    ),
    (
        "Statistik / Statistics",
        "Das konventionell verwendete Signifikanzniveau in der Marketingforschung beträgt:",
        "The conventional significance level used in marketing research is:",
        ["Alpha = 0,10", "Alpha = 0,05", "Alpha = 0,001", "Alpha = 0,50"],
        ["Alpha = 0.10", "Alpha = 0.05", "Alpha = 0.001", "Alpha = 0.50"],
        1,
    ),
],

# ════════════════════════════════════════════════════════════════════════════════
"Regressionsanalyse / Regression Analysis": [
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
    (
        "Regressionsanalyse / Regression Analysis",
        "Was minimiert die Methode der kleinsten Quadrate (OLS) bei der Schätzung von Regressionskoeffizienten?",
        "What does the Ordinary Least Squares (OLS) method minimize when estimating regression coefficients?",
        ["Die Summe der absoluten Residuen", "Die Summe der Residuen", "Die Summe der quadrierten Residuen", "Den Mittelwert der abhängigen Variablen"],
        ["The sum of absolute residuals", "The sum of residuals", "The sum of squared residuals", "The mean of the dependent variable"],
        2,
    ),
    (
        "Regressionsanalyse / Regression Analysis",
        "Das Bestimmtheitsmaß R² misst:",
        "The coefficient of determination R² measures:",
        ["Den durchschnittlichen Vorhersagefehler", "Die Anzahl signifikanter Prädiktoren", "Den Anteil der durch das Modell erklärten Varianz in Y", "Die Korrelation zwischen Residuen und Prädiktoren"],
        ["The average prediction error", "The number of significant predictors", "The proportion of variance in Y explained by the model", "The correlation between residuals and predictors"],
        2,
    ),
    (
        "Regressionsanalyse / Regression Analysis",
        "Der F-Test in der Regressionsanalyse prüft:",
        "The F-test in regression analysis tests:",
        ["Ob einzelne Regressionskoeffizienten signifikant sind", "Ob die Residuen normalverteilt sind", "Ob das Gesamtmodell einen signifikanten Anteil der Varianz in Y erklärt", "Ob der Achsenabschnitt signifikant von null abweicht"],
        ["Whether individual regression coefficients are significant", "Whether residuals are normally distributed", "Whether the overall model explains a significant amount of variance in Y", "Whether the intercept is significantly different from zero"],
        2,
    ),
    (
        "Regressionsanalyse / Regression Analysis",
        "Die Durbin-Watson-Statistik dient zur Überprüfung auf:",
        "The Durbin-Watson statistic is used to test for:",
        ["Heteroskedastizität", "Multikollinearität", "Autokorrelation der Residuen", "Nicht-Normalverteilung der Residuen"],
        ["Heteroscedasticity", "Multicollinearity", "Autocorrelation of residuals", "Non-normality of residuals"],
        2,
    ),
    (
        "Regressionsanalyse / Regression Analysis",
        "Cook's Distance wird in der Regressionsanalyse verwendet, um Folgendes zu identifizieren:",
        "Cook's Distance is used in regression to identify:",
        ["Multikollineare Prädiktoren", "Autokorrelierte Residuen", "Einflussreiche Ausreißer", "Nicht-lineare Zusammenhänge"],
        ["Multicollinear predictors", "Autocorrelated residuals", "Influential outliers", "Non-linear relationships"],
        2,
    ),
    (
        "Regressionsanalyse / Regression Analysis",
        "Endogenität in der Regression tritt auf, wenn:",
        "Endogeneity in regression occurs when:",
        ["Die abhängige Variable auf einer Nominalskala gemessen wird", "Die Residuen einer Nicht-Normalverteilung folgen", "Eine unabhängige Variable mit dem Fehlerterm korreliert", "Keine Variation in der abhängigen Variablen vorliegt"],
        ["The dependent variable is measured on a nominal scale", "The residuals follow a non-normal distribution", "An independent variable is correlated with the error term", "There is no variation in the dependent variable"],
        2,
    ),
    (
        "Regressionsanalyse / Regression Analysis",
        "Wenn eine kategoriale Variable k Ausprägungen hat, wie viele Dummy-Variablen sollen in das Regressionsmodell aufgenommen werden?",
        "If a categorical variable has k categories, how many dummy variables should be included in a regression model?",
        ["k Dummy-Variablen", "k − 1 Dummy-Variablen", "k + 1 Dummy-Variablen", "1 Dummy-Variable unabhängig von k"],
        ["k dummy variables", "k − 1 dummy variables", "k + 1 dummy variables", "1 dummy variable regardless of k"],
        1,
    ),
    (
        "Regressionsanalyse / Regression Analysis",
        "Im Log-Log-Regressionsmodell (ln Y = b₀ + b₁ ln X + ε) wird der Koeffizient b₁ interpretiert als:",
        "In a log-log regression model (ln Y = b₀ + b₁ ln X + ε), the coefficient b₁ is interpreted as:",
        ["Eine Einheitszunahme in X führt zu einer Zunahme von b₁ Einheiten in Y", "Eine 1%ige Zunahme in X führt zu einer b₁%igen Veränderung in Y (Elastizität)", "Eine Einheitszunahme in X führt zu einer b₁%igen Veränderung in Y", "Eine 1%ige Zunahme in X führt zu einer b₁-Einheiten-Veränderung in Y"],
        ["A one-unit increase in X leads to a b₁-unit increase in Y", "A 1% increase in X leads to a b₁% change in Y (elasticity)", "A one-unit increase in X leads to a b₁% change in Y", "A 1% increase in X leads to a b₁-unit change in Y"],
        1,
    ),
],

# ════════════════════════════════════════════════════════════════════════════════
"Mediation & Moderation": [
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
    (
        "Mediation & Moderation",
        "In der Mediationsanalyse ist die Mediatorvariable M definiert als:",
        "In mediation analysis, the mediator variable M is defined as:",
        ["Eine Variable, die den X→Y-Zusammenhang unter bestimmten Bedingungen verstärkt", "Eine Variable, die den Mechanismus erklärt, durch den X Y beeinflusst", "Eine Variable, die mit X und Y korreliert, aber keine kausale Rolle hat", "Eine Variable, die die Richtung des X→Y-Zusammenhangs moderiert"],
        ["A variable that strengthens the X→Y relationship under certain conditions", "A variable that explains the mechanism through which X affects Y", "A variable correlated with X and Y but with no causal role", "A variable that moderates the direction of the X→Y relationship"],
        1,
    ),
    (
        "Mediation & Moderation",
        "In der Moderationsanalyse ist die Moderatorvariable W definiert als:",
        "In moderation analysis, the moderator variable W is defined as:",
        ["Eine Variable, die den X→Y-Zusammenhang mediiert", "Eine Variable, die die Stärke oder Richtung des X→Y-Zusammenhangs beeinflusst", "Eine Variable, die den X→Y-Zusammenhang vollständig erklärt", "Eine Variable, die den direkten Effekt von X auf Y eliminiert"],
        ["A variable that mediates the X→Y relationship", "A variable that affects the strength or direction of the X→Y relationship", "A variable that fully explains the X→Y relationship", "A variable that eliminates the direct effect of X on Y"],
        1,
    ),
    (
        "Mediation & Moderation",
        "Kompetitive Mediation (inkonsistente Mediation) ist gekennzeichnet durch:",
        "Competitive mediation (also called inconsistent mediation) is characterized by:",
        ["Einen signifikanten indirekten Effekt und keinen direkten Effekt", "Keinen indirekten und keinen direkten Effekt", "Einen signifikanten indirekten Effekt und einen signifikanten direkten Effekt in entgegengesetzter Richtung", "Einen signifikanten Gesamteffekt, aber keinen indirekten Effekt"],
        ["A significant indirect effect and no direct effect", "No indirect effect and no direct effect", "A significant indirect effect and a significant direct effect in opposite directions", "A significant total effect but no indirect effect"],
        2,
    ),
    (
        "Mediation & Moderation",
        "Was deutet ein signifikanter direkter Effekt c' gemäß Zhao, Lynch & Chen (2010) an?",
        "What does a significant direct effect c' hint at, according to Zhao, Lynch & Chen (2010)?",
        ["Dass die Mediation vollständig ist und keine weitere Analyse erforderlich ist", "Dass der Mediator M schlecht gemessen ist", "Dass möglicherweise ausgelassene Mediatoren existieren, die nicht im Modell enthalten sind", "Dass der indirekte Effekt a×b spurios ist"],
        ["That mediation is complete and no further analysis is needed", "That the mediator M is poorly measured", "That there may be omitted mediators not included in the model", "That the indirect effect a×b is spurious"],
        2,
    ),
    (
        "Mediation & Moderation",
        "Im Mediationsmodell repräsentiert Pfad c:",
        "In a mediation model, path c represents:",
        ["Den Effekt von X auf M", "Den Effekt von M auf Y unter Kontrolle von X", "Den indirekten Effekt von X auf Y über M", "Den Gesamteffekt von X auf Y (ohne M im Modell)"],
        ["The effect of X on M", "The effect of M on Y controlling for X", "The indirect effect of X on Y through M", "The total effect of X on Y (without M in the model)"],
        3,
    ),
    (
        "Mediation & Moderation",
        "Im Moderationsmodell wird der Interaktionsterm gebildet durch:",
        "In a moderation model, the interaction term is formed by:",
        ["Multiplikation des Prädiktors X mit dem Moderator W", "Addition des Prädiktors X und des Moderators W", "Subtraktion des Moderators W vom Prädiktor X", "Division des Prädiktors X durch den Moderator W"],
        ["Multiplying the predictor X by the moderator W", "Adding the predictor X and the moderator W", "Subtracting the moderator W from the predictor X", "Dividing the predictor X by the moderator W"],
        0,
    ),
    (
        "Mediation & Moderation",
        "Welche der folgenden Sequenzen ist die korrekte Abfolge der Pfade in einem einfachen Mediationsmodell?",
        "Which of the following is the correct sequence of paths in a simple mediation model?",
        ["X → Y → M", "M → X → Y", "X → M → Y", "W → X → Y"],
        ["X → Y → M", "M → X → Y", "X → M → Y", "W → X → Y"],
        2,
    ),
    (
        "Mediation & Moderation",
        "Um Multikollinearität in der Moderationsanalyse zu vermeiden, wird empfohlen:",
        "To avoid multicollinearity in moderation analysis, it is recommended to:",
        ["Unzentrierte Variablen für den Interaktionsterm zu verwenden", "Die Haupteffekte von X und W aus dem Modell zu entfernen", "X und W vor der Bildung des Interaktionsterms X × W zu zentrieren", "Nur log-transformierte Variablen zu verwenden"],
        ["Use uncentered variables for the interaction term", "Remove the main effects of X and W from the model", "Mean-center X and W before forming the interaction term X × W", "Use log-transformed variables only"],
        2,
    ),
],

# ════════════════════════════════════════════════════════════════════════════════
"Survey-Forschung / Survey Research": [
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
    (
        "Survey-Forschung / Survey Research",
        "In der klassischen Testtheorie repräsentiert das Messmodell x = t + s + e:",
        "In classical test theory, the measurement model x = t + s + e represents:",
        ["x = Gesamtscore, t = wahrer Wert, s = Stichprobenfehler, e = systematischer Fehler", "x = beobachteter Wert, t = wahrer Wert, s = systematischer Fehler, e = zufälliger Fehler", "x = wahrer Wert, t = Gesamtscore, s = Standardabweichung, e = Fehlervarianz", "x = Fehlerterm, t = Zeit, s = Skalenreliabilität, e = Effizienz"],
        ["x = total score, t = true score, s = sampling error, e = systematic error", "x = observed score, t = true score, s = systematic error, e = random error", "x = true score, t = total score, s = standard deviation, e = error variance", "x = error term, t = time, s = scale reliability, e = efficiency"],
        1,
    ),
    (
        "Survey-Forschung / Survey Research",
        "Welcher Fehlertyp in der Messung ist konsistent und gerichtet und verfälscht Werte systematisch?",
        "Which type of error in measurement is consistent and directional, and therefore inflates or deflates scores systematically?",
        ["Zufälliger Fehler (e)", "Systematischer Fehler (s)", "Stichprobenfehler", "Non-Response-Fehler"],
        ["Random error (e)", "Systematic error (s)", "Sampling error", "Non-response error"],
        1,
    ),
    (
        "Survey-Forschung / Survey Research",
        "Key-Informant-Bias tritt auf, wenn:",
        "Key informant bias occurs when:",
        ["Befragte Fragen aufgrund kultureller Unterschiede unterschiedlich interpretieren", "Eine Person für eine Organisation antwortet, deren individuelle Wahrnehmung jedoch nicht die Realität der Organisation widerspiegelt", "Befragte systematisch extreme Skalenpunkte wählen", "Eine Umfrage online statt persönlich durchgeführt wird"],
        ["Respondents interpret questions differently due to cultural differences", "One person reports on behalf of an organization but their perceptions may not reflect organizational reality", "Respondents select extreme scale points systematically", "The survey is administered online rather than in person"],
        1,
    ),
    (
        "Survey-Forschung / Survey Research",
        "Der Extreme Response Style (ERS) beschreibt:",
        "Extreme Response Style (ERS) refers to:",
        ["Die Tendenz, allen Aussagen zuzustimmen", "Die Tendenz, den neutralen Mittelpunkt zu wählen", "Die Tendenz, die extremsten Skalenpunkte (Enden der Skala) zu wählen", "Die Tendenz, schwierige Fragen zu überspringen"],
        ["The tendency to agree with all statements", "The tendency to choose the neutral midpoint", "The tendency to select the most extreme scale points (ends of the scale)", "The tendency to skip difficult questions"],
        2,
    ),
    (
        "Survey-Forschung / Survey Research",
        "Für die Messung eines latenten Konstrukts mit einer Likert-Skala: Wie viele Antwortkategorien werden typischerweise empfohlen?",
        "For measuring a latent construct with a Likert-type scale, how many response categories are typically recommended?",
        ["2–3 Kategorien", "5–7 Kategorien", "8–10 Kategorien", "11–15 Kategorien"],
        ["2–3 categories", "5–7 categories", "8–10 categories", "11–15 categories"],
        1,
    ),
    (
        "Survey-Forschung / Survey Research",
        "Non-Response-Bias tritt auf, wenn:",
        "Non-response bias occurs when:",
        ["Einige Befragte nur einen Teil des Fragebogens ausfüllen", "Nicht-Teilnehmende sich systematisch von Teilnehmenden unterscheiden", "Befragte Skalenpunkte falsch interpretieren", "Der Fragebogen zu lang ist"],
        ["Some respondents complete only part of the questionnaire", "Those who do not respond systematically differ from those who do respond", "Respondents misunderstand the scale anchors", "The survey is too long"],
        1,
    ),
    (
        "Survey-Forschung / Survey Research",
        "Eine 'doppelläufige' Frage ist problematisch, weil:",
        "A 'double-barreled' question is problematic because:",
        ["Sie zwei separate Sachverhalte in einer Frage anspricht, sodass nicht bestimmbar ist, auf welchen sich die Antwort bezieht", "Sie zu viele Antwortkategorien verwendet", "Sie soziale Erwünschtheit fördert", "Sie Befragte zwingt, sich an vergangene Ereignisse zu erinnern"],
        ["It asks about two separate issues in one question, making it impossible to determine which the answer refers to", "It uses too many response categories", "It leads to social desirability bias", "It requires respondents to recall past events from memory"],
        0,
    ),
    (
        "Survey-Forschung / Survey Research",
        "Konvergenzvalidität ist gegeben, wenn:",
        "Convergent validity is demonstrated when:",
        ["Items, die dasselbe Konstrukt messen, hohe Interkorrelationen aufweisen", "Items verschiedener Konstrukte hohe Korrelationen aufweisen", "Die Skala das Konstrukt zuverlässig über die Zeit misst", "Die Skala zukünftiges Verhalten akkurat vorhersagt"],
        ["Items measuring the same construct show high intercorrelations", "Items measuring different constructs show high correlations", "The scale reliably measures the construct across time", "The scale accurately predicts future behavior"],
        0,
    ),
],

# ════════════════════════════════════════════════════════════════════════════════
"Internationales Marketing / International Marketing": [
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
    (
        "Internationales Marketing / International Marketing",
        "Der etische (etic) Ansatz in der internationalen Marketingforschung bezeichnet:",
        "The etic approach in international marketing research refers to:",
        ["Die Entwicklung eines universellen Rahmens, der kulturübergreifend anwendbar ist", "Die Entwicklung kulturspezifischer Rahmen für jedes Land", "Die Übersetzung bestehender Instrumente mittels Rückübersetzung", "Das Ignorieren kultureller Unterschiede in der Messung"],
        ["Developing a universal framework applicable across all cultures", "Developing culture-specific frameworks for each country", "Translating existing instruments using back-translation", "Ignoring cultural differences in measurement"],
        0,
    ),
    (
        "Internationales Marketing / International Marketing",
        "Der emische (emic) Ansatz in der internationalen Marketingforschung bezeichnet:",
        "The emic approach in international marketing research refers to:",
        ["Die Verwendung eines universellen Rahmens, der außerhalb einer bestimmten Kultur entwickelt wurde", "Die Entwicklung von Konstrukten und Maßen aus einer spezifischen Kultur heraus", "Die Verwendung von Hofstedes Dimensionen zum Kulturvergleich", "Die unveränderte Anwendung desselben Fragebogens auf alle Kulturen"],
        ["Using a universal framework developed outside of any specific culture", "Developing constructs and measures from within a specific culture", "Using Hofstede's dimensions to compare cultures", "Applying the same questionnaire across cultures without adaptation"],
        1,
    ),
    (
        "Internationales Marketing / International Marketing",
        "Konfigurale Messäquivalenz bedeutet:",
        "Configural measurement equivalence means:",
        ["Die gleiche Faktorstruktur (dieselben Items laden auf denselben Faktoren) gilt für alle kulturellen Gruppen", "Faktorladungen sind über kulturelle Gruppen hinweg gleich", "Item-Intercepts sind über kulturelle Gruppen hinweg gleich", "Latente Mittelwertvergleiche können zwischen Gruppen vorgenommen werden"],
        ["The same factor structure (same items loading on same factors) holds across cultural groups", "Factor loadings are equal across cultural groups", "Item intercepts are equal across cultural groups", "Latent mean comparisons can be made across groups"],
        0,
    ),
    (
        "Internationales Marketing / International Marketing",
        "Skalare Messäquivalenz (starke Äquivalenz) bedeutet:",
        "Scalar measurement equivalence (also called strong equivalence) means:",
        ["Die gleiche Faktorstruktur gilt für alle Gruppen", "Faktorladungen sind über alle Gruppen hinweg gleich", "Faktorladungen UND Item-Intercepts sind über alle Gruppen gleich – latente Mittelwertvergleiche sind möglich", "Alle Messparameter inklusive Residualvarianzen sind gleich"],
        ["The same factor structure holds across groups", "Factor loadings are equal across groups", "Factor loadings AND item intercepts are equal across groups, enabling latent mean comparisons", "All measurement parameters including residual variances are equal"],
        2,
    ),
    (
        "Internationales Marketing / International Marketing",
        "Hofstedes ursprüngliches Kulturmodell umfasste welche vier Dimensionen?",
        "Hofstede's original cultural framework included which four dimensions?",
        ["Machtdistanz, Individualismus/Kollektivismus, Maskulinität/Femininität, Unsicherheitsvermeidung", "Machtdistanz, Durchsetzungsvermögen, Individualismus, Langzeitorientierung", "Unsicherheitsvermeidung, Gleichstellung der Geschlechter, Zukunftsorientierung, humane Orientierung", "Kollektivismus, Schwartz-Werte, In-group-Kollektivismus, Machtdistanz"],
        ["Power distance, Individualism/Collectivism, Masculinity/Femininity, Uncertainty Avoidance", "Power distance, Assertiveness, Individualism, Long-term orientation", "Uncertainty avoidance, Gender egalitarianism, Future orientation, Humane orientation", "Collectivism, Schwartz values, In-group collectivism, Power distance"],
        0,
    ),
    (
        "Internationales Marketing / International Marketing",
        "Schwartz' Kulturwertetheorie schlägt wie viele Kulturdimensionen vor?",
        "Schwartz's cultural value theory proposes how many cultural dimensions?",
        ["4", "5", "7", "9"],
        ["4", "5", "7", "9"],
        2,
    ),
    (
        "Internationales Marketing / International Marketing",
        "Der kollaborativ-iterative Übersetzungsansatz wird der Standard-Rückübersetzung vorgezogen, weil:",
        "The collaborative iterative translation approach is preferred over standard back-translation because:",
        ["Er schneller und günstiger ist", "Er ein Team von Übersetzern einbezieht, die die Übersetzung iterativ verfeinern, um konzeptuelle statt nur linguistische Äquivalenz zu erreichen", "Er nur einen Übersetzer benötigt", "Er skalare Messäquivalenz garantiert"],
        ["It is faster and cheaper", "It involves a team of translators who iteratively refine the translation to achieve conceptual rather than just linguistic equivalence", "It requires only one translator", "It guarantees scalar measurement equivalence"],
        1,
    ),
    (
        "Internationales Marketing / International Marketing",
        "Konsumentenetnozentrismus im internationalen Marketing bezeichnet:",
        "Consumer ethnocentrism in international marketing refers to:",
        ["Die Präferenz der Verbraucher für globale gegenüber lokalen Marken", "Die Gleichgültigkeit der Verbraucher gegenüber inländischen und ausländischen Produkten", "Die Überzeugung der Verbraucher, dass der Kauf ausländischer Produkte moralisch falsch oder schädlich für die Volkswirtschaft ist", "Die Tendenz der Verbraucher, alle ausländischen Produkte als überlegen wahrzunehmen"],
        ["Consumers' preference for global brands over local brands", "Consumers' indifference between domestic and foreign products", "Consumers' belief that purchasing foreign products is morally wrong or harmful to the domestic economy", "Consumers' tendency to perceive all foreign products as superior"],
        2,
    ),
],

}  # end MASTER_POOL


# ── Version selection: non-overlapping draw of 4 per topic ───────────────────
def make_draws():
    """
    Shuffle each topic's 12 questions with GROUP_SEED, then assign
    indices [0-3] → A, [4-7] → B, [8-11] → C.
    Returns {version: [20 questions]}
    """
    rng = random.Random(GROUP_SEED)
    draws = {"A": [], "B": [], "C": []}
    for topic, qs in MASTER_POOL.items():
        pool = list(qs)
        rng.shuffle(pool)
        draws["A"].extend(pool[0:4])
        draws["B"].extend(pool[4:8])
        draws["C"].extend(pool[8:12])
    return draws


def shuffle_version(questions, seed):
    """Shuffle question order within each topic and reshuffle answer options."""
    rng = random.Random(seed)
    # group by topic preserving insertion order
    grouped, order = {}, []
    for q in questions:
        t = q[0]
        if t not in grouped:
            grouped[t] = []
            order.append(t)
        grouped[t].append(q)
    result = []
    for t in order:
        qs = list(grouped[t])
        rng.shuffle(qs)
        for q in qs:
            topic, qde, qen, opts_de, opts_en, correct = q
            idx = list(range(4))
            rng.shuffle(idx)
            result.append((
                topic, qde, qen,
                [opts_de[i] for i in idx],
                [opts_en[i] for i in idx],
                idx.index(correct),
            ))
    return result


# ── Styles ────────────────────────────────────────────────────────────────────
def make_styles(ver_color):
    return {
        "title":      ParagraphStyle("title",      fontSize=17, fontName="Helvetica-Bold",   textColor=ver_color, alignment=TA_CENTER, spaceAfter=3),
        "ver_badge":  ParagraphStyle("ver_badge",  fontSize=28, fontName="Helvetica-Bold",   textColor=ver_color, alignment=TA_CENTER),
        "subtitle":   ParagraphStyle("subtitle",   fontSize=10, fontName="Helvetica",        textColor=DGRAY, alignment=TA_CENTER, spaceAfter=2),
        "section":    ParagraphStyle("section",    fontSize=9,  fontName="Helvetica-Bold",   textColor=white, leading=12),
        "qnum":       ParagraphStyle("qnum",       fontSize=10, fontName="Helvetica-Bold",   textColor=ver_color, spaceBefore=3, spaceAfter=1),
        "qde":        ParagraphStyle("qde",        fontSize=10, fontName="Helvetica-Bold",   textColor=black, leading=13, spaceAfter=2),
        "qen":        ParagraphStyle("qen",        fontSize=8.5,fontName="Helvetica-Oblique",textColor=DGRAY, leading=11, spaceAfter=3),
        "opt_de":     ParagraphStyle("opt_de",     fontSize=9.5,fontName="Helvetica",        textColor=black, leading=12),
        "opt_en":     ParagraphStyle("opt_en",     fontSize=8,  fontName="Helvetica-Oblique",textColor=DGRAY, leading=10),
        "opt_de_c":   ParagraphStyle("opt_de_c",   fontSize=9.5,fontName="Helvetica-Bold",   textColor=GREEN, leading=12),
        "opt_en_c":   ParagraphStyle("opt_en_c",   fontSize=8,  fontName="Helvetica-BoldOblique", textColor=GREEN, leading=10),
        "hdr_label":  ParagraphStyle("hdr_label",  fontSize=9,  fontName="Helvetica-Bold",   textColor=DGRAY),
        "hdr_line":   ParagraphStyle("hdr_line",   fontSize=9,  fontName="Helvetica",        textColor=DGRAY),
        "footer":     ParagraphStyle("footer",     fontSize=7.5,fontName="Helvetica",        textColor=DGRAY, alignment=TA_CENTER),
        "sol_warn":   ParagraphStyle("sol_warn",   fontSize=10, fontName="Helvetica-Bold",   textColor=RED, alignment=TA_CENTER, spaceBefore=4, spaceAfter=6),
        "sh_title":   ParagraphStyle("sh_title",   fontSize=12, fontName="Helvetica-Bold",   textColor=ver_color, alignment=TA_CENTER, spaceAfter=5),
        "sh_hdr":     ParagraphStyle("sh_hdr",     fontSize=9,  fontName="Helvetica-Bold",   textColor=white, alignment=TA_CENTER, leading=11),
        "sh_cell":    ParagraphStyle("sh_cell",    fontSize=9,  fontName="Helvetica",        textColor=black, alignment=TA_CENTER, leading=11),
        "sh_cell_c":  ParagraphStyle("sh_cell_c",  fontSize=10, fontName="Helvetica-Bold",   textColor=white, alignment=TA_CENTER, leading=11),
        "sh_q":       ParagraphStyle("sh_q",       fontSize=9,  fontName="Helvetica-Bold",   textColor=ver_color, alignment=TA_CENTER, leading=11),
    }


def _sp(h=0.2): return Spacer(1, h * cm)
def _hr(t=1.0, c=MGRAY): return HRFlowable(width="100%", thickness=t, color=c)
def _p(text, style, S): return Paragraph(text, S[style])


# ── Page 1 header ─────────────────────────────────────────────────────────────
def header_block(version, S, vc):
    title_col = [Paragraph("Quantitative Methods — Exam / Prüfung", S["title"]),
                 _sp(0.25),
                 Paragraph("WU Vienna &nbsp;·&nbsp; Dr. Arne Floh", S["subtitle"])]
    top = Table([[title_col, Paragraph(f"Version&nbsp;{version}", S["ver_badge"])]],
                colWidths=[15.5*cm, 3.7*cm])
    top.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                              ("LEFTPADDING",(0,0),(-1,-1),0),
                              ("RIGHTPADDING",(0,0),(-1,-1),0),
                              ("LINERIGHT",(0,0),(0,0),1,MGRAY)]))
    elems = [top, _sp(0.3), _hr(2.0, vc), _sp(0.25)]

    nr = Table([[Paragraph("Name:", S["hdr_label"]), Paragraph(" ", S["hdr_line"]),
                 Paragraph("Student ID:", S["hdr_label"]), Paragraph(" ", S["hdr_line"])]],
               colWidths=[2.0*cm, 10.5*cm, 2.5*cm, 4.2*cm])
    nr.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"BOTTOM"),
                             ("LEFTPADDING",(0,0),(-1,-1),0),
                             ("RIGHTPADDING",(0,0),(-1,-1),6),
                             ("BOTTOMPADDING",(0,0),(-1,-1),3),
                             ("LINEBELOW",(1,0),(1,0),0.8,DGRAY),
                             ("LINEBELOW",(3,0),(3,0),0.8,DGRAY)]))
    elems.append(nr)
    elems.append(_sp(0.12))

    ir = Table([[Paragraph("Instructions / Anweisungen:", S["hdr_label"]),
                 Paragraph("Select exactly ONE answer per question. &nbsp;|&nbsp; Bitte genau EINE Antwort pro Frage ankreuzen.", S["hdr_line"])]],
               colWidths=[4.8*cm, 14.4*cm])
    ir.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
                             ("LEFTPADDING",(0,0),(-1,-1),0),
                             ("RIGHTPADDING",(0,0),(-1,-1),0)]))
    elems += [ir, _hr(1.0, MGRAY), _sp(0.15)]
    return elems


def topic_banner(topic, vc, S):
    t = Table([[Paragraph(topic, S["section"])]], colWidths=[19.2*cm])
    t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),vc),
                            ("TOPPADDING",(0,0),(-1,-1),5),
                            ("BOTTOMPADDING",(0,0),(-1,-1),5),
                            ("LEFTPADDING",(0,0),(-1,-1),6)]))
    return t


def question_block(idx, q, S, vc, solution=False, first_in_topic=False):
    topic, qde, qen, opts_de, opts_en, correct = q
    inner = []
    if first_in_topic:
        inner += [topic_banner(topic, vc, S), _sp(0.12)]
    inner += [Paragraph(f"Frage / Question {idx}", S["qnum"]),
              Paragraph(qde, S["qde"]),
              Paragraph(qen, S["qen"])]
    for i, (ode, oen) in enumerate(zip(opts_de, opts_en)):
        is_c = solution and (i == correct)
        ds, es = ("opt_de_c", "opt_en_c") if is_c else ("opt_de", "opt_en")
        row = Table([[Paragraph(f"<b>{LETTERS[i]})</b>", S[ds]),
                      [Paragraph(ode, S[ds]), Paragraph(oen, S[es])]]],
                    colWidths=[0.85*cm, 18.35*cm])
        row.setStyle(TableStyle([
            ("VALIGN",(0,0),(-1,-1),"TOP"),
            ("LEFTPADDING",(0,0),(-1,-1),1),
            ("RIGHTPADDING",(0,0),(-1,-1),1),
            ("TOPPADDING",(0,0),(-1,-1),2),
            ("BOTTOMPADDING",(0,0),(-1,-1),2),
            ("BACKGROUND",(0,0),(-1,-1), LGREEN if is_c else (LGRAY if i%2==0 else white)),
        ]))
        inner.append(row)
    inner.append(_sp(0.25))
    return KeepTogether(inner)


def answer_sheet(version, questions, S, vc, solution=False):
    elems = [PageBreak()]
    title = (f"Version {version} — Lösungsschlüssel / Solution Key"
             if solution else f"Version {version} — Antwortbogen / Answer Sheet")
    elems += [Paragraph(title, S["sh_title"]), _hr(1.5, vc), _sp(0.2)]

    if not solution:
        nr = Table([[Paragraph("Name:", S["hdr_label"]), Paragraph(" ", S["hdr_line"]),
                     Paragraph("Student ID:", S["hdr_label"]), Paragraph(" ", S["hdr_line"])]],
                   colWidths=[2.0*cm, 10.5*cm, 2.5*cm, 4.2*cm])
        nr.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"BOTTOM"),
                                 ("LEFTPADDING",(0,0),(-1,-1),0),
                                 ("RIGHTPADDING",(0,0),(-1,-1),6),
                                 ("BOTTOMPADDING",(0,0),(-1,-1),3),
                                 ("LINEBELOW",(1,0),(1,0),0.8,DGRAY),
                                 ("LINEBELOW",(3,0),(3,0),0.8,DGRAY)]))
        elems.append(nr)
    else:
        elems.append(Paragraph(
            f"<b>LÖSUNG / SOLUTION Version {version} — Nur für Lehrende / For instructors only</b>",
            S["sol_warn"]))

    elems += [_hr(0.8, MGRAY), _sp(0.3)]

    def half_table(qs_slice):
        rows = [[Paragraph(h, S["sh_hdr"]) for h in ["Frage/Q","A","B","C","D"]]]
        for q_num, q in qs_slice:
            c = q[5]
            row = [Paragraph(str(q_num), S["sh_q"])]
            for i in range(4):
                row.append(Paragraph(LETTERS[i] if (solution and i==c) else " ",
                                     S["sh_cell_c"] if (solution and i==c) else S["sh_cell"]))
            rows.append(row)
        t = Table(rows, colWidths=[1.6*cm,1.4*cm,1.4*cm,1.4*cm,1.4*cm], repeatRows=1)
        cmds = [("BACKGROUND",(0,0),(-1,0),vc),("TEXTCOLOR",(0,0),(-1,0),white),
                ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),9),
                ("ALIGN",(0,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[LGRAY,white]),
                ("GRID",(0,0),(-1,-1),0.5,MGRAY),
                ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]
        if solution:
            for ri, (_, q) in enumerate(qs_slice, 1):
                c = q[5]
                cmds += [("BACKGROUND",(c+1,ri),(c+1,ri),GREEN),
                         ("TEXTCOLOR",(c+1,ri),(c+1,ri),white)]
        t.setStyle(TableStyle(cmds))
        return t

    indexed = list(enumerate(questions, 1))
    combined = Table([[half_table(indexed[:10]), Spacer(1,1*cm), half_table(indexed[10:])]],
                     colWidths=[7.2*cm,1.2*cm,7.2*cm])
    combined.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"TOP"),
                                   ("LEFTPADDING",(0,0),(-1,-1),0),
                                   ("RIGHTPADDING",(0,0),(-1,-1),0)]))
    elems.append(combined)
    if not solution:
        elems += [_sp(0.5), _hr(0.8,MGRAY), _sp(0.15),
                  Paragraph("Bitte nur EINE Antwort pro Zeile ankreuzen. &nbsp;|&nbsp; Please tick exactly ONE box per row.", S["footer"])]
    return elems


def build_pdf(path, version, questions, solution=False):
    vc = VERSION_COLORS[version]
    S  = make_styles(vc)
    doc = SimpleDocTemplate(path, pagesize=A4,
                            leftMargin=1.5*cm, rightMargin=1.5*cm,
                            topMargin=1.5*cm,  bottomMargin=1.8*cm)
    story = header_block(version, S, vc)
    if solution:
        story.append(Paragraph(
            f"<b>LÖSUNG / SOLUTION Version {version} — Nur für Lehrende / For instructors only</b>",
            S["sol_warn"]))

    current_topic = None
    for idx, q in enumerate(questions, 1):
        first = (q[0] != current_topic)
        story.append(question_block(idx, q, S, vc, solution=solution, first_in_topic=first))
        current_topic = q[0]

    story += answer_sheet(version, questions, S, vc, solution=solution)

    label = "Lösungsschlüssel" if solution else "Prüfungsbogen"
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(DGRAY)
        w, _ = A4
        canvas.drawCentredString(w/2, 1.0*cm,
            f"WU Vienna · Quantitative Methods · Version {version} · {label} · 20 Fragen/Questions  —  Seite/Page {doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"  Written: {path}")


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    out = "/home/user/quantmethods/exam/exam-mc-questions"
    os.makedirs(out, exist_ok=True)

    draws = make_draws()

    # Print draw summary for transparency
    print(f"\nDraw summary (GROUP_SEED={GROUP_SEED}):")
    for ver in ["A","B","C"]:
        qs = draws[ver]
        topics = {}
        for q in qs:
            topics[q[0]] = topics.get(q[0], 0) + 1
        print(f"  Version {ver}: {dict(topics)}")

    for ver in ["A", "B", "C"]:
        print(f"\nGenerating Version {ver} …")
        qs = shuffle_version(draws[ver], VERSION_SEEDS[ver])
        build_pdf(f"{out}/exam_student_{ver}.pdf", ver, qs, solution=False)
        build_pdf(f"{out}/exam_solution_{ver}.pdf", ver, qs, solution=True)

    print("\nDone. 6 files written.")
