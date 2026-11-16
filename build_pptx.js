const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "PhishNet-GNN: Real-Time Phishing Detection Using Graph Neural Networks";
pres.author = "Project Team";

const C = {
  navy: "1E2761", iceBlue: "CADCFC", lightBg: "F8F9FC", white: "FFFFFF",
  darkGray: "2C3E50", textBlue: "3498DB", green: "27AE60", red: "E74C3C",
  mutedGray: "8BA4C4"
};

// Master Slides
const COVER = pres.defineSlideMaster({
  title: "Cover Layout", background: { color: C.navy }, margin: [0, 0, 0, 0],
  objects: [
    { placeholder: { options: { name: "title", w: 9, h: 1.0, x: 0.5, y: 1.5 } } },
    { placeholder: { options: { name: "subtitle", w: 9, h: 0.4, x: 0.5, y: 2.7 } } },
    { placeholder: { options: { name: "body", w: 9, h: 2.2, x: 0.5, y: 3.3 } } }
  ]
});

const DARK_HDR = pres.defineSlideMaster({
  title: "Dark Header Layout", background: { color: C.navy }, margin: [0.4, 0.5, 0.4, 0.5],
  objects: [
    { placeholder: { options: { name: "title", w: 10, h: 0.7, x: 0.5, y: 0.4 } } },
    { placeholder: { options: { name: "body", w: 10, h: 4.2, x: 0.5, y: 1.2 } } }
  ]
});

const LIGHT_SLIDE = pres.defineSlideMaster({
  title: "Light Content Layout", background: { color: C.lightBg }, margin: [0.4, 0.5, 0.4, 0.5],
  objects: [
    { placeholder: { options: { name: "title", w: 10, h: 0.6, x: 0.5, y: 0.2 } } },
    { placeholder: { options: { name: "body", w: 10, h: 4.5, x: 0.5, y: 0.85 } } }
  ]
});

const TWO_COL = pres.defineSlideMaster({
  title: "Two Column Layout", background: { color: C.lightBg }, margin: [0.4, 0.4, 0.4, 0.4],
  objects: [
    { placeholder: { options: { name: "title", w: 10, h: 0.55, x: 0.4, y: 0.15 } } },
    { placeholder: { options: { name: "left", w: 4.6, h: 4.8, x: 0.4, y: 0.8 } } },
    { placeholder: { options: { name: "right", w: 4.6, h: 4.8, x: 5.0, y: 0.8 } } }
  ]
});

// ── SLIDE 1: TITLE ────────────────────────────────────────
let s1 = pres.addSlide(COVER);
s1.addText("PhishNet-GNN", { placeholder: "title", options: { fontFace: "Cambria", size: 48, bold: true, color: C.white } });
s1.addText("Real-Time Phishing Domain Detection Using Graph Neural Networks", { placeholder: "subtitle", options: { fontFace: "Calibri", size: 20, color: C.iceBlue } });
s1.addText([
  { text: "Department of Computer Science & Engineering (AIML/DS/CS)", options: { breakLine: true, fontSize: 14, color: C.iceBlue } },
  { text: "School of Engineering and Technology", options: { breakLine: true, fontSize: 14, color: C.iceBlue } },
  { text: "GIET University, Gunupur", options: { breakLine: true, fontSize: 14, color: C.iceBlue } },
  { text: "", options: { breakLine: true, fontSize: 12, color: C.mutedGray } },
  { text: "Submitted by:", options: { bold: true, fontSize: 13, color: C.white } },
  { text: "\nUnder the Guidance of:", options: { breakLine: true, fontSize: 13, color: C.mutedGray } },
], { placeholder: "body", options: { fontFace: "Calibri", size: 14, color: C.iceBlue } });

