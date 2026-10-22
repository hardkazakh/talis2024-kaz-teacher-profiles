"""Variable lists shared by all scripts (definitions follow Table 1 of the manuscript)."""

ID_VARS = ["CNTRY", "IDCNTRY", "IDSCHOOL", "IDTEACH", "IDTQUEST"]

DOMAINS = {
    "digital_practice": ["T4DRTWCI", "T4DRTIIA"],
    "self_efficacy": ["T4SECLS", "T4SEINS", "T4SEENG"],
    "instructional_practice": ["T4CLAIN", "T4COGAC", "T4CLASM", "T4ADLE", "T4PBLE", "T4FULFIL"],
    "collaboration_autonomy": ["T4EXINF", "T4COLES", "T4AUTCH"],
    "wellbeing_stress": ["T4WELS", "T4WLOADT", "T4STBEH"],
    "job_satisfaction": ["T4JOBSAT", "T4JOYTCH"],
}
COMPETENCE = [v for vs in DOMAINS.values() for v in vs]          # 19 scales
TARGET = "T4PDGENP"                                              # PD need: general pedagogy
EXCLUDED = ["T4PDSUBMP", "T4PDIV"]                               # sibling PD-need scales
BACKGROUND = ["T4TAGEGR", "T4THEDAT", "T4TYQUAL", "T4TYEXPE", "T4TNSCH", "T4TCSIZE"]
WEIGHT = "TCHWGT"

SUBSET = ID_VARS + COMPETENCE + [TARGET] + EXCLUDED + BACKGROUND + [WEIGHT]

# Missing-value codes in the OECD public-use file (verified against IDTQUEST in this extract):
#   scale scores : 9998 = not administered (rotated form), 9999 = omitted/invalid
#   1-digit cats : 8 = not administered, 9 = omitted/invalid
#   2-digit cats : 98 = not administered, 99 = omitted/invalid
SCALE_MISSING = (9998, 9999)
CAT_MISSING = {"T4TYQUAL": (98, 99)}          # all other background variables use (8, 9)
DEFAULT_CAT_MISSING = (8, 9)
