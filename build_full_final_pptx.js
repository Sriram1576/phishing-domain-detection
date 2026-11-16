const pptxgen = require("pptxgenjs");
const path = require("path");

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625 inches
pres.title = "PhishNet-GNN: Minor Project Final Review";
pres.author = "Subham Sadangi";

// Color Palette
const C = {
  navy: "0F2C59",
  deepBlue: "1B3B6F",
  accentBlue: "2A69AC",
  iceBlue: "DCEBFA",
  lightBg: "F8FAFC",
  cardBg: "FFFFFF",
  white: "FFFFFF",
  darkGray: "1E293B",
  slate: "475569",
  mutedGray: "64748B",
  border: "CBD5E1",
  green: "0D9488",
  lightGreen: "CCFBF1",
  red: "E11D48",
  lightRed: "FFE4E6",
  amber: "D97706",
  lightAmber: "FEF3C7"
};

const imgDir = "S:/Business/phishing-domain-detection/extracted_images";

// Helper: Slide with standard top header & section pill
function createSlide(sectionNum, sectionTitle, slideTitle) {
  const slide = pres.addSlide();
  slide.background = { color: C.lightBg };

  // Top header banner
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 0.75,
    fill: { color: C.navy }, line: { color: C.navy }
  });

  // Section badge / breadcrumb
  if (sectionTitle) {
    slide.addText(`OUTLINE ${sectionNum}: ${sectionTitle.toUpperCase()}`, {
      x: 0.5, y: 0.08, w: 9.0, h: 0.22,
      fontFace: "Calibri", size: 9, bold: true, color: "93C5FD"
    });
  }

  // Slide main title
  slide.addText(slideTitle, {
    x: 0.5, y: sectionTitle ? 0.28 : 0.15, w: 9.0, h: 0.42,
    fontFace: "Calibri", size: 20, bold: true, color: C.white
  });

  // Bottom footer bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.4, w: 10, h: 0.225,
    fill: { color: "0B1E3F" }, line: { color: "0B1E3F" }
  });
  slide.addText("GIET University, Gunupur | Dept. of CSE (Data Science) | Minor Project Review — PhishNet-GNN", {
    x: 0.5, y: 5.42, w: 7.5, h: 0.18,
    fontFace: "Calibri", size: 8, color: "94A3B8"
  });
  slide.addText("Presented by: Subham Sadangi", {
    x: 7.5, y: 5.42, w: 2.0, h: 0.18,
    fontFace: "Calibri", size: 8, color: "CBD5E1", align: "right"
  });

  return slide;
}

// ════════════════════════════════════════════════════════════════
// SLIDE 1: TITLE SLIDE (Official University Template Alignment)
// ════════════════════════════════════════════════════════════════
{
  const s = pres.addSlide();
  s.background = { color: C.navy };

  // University Header Banner
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 10, h: 1.15,
    fill: { color: "091A36" }, line: { color: "091A36" }
  });

  // Logo
  try {
    s.addImage({ path: `${imgDir}/giet_logo.png`, x: 0.5, y: 0.12, w: 0.9, h: 0.9 });
  } catch (e) {}

  s.addText("SCHOOL OF ENGINEERING AND TECHNOLOGY", {
    x: 1.6, y: 0.18, w: 8.0, h: 0.4,
    fontFace: "Times New Roman", size: 18, bold: true, color: C.white
  });
  s.addText("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING (DATA SCIENCE)", {
    x: 1.6, y: 0.55, w: 8.0, h: 0.35,
    fontFace: "Times New Roman", size: 13, bold: true, color: "93C5FD"
  });
  s.addText("GIET UNIVERSITY, GUNUPUR, ODISHA", {
    x: 1.6, y: 0.82, w: 8.0, h: 0.25,
    fontFace: "Calibri", size: 10, bold: true, color: "CBD5E1"
  });

  // Project Title Block
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.8, y: 1.45, w: 8.4, h: 1.7,
    fill: { color: "133E7C" }, line: { color: "38BDF8", pt: 1.5 }, rectRadius: 0.08
  });
  s.addText("MINOR PROJECT FINAL REVIEW PRESENTATION", {
    x: 1.0, y: 1.6, w: 8.0, h: 0.3,
    fontFace: "Calibri", size: 12, bold: true, color: "FDE047", align: "center"
  });
  s.addText("REAL-TIME PHISHING DOMAIN DETECTION VIA HETEROGENEOUS GRAPH NEURAL NETWORKS", {
    x: 1.0, y: 1.95, w: 8.0, h: 0.75,
    fontFace: "Cambria", size: 21, bold: true, color: C.white, align: "center"
  });
  s.addText("Architecture: Multi-Relational Star Graph (Domain-IP-NS-Registrar) + RGCN Deep Learning", {
    x: 1.0, y: 2.7, w: 8.0, h: 0.3,
    fontFace: "Calibri", size: 11, italic: true, color: "BAE6FD", align: "center"
  });

  // Two columns: Student Details & Supervisor Details
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.8, y: 3.35, w: 4.0, h: 1.7,
    fill: { color: "0B2247" }, line: { color: "1E40AF" }, rectRadius: 0.08
  });
  s.addText("Presented By:", {
    x: 1.0, y: 3.48, w: 3.6, h: 0.25,
    fontFace: "Calibri", size: 11, bold: true, color: "93C5FD"
  });
  s.addText("Subham Sadangi", {
    x: 1.0, y: 3.75, w: 3.6, h: 0.35,
    fontFace: "Calibri", size: 16, bold: true, color: C.white
  });
  s.addText("B.Tech CSE (Data Science) | 5th Semester\nGIET University, Gunupur", {
    x: 1.0, y: 4.12, w: 3.6, h: 0.5,
    fontFace: "Calibri", size: 11, color: "CBD5E1"
  });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 5.2, y: 3.35, w: 4.0, h: 1.7,
    fill: { color: "0B2247" }, line: { color: "1E40AF" }, rectRadius: 0.08
  });
  s.addText("Under the Guidance of:", {
    x: 5.4, y: 3.48, w: 3.6, h: 0.25,
    fontFace: "Calibri", size: 11, bold: true, color: "93C5FD"
  });
  s.addText("Project Supervisor / Guide", {
    x: 5.4, y: 3.75, w: 3.6, h: 0.35,
    fontFace: "Calibri", size: 14, bold: true, color: C.white
  });
  s.addText("Department of Computer Science & Engineering\nSchool of Engineering and Technology\nGIET University, Gunupur", {
    x: 5.4, y: 4.12, w: 3.6, h: 0.6,
    fontFace: "Calibri", size: 11, color: "CBD5E1"
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.35, w: 10, h: 0.275,
    fill: { color: "061224" }, line: { color: "061224" }
  });
  s.addText("Academic Session 2024–2028 | GIET University", {
    x: 0.5, y: 5.4, w: 9.0, h: 0.2,
    fontFace: "Calibri", size: 9, color: "64748B", align: "center"
  });
}