// ── SLIDE 2: ABSTRACT ─────────────────────────────────────
let s2 = pres.addSlide(LIGHT_SLIDE);
s2.addText("Abstract", { placeholder: "title", options: { fontFace: "Cambria", size: 32, bold: true, color: C.navy } });
s2.addText(
  "Phishing websites steal login credentials, banking details, and personal information through deceptive sites that mimic legitimate portals. Traditional detection methods like blacklists and rule-based techniques fail against newly created zero-hour phishing domains.",
  { placeholder: "body", options: { fontFace: "Calibri", size: 18, color: C.darkGray, paraSpaceAfter: 24, margin: 0 } }
);
s2.addText(
  "Our system models the network infrastructure behind each domain\u2014DNS records, IP addresses, nameservers, SSL certificates, and WHOIS data\u2014as a heterogeneous star graph. A trained Graph Convolutional Network (GCN) in PyTorch Geometric classifies domains as Legitimate or Phishing, achieving 96.85% accuracy in under 2.2 seconds, overcoming the limitations of isolated URL-string analysis.",
  { placeholder: "body", options: { fontFace: "Calibri", size: 18, color: C.darkGray, paraSpaceBefore: 12, margin: 0 } }
);

// ── SLIDE 3: PROBLEM STATEMENT ───────────────────────────
let s3 = pres.addSlide(DARK_HDR);
s3.addText("Problem Statement", { placeholder: "title", options: { fontFace: "Cambria", size: 36, bold: true, color: C.white } });
s3.addText(
  "Phishing detection based purely on static rules or isolated URL strings ignores the network relationships that connect malicious operations. Attackers reuse DNS nameservers, register domains through shared registrar accounts, and host pages across common IP subnets. Evaluating a URL in isolation throws away this critical relational context.",
  { placeholder: "body", options: { fontFace: "Calibri", size: 20, color: C.iceBlue, paraSpaceAfter: 20, margin: 0 } }
);
s3.addText("\u2192  Blacklists lag behind rapid automated domain generation", { options: { fontFace: "Calibri", size: 16, color: C.mutedGray, bullet: true, paraSpaceAfter: 6 } });
s3.addText("\u2192  Lexical heuristics easily bypassed by clean-looking domain names", { options: { fontFace: "Calibri", size: 16, color: C.mutedGray, bullet: true, paraSpaceAfter: 6 } });
s3.addText("\u2192  Headless-browser inspection takes 5\u201315 sec per page \u2014 too slow for real-time use", { options: { fontFace: "Calibri", size: 16, color: C.mutedGray, bullet: true } });

// ── SLIDE 4: OBJECTIVES & FEATURES ────────────────────────
let s4 = pres.addSlide(LIGHT_SLIDE);
s4.addText("Objectives & Key Features", { placeholder: "title", options: { fontFace: "Cambria", size: 32, bold: true, color: C.navy } });
const objs = [
  { t: "Automated Feature Pipeline", d: "Live DNS, WHOIS, and SSL extraction for any submitted URL" },
  { t: "Graph-Based Modelling", d: "Heterogeneous star graphs via NetworkX (Domain \u2194 IP \u2194 NS \u2194 Registrar)" },
  { t: "GCN Classification", d: "PyTorch Geometric GCN achieving \u2265 95% accuracy target" },
  { t: "Real-Time Response", d: "End-to-end detection within 2\u20133 seconds" },
  { t: "Web Interface", d: "Flask + SQLite dashboard for predictions and history logging" },
  { t: "Baseline Benchmarking", d: "Compare GNN performance vs. Random Forest & XGBoost" },
];
objs.forEach((o, i) => {
  const col = Math.floor(i / 3);
  const row = i % 3;
  const cx = 0.5 + col * 4.8;
  const cy = 0.9 + row * 1.4;
  const bgColor = col === 0 ? "EBF5FB" : "E9F7EF";
  s4.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx, y: cy, w: 4.5, h: 1.2, fill: { color: bgColor }, rectRadius: 0.08 });
  s4.addText(o.t, { x: cx + 0.15, y: cy + 0.1, w: 4.2, h: 0.4, fontSize: 14, bold: true, color: C.navy, fontFace: "Calibri" });
  s4.addText(o.d, { x: cx + 0.15, y: cy + 0.55, w: 4.2, h: 0.55, fontSize: 12, color: C.darkGray, fontFace: "Calibri" });
});

