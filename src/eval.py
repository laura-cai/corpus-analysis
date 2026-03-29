"""
CLAN Corpus Analysis — Bates Free20 Dataset
============================================
Analyzes mother–child interaction data exported from CLAN (CHILDES).
Each row = one mother's speech to her child (named by the .cha file).

Questions addressed:
  Q1. Most frequently used words (FREQ_tokens / FREQ_types)
  Q2. Average vocabulary type usage (nouns, verbs, adjectives, function words)
  Q3. Which mother shows highest word frequency, lexical diversity,
      utterance length, and interactiveness?
  Q4. (Extended) Child-directed speech patterns by dyad
  Q5. Additional observations: open/closed-class ratio, verb density,
      utterance complexity clustering
"""

import xml.etree.ElementTree as ET
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch
import warnings
warnings.filterwarnings("ignore")

# ── 0. PARSE DATA ──────────────────────────────────────────────────────────────

SS = "urn:schemas-microsoft-com:office:spreadsheet"

def parse_xls_xml(filepath: str) -> pd.DataFrame:
    """Parse SpreadsheetML (.xls XML) into a DataFrame."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    ns = {"ss": SS}
    headers, data = [], []
    ws = root.find("ss:Worksheet", ns)
    table = ws.find("ss:Table", ns)
    for i, row in enumerate(table.findall("ss:Row", ns)):
        row_data = []
        for cell in row.findall("ss:Cell", ns):
            idx = cell.get(f"{{{SS}}}Index")
            data_el = cell.find("ss:Data", ns)
            val = data_el.text if data_el is not None else ""
            if idx:
                while len(row_data) < int(idx) - 1:
                    row_data.append("")
            row_data.append(val or "")
        if i == 0:
            headers = row_data
        else:
            data.append(row_data)
    for r in data:
        while len(r) < len(headers):
            r.append("")
    return pd.DataFrame(data, columns=headers)


# Load & clean
df_raw = parse_xls_xml("free20.eval.xls")
df = df_raw[df_raw["File"] != ""].copy()
df["Mom"] = df["File"].str.replace(r"\.cha$", "", regex=True).str.title()

NUM_COLS = [
    "FREQ_types", "FREQ_tokens", "FREQ_TTR",
    "MLU_Words", "MLU_Morphemes", "MLU_Utts",
    "Total_Utts", "Words_Min",
    "Verbs_Utt",
    "%_Nouns", "%_Verbs", "%_adj", "%_adv",
    "%_prep", "%_det", "%_pro", "%_conj", "%_Aux",
    "%_Plurals", "%_3S", "%_PAST", "%_PASTP", "%_PRESP",
    "#open-class", "#closed-class",
    "open_closed", "noun_verb",
    "retracing", "repetition",
]
for c in NUM_COLS:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# Derived metrics
df["function_words_pct"] = (
    df["%_prep"] + df["%_det"] + df["%_pro"] + df["%_conj"] + df["%_Aux"]
)
df["interactiveness"] = (
    df["retracing"] + df["repetition"] + df["Verbs_Utt"]
)

N = len(df)
print(f"✓ Loaded {N} mother–child dyads.\n")

# ── 1. MOST FREQUENT WORDS ─────────────────────────────────────────────────────

print("=" * 60)
print("Q1 — MOST FREQUENTLY USED WORDS (corpus-level)")
print("=" * 60)

total_tokens = df["FREQ_tokens"].sum()
total_types  = df["FREQ_types"].sum()
mean_tokens  = df["FREQ_tokens"].mean()
mean_types   = df["FREQ_types"].mean()

top_tokens = df.nlargest(5, "FREQ_tokens")[["Mom", "FREQ_tokens", "FREQ_types", "FREQ_TTR"]]
print(f"\nCorpus totals:  {total_tokens:.0f} tokens,  {total_types:.0f} types")
print(f"Per-dyad mean:  {mean_tokens:.1f} tokens,  {mean_types:.1f} types")
print(f"\nTop-5 dyads by FREQ_tokens (word frequency):")
print(top_tokens.to_string(index=False))

# ── 2. AVERAGE VOCABULARY TYPE USAGE ──────────────────────────────────────────

print("\n" + "=" * 60)
print("Q2 — AVERAGE VOCABULARY TYPE USAGE (%)")
print("=" * 60)

voc_cols = {
    "Nouns":          "%_Nouns",
    "Verbs":          "%_Verbs",
    "Adjectives":     "%_adj",
    "Function Words": "function_words_pct",
}
means = {label: df[col].mean() for label, col in voc_cols.items()}
stds  = {label: df[col].std()  for label, col in voc_cols.items()}

print(f"\n{'Category':<18} {'Mean %':>8} {'SD':>8}")
print("-" * 36)
for label in means:
    print(f"{label:<18} {means[label]:>8.2f} {stds[label]:>8.2f}")

dominant = max(means, key=means.get)
print(f"\n→ Dominant category: {dominant} ({means[dominant]:.2f}%)")

# ── 3. WHICH MOTHER SHOWS HIGHEST LEVELS? ─────────────────────────────────────

print("\n" + "=" * 60)
print("Q3 — MOTHERS WITH HIGHEST LEVELS (each metric)")
print("=" * 60)

metrics = {
    "Word Frequency (tokens)":  "FREQ_tokens",
    "Lexical Diversity (TTR)":  "FREQ_TTR",
    "Utterance Length (MLU)":   "MLU_Words",
    "Interactiveness Score":    "interactiveness",
}
print(f"\n{'Metric':<30} {'Mother':<12} {'Value':>8}")
print("-" * 52)
for label, col in metrics.items():
    best_row = df.loc[df[col].idxmax()]
    print(f"{label:<30} {best_row['Mom']:<12} {best_row[col]:>8.3f}")

# Composite ranking
df["rank_freq"]    = df["FREQ_tokens"].rank(ascending=False)
df["rank_ttr"]     = df["FREQ_TTR"].rank(ascending=False)
df["rank_mlu"]     = df["MLU_Words"].rank(ascending=False)
df["rank_inter"]   = df["interactiveness"].rank(ascending=False)
df["composite_rank"] = (
    df["rank_freq"] + df["rank_ttr"] + df["rank_mlu"] + df["rank_inter"]
) / 4

top3 = df.nsmallest(3, "composite_rank")[
    ["Mom", "FREQ_tokens", "FREQ_TTR", "MLU_Words", "interactiveness", "composite_rank"]
]
print(f"\nTop-3 overall (composite rank across all 4 metrics):")
print(top3.to_string(index=False))

# ── 4. CHILD-DIRECTED SPEECH PATTERNS ─────────────────────────────────────────
# Note: This dataset contains ONLY mother speech. 'Child' refers to
# the target child each mother is talking to.  We compare mothers using
# all available metrics to infer the child-directed register differences.

print("\n" + "=" * 60)
print("Q4 — CHILD-DIRECTED PATTERNS (per dyad / mother)")
print("=" * 60)

ordered_cols = [
    "Mom", "FREQ_tokens", "FREQ_TTR", "MLU_Words", "interactiveness",
    "%_Nouns", "%_Verbs", "function_words_pct"
]
summary = df[ordered_cols].sort_values("FREQ_tokens", ascending=False)
print("\nFull dyad summary (sorted by word frequency):")
print(summary.to_string(index=False))

# ── 5. ADDITIONAL OBSERVATIONS ────────────────────────────────────────────────

print("\n" + "=" * 60)
print("Q5 — ADDITIONAL OBSERVATIONS")
print("=" * 60)

# 5a. Open vs closed class ratio
print("\n[5a] Open/Closed-class word ratio:")
df_sorted_oc = df.sort_values("open_closed", ascending=False)
print(df_sorted_oc[["Mom","open_closed","#open-class","#closed-class"]].head(5).to_string(index=False))

# 5b. Verb density
print("\n[5b] Verb density (verbs per utterance):")
df_sorted_v = df.sort_values("Verbs_Utt", ascending=False)
print(df_sorted_v[["Mom","Verbs_Utt","%_Verbs","Total_Utts"]].head(5).to_string(index=False))

# 5c. Correlation matrix of key metrics
corr_cols = ["FREQ_tokens","FREQ_TTR","MLU_Words","interactiveness",
             "%_Nouns","%_Verbs","function_words_pct","open_closed"]
corr = df[corr_cols].corr().round(3)
print("\n[5c] Correlation matrix (key metrics):")
print(corr)

# ── FIGURES ───────────────────────────────────────────────────────────────────

PALETTE = ["#2196F3","#FF5722","#4CAF50","#9C27B0","#FF9800","#00BCD4"]
BG      = "#F8F9FA"
GRID_C  = "#E0E0E0"

def style_ax(ax, title, xlabel="", ylabel=""):
    ax.set_facecolor(BG)
    ax.grid(axis="y", color=GRID_C, linewidth=0.8, zorder=0)
    ax.spines[["top","right","left"]].set_visible(False)
    ax.set_title(title, fontsize=11, fontweight="bold", pad=8)
    if xlabel: ax.set_xlabel(xlabel, fontsize=9)
    if ylabel: ax.set_ylabel(ylabel, fontsize=9)
    ax.tick_params(axis="both", labelsize=8)


# ── Figure 1: Overview Dashboard ──────────────────────────────────────────────
fig1, axes = plt.subplots(2, 3, figsize=(16, 9))
fig1.patch.set_facecolor("white")
fig1.suptitle("CLAN Corpus Analysis — Bates Free20\nMother–Child Interaction Overview",
              fontsize=14, fontweight="bold", y=0.98)

## 1a. Word Frequency (tokens) per dyad
ax = axes[0, 0]
colors = [PALETTE[3] if v == df["FREQ_tokens"].max() else PALETTE[0]
          for v in df["FREQ_tokens"]]
ax.bar(df["Mom"], df["FREQ_tokens"], color=colors, edgecolor="white", width=0.7)
ax.set_xticklabels(df["Mom"], rotation=55, ha="right", fontsize=6.5)
style_ax(ax, "Q1 · Word Frequency (Tokens) per Dyad", ylabel="Token Count")

## 1b. Vocabulary type breakdown (Q2)
ax = axes[0, 1]
categories = list(means.keys())
values     = [means[k] for k in categories]
bars = ax.bar(categories, values, color=PALETTE[:4], edgecolor="white", width=0.55)
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f"{val:.1f}%", ha="center", va="bottom", fontsize=8, fontweight="bold")
style_ax(ax, "Q2 · Average Vocabulary Type Usage", ylabel="Mean %")

## 1c. Lexical Diversity (TTR) per dyad
ax = axes[0, 2]
colors = [PALETTE[1] if v == df["FREQ_TTR"].max() else PALETTE[2]
          for v in df["FREQ_TTR"]]
ax.bar(df["Mom"], df["FREQ_TTR"], color=colors, edgecolor="white", width=0.7)
ax.set_xticklabels(df["Mom"], rotation=55, ha="right", fontsize=6.5)
ax.axhline(df["FREQ_TTR"].mean(), color="#333", linestyle="--", linewidth=1.2,
           label=f"Mean={df['FREQ_TTR'].mean():.3f}")
ax.legend(fontsize=7)
style_ax(ax, "Q3 · Lexical Diversity (TTR)", ylabel="TTR")

## 1d. MLU per dyad
ax = axes[1, 0]
colors = [PALETTE[4] if v == df["MLU_Words"].max() else PALETTE[0]
          for v in df["MLU_Words"]]
ax.bar(df["Mom"], df["MLU_Words"], color=colors, edgecolor="white", width=0.7)
ax.set_xticklabels(df["Mom"], rotation=55, ha="right", fontsize=6.5)
ax.axhline(df["MLU_Words"].mean(), color="#333", linestyle="--", linewidth=1.2,
           label=f"Mean={df['MLU_Words'].mean():.2f}")
ax.legend(fontsize=7)
style_ax(ax, "Q3 · Mean Length of Utterance (MLU)", ylabel="Words per Utterance")

## 1e. Interactiveness per dyad
ax = axes[1, 1]
colors = [PALETTE[3] if v == df["interactiveness"].max() else PALETTE[5]
          for v in df["interactiveness"]]
ax.bar(df["Mom"], df["interactiveness"], color=colors, edgecolor="white", width=0.7)
ax.set_xticklabels(df["Mom"], rotation=55, ha="right", fontsize=6.5)
style_ax(ax, "Q3 · Interactiveness Score", ylabel="Score (retracing + repetition + Verbs/Utt)")

## 1f. Scatter: MLU vs TTR
ax = axes[1, 2]
sc = ax.scatter(df["MLU_Words"], df["FREQ_TTR"],
                c=df["FREQ_tokens"], cmap="viridis",
                s=60, edgecolors="white", linewidth=0.5, zorder=3)
plt.colorbar(sc, ax=ax, label="Token Count", shrink=0.85)
for _, row in df.iterrows():
    ax.annotate(row["Mom"], (row["MLU_Words"], row["FREQ_TTR"]),
                fontsize=5.5, alpha=0.8,
                xytext=(2, 2), textcoords="offset points")
z = np.polyfit(df["MLU_Words"].dropna(), df["FREQ_TTR"].dropna(), 1)
xs = np.linspace(df["MLU_Words"].min(), df["MLU_Words"].max(), 100)
ax.plot(xs, np.polyval(z, xs), "r--", linewidth=1.2, alpha=0.7)
style_ax(ax, "Q5 · MLU vs. Lexical Diversity", "MLU (Words)", "TTR")

plt.tight_layout(rect=[0, 0, 1, 0.95])
fig1.savefig("clan_analysis_fig1_overview.png", dpi=150, bbox_inches="tight")
print("\n✓ Figure 1 saved: clan_analysis_fig1_overview.png")
plt.close()


# ── Figure 2: Top Performers & Vocabulary Profile ─────────────────────────────
fig2, axes2 = plt.subplots(1, 3, figsize=(16, 5))
fig2.patch.set_facecolor("white")
fig2.suptitle("CLAN Corpus — Vocabulary Profile & Top Performers",
              fontsize=13, fontweight="bold")

## 2a. Open vs Closed class stacked bar
ax = axes2[0]
df_oc = df.set_index("Mom")[["#open-class","#closed-class"]].sort_values(
    "#open-class", ascending=False)
bottom = np.zeros(len(df_oc))
for i, (col, lbl, col_) in enumerate(
        [("#open-class","Open-class",PALETTE[0]),
         ("#closed-class","Closed-class",PALETTE[1])]):
    ax.bar(df_oc.index, df_oc[col], bottom=bottom,
           color=col_, label=lbl, edgecolor="white", width=0.7)
    bottom += df_oc[col].values
ax.set_xticklabels(df_oc.index, rotation=55, ha="right", fontsize=6.5)
ax.legend(fontsize=8)
style_ax(ax, "Q5 · Open vs. Closed-class Words", ylabel="Word Count")

## 2b. Verb density ranking
ax = axes2[1]
df_vb = df.sort_values("Verbs_Utt", ascending=True)
ax.barh(df_vb["Mom"], df_vb["Verbs_Utt"],
        color=[PALETTE[2] if v >= df["Verbs_Utt"].quantile(0.75)
               else PALETTE[0] for v in df_vb["Verbs_Utt"]],
        edgecolor="white", height=0.7)
ax.axvline(df["Verbs_Utt"].mean(), color="#333", linestyle="--",
           linewidth=1.2, label=f"Mean={df['Verbs_Utt'].mean():.3f}")
ax.legend(fontsize=7)
ax.tick_params(axis="y", labelsize=7)
style_ax(ax, "Q5 · Verb Density (Verbs/Utterance)", "Verbs per Utterance")

## 2c. Composite rank radar / lollipop
ax = axes2[2]
df_rank = df.sort_values("composite_rank")
rank_metrics = ["FREQ_tokens","FREQ_TTR","MLU_Words","interactiveness"]
rank_labels  = ["Frequency","Diversity","MLU","Interactive"]
# Normalise 0-1
norm = df[rank_metrics].apply(lambda x: (x - x.min())/(x.max()-x.min()))
for i, mom in enumerate(df["Mom"]):
    idx = df[df["Mom"]==mom].index[0]
    vals = [norm.loc[idx, c] for c in rank_metrics]
    comp = sum(vals)/4
    color = PALETTE[3] if comp >= norm.mean().mean()*1.3 else PALETTE[0]
    ax.barh(i, comp, color=color, alpha=0.8, height=0.6)
ax.set_yticks(range(len(df)))
ax.set_yticklabels(df["Mom"].tolist(), fontsize=6.5)
ax.axvline(0.5, color="gray", linestyle="--", linewidth=1)
style_ax(ax, "Q3 · Composite Performance Score\n(normalised avg. of 4 metrics)",
         "Composite Score (0–1)")

plt.tight_layout()
fig2.savefig("clan_analysis_fig2_profiles.png", dpi=150, bbox_inches="tight")
print("✓ Figure 2 saved: clan_analysis_fig2_profiles.png")
plt.close()


# ── Figure 3: Correlation Heatmap ─────────────────────────────────────────────
fig3, ax3 = plt.subplots(figsize=(9, 7))
fig3.patch.set_facecolor("white")

corr_display = corr.copy()
labels = ["Tokens","TTR","MLU","Interact.","%Nouns","%Verbs","%FuncW","Open/Closed"]
corr_display.index   = labels
corr_display.columns = labels

im = ax3.imshow(corr_display.values, cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
plt.colorbar(im, ax=ax3, shrink=0.8, label="Pearson r")
ax3.set_xticks(range(len(labels))); ax3.set_yticks(range(len(labels)))
ax3.set_xticklabels(labels, rotation=35, ha="right", fontsize=9)
ax3.set_yticklabels(labels, fontsize=9)
for i in range(len(labels)):
    for j in range(len(labels)):
        val = corr_display.values[i, j]
        ax3.text(j, i, f"{val:.2f}", ha="center", va="center",
                 fontsize=7.5, color="white" if abs(val) > 0.6 else "black")
ax3.set_title("Q5 · Correlation Matrix — Key CLAN Metrics", fontsize=12, fontweight="bold")
plt.tight_layout()
fig3.savefig("clan_analysis_fig3_corr.png", dpi=150, bbox_inches="tight")
print("✓ Figure 3 saved: clan_analysis_fig3_corr.png")
plt.close()

print("\n✅  All analyses and figures complete.")
print("\n── SUMMARY OF FINDINGS ──────────────────────────────────────")
for label, col in metrics.items():
    best = df.loc[df[col].idxmax(), "Mom"]
    val  = df[col].max()
    print(f"  Highest {label:30s}: {best} ({val:.3f})")
print()