// ════════════════════════════════════════════════════════════════
// SLIDE 2: OUTLINES (Official Template Table Structure)
// ════════════════════════════════════════════════════════════════
{
  const s = createSlide("", "", "PRESENTATION OUTLINES & EVALUATION CRITERIA");

  s.addText("This presentation strictly adheres to the official evaluation framework defined for the Final Minor Project Review:", {
    x: 0.6, y: 0.9, w: 8.8, h: 0.3,
    fontFace: "Calibri", size: 12, italic: true, color: C.slate
  });

  const outlines = [
    { no: "1", title: "Functional Prototype / Product Demonstration", scope: "Live web dashboard, real-time URL scanning, dynamic graph visualization, and verified DGL_RGCN runtime execution." },
    { no: "2", title: "Functionality & Feature Completeness", scope: "21 multi-modal features, live DNS/WHOIS/SSL harvesting, on-demand star-graph builder, and Relational GCN architecture." },
    { no: "3", title: "Testing & Validation", scope: "8/8 unit/integration test cases (TC-01–TC-08), benchmark against Random Forest & XGBoost, and real-world attack case studies." },
    { no: "4", title: "Final Presentation & Viva-Voce", scope: "Literature review gap analysis, technical defense of key design decisions (GNN vs Tabular, Focal Loss, latency), and future roadmap." },
    { no: "5", title: "Documentation & User Manual", scope: "System requirements, CLI operations (main.py commands), end-user manual, and complete project deliverables package." }
  ];

  outlines.forEach((o, i) => {
    const y = 1.3 + i * 0.77;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.6, y: y, w: 8.8, h: 0.68,
      fill: { color: C.cardBg }, line: { color: C.border, pt: 1 }, rectRadius: 0.05
    });
    // Number badge
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.75, y: y + 0.12, w: 0.45, h: 0.44,
      fill: { color: C.navy }, line: { color: C.navy }, rectRadius: 0.08
    });
    s.addText(o.no, {
      x: 0.75, y: y + 0.14, w: 0.45, h: 0.4,
      fontFace: "Calibri", size: 14, bold: true, color: C.white, align: "center"
    });
    // Text
    s.addText(o.title, {
      x: 1.35, y: y + 0.08, w: 8.0, h: 0.28,
      fontFace: "Calibri", size: 13, bold: true, color: C.navy
    });
    s.addText(o.scope, {
      x: 1.35, y: y + 0.35, w: 7.9, h: 0.28,
      fontFace: "Calibri", size: 10.5, color: C.slate
    });
  });
}

// ════════════════════════════════════════════════════════════════
// SECTION 1: FUNCTIONAL PROTOTYPE / PRODUCT DEMONSTRATION
// ════════════════════════════════════════════════════════════════

// Slide 3: Three-Tier Architecture
{
  const s = createSlide(1, "Functional Prototype", "System Architecture & High-Level Design (HLD)");

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.5, y: 0.9, w: 4.3, h: 4.3,
    fill: { color: C.cardBg }, line: { color: C.border }, rectRadius: 0.06
  });
  s.addText("Three-Tier Operating Paradigm", {
    x: 0.7, y: 1.05, w: 3.9, h: 0.3,
    fontFace: "Calibri", size: 14, bold: true, color: C.navy
  });

  const tiers = [
    { title: "Presentation Layer (Web UI)", color: "E0F2FE", border: "0284C7", desc: "Responsive single-page interface (HTML5, CSS3, Vanilla JS). Provides real-time input validation, risk gauge rendering, and dynamic D3/Vis network graph visualization." },
    { title: "Application Layer (Flask REST)", color: "FEF3C7", border: "D97706", desc: "Flask 3.x backend server running on Python 3.11. Coordinates URL sanitization, multi-threaded network harvesting, NetworkX graph assembly, and GNN forward inference." },
    { title: "Data & Model Layer (SQLite / PyTorch)", color: "DCFCE7", border: "16A34A", desc: "SQLite database with WAL mode for caching DNS/WHOIS records. Stores trained PyTorch RGCN model weights (phish_rgcn.pt) and 21-feature precomputed lookup tables." }
  ];

  tiers.forEach((t, i) => {
    const y = 1.45 + i * 1.15;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.7, y: y, w: 3.9, h: 1.02,
      fill: { color: t.color }, line: { color: t.border, pt: 1 }, rectRadius: 0.05
    });
    s.addText(t.title, {
      x: 0.82, y: y + 0.06, w: 3.65, h: 0.22,
      fontFace: "Calibri", size: 11, bold: true, color: C.darkGray
    });
    s.addText(t.desc, {
      x: 0.82, y: y + 0.28, w: 3.65, h: 0.7,
      fontFace: "Calibri", size: 9.5, color: C.slate
    });
  });

  // Right column: Context Diagram
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 5.1, y: 0.9, w: 4.4, h: 4.3,
    fill: { color: C.cardBg }, line: { color: C.border }, rectRadius: 0.06
  });
  s.addText("Figure 4.1: Level-0 Context Diagram", {
    x: 5.3, y: 1.05, w: 4.0, h: 0.3,
    fontFace: "Calibri", size: 14, bold: true, color: C.navy
  });

  try {
    s.addImage({ path: `${imgDir}/image1.jpeg`, x: 5.3, y: 1.45, w: 4.0, h: 2.2 });
  } catch (e) {}

  s.addText("Key Operational Highlights:", {
    x: 5.3, y: 3.8, w: 4.0, h: 0.25,
    fontFace: "Calibri", size: 11, bold: true, color: C.navy
  });
  s.addText("• Zero installation for end-users — completely web-accessible.\n• Decoupled backend architecture enables independent model retraining.\n• Graceful degradation: heuristic baseline fallback if DNS is unreachable.", {
    x: 5.3, y: 4.05, w: 4.0, h: 1.0,
    fontFace: "Calibri", size: 9.5, color: C.slate
  });
}

// Slide 4: Real-Time Operational Pipeline
{
  const s = createSlide(1, "Functional Prototype", "End-to-End Operational Pipeline & Latency Profile");

  // Left column: Flow steps
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.5, y: 0.9, w: 4.8, h: 4.3,
    fill: { color: C.cardBg }, line: { color: C.border }, rectRadius: 0.06
  });
  s.addText("4-Stage Real-Time Execution Pipeline", {
    x: 0.7, y: 1.05, w: 4.4, h: 0.3,
    fontFace: "Calibri", size: 14, bold: true, color: C.navy
  });

  const steps = [
    { num: "1", name: "URL Sanitization & Lexical Parsing", time: "< 10 ms", desc: "Domain regex extraction via tldextract, XSS sanitization, character ratio computation." },
    { num: "2", name: "Live Network Reconnaissance", time: "~1.80 s", desc: "Parallel DNS queries (A/NS records), socket SSL certificate checks, and WHOIS age check." },
    { num: "3", name: "Heterogeneous Graph Assembly", time: "0.03 s", desc: "NetworkX star-graph builder constructs 4 entity node types and relational edges." },
    { num: "4", name: "DGL RGCN Forward Inference", time: "0.12 s", desc: "Graph convolution forward pass, global mean pooling, calibrated softmax classification." }
  ];

  steps.forEach((st, i) => {
    const y = 1.42 + i * 0.95;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.7, y: y, w: 4.4, h: 0.85,
      fill: { color: "F1F5F9" }, line: { color: C.border, pt: 0.75 }, rectRadius: 0.05
    });
    s.addText(`Stage ${st.num}: ${st.name}`, {
      x: 0.82, y: y + 0.06, w: 3.3, h: 0.22,
      fontFace: "Calibri", size: 10.5, bold: true, color: C.navy
    });
    s.addText(st.time, {
      x: 4.0, y: y + 0.06, w: 1.0, h: 0.22,
      fontFace: "Calibri", size: 9.5, bold: true, color: C.green, align: "right"
    });
    s.addText(st.desc, {
      x: 0.82, y: y + 0.28, w: 4.15, h: 0.5,
      fontFace: "Calibri", size: 9, color: C.slate
    });
  });

  // Right column: Workflow diagram
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 5.5, y: 0.9, w: 4.0, h: 4.3,
    fill: { color: C.cardBg }, line: { color: C.border }, rectRadius: 0.06
  });
  s.addText("Figure 5.1: System Workflow", {
    x: 5.7, y: 1.05, w: 3.6, h: 0.3,
    fontFace: "Calibri", size: 14, bold: true, color: C.navy
  });

  try {
    s.addImage({ path: `${imgDir}/image5.png`, x: 5.9, y: 1.45, w: 3.2, h: 3.2 });
  } catch (e) {}

  s.addText("Total End-to-End Latency: ~2.16 s (Target: < 3.0 s)", {
    x: 5.7, y: 4.75, w: 3.6, h: 0.3,
    fontFace: "Calibri", size: 10, bold: true, color: C.green, align: "center"
  });
}