// ── SLIDE 5: LITERATURE REVIEW TABLE ─────────────────────
let s5 = pres.addSlide(LIGHT_SLIDE);
s5.addText("Literature Review: Comparative Analysis", { placeholder: "title", options: { fontFace: "Cambria", size: 32, bold: true, color: C.navy } });
const tableData = [
  [{ text: "Author(s)", options: { bold: true, fill: { color: C.navy }, color: C.white, fontSize: 11 } },
   { text: "Technology", options: { bold: true, fill: { color: C.navy }, color: C.white, fontSize: 11 } },
   { text: "Key Result", options: { bold: true, fill: { color: C.navy }, color: C.white, fontSize: 11 } },
   { text: "Limitation", options: { bold: true, fill: { color: C.navy }, color: C.white, fontSize: 11 } }],
  ["Marchal et al. (2016)", "Lexical + Search Ranking", "93.5% accuracy", "SEO manipulation risk"],
  ["Sahingoz et al. (2019)", "RF on NLP features", "97.98% accuracy", "Fails on compromised legit sites"],
  ["Rao et al. (2020)", "CatchPhish (CNN+URL)", "94.2% detection", "6+ sec per page render"],
  ["Al-Ahmadi (2020)", "XGBoost on DNS logs", "96.7% detection", "CDN masking (Cloudflare)"],
  ["Li et al. (2022)", "GCN on ISP graphs", "98.1% F1-score", "Offline batch only, no single URL"],
  ["Proposed System (2026)", "On-demand Graph + GCN", "96.85% accuracy, ~2.16s", "Relies on public DNS/WHOIS"],
];
s5.addTable(tableData, {
  x: 0.4, y: 0.8, w: 9.2, h: 4.2,
  fontSize: 11, fontFace: "Calibri", color: C.darkGray,
  border: { pt: 0.5, color: "DDDDDD" },
  colW: [2.2, 2.6, 2.2, 2.2],
  rowH: [0.35, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6]
});

// ── SLIDE 6: SYSTEM ARCHITECTURE ─────────────────────────
let s6 = pres.addSlide(TWO_COL);
s6.addText("System Architecture", { placeholder: "title", options: { fontFace: "Cambria", size: 30, bold: true, color: C.navy } });
s6.addText("Three-Tier Design", { placeholder: "left", options: { fontFace: "Calibri", size: 16, color: C.navy, margin: 0 } });
// Tier boxes inside left column
s6.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.3, w: 4.3, h: 1.3, fill: { color: "EBF5FB" }, line: { color: C.textBlue, pt: 1 } });
s6.addText("User Web Browser\nHTML5 / CSS3 / Vanilla JavaScript", { x: 0.6, y: 1.35, w: 4.1, h: 1.2, fontSize: 13, fontFace: "Calibri", color: C.navy, valign: "middle" });
s6.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 2.75, w: 4.3, h: 1.3, fill: { color: "FEF9E7" }, line: { color: "F39C12", pt: 1 } });
s6.addText("Flask Backend Server\nURL Sanitization \u2192 Feature Extraction \u2192 Graph Build \u2192 Inference", { x: 0.6, y: 2.8, w: 4.1, h: 1.2, fontSize: 13, fontFace: "Calibri", color: C.navy, valign: "middle" });
s6.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 4.2, w: 4.3, h: 1.0, fill: { color: "E9F7EF" }, line: { color: C.green, pt: 1 } });
s6.addText("SQLite Database\nLookup History & Model Weights", { x: 0.6, y: 4.25, w: 4.1, h: 0.9, fontSize: 13, fontFace: "Calibri", color: C.navy, valign: "middle" });

s6.addText("Technology Stack", { placeholder: "right", options: { fontFace: "Calibri", size: 16, bold: true, color: C.navy, margin: 0 } });
const tech = [
  { label: "Deep Learning", items: "PyTorch 2.x, PyTorch Geometric" },
  { label: "Graph Processing", items: "NetworkX 3.x" },
  { label: "ML Baselines", items: "scikit-learn, XGBoost" },
  { label: "Networking Tools", items: "dnspython, python-whois, tldextract" },
  { label: "Backend Framework", items: "Flask 3.x, Flask-CORS" },
  { label: "Database", items: "SQLite 3" },
  { label: "Environment", items: "Python 3.11, VS Code, Git" },
];
tech.forEach((t, i) => {
  s6.addText(t.label, { x: 5.1, y: 1.0 + i * 0.58, w: 4.4, h: 0.25, fontSize: 12, bold: true, color: C.textBlue, fontFace: "Calibri" });
  s6.addText(t.items, { x: 5.1, y: 1.25 + i * 0.58, w: 4.4, h: 0.25, fontSize: 12, color: C.darkGray, fontFace: "Calibri" });
});

