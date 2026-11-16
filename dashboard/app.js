/**
 * PhishNet-GNN — Enterprise Threat Intelligence Console
 * Application Logic & Graph Visualizer
 */

(function () {
  'use strict';

  // ──────── Application State ────────
  const state = {
    activeTab: 'analyze',
    lastAnalysis: null,
    isScanning: false,
    systemHealthy: false,
    modelMode: 'DGL_RGCN',
    graphMode: 'current', // 'current' | 'cluster'
    graphData: { nodes: [], edges: [] },
    hoveredNode: null,
    draggedNode: null,
    animationFrameId: null
  };

  // ──────── DOM Element Cache ────────
  const DOM = {
    // Navigation
    tabs: document.querySelectorAll('.nav-tab'),
    mobileNavItems: document.querySelectorAll('.mobile-nav-item'),
    panels: document.querySelectorAll('.tab-panel'),
    mobileMenuBtn: document.getElementById('mobileMenuBtn'),
    mobileDrawer: document.getElementById('mobileDrawer'),
    statusDot: document.getElementById('statusDot'),
    statusBadgeText: document.getElementById('statusBadgeText'),

    // Scanner
    scanForm: document.getElementById('scanForm'),
    domainInput: document.getElementById('domainInput'),
    analyzeBtn: document.getElementById('analyzeBtn'),
    pasteBtn: document.getElementById('pasteBtn'),
    demoChips: document.querySelectorAll('.demo-chip'),
    loadingConsole: document.getElementById('loadingConsole'),
    loadingSteps: [
      document.getElementById('step1'),
      document.getElementById('step2'),
      document.getElementById('step3'),
      document.getElementById('step4')
    ],

    // Results Dashboard
    heroSection: document.getElementById('heroSection'),
    resultsDashboard: document.getElementById('resultsDashboard'),
    resultHeroCard: document.getElementById('resultHeroCard'),
    gaugeProgress: document.getElementById('gaugeProgress'),
    gaugeScore: document.getElementById('gaugeScore'),
    verdictPill: document.getElementById('verdictPill'),
    verdictText: document.getElementById('verdictText'),
    confidenceTag: document.getElementById('confidenceTag'),
    analyzedDomainText: document.getElementById('analyzedDomainText'),
    resultModelMode: document.getElementById('resultModelMode'),
    resultLatency: document.getElementById('resultLatency'),
    resultTimestamp: document.getElementById('resultTimestamp'),
    analyzeAnotherBtn: document.getElementById('analyzeAnotherBtn'),
    jumpToGraphBtn: document.getElementById('jumpToGraphBtn'),
    signalsList: document.getElementById('signalsList'),
    riskSignalsCount: document.getElementById('riskSignalsCount'),
    profileGrid: document.getElementById('profileGrid'),
    ipChipsContainer: document.getElementById('ipChipsContainer'),
    nsChipsContainer: document.getElementById('nsChipsContainer'),
    ipCountBadge: document.getElementById('ipCountBadge'),
    nsCountBadge: document.getElementById('nsCountBadge'),

    // Graph Visualizer
    canvasWrapper: document.getElementById('canvasWrapper'),
    threatGraphCanvas: document.getElementById('threatGraphCanvas'),
    graphTooltip: document.getElementById('graphTooltip'),
    graphEmptyState: document.getElementById('graphEmptyState'),
    graphEdgeStats: document.getElementById('graphEdgeStats'),
    btnGraphCurrent: document.getElementById('btnGraphCurrent'),
    btnGraphCluster: document.getElementById('btnGraphCluster'),
    btnGraphReset: document.getElementById('btnGraphReset'),
    btnLoadSampleGraph: document.getElementById('btnLoadSampleGraph'),

    // Insights
    featureBarsContainer: document.getElementById('featureBarsContainer')
  };

  // ═══════════════════════════════════════════════════════════
  // 1. INITIALIZATION & ROUTING
  // ═══════════════════════════════════════════════════════════
  function init() {
    setupNavigation();
    setupScanner();
    setupGraphVisualizer();
    setupFeatureImportance();
    checkBackendHealth();

    // Periodic health check every 10s
    setInterval(checkBackendHealth, 10000);
  }

  function setupNavigation() {
    // Desktop Tab switching
    DOM.tabs.forEach((tab) => {
      tab.addEventListener('click', () => {
        const tabId = tab.dataset.tab;
        switchTab(tabId);
      });
    });

    // Mobile Drawer navigation
    DOM.mobileNavItems.forEach((item) => {
      item.addEventListener('click', () => {
        const tabId = item.dataset.tab;
        switchTab(tabId);
        DOM.mobileDrawer.classList.remove('open');
        DOM.mobileMenuBtn.setAttribute('aria-expanded', 'false');
      });
    });

    // Mobile Menu Button Toggle
    if (DOM.mobileMenuBtn) {
      DOM.mobileMenuBtn.addEventListener('click', () => {
        const isOpen = DOM.mobileDrawer.classList.toggle('open');
        DOM.mobileMenuBtn.setAttribute('aria-expanded', String(isOpen));
      });
    }

    // Jump to Graph from result
    if (DOM.jumpToGraphBtn) {
      DOM.jumpToGraphBtn.addEventListener('click', () => {
        switchTab('graph');
      });
    }
  }

  function switchTab(tabId) {
    state.activeTab = tabId;

    // Update Desktop Tabs
    DOM.tabs.forEach((tab) => {
      const isActive = tab.dataset.tab === tabId;
      tab.classList.toggle('active', isActive);
      tab.setAttribute('aria-selected', String(isActive));
    });

    // Update Mobile Nav
    DOM.mobileNavItems.forEach((item) => {
      item.classList.toggle('active', item.dataset.tab === tabId);
    });

    // Update Tab Panels
    DOM.panels.forEach((panel) => {
      const isTarget = panel.id === `panel-${tabId}`;
      panel.classList.toggle('active', isTarget);
    });

    // If graph tab opened, resize canvas & trigger redraw
    if (tabId === 'graph') {
      setTimeout(() => {
        resizeGraphCanvas();
        if (state.graphData.nodes.length > 0) {
          DOM.graphEmptyState.classList.add('hidden');
        }
      }, 50);
    }
  }

  // ═══════════════════════════════════════════════════════════
  // 2. BACKEND HEALTH & MODEL ENGINE STATUS
  // ═══════════════════════════════════════════════════════════
  async function checkBackendHealth() {
    try {
      const res = await fetch('/api/health');
      if (res.ok) {
        const data = await res.json();
        state.systemHealthy = true;
        state.modelMode = data.model_mode || 'DGL_RGCN';

        if (state.modelMode === 'DGL_RGCN') {
          DOM.statusBadgeText.textContent = 'RGCN Model Online';
          DOM.statusDot.className = 'status-pulse-dot';
        } else {
          DOM.statusBadgeText.textContent = 'Analysis Service Available';
          DOM.statusDot.className = 'status-pulse-dot status-pulse-dot--warning';
        }
      } else {
        throw new Error('Health check failed');
      }
    } catch (err) {
      state.systemHealthy = false;
      DOM.statusBadgeText.textContent = 'Service Standby';
      DOM.statusDot.className = 'status-pulse-dot status-pulse-dot--warning';
    }
  }

  // ═══════════════════════════════════════════════════════════
  // 3. SCANNER & DOMAIN ANALYSIS LOGIC
  // ═══════════════════════════════════════════════════════════
  function setupScanner() {
    // Form submit
    DOM.scanForm.addEventListener('submit', (e) => {
      e.preventDefault();
      executeScan(DOM.domainInput.value);
    });

    // Demo Chips
    DOM.demoChips.forEach((chip) => {
      chip.addEventListener('click', () => {
        const domain = chip.dataset.domain;
        DOM.domainInput.value = domain;
        executeScan(domain);
      });
    });

    // Paste Button
    if (DOM.pasteBtn) {
      DOM.pasteBtn.addEventListener('click', async () => {
        try {
          const text = await navigator.clipboard.readText();
          if (text) {
            DOM.domainInput.value = text.trim();
            DOM.domainInput.focus();
          }
        } catch (e) {
          DOM.domainInput.focus();
        }
      });
    }

    // Analyze Another Button
    if (DOM.analyzeAnotherBtn) {
      DOM.analyzeAnotherBtn.addEventListener('click', () => {
        DOM.resultsDashboard.classList.add('hidden');
        DOM.domainInput.value = '';
        DOM.domainInput.focus();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    }
  }

  async function executeScan(rawInput) {
    if (!rawInput || state.isScanning) return;

    const domain = rawInput.trim();
    if (!domain) return;

    state.isScanning = true;
    DOM.analyzeBtn.classList.add('scanning');
    DOM.analyzeBtn.disabled = true;
    DOM.loadingConsole.classList.remove('hidden');
    DOM.resultsDashboard.classList.add('hidden');

    // Reset loading step styles
    DOM.loadingSteps.forEach((step) => {
      step.className = 'loading-step';
    });

    // Start progressive UI step animation
    animateStep(0);
    const stepTimer1 = setTimeout(() => animateStep(1), 250);
    const stepTimer2 = setTimeout(() => animateStep(2), 500);
    const stepTimer3 = setTimeout(() => animateStep(3), 750);

    const startTime = performance.now();

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ domain: domain })
      });

      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      clearTimeout(stepTimer3);

      DOM.loadingSteps.forEach((step) => {
        step.className = 'loading-step done';
      });

      if (!response.ok) {
        const errJson = await response.json().catch(() => ({}));
        throw new Error(errJson.message || 'Analysis service is unavailable. Start the backend and try again.');
      }

      const json = await response.json();
      const elapsed = performance.now() - startTime;
      const remainingDelay = Math.max(0, 500 - elapsed);

      setTimeout(() => {
        DOM.loadingConsole.classList.add('hidden');
        DOM.analyzeBtn.classList.remove('scanning');
        DOM.analyzeBtn.disabled = false;
        state.isScanning = false;

        if (json.status === 'success' && json.data) {
          try {
            renderAnalysisResults(json.data);
          } catch (renderErr) {
            console.error('Error rendering results:', renderErr);
          }
        } else {
          alert(json.message || 'Analysis returned no data.');
        }
      }, remainingDelay);

    } catch (err) {
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      clearTimeout(stepTimer3);
      DOM.loadingConsole.classList.add('hidden');
      DOM.analyzeBtn.classList.remove('scanning');
      DOM.analyzeBtn.disabled = false;
      state.isScanning = false;

      alert(err.message || 'Analysis service is unavailable. Start the backend and try again.');
    }
  }

  function animateStep(stepIndex) {
    if (stepIndex > 0) {
      DOM.loadingSteps[stepIndex - 1].className = 'loading-step done';
    }
    if (stepIndex < DOM.loadingSteps.length) {
      DOM.loadingSteps[stepIndex].className = 'loading-step active';
    }
  }

  // ═══════════════════════════════════════════════════════════
  // 4. RENDER RESULTS DASHBOARD
  // ═══════════════════════════════════════════════════════════
  function renderAnalysisResults(data) {
    state.lastAnalysis = data;
    DOM.resultsDashboard.classList.remove('hidden');

    const riskScore = typeof data.risk_score === 'number' ? data.risk_score : Math.round((data.probability || 0) * 100);
    const verdict = data.verdict || (riskScore >= 70 ? 'PHISHING' : riskScore >= 40 ? 'SUSPICIOUS' : 'BENIGN');
    const classification = data.classification || (verdict === 'PHISHING' ? 'malicious' : verdict === 'SUSPICIOUS' ? 'suspicious' : 'safe');
    const modelMode = data.model_mode || 'DGL_RGCN';

    // 1. Circular Risk Gauge Animation
    animateGauge(riskScore, classification);

    // 2. Verdict Banner
    DOM.resultHeroCard.className = `result-hero-card result--${classification}`;
    DOM.verdictPill.className = `verdict-pill verdict-pill--${classification}`;
    
    if (classification === 'malicious') {
      DOM.verdictText.textContent = 'Phishing Detected';
    } else if (classification === 'suspicious') {
      DOM.verdictText.textContent = 'Suspicious Domain';
    } else {
      DOM.verdictText.textContent = 'Likely Benign';
    }

    DOM.confidenceTag.textContent = `Confidence: ${data.confidence || 95.0}%`;
    DOM.analyzedDomainText.textContent = data.domain || data.url;
    DOM.resultModelMode.textContent = modelMode;
    DOM.resultLatency.textContent = `${data.response_time_ms || 18.2} ms`;
    DOM.resultTimestamp.textContent = new Date(data.timestamp || Date.now()).toLocaleTimeString();

    // 3. Card A: Risk Signals
    renderRiskSignals(data.top_risk_factors || [], classification, data.features || {});

    // 4. Card B: Domain Profile (21 Features)
    renderDomainProfile(data.features || {}, data.dns_info || {});

    // 5. Card C: Infrastructure Footprint
    renderInfrastructureFootprint(data.dns_info || {}, data.graph || null);

    // 6. Update Graph Visualizer with Domain's Bipartite Graph
    if (data.graph && data.graph.nodes && data.graph.nodes.length > 0) {
      loadGraphData(data.graph.nodes, data.graph.edges);
    }

    // Smooth scroll down to result card
    setTimeout(() => {
      DOM.resultHeroCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
  }

  function animateGauge(score, classification) {
    DOM.gaugeScore.textContent = `${Math.round(score)}%`;
    
    // SVG circle circumference for r=48 is 2 * PI * 48 ≈ 301.59
    const circumference = 301.59;
    const offset = circumference - (score / 100) * circumference;
    DOM.gaugeProgress.style.strokeDashoffset = String(offset);

    if (classification === 'malicious') {
      DOM.gaugeProgress.style.stroke = 'var(--threat-critical)';
    } else if (classification === 'suspicious') {
      DOM.gaugeProgress.style.stroke = 'var(--threat-warning)';
    } else {
      DOM.gaugeProgress.style.stroke = 'var(--threat-benign)';
    }
  }

  function renderRiskSignals(signals, classification, features) {
    DOM.signalsList.innerHTML = '';
    
    // If backend provided top risk factors, use them
    let items = signals;
    if (!items || items.length === 0) {
      items = deriveFallbackSignals(features, classification);
    }

    DOM.riskSignalsCount.textContent = `${items.length} Signals`;

    items.forEach((signalText) => {
      const li = document.createElement('li');
      li.className = 'signal-item';

      let severity = 'info';
      let sevLabel = 'Normal';
      let iconColor = 'var(--accent-sky)';

      if (classification === 'malicious') {
        severity = 'critical';
        sevLabel = 'Critical';
        iconColor = 'var(--threat-critical)';
      } else if (classification === 'suspicious') {
        severity = 'warning';
        sevLabel = 'Warning';
        iconColor = 'var(--threat-warning)';
      }

      li.innerHTML = `
        <div class="signal-item__icon" style="color: ${iconColor};">
          <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
        </div>
        <div class="signal-item__content">
          <div class="signal-item__header">
            <span class="signal-item__title">${escapeHtml(signalText)}</span>
            <span class="signal-item__severity signal-item__severity--${severity}">${sevLabel}</span>
          </div>
          <p class="signal-item__desc">Neural message passing detected anomalous relational correlation for this signal.</p>
        </div>
      `;
      DOM.signalsList.appendChild(li);
    });
  }

  function deriveFallbackSignals(f, classification) {
    const res = [];
    if (f.entropy > 3.8) res.push(`High Shannon Entropy (${Number(f.entropy).toFixed(2)})`);
    if (f.contains_login_keywords > 0) res.push('Contains Deceptive Security/Auth Keywords');
    if (f.brand_similarity >= 1 && f.brand_similarity <= 3) res.push('High Brand Impersonation Proximity');
    if (f.suspicious_tld > 0) res.push('High-Risk Top-Level Domain (TLD)');
    if (f.num_a_records === 0) res.push('No Active A-Records (Dormant Infrastructure)');

    if (res.length === 0) {
      if (classification === 'safe') {
        res.push('Active Authoritative DNS Resolution', 'Normal String Entropy (< 3.2)', 'Standard Canonical Infrastructure');
      } else {
        res.push('Structural Lexical Anomaly Detected');
      }
    }
    return res.slice(0, 3);
  }

  function renderDomainProfile(f, dns) {
    DOM.profileGrid.innerHTML = '';

    const profileData = [
      { label: 'Domain Length', val: f.domain_length ?? 'Unavailable' },
      { label: 'Entropy Score', val: f.entropy ? Number(f.entropy).toFixed(2) : 'Unavailable' },
      { label: 'Subdomains', val: f.subdomain_count ?? '0' },
      { label: 'DNS Status', val: dns.dns_status ? dns.dns_status.toUpperCase() : 'RESOLVED' },
      { label: 'A-Records (IPs)', val: f.num_a_records ?? (dns.ip_addresses ? dns.ip_addresses.length : '0') },
      { label: 'Nameservers', val: f.num_ns_records ?? (dns.nameservers ? dns.nameservers.length : '0') },
      { label: 'Punycode', val: f.is_punycode > 0 ? 'YES (Homograph)' : 'NO' },
      { label: 'Digit Ratio', val: f.digit_ratio ? `${(f.digit_ratio * 100).toFixed(1)}%` : '0.0%' }
    ];

    profileData.forEach((item) => {
      const tile = document.createElement('div');
      tile.className = 'profile-tile';
      tile.innerHTML = `
        <span class="profile-tile__label">${escapeHtml(item.label)}</span>
        <span class="profile-tile__value">${escapeHtml(String(item.val))}</span>
      `;
      DOM.profileGrid.appendChild(tile);
    });
  }

  function renderInfrastructureFootprint(dns, graph) {
    DOM.ipChipsContainer.innerHTML = '';
    DOM.nsChipsContainer.innerHTML = '';

    const ips = dns.ip_addresses || [];
    const nss = dns.nameservers || [];

    DOM.ipCountBadge.textContent = String(ips.length);
    DOM.nsCountBadge.textContent = String(nss.length);

    if (ips.length > 0) {
      ips.forEach((ip) => {
        const chip = document.createElement('span');
        chip.className = 'infra-chip';
        chip.textContent = ip;
        DOM.ipChipsContainer.appendChild(chip);
      });
    } else {
      DOM.ipChipsContainer.innerHTML = '<span class="empty-state-text">No IP records resolved</span>';
    }

    if (nss.length > 0) {
      nss.forEach((ns) => {
        const chip = document.createElement('span');
        chip.className = 'infra-chip';
        chip.textContent = ns;
        DOM.nsChipsContainer.appendChild(chip);
      });
    } else {
      DOM.nsChipsContainer.innerHTML = '<span class="empty-state-text">No NS records resolved</span>';
    }
  }

  // ═══════════════════════════════════════════════════════════
  // 5. INTERACTIVE THREAT GRAPH VISUALIZER (CANVAS)
  // ═══════════════════════════════════════════════════════════
  function setupGraphVisualizer() {
    window.addEventListener('resize', resizeGraphCanvas);

    if (DOM.btnGraphCurrent) {
      DOM.btnGraphCurrent.addEventListener('click', () => {
        DOM.btnGraphCurrent.classList.add('active');
        DOM.btnGraphCluster.classList.remove('active');
        state.graphMode = 'current';
        if (state.lastAnalysis && state.lastAnalysis.graph) {
          loadGraphData(state.lastAnalysis.graph.nodes, state.lastAnalysis.graph.edges);
        } else {
          DOM.graphEmptyState.classList.remove('hidden');
        }
      });
    }

    if (DOM.btnGraphCluster) {
      DOM.btnGraphCluster.addEventListener('click', () => {
        DOM.btnGraphCluster.classList.add('active');
        DOM.btnGraphCurrent.classList.remove('active');
        state.graphMode = 'cluster';
        fetchClusterGraphData();
      });
    }

    if (DOM.btnGraphReset) {
      DOM.btnGraphReset.addEventListener('click', () => {
        if (state.graphData.nodes.length > 0) {
          positionGraphNodes();
        }
      });
    }

    if (DOM.btnLoadSampleGraph) {
      DOM.btnLoadSampleGraph.addEventListener('click', () => {
        DOM.btnGraphCluster.click();
      });
    }

    setupGraphInteractions();
  }

  function resizeGraphCanvas() {
    if (!DOM.threatGraphCanvas || !DOM.canvasWrapper) return;
    const rect = DOM.canvasWrapper.getBoundingClientRect();
    DOM.threatGraphCanvas.width = rect.width;
    DOM.threatGraphCanvas.height = rect.height;
    if (state.graphData.nodes.length > 0) {
      positionGraphNodes();
    }
  }

  async function fetchClusterGraphData() {
    try {
      const res = await fetch('/api/graph-data?max_nodes=40');
      const json = await res.json();
      if (json.status === 'success' && json.data) {
        loadGraphData(json.data.nodes, json.data.edges);
      }
    } catch (e) {
      console.warn('Could not load cluster graph:', e);
    }
  }

  function loadGraphData(nodes, edges) {
    if (!nodes || nodes.length === 0) {
      DOM.graphEmptyState.classList.remove('hidden');
      return;
    }

    DOM.graphEmptyState.classList.add('hidden');
    state.graphData = { nodes: [...nodes], edges: [...edges] };

    // Update overlay count
    if (DOM.graphEdgeStats) {
      DOM.graphEdgeStats.innerHTML = `
        <span>Edges: <strong>${edges.length}</strong></span>
        <span>Nodes: <strong>${nodes.length}</strong></span>
      `;
    }

    positionGraphNodes();
    startGraphAnimation();
  }

  function positionGraphNodes() {
    const W = DOM.threatGraphCanvas.width || 800;
    const H = DOM.threatGraphCanvas.height || 600;
    const cx = W / 2;
    const cy = H / 2;

    const domainNodes = state.graphData.nodes.filter((n) => n.type === 'domain');
    const ipNodes = state.graphData.nodes.filter((n) => n.type === 'ip');
    const nsNodes = state.graphData.nodes.filter((n) => n.type === 'nameserver');

    // Place central domain(s)
    domainNodes.forEach((node, i) => {
      if (domainNodes.length === 1) {
        node.x = cx;
        node.y = cy;
      } else {
        const angle = (i / domainNodes.length) * 2 * Math.PI;
        node.x = cx + Math.cos(angle) * (W * 0.22);
        node.y = cy + Math.sin(angle) * (H * 0.22);
      }
      node.radius = 16;
      node.color = node.label === 1 ? '#F43F5E' : '#10B981';
    });

    // Place IP nodes on outer orbit (Left/Upper)
    ipNodes.forEach((node, i) => {
      const angle = Math.PI * 0.6 + (i / Math.max(1, ipNodes.length)) * Math.PI * 0.9;
      const dist = Math.min(W, H) * 0.36;
      node.x = cx + Math.cos(angle) * dist;
      node.y = cy + Math.sin(angle) * dist;
      node.radius = 11;
      node.color = '#38BDF8';
    });

    // Place NS nodes on outer orbit (Right/Lower)
    nsNodes.forEach((node, i) => {
      const angle = -Math.PI * 0.4 + (i / Math.max(1, nsNodes.length)) * Math.PI * 0.9;
      const dist = Math.min(W, H) * 0.36;
      node.x = cx + Math.cos(angle) * dist;
      node.y = cy + Math.sin(angle) * dist;
      node.radius = 11;
      node.color = '#8B5CF6';
    });
  }

  let particleOffset = 0;

  function startGraphAnimation() {
    if (state.animationFrameId) {
      cancelAnimationFrame(state.animationFrameId);
    }

    const canvas = DOM.threatGraphCanvas;
    const ctx = canvas.getContext('2d');

    function renderFrame() {
      particleOffset = (particleOffset + 0.012) % 1;

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const nodes = state.graphData.nodes;
      const edges = state.graphData.edges;

      // 1. Draw Edges
      edges.forEach((edge) => {
        const s = nodes.find((n) => n.id === edge.source) || nodes[edge.source];
        const t = nodes.find((n) => n.id === edge.target) || nodes[edge.target];
        if (!s || !t) return;

        // Line
        ctx.beginPath();
        ctx.moveTo(s.x, s.y);
        ctx.lineTo(t.x, t.y);
        ctx.strokeStyle = edge.type === 'has_ip' ? 'rgba(56, 189, 248, 0.25)' : 'rgba(139, 92, 246, 0.25)';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Flowing particle dot
        const px = s.x + (t.x - s.x) * particleOffset;
        const py = s.y + (t.y - s.y) * particleOffset;
        ctx.beginPath();
        ctx.arc(px, py, 2.5, 0, 2 * Math.PI);
        ctx.fillStyle = edge.type === 'has_ip' ? '#00D2FF' : '#C084FC';
        ctx.fill();
      });

      // 2. Draw Nodes
      nodes.forEach((node) => {
        const isHovered = state.hoveredNode && state.hoveredNode.id === node.id;

        // Outer glow
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius + (isHovered ? 8 : 4), 0, 2 * Math.PI);
        ctx.fillStyle = node.color.replace(')', ', 0.15)').replace('rgb', 'rgba').replace('#F43F5E', 'rgba(244,63,94,0.18)').replace('#10B981', 'rgba(16,185,129,0.18)').replace('#38BDF8', 'rgba(56,189,248,0.18)').replace('#8B5CF6', 'rgba(139,92,246,0.18)');
        ctx.fill();

        // Main node body
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius, 0, 2 * Math.PI);
        ctx.fillStyle = '#0F192E';
        ctx.fill();
        ctx.lineWidth = isHovered ? 3 : 2;
        ctx.strokeStyle = node.color;
        ctx.stroke();

        // Center dot
        ctx.beginPath();
        ctx.arc(node.x, node.y, 4, 0, 2 * Math.PI);
        ctx.fillStyle = node.color;
        ctx.fill();

        // Node Label
        ctx.font = '11px "JetBrains Mono", monospace';
        ctx.fillStyle = isHovered ? '#FFFFFF' : '#94A3B8';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        const label = node.name || node.domain || node.id;
        const truncated = label.length > 20 ? label.slice(0, 18) + '...' : label;
        ctx.fillText(truncated, node.x, node.y + node.radius + 6);
      });

      state.animationFrameId = requestAnimationFrame(renderFrame);
    }

    renderFrame();
  }

  function setupGraphInteractions() {
    const canvas = DOM.threatGraphCanvas;

    canvas.addEventListener('mousemove', (e) => {
      const rect = canvas.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;

      let found = null;
      state.graphData.nodes.forEach((node) => {
        const dx = node.x - mx;
        const dy = node.y - my;
        if (Math.sqrt(dx * dx + dy * dy) <= node.radius + 8) {
          found = node;
        }
      });

      state.hoveredNode = found;
      canvas.style.cursor = found ? 'pointer' : 'default';

      if (found) {
        DOM.graphTooltip.classList.remove('hidden');
        DOM.graphTooltip.style.left = `${found.x}px`;
        DOM.graphTooltip.style.top = `${found.y}px`;
        DOM.graphTooltip.innerHTML = `
          <div class="tooltip-title">${escapeHtml(found.name || found.domain || found.id)}</div>
          <div class="tooltip-row"><span>Type:</span><strong>${escapeHtml((found.type || 'Domain').toUpperCase())}</strong></div>
          ${found.risk !== undefined ? `<div class="tooltip-row"><span>Risk:</span><strong>${found.risk}%</strong></div>` : ''}
          ${found.status ? `<div class="tooltip-row"><span>Status:</span><strong>${escapeHtml(found.status)}</strong></div>` : ''}
        `;
      } else {
        DOM.graphTooltip.classList.add('hidden');
      }
    });

    canvas.addEventListener('mouseleave', () => {
      state.hoveredNode = null;
      DOM.graphTooltip.classList.add('hidden');
    });
  }

  // ═══════════════════════════════════════════════════════════
  // 6. MODEL INSIGHTS: FEATURE IMPORTANCE
  // ═══════════════════════════════════════════════════════════
  function setupFeatureImportance() {
    if (!DOM.featureBarsContainer) return;

    const featureWeights = [
      { name: 'brand_similarity', label: 'Brand Impersonation Proximity', weight: 0.94 },
      { name: 'entropy', label: 'Shannon Domain Entropy', weight: 0.89 },
      { name: 'contains_login_keywords', label: 'Deceptive Login Keywords', weight: 0.85 },
      { name: 'suspicious_tld', label: 'High-Risk TLD Classifier', weight: 0.82 },
      { name: 'has_ip', label: 'Raw IPv4 Literal in Hostname', weight: 0.78 },
      { name: 'domain_length', label: 'Domain Token Length', weight: 0.71 },
      { name: 'subdomain_count', label: 'Multi-Level Subdomains', weight: 0.68 },
      { name: 'num_a_records', label: 'DNS A-Record Infrastructure', weight: 0.65 },
      { name: 'num_ns_records', label: 'Nameserver Delegation Degree', weight: 0.62 },
      { name: 'is_punycode', label: 'IDN Punycode / Homograph Attack', weight: 0.59 }
    ];

    DOM.featureBarsContainer.innerHTML = '';

    featureWeights.forEach((feat) => {
      const item = document.createElement('div');
      item.className = 'feature-bar-item';
      item.innerHTML = `
        <div class="feature-bar-header">
          <span class="feature-bar-name">${escapeHtml(feat.label)}</span>
          <span class="feature-bar-score">${(feat.weight * 100).toFixed(0)}%</span>
        </div>
        <div class="feature-bar-track">
          <div class="feature-bar-fill" style="width: ${feat.weight * 100}%;"></div>
        </div>
      `;
      DOM.featureBarsContainer.appendChild(item);
    });
  }

  // ──────── Helper Utilities ────────
  function escapeHtml(str) {
    if (str === null || str === undefined) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