// Slide 5: Live UI Demonstration (Screenshots)
{
  const s = createSlide(1, "Functional Prototype", "Live Product Demonstration: Interactive Web Interface");

  // Screenshot 1: Home / Input Page
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.5, y: 0.9, w: 4.3, h: 4.3,
    fill: { color: C.cardBg }, line: { color: C.border }, rectRadius: 0.06
  });
  s.addText("Dashboard Homepage & Input Portal", {
    x: 0.7, y: 1.05, w: 3.9, h: 0.3,
    fontFace: "Calibri", size: 13, bold: true, color: C.navy
  });
  try {
    s.addImage({ path: `${imgDir}/image6.jpeg`, x: 0.7, y: 1.4, w: 3.9, h: 2.2 });
  } catch (e) {}
  s.addText("• Clean UI with instant URL submission box.\n• Pre-configured quick-scan buttons for benign and malicious samples.\n• Real-time system health and DGL_RGCN runtime indicator.", {
    x: 0.7, y: 3.75, w: 3.9, h: 1.3,
    fontFace: "Calibri", size: 9.5, color: C.slate
  });

  // Screenshot 2: Output / Result Page
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 5.1, y: 0.9, w: 4.4, h: 4.3,
    fill: { color: C.cardBg }, line: { color: C.border }, rectRadius: 0.06
  });
  s.addText("Real-Time Threat Intelligence & Output", {
    x: 5.3, y: 1.05, w: 4.0, h: 0.3,
    fontFace: "Calibri", size: 13, bold: true, color: C.navy
  });
  try {
    s.addImage({ path: `${imgDir}/image8.jpeg`, x: 5.3, y: 1.4, w: 4.0, h: 1.8 });
  } catch (e) {}
  s.addText("Verified Output Metrics on Live Scan:", {
    x: 5.3, y: 3.35, w: 4.0, h: 0.25,
    fontFace: "Calibri", size: 10.5, bold: true, color: C.navy
  });
  s.addText("• Verdict: PHISHING (High Risk) vs. BENIGN (Safe)\n• Calibrated Risk Score: 0% to 100% confidence gauge\n• Granular Risk Factors: (e.g. brand imitation, missing SSL, zero-day age)\n• Network Infrastructure Topology: interactive node-link visualization", {
    x: 5.3, y: 3.6, w: 4.0, h: 1.4,
    fontFace: "Calibri", size: 9.5, color: C.slate
  });
}

// ════════════════════════════════════════════════════════════════
// SECTION 2: FUNCTIONALITY & FEATURE COMPLETENESS
// ════════════════════════════════════════════════════════════════

// Slide 6: 21-Dimensional Multi-Modal Features
{
  const s = createSlide(2, "Functionality & Feature Completeness", "Multi-Modal Feature Engineering (21 Dimensional Vector)");

  s.addText("Our feature extractor extracts 21 distinct signals across 4 complementary cybersecurity domains:", {
    x: 0.5, y: 0.85, w: 9.0, h: 0.25,
    fontFace: "Calibri", size: 11, italic: true, color: C.slate
  });

  const categories = [
    {
      title: "1. Lexical URL Features (11)", color: "E0F2FE", border: "0284C7",
      items: "• Domain Length & Dot Count\n• Shannon Entropy (randomness)\n• Vowel-to-Consonant Ratio\n• Digit Count & Digit Ratio\n• Hyphen & Special Char Counts\n• Subdomain Depth\n• Punycode / IDN Flag\n• Suspicious TLD Indicator"
    },
    {
      title: "2. DNS & Network Footprint (4)", color: "FEF3C7", border: "D97706",
      items: "• Resolved IPv4 A-Record Count\n• Authoritative NS Record Count\n• DNS Resolution Status\n• Host IP Hash Encoding\n(Captures fast-flux infrastructure and bulletproof hosting networks)"
    },
    {
      title: "3. WHOIS & Infrastructure (3)", color: "DCFCE7", border: "16A34A",
      items: "• Registration Age (Days)\n• Expiration Delta\n• Registrar Reputation Hash\n(Identifies zero-day disposable domains registered within 24–72 hours)"
    },
    {
      title: "4. SSL & Security Protocol (3)", color: "FCE7F3", border: "DB2777",
      items: "• HTTPS Handshake Status\n• SSL Certificate Validity Days\n• Trusted CA Authority Match\n(Flags free/untrusted certificates used on credential-stealing portals)"
    }
  ];

  categories.forEach((c, i) => {
    const x = 0.5 + i * 2.28;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: x, y: 1.15, w: 2.18, h: 4.0,
      fill: { color: c.color }, line: { color: c.border, pt: 1 }, rectRadius: 0.06
    });
    s.addText(c.title, {
      x: x + 0.1, y: 1.25, w: 1.98, h: 0.45,
      fontFace: "Calibri", size: 11, bold: true, color: C.darkGray
    });
    s.addText(c.items, {
      x: x + 0.1, y: 1.75, w: 1.98, h: 3.3,
      fontFace: "Calibri", size: 9, color: C.slate
    });
  });
}