// ── SLIDE 7: GRAPH CONSTRUCTION & GCN ────────────────────
let s7 = pres.addSlide(LIGHT_SLIDE);
s7.addText("Graph Construction & GCN Pipeline", { placeholder: "title", options: { fontFace: "Cambria", size: 32, bold: true, color: C.navy } });
s7.addText("Node Types (4) \u2014 Each receives a 16-dim feature vector augmented with one-hot entity-type indicator:", { options: { fontFace: "Calibri", size: 16, color: C.darkGray, paraSpaceAfter: 8, margin: 0 } });
s7.addText("\u2022  URL Node     \u2014 lexical features (Shannon entropy, char ratios, special chars)", { options: { fontFace: "Calibri", size: 14, color: C.darkGray, bullet: true, paraSpaceAfter: 4 } });
s7.addText("\u2022  IP Node      \u2014 resolved A-record IPs, ASN reputation, GeoIP hints", { options: { fontFace: "Calibri", size: 14, color: C.darkGray, bullet: true, paraSpaceAfter: 4 } });
s7.addText("\u2022  Nameserver   \u2014 authoritative NS records, TTL values", { options: { fontFace: "Calibri", size: 14, color: C.darkGray, bullet: true, paraSpaceAfter: 4 } });
s7.addText("\u2022  Registrar    \u2014 WHOIS registration age, expiry date, registrar reputation", { options: { fontFace: "Calibri", size: 14, color: C.darkGray, bullet: true, paraSpaceAfter: 16 } });
s7.addText("Edge Relations \u2014 RESOLVES_TO, DELEGATED_TO, REGISTERED_BY", { options: { fontFace: "Calibri", size: 14, bold: true, color: C.navy, paraSpaceAfter: 4, margin: 0 } });
s7.addText("A_norm \u00B7 X \u00B7 W1 \u2192 BatchNorm \u2192 ReLU \u2192 A_norm \u00B7 H1 \u00B7 W2 \u2192 BatchNorm \u2192 ReLU\nGlobal Mean Pooling \u2192 Linear Head \u2192 Softmax \u2192 P(Legitimate) vs P(Phishing)", { options: { fontFace: "Courier New", size: 13, color: C.navy, paraSpaceBefore: 8, margin: 0 } });

// ── SLIDE 8: IMPLEMENTATION MODULES ──────────────────────
let s8 = pres.addSlide(LIGHT_SLIDE);
s8.addText("Implementation Modules", { placeholder: "title", options: { fontFace: "Cambria", size: 32, bold: true, color: C.navy } });
const mods = [
  { name: "URL Sanitizer", desc: "Input validation, XSS sanitisation, tldextract domain parsing" },
  { name: "Feature Extractor", desc: "Live DNS A/NS lookups, WHOIS parse, SSL handshake check" },
  { name: "Graph Builder", desc: "NetworkX star-graph construction, PyG tensor export" },
  { name: "GCN Engine", desc: "Load gcn_model.pt weights, run inference, return confidence" },
  { name: "Flask API", desc: "/api/detect endpoint, SQLite logging, JSON response" },
  { name: "Dashboard UI", desc: "Single-page HTML/JS interface with risk bars & history" },
];
mods.forEach((m, i) => {
  const col = i % 3;
  const row = Math.floor(i / 3);
  const cx = 0.5 + col * 3.2;
  const cy = 0.85 + row * 2.1;
  s8.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx, y: cy, w: 3.0, h: 1.9, fill: { color: "FFFFFF" }, shadow: { type: "outer", blur: 4, offset: 2, angle: 135, color: "000000", opacity: 0.1 } });
  s8.addText(m.name, { x: cx + 0.15, y: cy + 0.15, w: 2.7, h: 0.4, fontSize: 13, bold: true, color: C.navy, fontFace: "Calibri" });
  s8.addText(m.desc, { x: cx + 0.15, y: cy + 0.65, w: 2.7, h: 1.1, fontSize: 11, color: C.darkGray, fontFace: "Calibri" });
});