// Slide 7: Heterogeneous Star Graph Synthesis
{
  const s = createSlide(2, "Functionality & Feature Completeness", "Heterogeneous Star Graph Construction & Topological Schema");

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.5, y: 0.9, w: 4.4, h: 4.3,
    fill: { color: C.cardBg }, line: { color: C.border }, rectRadius: 0.06
  });
  s.addText("Star Graph Schema & Entity Nodes", {
    x: 0.7, y: 1.05, w: 4.0, h: 0.3,
    fontFace: "Calibri", size: 14, bold: true, color: C.navy
  });

  const nodes = [
    { type: "Domain Node (Center)", feat: "16-dim normalized lexical vector + entity indicator" },
    { type: "IP Address Node", feat: "Host IP hash, ASN identifier, GeoIP reputation" },
    { type: "Nameserver Node", feat: "Authoritative NS cluster hash, DNS TTL attributes" },
    { type: "Registrar Node", feat: "WHOIS domain age, registrar entity identification" }
  ];

  nodes.forEach((n, i) => {
    const y = 1.45 + i * 0.95;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.7, y: y, w: 4.0, h: 0.82,
      fill: { color: "F8FAFC" }, line: { color: C.border }, rectRadius: 0.05
    });
    s.addText(`Node: ${n.type}`, {
      x: 0.82, y: y + 0.08, w: 3.75, h: 0.25,
      fontFace: "Calibri", size: 11, bold: true, color: C.navy
    });
    s.addText(n.feat, {
      x: 0.82, y: y + 0.35, w: 3.75, h: 0.4,
      fontFace: "Calibri", size: 9.5, color: C.slate
    });
  });

  // Right column: Canonical Relations & ER Diagram
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 5.1, y: 0.9, w: 4.4, h: 4.3,
    fill: { color: C.cardBg }, line: { color: C.border }, rectRadius: 0.06
  });
  s.addText("Canonical Edge Types & DGL Representation", {
    x: 5.3, y: 1.05, w: 4.0, h: 0.3,
    fontFace: "Calibri", size: 14, bold: true, color: C.navy
  });

  const edges = [
    "('domain', 'has_ip', 'ip') ── Forward hosting relation",
    "('ip', 'ip_of', 'domain') ── Reverse infrastructure relation",
    "('domain', 'has_ns', 'nameserver') ── DNS delegation relation",
    "('nameserver', 'ns_of', 'domain') ── Reverse delegation relation",
    "('domain', 'self', 'domain') ── Ego self-loop preservation"
  ];
  edges.forEach((e, i) => {
    s.addText(`• ${e}`, {
      x: 5.3, y: 1.45 + i * 0.38, w: 4.0, h: 0.35,
      fontFace: "Calibri", size: 9.5, color: C.slate
    });
  });

  s.addText("Why Heterogeneous Graphs Outperform Flat Arrays:", {
    x: 5.3, y: 3.45, w: 4.0, h: 0.25,
    fontFace: "Calibri", size: 11, bold: true, color: C.navy
  });
  s.addText("Attackers constantly alter domain spelling, but cannot economically rebuild bulletproof DNS clusters and IP blocks for every zero-day campaign. RGCN message-passing propagates malicious guilt-by-association across shared infrastructure nodes.", {
    x: 5.3, y: 3.75, w: 4.0, h: 1.3,
    fontFace: "Calibri", size: 9.5, color: C.slate
  });
}

// Slide 8: RGCN Deep Learning Architecture
{
  const s = createSlide(2, "Functionality & Feature Completeness", "Relational Graph Convolutional Network (RGCN) Engine");

  // Left column: Mathematical Formulation
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.5, y: 0.9, w: 4.5, h: 4.3,
    fill: { color: C.cardBg }, line: { color: C.border }, rectRadius: 0.06
  });
  s.addText("Relational Graph Convolution Formulation", {
    x: 0.7, y: 1.05, w: 4.1, h: 0.3,
    fontFace: "Calibri", size: 14, bold: true, color: C.navy
  });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.7, y: 1.4, w: 4.1, h: 0.9,
    fill: { color: "EFF6FF" }, line: { color: "3B82F6", pt: 1 }, rectRadius: 0.05
  });
  s.addText("h_i^(l+1) = σ ( W_0^(l) h_i^(l) + Σ_{r∈R} Σ_{j∈N_i^r} (1 / c_{i,r}) W_r^(l) h_j^(l) )", {
    x: 0.8, y: 1.55, w: 3.9, h: 0.6,
    fontFace: "Courier New", size: 9.5, bold: true, color: C.navy, align: "center"
  });

  s.addText("Key Architectural Specifications:", {
    x: 0.7, y: 2.4, w: 4.1, h: 0.25,
    fontFace: "Calibri", size: 11, bold: true, color: C.navy
  });
  s.addText("• 2-Layer HeteroGraphConv: Relation-specific linear projection matrices (W_r) for each edge type.\n• Regularization: Batch Normalization + ReLU activation + Dropout (p=0.3).\n• Pooling: Global Mean Pooling aggregates domain node embeddings into graph-level representation.\n• Readout Head: Fully connected layer + calibrated Softmax outputting P(Legitimate) vs. P(Phishing).", {
    x: 0.7, y: 2.68, w: 4.1, h: 2.4,
    fontFace: "Calibri", size: 9.5, color: C.slate
  });

  // Right column: Focal Loss
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 5.2, y: 0.9, w: 4.3, h: 4.3,
    fill: { color: C.cardBg }, line: { color: C.border }, rectRadius: 0.06
  });
  s.addText("Class Imbalance Mitigation: Focal Loss", {
    x: 5.4, y: 1.05, w: 3.9, h: 0.3,
    fontFace: "Calibri", size: 14, bold: true, color: C.navy
  });

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 5.4, y: 1.4, w: 3.9, h: 0.9,
    fill: { color: "FEF3C7" }, line: { color: "D97706", pt: 1 }, rectRadius: 0.05
  });
  s.addText("FL(p_t) = - α_t · (1 - p_t)^γ · log(p_t)       [γ = 2.0]", {
    x: 5.5, y: 1.6, w: 3.7, h: 0.5,
    fontFace: "Courier New", size: 10, bold: true, color: C.navy, align: "center"
  });

  s.addText("Why Focal Loss over Cross-Entropy?", {
    x: 5.4, y: 2.4, w: 3.9, h: 0.25,
    fontFace: "Calibri", size: 11, bold: true, color: C.navy
  });
  s.addText("• Standard Cross-Entropy produces large gradients for easy negative domains, overwhelming updates during training.\n• The modulating factor (1 - p_t)^γ dynamically suppresses gradients from easy examples.\n• Forces gradient descent to prioritize ambiguous, zero-day phishing samples, yielding zero false alarms on major brands (e.g., google.com, github.com).", {
    x: 5.4, y: 2.68, w: 3.9, h: 2.4,
    fontFace: "Calibri", size: 9.5, color: C.slate
  });
}

// Slide 9: Modular Implementation Traceability
{
  const s = createSlide(2, "Functionality & Feature Completeness", "Requirements Traceability & Feature Completeness Matrix");

  const reqTable = [
    [
      { text: "Requirement ID", options: { bold: true, fill: { color: C.navy }, color: C.white, fontSize: 10 } },
      { text: "Specified Capability", options: { bold: true, fill: { color: C.navy }, color: C.white, fontSize: 10 } },
      { text: "Implementation Module", options: { bold: true, fill: { color: C.navy }, color: C.white, fontSize: 10 } },
      { text: "Status", options: { bold: true, fill: { color: C.navy }, color: C.white, fontSize: 10 } }
    ],
    ["FR-1: Input Handling", "URL syntax parsing, XSS sanitization, TLD split", "src/data/sanitizer.py", "100% COMPLETE"],
    ["FR-2: Live Reconnaissance", "DNS A/NS records, WHOIS age, SSL validity", "src/data/dns_resolver.py", "100% COMPLETE"],
    ["FR-3: Graph Modeling", "4-entity star graph, PyTorch/DGL conversion", "src/graph/graph_builder.py", "100% COMPLETE"],
    ["FR-4: Real-Time Inference", "RGCN forward pass under 2.5 second window", "src/models/gnn_model.py", "100% COMPLETE"],
    ["FR-5: Web Interface", "Risk gauge, network graph visualizer, history log", "src/api/server.py & app.js", "100% COMPLETE"],
    ["NFR-1: Fault Tolerance", "Fallback scoring on DNS dropouts or WHOIS blocks", "src/predict.py", "100% COMPLETE"],
    ["NFR-2: Concurrency", "Thread-safe concurrent queries via SQLite WAL", "data/dns_cache.db", "100% COMPLETE"]
  ];

  s.addTable(reqTable, {
    x: 0.5, y: 0.95, w: 9.0, h: 4.1,
    fontSize: 10, fontFace: "Calibri", color: C.darkGray,
    border: { pt: 0.5, color: "CBD5E1" },
    colW: [1.8, 3.4, 2.3, 1.5]
  });
}

// ════════════════════════════════════════════════════════════════
// SECTION 3: TESTING & VALIDATION
// ════════════════════════════════════════════════════════════════

// Slide 10: Test Case Execution Summary
{
  const s = createSlide(3, "Testing & Validation", "Empirical Testing & Test Case Execution Summary (TC-01 – TC-08)");

  const tcTable = [
    [
      { text: "TC ID", options: { bold: true, fill: { color: C.navy }, color: C.white, fontSize: 9.5 } },
      { text: "Test Focus", options: { bold: true, fill: { color: C.navy }, color: C.white, fontSize: 9.5 } },
      { text: "Test Input / Condition", options: { bold: true, fill: { color: C.navy }, color: C.white, fontSize: 9.5 } },
      { text: "Observed Behavior", options: { bold: true, fill: { color: C.navy }, color: C.white, fontSize: 9.5 } },
      { text: "Result", options: { bold: true, fill: { color: C.navy }, color: C.white, fontSize: 9.5 } }
    ],
    ["TC-01", "Empty Input", "User submits blank domain field", "Inline error prompt displayed; submission blocked", "PASSED"],
    ["TC-02", "XSS Injection", "https://<script>alert('xss')</script>.com", "Script tags stripped; sanitized cleanly before parse", "PASSED"],
    ["TC-03", "CDN / Privacy", "Scanning Cloudflare-proxied domain", "Neutral fallback imputed for missing WHOIS", "PASSED"],
    ["TC-04", "Network Timeout", "Simulating socket disconnection", "Graceful timeout return within 2.8s without crash", "PASSED"],
    ["TC-05", "Graph Integrity", "Domain with missing NS record", "Single-node graph with self-loops built cleanly", "PASSED"],
    ["TC-06", "Malicious URL", "Live PhishTank credential-harvesting link", "Flagged as PHISHING (Confidence: 96.2%)", "PASSED"],
    ["TC-07", "Legitimate URL", "Live authentic link (https://github.com)", "Flagged as LEGITIMATE (Confidence: 99.1%)", "PASSED"],
    ["TC-08", "Concurrency", "Sequential batch submissions to SQLite", "Zero database locks; WAL logging verified", "PASSED"]
  ];

  s.addTable(tcTable, {
    x: 0.5, y: 0.95, w: 9.0, h: 4.1,
    fontSize: 9.5, fontFace: "Calibri", color: C.darkGray,
    border: { pt: 0.5, color: "CBD5E1" },
    colW: [0.9, 1.8, 2.7, 2.6, 1.0]
  });
}

// Slide 11: Experimental Benchmarking vs Baselines
{
  const s = createSlide(3, "Testing & Validation", "Experimental Benchmarking & Model Performance Comparison");

  s.addText("Evaluation on 10,000 domains dataset (PhishTank, OpenPhish, Tranco Top 100k):", {
    x: 0.5, y: 0.85, w: 9.0, h: 0.25,
    fontFace: "Calibri", size: 11, italic: true, color: C.slate
  });

  const bTable = [
    [
      { text: "Model Architecture", options: { bold: true, fill: { color: C.navy }, color: C.white, fontSize: 11 } },
      { text: "Accuracy", options: { bold: true, fill: { color: C.navy }, color: C.white, fontSize: 11 } },
      { text: "Precision", options: { bold: true, fill: { color: C.navy }, color: C.white, fontSize: 11 } },
      { text: "Recall", options: { bold: true, fill: { color: C.navy }, color: C.white, fontSize: 11 } },
      { text: "F1-Score", options: { bold: true, fill: { color: C.navy }, color: C.white, fontSize: 11 } },
      { text: "ROC-AUC", options: { bold: true, fill: { color: C.navy }, color: C.white, fontSize: 11 } },
      { text: "Model Latency", options: { bold: true, fill: { color: C.navy }, color: C.white, fontSize: 11 } }
    ],
    ["Random Forest (Baseline)", "91.20%", "89.80%", "90.50%", "90.15%", "0.942", "~0.08 s"],
    ["XGBoost (Baseline)", "93.45%", "92.60%", "92.10%", "92.35%", "0.961", "~0.09 s"],
    [{ text: "Proposed RGCN (Our System)", options: { bold: true, color: C.navy, fill: { color: "DCFCE7" } } },
     { text: "96.85%", options: { bold: true, fill: { color: "DCFCE7" } } },
     { text: "96.10%", options: { bold: true, fill: { color: "DCFCE7" } } },
     { text: "95.90%", options: { bold: true, fill: { color: "DCFCE7" } } },
     { text: "96.00%", options: { bold: true, fill: { color: "DCFCE7" } } },
     { text: "0.987", options: { bold: true, fill: { color: "DCFCE7" } } },
     { text: "~0.12 s", options: { bold: true, fill: { color: "DCFCE7" } } }]
  ];

  s.addTable(bTable, {
    x: 0.5, y: 1.15, w: 9.0, h: 2.1,
    fontSize: 11, fontFace: "Calibri", color: C.darkGray,
    border: { pt: 0.5, color: "CBD5E1" },
    colW: [2.5, 1.1, 1.1, 1.1, 1.1, 1.0, 1.1]
  });

  // Summary Cards below table
  const cards = [
    { title: "Target Exceeded", metric: "+3.65% F1", desc: "Outperforms tuned XGBoost by incorporating topological network relational patterns." },
    { title: "ROC-AUC Superiority", metric: "0.987 AUC", desc: "Maintains near-perfect separation between zero-hour malicious domains and authentic hosts." },
    { title: "Real-Time Viability", metric: "~2.16s Total", desc: "Full end-to-end pipeline operates smoothly within typical user web browser navigation windows." }
  ];

  cards.forEach((c, i) => {
    const x = 0.5 + i * 3.08;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: x, y: 3.45, w: 2.85, h: 1.7,
      fill: { color: C.cardBg }, line: { color: C.border }, rectRadius: 0.06
    });
    s.addText(c.title, {
      x: x + 0.15, y: 3.55, w: 2.55, h: 0.25,
      fontFace: "Calibri", size: 10, bold: true, color: C.mutedGray
    });
    s.addText(c.metric, {
      x: x + 0.15, y: 3.8, w: 2.55, h: 0.45,
      fontFace: "Calibri", size: 20, bold: true, color: C.navy
    });
    s.addText(c.desc, {
      x: x + 0.15, y: 4.3, w: 2.55, h: 0.75,
      fontFace: "Calibri", size: 9.5, color: C.slate
    });
  });
}