// ── SLIDE 9: RESULTS ──────────────────────────────────────
let s9 = pres.addSlide(LIGHT_SLIDE);
s9.addText("Experimental Results", { placeholder: "title", options: { fontFace: "Cambria", size: 32, bold: true, color: C.navy } });
const rTable = [
  ["Model", "Accuracy", "Precision", "Recall", "F1-Score", "Latency"],
  ["Random Forest", "91.20%", "89.80%", "90.50%", "90.15%", "~0.08 s"],
  ["XGBoost", "93.45%", "92.60%", "92.10%", "92.35%", "~0.09 s"],
  [{ text: "Proposed GCN", options: { bold: true, color: C.navy } }, "96.85%", "96.10%", "95.90%", "96.00%", "~0.12 s"],
];
s9.addTable(rTable, {
  x: 0.4, y: 0.8, w: 9.2, h: 1.9,
  fontSize: 13, fontFace: "Calibri", color: C.darkGray,
  border: { pt: 0.5, color: "CCCCCC" },
  colW: [2.0, 1.2, 1.2, 1.2, 1.2, 1.2],
  fill: { color: "FFFFFF" }
});
s9.addText("Key Observations:\nThe GCN outperforms tabular baselines by leveraging relational context \u2014 correctly flagging zero-day domains with clean lexical profiles that fool RF/XGB. An in-memory cache cut repeat-scan latency to 0.25 s.", { options: { fontFace: "Calibri", size: 14, color: C.darkGray, paraSpaceBefore: 8, margin: 0 } });

// ── SLIDE 10: TESTING ─────────────────────────────────────
let s10 = pres.addSlide(LIGHT_SLIDE);
s10.addText("Testing & Validation", { placeholder: "title", options: { fontFace: "Cambria", size: 32, bold: true, color: C.navy } });
s10.addText("All eight test cases passed successfully:", { options: { fontFace: "Calibri", size: 16, color: C.darkGray, paraSpaceAfter: 12, margin: 0 } });
const tests = [
  { id: "TC-01", focus: "Empty Submission", result: "PASSED" },
  { id: "TC-02", focus: "Input Sanitization (XSS)", result: "PASSED" },
  { id: "TC-03", focus: "Hidden WHOIS (Cloudflare)", result: "PASSED" },
  { id: "TC-04", focus: "Network Timeout Handling", result: "PASSED" },
  { id: "TC-05", focus: "Graph Integrity (no NS)", result: "PASSED" },
  { id: "TC-06", focus: "Malicious PhishTank URL", result: "PASSED (96.2% conf.)" },
  { id: "TC-07", focus: "Legitimate URL (GitHub)", result: "PASSED (99.1% conf.)" },
  { id: "TC-08", focus: "History Logging (SQLite)", result: "PASSED" },
];
tests.forEach((tc, i) => {
  const col = i % 4;
  const row = Math.floor(i / 4);
  const cx = 0.4 + col * 2.35;
  const cy = 1.0 + row * 1.5;
  s10.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx, y: cy, w: 2.2, h: 1.3, fill: { color: "E9F7EF" }, rectRadius: 0.06 });
  s10.addText(tc.id, { x: cx + 0.1, y: cy + 0.1, w: 0.8, h: 0.3, fontSize: 11, bold: true, color: C.darkGray, fontFace: "Calibri" });
  s10.addText(tc.focus, { x: cx + 0.1, y: cy + 0.4, w: 2.0, h: 0.35, fontSize: 11, color: C.darkGray, fontFace: "Calibri" });
  s10.addText("\u2713 " + tc.result, { x: cx + 0.1, y: cy + 0.85, w: 2.0, h: 0.35, fontSize: 12, bold: true, color: C.green, fontFace: "Calibri" });
});