// Slide 12: Real-World Case Studies & Detection Observations
{
  const s = createSlide(3, "Testing & Validation", "Real-World Efficacy: Tackling Zero-Day & Hijacked Attacks");

  const cases = [
    {
      title: "Case 1: Deceptive Zero-Day Brand Impersonation",
      badge: "Caught by RGCN (96.8%)", badgeColor: C.green,
      url: "Target Domain: chase-security-verify-login.com",
      tabular: "• Random Forest / XGBoost Result: MISSED (Flagged as Safe)\n  Reason: Lexical words 'chase', 'security', 'verify' match normal English dictionary words; length is moderate.",
      gnn: "• PhishNet RGCN Result: CAUGHT AS PHISHING (96.8% Confidence)\n  Reason: Domain was registered 3 days prior, pointed to a known bulletproof hosting ASN, and possessed a mismatching Let's Encrypt certificate."
    },
    {
      title: "Case 2: Compromised Authentic Legitimate Websites",
      badge: "Flagged Anomaly", badgeColor: C.navy,
      url: "Target Domain: authentic-school-portal.org/login-update",
      tabular: "• Tabular Model Result: MISSED\n  Reason: Domain age is 8+ years; high search ranking and clean lexical structure trick static classifiers.",
      gnn: "• PhishNet RGCN Result: FLAGGED ANOMALY\n  Reason: Detects routing divergence where DNS resolution shifts to unfamiliar offshore hosting subnets with mismatched SSL issuers."
    }
  ];

  cases.forEach((cs, i) => {
    const y = 0.95 + i * 2.2;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.5, y: y, w: 9.0, h: 2.05,
      fill: { color: C.cardBg }, line: { color: C.border }, rectRadius: 0.06
    });
    s.addText(cs.title, {
      x: 0.7, y: y + 0.1, w: 5.5, h: 0.28,
      fontFace: "Calibri", size: 12.5, bold: true, color: C.navy
    });
    s.addText(cs.badge, {
      x: 6.2, y: y + 0.1, w: 3.1, h: 0.28,
      fontFace: "Calibri", size: 11, bold: true, color: cs.badgeColor, align: "right"
    });
    s.addText(cs.url, {
      x: 0.7, y: y + 0.4, w: 8.6, h: 0.22,
      fontFace: "Courier New", size: 9.5, bold: true, color: "0284C7"
    });
    s.addText(cs.tabular, {
      x: 0.7, y: y + 0.68, w: 8.6, h: 0.55,
      fontFace: "Calibri", size: 9.5, color: C.slate
    });
    s.addText(cs.gnn, {
      x: 0.7, y: y + 1.25, w: 8.6, h: 0.65,
      fontFace: "Calibri", size: 9.5, bold: true, color: C.darkGray
    });
  });
}

// ════════════════════════════════════════════════════════════════
// SECTION 4: FINAL PRESENTATION & VIVA-VOCE
// ════════════════════════════════════════════════════════════════

// Slide 13: Literature Review & Gap Analysis
{
  const s = createSlide(4, "Final Presentation & Viva-Voce", "Literature Review & State-of-the-Art Gap Analysis");

  const litTable = [
    [
      { text: "Author & Year", options: { bold: true, fill: { color: C.navy }, color: C.white, fontSize: 9.5 } },
      { text: "Technology / Approach", options: { bold: true, fill: { color: C.navy }, color: C.white, fontSize: 9.5 } },
      { text: "Key Result", options: { bold: true, fill: { color: C.navy }, color: C.white, fontSize: 9.5 } },
      { text: "Identified Gap / Limitation", options: { bold: true, fill: { color: C.navy }, color: C.white, fontSize: 9.5 } }
    ],
    ["Marchal et al. (2016)", "Lexical + Search Engine Ranking checks", "93.5% accuracy", "High latency; vulnerable to SEO poisoning and index evasion."],
    ["Sahingoz et al. (2019)", "Word n-grams with Random Forest", "97.98% accuracy", "Fails completely on compromised sites and URL shorteners."],
    ["Rao et al. (2020)", "CatchPhish: Deep learning + Computer Vision", "94.2% detection", "Headless browser takes >6 sec/page; impractical for real-time."],
    ["Al-Ahmadi (2020)", "Passive DNS mining with XGBoost", "96.7% detection", "Limited to enterprise ISP log files; fails on CDN-masked domains."],
    ["Li et al. (2022)", "GCN on massive ISP domain-IP graphs", "98.1% F1-score", "Offline batch processing only; cannot classify single new URLs."],
    [{ text: "Proposed System (2026)", options: { bold: true, color: C.navy, fill: { color: "DCFCE7" } } },
     { text: "On-demand Star Graph + RGCN", options: { bold: true, fill: { color: "DCFCE7" } } },
     { text: "96.85% accuracy, ~2.16s", options: { bold: true, fill: { color: "DCFCE7" } } },
     { text: "Solves single-URL real-time inspection via on-demand ego graphs.", options: { bold: true, fill: { color: "DCFCE7" } } }]
  ];

  s.addTable(litTable, {
    x: 0.5, y: 0.95, w: 9.0, h: 4.1,
    fontSize: 9.5, fontFace: "Calibri", color: C.darkGray,
    border: { pt: 0.5, color: "CBD5E1" },
    colW: [1.8, 2.5, 1.8, 2.9]
  });
}

// Slide 14: Viva-Voce Technical Defense
{
  const s = createSlide(4, "Final Presentation & Viva-Voce", "Viva-Voce Technical Defense: Core Architectural Decisions");

  const qas = [
    {
      q: "Q1: Why Graph Neural Networks instead of classic Random Forest or XGBoost?",
      a: "Phishers modify URL strings at zero cost, but infrastructure reuse (bulletproof IPs, nameservers, registrars) cannot be easily hidden. Tabular models treat URLs in complete isolation, losing connectivity. RGCN models relational message passing across heterogeneous nodes."
    },
    {
      q: "Q2: How does the system achieve sub-2.5s real-time response for a single URL?",
      a: "Instead of building a massive internet-scale graph, we synthesize an on-demand ego star graph containing only the target domain and its 1-hop infrastructure neighbors (4-6 nodes). Combined with 1.5s socket timeouts and SQLite caching, forward pass takes ~0.12s."
    },
    {
      q: "Q3: How do you handle domains hiding behind Cloudflare CDN or WHOIS privacy?",
      a: "When WHOIS or real hosting IPs are masked, the system imputes a neutral fallback vector for those missing nodes. The GNN relies on the remaining multi-modal signals (lexical features, SSL certificate issuer validity, and nameserver reputation) to maintain high confidence."
    },
    {
      q: "Q4: Why Relational GCN (RGCN) over standard GCN?",
      a: "A standard GCN assumes homogeneous nodes and edges. Our graph is heterogeneous: domain-to-IP is 'has_ip', while domain-to-NS is 'has_ns'. RGCN learns distinct transformation matrices (W_r) for each edge relation, capturing unique semantic meanings."
    }
  ];

  qas.forEach((qa, i) => {
    const y = 0.95 + i * 1.05;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.5, y: y, w: 9.0, h: 0.95,
      fill: { color: C.cardBg }, line: { color: C.border }, rectRadius: 0.05
    });
    s.addText(qa.q, {
      x: 0.7, y: y + 0.08, w: 8.6, h: 0.25,
      fontFace: "Calibri", size: 11, bold: true, color: C.navy
    });
    s.addText(qa.a, {
      x: 0.7, y: y + 0.35, w: 8.6, h: 0.55,
      fontFace: "Calibri", size: 9.5, color: C.slate
    });
  });
}

// Slide 15: Limitations & Future Scope
{
  const s = createSlide(4, "Final Presentation & Viva-Voce", "System Limitations & Strategic Future Research Directions");

  // Left column: Limitations
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.5, y: 0.9, w: 4.3, h: 4.3,
    fill: { color: C.cardBg }, line: { color: C.border }, rectRadius: 0.06
  });
  s.addText("Current System Constraints", {
    x: 0.7, y: 1.05, w: 3.9, h: 0.3,
    fontFace: "Calibri", size: 14, bold: true, color: C.red
  });

  const lims = [
    { t: "Third-Party Rate Limits", d: "High-frequency queries may trigger throttling on public WHOIS port 43 and DNS servers." },
    { t: "Cloud CDN IP Masking", d: "Cloudflare and Fastly reverse proxies mask the true backend server hosting IP." },
    { t: "Ephemeral Free Cloud Hosting", d: "Phishing hosted on free subdomains (Firebase, Vercel) produces sparse graph neighborhoods." },
    { t: "No Full Visual DOM Scraping", d: "Purely infrastructure/lexical based; does not render full HTML/canvas screenshots." }
  ];

  lims.forEach((l, i) => {
    const y = 1.45 + i * 0.92;
    s.addText(`• ${l.t}:`, {
      x: 0.7, y: y, w: 3.9, h: 0.22,
      fontFace: "Calibri", size: 10.5, bold: true, color: C.darkGray
    });
    s.addText(l.d, {
      x: 0.9, y: y + 0.22, w: 3.7, h: 0.65,
      fontFace: "Calibri", size: 9.5, color: C.slate
    });
  });

  // Right column: Future Scope
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 5.1, y: 0.9, w: 4.4, h: 4.3,
    fill: { color: C.cardBg }, line: { color: C.border }, rectRadius: 0.06
  });
  s.addText("Strategic Future Enhancements", {
    x: 5.3, y: 1.05, w: 4.0, h: 0.3,
    fontFace: "Calibri", size: 14, bold: true, color: C.green
  });

  const futs = [
    { t: "Graph Attention Networks (GAT / HAN)", d: "Dynamic edge attention coefficients to weight nameserver changes more heavily than static registrar data." },
    { t: "Lightweight Favicon & Title Scraping", d: "Extract MD5 favicon hashes and HTML page titles to detect branded login page spoofs." },
    { t: "Browser Extension Deployment", d: "Compile into a Chrome/Firefox WebExtension for proactive zero-click link protection." },
    { t: "Continuous Streaming Retraining", d: "Automated worker pipeline pulling live feeds from OpenPhish and PhishTank daily." }
  ];

  futs.forEach((f, i) => {
    const y = 1.45 + i * 0.92;
    s.addText(`• ${f.t}:`, {
      x: 5.3, y: y, w: 4.0, h: 0.22,
      fontFace: "Calibri", size: 10.5, bold: true, color: C.darkGray
    });
    s.addText(f.d, {
      x: 5.5, y: y + 0.22, w: 3.8, h: 0.65,
      fontFace: "Calibri", size: 9.5, color: C.slate
    });
  });
}

// ════════════════════════════════════════════════════════════════
// SECTION 5: DOCUMENTATION & USER MANUAL
// ════════════════════════════════════════════════════════════════

// Slide 16: Setup & Environment
{
  const s = createSlide(5, "Documentation & User Manual", "System Specifications & Reproducible Environment Setup");

  // Left column: Specifications
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.5, y: 0.9, w: 4.3, h: 4.3,
    fill: { color: C.cardBg }, line: { color: C.border }, rectRadius: 0.06
  });
  s.addText("Hardware & Software Specifications", {
    x: 0.7, y: 1.05, w: 3.9, h: 0.3,
    fontFace: "Calibri", size: 14, bold: true, color: C.navy
  });

  const specs = [
    { l: "Operating System", v: "Windows 11 / Ubuntu 22.04 LTS" },
    { l: "Runtime Environment", v: "Python 3.11.9 (Dedicated .venv-gnn)" },
    { l: "Deep Learning Stack", v: "PyTorch 2.2.1+cpu & DGL 2.2.1" },
    { l: "Graph Processing", v: "NetworkX 3.2.1" },
    { l: "Machine Learning", v: "Scikit-Learn 1.4.1.post1, NumPy 1.26.4" },
    { l: "Network Tools", v: "dnspython 2.4.2, tldextract, cryptography" },
    { l: "Web & Storage", v: "Flask 3.0.0, SQLite 3 (WAL mode)" }
  ];

  specs.forEach((sp, i) => {
    const y = 1.45 + i * 0.52;
    s.addText(sp.l + ":", {
      x: 0.7, y: y, w: 1.7, h: 0.22,
      fontFace: "Calibri", size: 10, bold: true, color: C.navy
    });
    s.addText(sp.v, {
      x: 2.4, y: y, w: 2.2, h: 0.22,
      fontFace: "Calibri", size: 10, color: C.slate
    });
  });

  // Right column: Setup Commands
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 5.1, y: 0.9, w: 4.4, h: 4.3,
    fill: { color: C.cardBg }, line: { color: C.border }, rectRadius: 0.06
  });
  s.addText("Step-by-Step Installation Commands", {
    x: 5.3, y: 1.05, w: 4.0, h: 0.3,
    fontFace: "Calibri", size: 14, bold: true, color: C.navy
  });

  const codeBlocks = [
    { title: "1. Create & Activate Environment", cmd: "python -m venv .venv-gnn\n.\\.venv-gnn\\Scripts\\Activate.ps1" },
    { title: "2. Install Pinned Dependencies", cmd: "pip install -r requirements-gnn.txt" },
    { title: "3. Verify DGL & PyTorch Runtime", cmd: "python verify_gnn.py\n# Checks: DGL 2.2.1 + MODEL_MODE: DGL_RGCN" },
    { title: "4. Launch REST API & Web UI", cmd: "python main.py serve\n# Open: http://localhost:5000" }
  ];

  codeBlocks.forEach((cb, i) => {
    const y = 1.42 + i * 0.95;
    s.addText(cb.title, {
      x: 5.3, y: y, w: 4.0, h: 0.22,
      fontFace: "Calibri", size: 10, bold: true, color: C.navy
    });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 5.3, y: y + 0.22, w: 4.0, h: 0.6,
      fill: { color: "0F172A" }, line: { color: "334155" }, rectRadius: 0.04
    });
    s.addText(cb.cmd, {
      x: 5.4, y: y + 0.25, w: 3.8, h: 0.55,
      fontFace: "Courier New", size: 8.5, color: "38BDF8"
    });
  });
}

// Slide 17: Operational CLI & User Manual
{
  const s = createSlide(5, "Documentation & User Manual", "Operational User Manual: Command-Line Interface (CLI)");

  const cliCommands = [
    {
      cmd: "python main.py generate-data",
      desc: "Ingests 10,000 raw domains from PhishTank, OpenPhish, and Tranco. Balances benign/malicious ratios and generates data/domains_dataset.csv."
    },
    {
      cmd: "python main.py train",
      desc: "Executes 2-layer Hetero-RGCN model training with Focal Loss (gamma=2.0) across 50 epochs. Saves best checkpoint to models/saved/phish_rgcn.pt."
    },
    {
      cmd: "python main.py evaluate",
      desc: "Evaluates test set split; computes Accuracy (96.85%), Precision (96.10%), Recall (95.90%), F1 (96.00%), ROC-AUC (0.987), and Confusion Matrix."
    },
    {
      cmd: "python main.py serve",
      desc: "Initializes Flask REST API server on 0.0.0.0:5000 with pre-warmed GNN weights and SQLite connection pool. Serves dashboard at http://localhost:5000."
    },
    {
      cmd: "python main.py infer --domain <url>",
      desc: "CLI single-domain scanner. Runs live feature extraction, builds on-demand star graph, runs GNN forward pass, and prints calibrated verdict."
    }
  ];

  cliCommands.forEach((c, i) => {
    const y = 0.95 + i * 0.85;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.5, y: y, w: 9.0, h: 0.78,
      fill: { color: C.cardBg }, line: { color: C.border }, rectRadius: 0.05
    });
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.65, y: y + 0.1, w: 3.2, h: 0.3,
      fill: { color: "0F172A" }, line: { color: "334155" }, rectRadius: 0.04
    });
    s.addText(c.cmd, {
      x: 0.72, y: y + 0.14, w: 3.05, h: 0.22,
      fontFace: "Courier New", size: 8.5, bold: true, color: "38BDF8"
    });
    s.addText(c.desc, {
      x: 4.0, y: y + 0.08, w: 5.3, h: 0.62,
      fontFace: "Calibri", size: 9.5, color: C.slate
    });
  });
}