// ── SLIDE 11: LIMITATIONS & FUTURE SCOPE ──────────────────
let s11 = pres.addSlide(TWO_COL);
s11.addText("Limitations & Future Scope", { placeholder: "title", options: { fontFace: "Cambria", size: 30, bold: true, color: C.navy } });
s11.addText("Current Limitations", { placeholder: "left", options: { fontFace: "Calibri", size: 16, bold: true, color: C.red, margin: 0 } });
s11.addText([
  { text: "\u2022  Dependency on live DNS/WHOIS servers;", options: { breakLine: true, fontSize: 13, color: C.darkGray } },
  { text: "\u2022  CDN masking hides real backend IPs;", options: { breakLine: true, fontSize: 13, color: C.darkGray } },
  { text: "\u2022  Sparse graphs for free-hosted subdomains;", options: { breakLine: true, fontSize: 13, color: C.darkGray } },
  { text: "\u2022  No full-page visual inspection module;", options: { breakLine: true, fontSize: 13, color: C.darkGray } },
], { placeholder: "left", options: { fontFace: "Calibri", size: 14, color: C.darkGray, paraSpaceAfter: 16, margin: 0 } });
s11.addText("Future Enhancements", { placeholder: "right", options: { fontFace: "Calibri", size: 16, bold: true, color: C.green, margin: 0 } });
s11.addText([
  { text: "\u2022  Graph Attention Networks (GAT/HAN) for weighted edges;", options: { breakLine: true, fontSize: 13, color: C.darkGray } },
  { text: "\u2022  Lightweight favicon/title-tag checks for brand spoofing;", options: { breakLine: true, fontSize: 13, color: C.darkGray } },
  { text: "\u2022  Chrome/Firefox browser extension deployment;", options: { breakLine: true, fontSize: 13, color: C.darkGray } },
  { text: "\u2022  Automated daily retraining pipeline from OpenPhish feeds;", options: { breakLine: true, fontSize: 13, color: C.darkGray } },
], { placeholder: "right", options: { fontFace: "Calibri", size: 14, color: C.darkGray, paraSpaceAfter: 16, margin: 0 } });

// ── SLIDE 12: CONCLUSION ───────────────────────────────────
let s12 = pres.addSlide(DARK_HDR);
s12.addText("Conclusion", { placeholder: "title", options: { fontFace: "Cambria", size: 36, bold: true, color: C.white } });
s12.addText(
  "PhishNet-GNN demonstrates that modelling the network infrastructure behind a domain as a heterogeneous graph significantly improves phishing detection over traditional approaches. By combining live feature extraction with a two-layer GCN, our system achieved 96.85% accuracy while keeping inference within practical real-time bounds (~2.16 s end-to-end).",
  { placeholder: "body", options: { fontFace: "Calibri", size: 18, color: C.iceBlue, paraSpaceAfter: 20, margin: 0 } }
);
s12.addText("\u2022  Overcomes zero-hour attack blind spots of blacklists", { options: { fontFace: "Calibri", size: 15, color: C.mutedGray, bullet: true, paraSpaceAfter: 8 } });
s12.addText("\u2022  Relational signals detect spoofed domains with clean lexical profiles", { options: { fontFace: "Calibri", size: 15, color: C.mutedGray, bullet: true, paraSpaceAfter: 8 } });
s12.addText("\u2022  Sub-3-second latency makes it viable for end-user deployment", { options: { fontFace: "Calibri", size: 15, color: C.mutedGray, bullet: true } });

// ── SLIDE 13: THANK YOU / Q&A ─────────────────────────────
let s13 = pres.addSlide(COVER);
s13.addText("Thank You", { placeholder: "title", options: { fontFace: "Cambria", size: 48, bold: true, color: C.white } });
s13.addText("Any Questions?", { placeholder: "subtitle", options: { fontFace: "Calibri", size: 24, color: C.iceBlue } });
s13.addText([
  { text: "Department of CSE (AIML/DS/CS)\nGIET University, Gunupur", options: { breakLine: true, color: C.mutedGray, fontSize: 16 } },
], { placeholder: "body", options: { fontFace: "Calibri", size: 16, color: C.iceBlue } });

// Write file
const outFile = "S:/PhishNet_GNN_Presentation.pptx";
pres.writeFile({ fileName: outFile })
  .then(() => console.log("PPT saved to:", outFile))
  .catch(err => { console.error("Error writing PPT:", err.message); process.exit(1); });