// Slide 18: Project Deliverables Package
{
  const s = createSlide(5, "Documentation & User Manual", "Project Deliverables & Repository Package Overview");

  const delivs = [
    { title: "Comprehensive Project Report", badge: "31 Pages / 9 Chapters", file: "Minor project1 report.docx", desc: "Complete documentation including Problem Statement, Literature Review, HLD/LLD diagrams, Algorithm pseudocode, and Test Case execution tables." },
    { title: "Production Source Code", badge: "Modular Python Architecture", file: "src/ (data, graph, models, api)", desc: "Clean, PEP8-compliant modular Python codebase with automated logging, exception handling, and decoupled sub-modules." },
    { title: "Serialized Pretrained Models", badge: "Verified Weights", file: "models/saved/phish_rgcn.pt", desc: "Trained DGL HeteroGraphConv state dictionary achieving 96.85% test accuracy and precomputed feature cache for sub-second inference." },
    { title: "Interactive Web Dashboard", badge: "SPA Architecture", file: "dashboard/ (HTML, CSS, JS)", desc: "Zero-dependency frontend featuring real-time risk gauges, interactive network graph topology, and SQLite history logging." },
    { title: "Deployment & Setup Guides", badge: "Windows 11 & Linux", file: "SETUP_WINDOWS_GNN.md", desc: "Reproducible environment instructions, dependency pinning, and verification scripts ensuring zero DLL runtime errors." }
  ];

  delivs.forEach((d, i) => {
    const y = 0.95 + i * 0.85;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.5, y: y, w: 9.0, h: 0.78,
      fill: { color: C.cardBg }, line: { color: C.border }, rectRadius: 0.05
    });
    s.addText(d.title, {
      x: 0.7, y: y + 0.08, w: 4.0, h: 0.25,
      fontFace: "Calibri", size: 12, bold: true, color: C.navy
    });
    s.addText(d.badge, {
      x: 4.8, y: y + 0.08, w: 4.5, h: 0.25,
      fontFace: "Calibri", size: 10, bold: true, color: C.green, align: "right"
    });
    s.addText(`Artifact: ${d.file}  |  ${d.desc}`, {
      x: 0.7, y: y + 0.35, w: 8.6, h: 0.38,
      fontFace: "Calibri", size: 9.5, color: C.slate
    });
  });
}

// ════════════════════════════════════════════════════════════════
// CONCLUSION & Q&A
// ════════════════════════════════════════════════════════════════

// Slide 19: Conclusion
{
  const s = createSlide("", "", "CONCLUSION & SUMMARY OF RESEARCH ACHIEVEMENTS");

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 0.5, y: 0.95, w: 9.0, h: 4.25,
    fill: { color: C.cardBg }, line: { color: C.border }, rectRadius: 0.08
  });

  s.addText("Core Contributions to Phishing Cybersecurity:", {
    x: 0.8, y: 1.15, w: 8.4, h: 0.35,
    fontFace: "Calibri", size: 15, bold: true, color: C.navy
  });

  const points = [
    { t: "Paradigm Shift", d: "Successfully shifted phishing defense from fragile static text pattern matching to robust infrastructure relationship modeling." },
    { t: "Superior Predictive Performance", d: "Achieved 96.85% Accuracy and 0.987 ROC-AUC, outperforming industry-standard XGBoost and Random Forest baselines by +3.65% F1-score." },
    { t: "Real-Time Engineering Feasibility", d: "Engineered on-demand star-graph generation and multi-threaded socket lookups, maintaining a ~2.16 second total response window." },
    { t: "Production Readiness", d: "Delivered a fully integrated, reproducible, end-to-end software product comprising REST API, web dashboard, and SQLite audit logging." }
  ];

  points.forEach((p, i) => {
    const y = 1.6 + i * 0.85;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
      x: 0.8, y: y, w: 8.4, h: 0.72,
      fill: { color: "F8FAFC" }, line: { color: C.border, pt: 0.75 }, rectRadius: 0.05
    });
    s.addText(p.t, {
      x: 0.95, y: y + 0.06, w: 8.1, h: 0.22,
      fontFace: "Calibri", size: 11, bold: true, color: C.navy
    });
    s.addText(p.d, {
      x: 0.95, y: y + 0.28, w: 8.1, h: 0.4,
      fontFace: "Calibri", size: 10, color: C.slate
    });
  });
}

// Slide 20: Q&A / Thank You (Template-Compliant Closing)
{
  const s = pres.addSlide();
  s.background = { color: C.navy };

  s.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x: 1.0, y: 1.0, w: 8.0, h: 3.5,
    fill: { color: "0B2247" }, line: { color: "1E40AF", pt: 2 }, rectRadius: 0.1
  });

  s.addText("QUESTIONS & ANSWERS", {
    x: 1.5, y: 1.35, w: 7.0, h: 0.5,
    fontFace: "Cambria", size: 32, bold: true, color: "FDE047", align: "center"
  });
  s.addText("Thank You for Your Time & Attention!", {
    x: 1.5, y: 1.95, w: 7.0, h: 0.5,
    fontFace: "Calibri", size: 22, color: C.white, align: "center"
  });
  s.addText("Open for Viva-Voce Evaluation, Faculty Review & Questions", {
    x: 1.5, y: 2.5, w: 7.0, h: 0.35,
    fontFace: "Calibri", size: 13, italic: true, color: "93C5FD", align: "center"
  });

  s.addText("Candidate: Subham Sadangi  |  B.Tech CSE (Data Science)\nSchool of Engineering and Technology | GIET University, Gunupur", {
    x: 1.5, y: 3.2, w: 7.0, h: 0.7,
    fontFace: "Calibri", size: 11, color: "CBD5E1", align: "center"
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 5.35, w: 10, h: 0.275,
    fill: { color: "061224" }, line: { color: "061224" }
  });
  s.addText("PhishNet-GNN © 2026 | GIET University Gunupur", {
    x: 0.5, y: 5.4, w: 9.0, h: 0.2,
    fontFace: "Calibri", size: 9, color: "64748B", align: "center"
  });
}

// Save outputs using fs.writeFileSync
const fs = require("fs");
const outFinal = "S:/PPT (Final Review).pptx";
const outPresentation = "S:/PhishNet_GNN_Presentation.pptx";

pres.write({ outputType: "nodebuffer" })
  .then(buffer => {
    fs.writeFileSync(outFinal, buffer);
    console.log("Successfully wrote:", outFinal, "Size:", fs.statSync(outFinal).size);
    fs.writeFileSync(outPresentation, buffer);
    console.log("Successfully wrote:", outPresentation, "Size:", fs.statSync(outPresentation).size);
    process.exit(0);
  })
  .catch(err => {
    console.error("Error generating PPT:", err);
    process.exit(1);
  });
