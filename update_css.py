"""
Replace the entire <style>...</style> section in shensuanzi.html with new Taoist-themed CSS.
"""
import re

NEW_CSS = r"""/* ====== CSS Reset & Variables ====== */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}

:root {
  --ink-black: #1a1410;
  --ink-dark: #2c2418;
  --ink-gray: #4a4238;
  --ink-light: #8b8170;
  --paper: #f5efe0;
  --paper-light: #faf7ef;
  --paper-dark: #ebe2cf;
  --cinnabar: #c43a31;
  --cinnabar-dark: #8b1a1a;
  --cinnabar-light: #e85d5d;
  --gold: #b8942e;
  --gold-light: #d4b868;
  --gold-pale: #e8d9a0;
  --jade: #4a7c59;
  --jade-light: #6b9a78;
  --azure: #3a6186;
  --ochre: #8b6914;
  --border-ink: #8b8170;
  --shadow: rgba(26,20,16,0.08);
  --shadow-lg: rgba(26,20,16,0.15);
  --radius-sm: 2px;
  --radius-md: 4px;
  --radius-lg: 6px;
  --font-title: 'Ma Shan Zheng','ZCOOL XiaoWei','STKaiti','KaiTi',cursive;
  --font-body: 'ZCOOL XiaoWei','STSong','SimSun','Noto Serif SC',serif;
  --transition: 0.3s cubic-bezier(0.4,0,0.2,1);
}

/* ====== Body & Ink-wash Background ====== */
body {
  font-family: var(--font-body);
  background-color: var(--paper);
  color: var(--ink-black);
  min-height: 100vh;
  line-height: 1.9;
  letter-spacing: 0.02em;
  background-image:
    /* 远山水墨 */
    radial-gradient(ellipse 600px 300px at 15% 25%, rgba(58,97,134,0.06) 0%, transparent 70%),
    radial-gradient(ellipse 400px 200px at 20% 30%, rgba(26,20,16,0.05) 0%, transparent 65%),
    radial-gradient(ellipse 350px 180px at 80% 20%, rgba(58,97,134,0.04) 0%, transparent 60%),
    /* 宣纸纹理 */
    repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(139,129,112,0.015) 3px, rgba(139,129,112,0.015) 6px),
    repeating-linear-gradient(90deg, transparent, transparent 5px, rgba(139,129,112,0.008) 5px, rgba(139,129,112,0.008) 10px);
  background-size: cover, 200px, auto, auto;
  background-repeat: no-repeat, repeat, repeat, repeat;
  background-position: center top, 0 0, 0 0, 0 0;
  background-attachment: fixed, scroll, scroll, scroll;
}
/* 底部水墨晕染 */
body::before {
  content: '';
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background:
    radial-gradient(ellipse 800px 200px at 50% 100%, rgba(26,20,16,0.04) 0%, transparent 60%);
  pointer-events: none; z-index: 0;
}

/* ====== Header ====== */
.app-header {
  text-align: center;
  padding: 48px 20px 36px;
  position: relative;
  z-index: 1;
}
.bagua-container {
  display: inline-block;
  position: relative;
  margin-bottom: 20px;
}
.bagua-svg {
  width: 130px; height: 130px;
  filter: drop-shadow(0 4px 16px var(--shadow-lg));
  animation: bagua-rotate 120s linear infinite;
}
@keyframes bagua-rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.app-title {
  font-family: var(--font-title);
  font-size: 3.6rem;
  font-weight: normal;
  color: var(--ink-black);
  letter-spacing: 12px;
  margin-bottom: 6px;
  text-shadow: 1px 1px 0 rgba(184,148,46,0.2);
}
.app-subtitle {
  font-size: 1.15rem;
  color: var(--cinnabar);
  letter-spacing: 6px;
  font-family: var(--font-title);
}
.app-tagline {
  font-size: 0.95rem;
  color: var(--ink-light);
  margin-top: 8px;
  letter-spacing: 3px;
  font-style: italic;
}

/* ====== Main Container ====== */
.app-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 24px 80px;
  position: relative;
  z-index: 1;
}

/* ====== Mode Toggle ====== */
.mode-toggle {
  display: flex;
  justify-content: center;
  gap: 0;
  margin-bottom: 32px;
}
.mode-btn {
  padding: 12px 36px;
  border: 2px solid var(--border-ink);
  background: var(--paper-light);
  color: var(--ink-gray);
  font-family: var(--font-title);
  font-size: 1.05rem;
  cursor: pointer;
  transition: var(--transition);
  letter-spacing: 3px;
  position: relative;
}
.mode-btn:first-child { border-radius: var(--radius-md) 0 0 var(--radius-md); }
.mode-btn:last-child { border-radius: 0 var(--radius-md) var(--radius-md) 0; }
.mode-btn.active {
  background: var(--ink-black);
  color: var(--gold-light);
  border-color: var(--ink-black);
  box-shadow: 0 2px 12px var(--shadow);
}
.mode-btn:hover:not(.active) {
  border-color: var(--gold);
  color: var(--gold);
}

/* ====== Card - Talisman Style ====== */
.card {
  background: linear-gradient(135deg, rgba(250,247,239,0.96), rgba(245,239,224,0.94));
  border: 2px solid var(--border-ink);
  border-radius: var(--radius-md);
  padding: 32px;
  margin-bottom: 28px;
  box-shadow:
    0 2px 16px var(--shadow),
    inset 0 0 0 1px rgba(184,148,46,0.06);
  position: relative;
}
.card::before {
  content: '';
  position: absolute; top: -1px; left: 24px; right: 24px;
  height: 3px;
  background: linear-gradient(90deg, transparent, var(--cinnabar), var(--gold), var(--cinnabar), transparent);
  border-radius: 2px;
}
.card::after {
  content: '';
  position: absolute; bottom: -1px; left: 24px; right: 24px;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold-pale), transparent);
}
.card-title {
  font-family: var(--font-title);
  font-size: 1.25rem;
  color: var(--ink-black);
  letter-spacing: 4px;
  margin-bottom: 24px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--border-ink);
  display: flex;
  align-items: center;
  gap: 10px;
}

/* ====== Form ====== */
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
  gap: 16px;
}
.form-group {
  display: flex; flex-direction: column; gap: 5px;
}
.form-group label {
  font-size: 0.85rem;
  color: var(--ink-gray);
  letter-spacing: 2px;
}
.form-group input, .form-group select {
  padding: 11px 15px;
  border: 1px solid var(--border-ink);
  border-radius: var(--radius-sm);
  background: var(--paper-light);
  color: var(--ink-black);
  font-family: var(--font-body);
  font-size: 0.95rem;
  transition: var(--transition);
}
.form-group input:focus, .form-group select:focus {
  outline: none;
  border-color: var(--gold);
  box-shadow: 0 0 0 3px rgba(184,148,46,0.1);
}
.form-hint { font-size: 0.75rem; color: var(--ink-light); }

/* ====== Buttons ====== */
.btn-primary {
  padding: 15px 44px;
  background: linear-gradient(180deg, var(--cinnabar-light), var(--cinnabar));
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  font-family: var(--font-title);
  font-size: 1.2rem;
  letter-spacing: 5px;
  cursor: pointer;
  transition: all 0.25s ease;
  box-shadow: 0 4px 16px rgba(196,58,49,0.3);
  position: relative; overflow: hidden;
}
.btn-primary::after {
  content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
  transition: left 0.5s ease;
}
.btn-primary:hover {
  background: linear-gradient(180deg, var(--cinnabar), var(--cinnabar-dark));
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(196,58,49,0.4);
}
.btn-primary:hover::after { left: 100%; }
.btn-primary:active { transform: translateY(0); box-shadow: 0 2px 8px rgba(196,58,49,0.3); }
.btn-secondary {
  padding: 10px 24px; font-size: 0.95rem;
  background: transparent; color: var(--ink-black);
  border: 2px solid var(--ink-black); border-radius: var(--radius-sm);
  font-family: var(--font-title); letter-spacing: 2px;
  cursor: pointer; transition: all 0.2s ease;
}
.btn-secondary:hover {
  background: var(--ink-black); color: var(--gold-light);
  transform: translateY(-1px); box-shadow: 0 3px 12px var(--shadow);
}
.btn-secondary:active { transform: translateY(0); }
.btn-danger {
  background: transparent; color: var(--cinnabar);
  border: 1px solid var(--cinnabar); border-radius: var(--radius-sm);
  padding: 6px 16px; font-size: 0.85rem;
  cursor: pointer; transition: all 0.2s ease;
}
.btn-danger:hover { background: var(--cinnabar); color: #fff; transform: scale(1.05); }
.btn-danger:active { transform: scale(0.95); }

.btn-export {
  padding: 10px 22px;
  background: linear-gradient(135deg, var(--gold), #9a7a22);
  color: #fff; border: none; border-radius: var(--radius-sm);
  font-family: var(--font-title); font-size: 0.9rem;
  cursor: pointer; letter-spacing: 2px; transition: all 0.2s ease;
  white-space: nowrap;
}
.btn-export:hover {
  background: linear-gradient(135deg, var(--gold-light), var(--gold));
  transform: translateY(-2px); box-shadow: 0 4px 16px rgba(184,148,46,0.35);
}
.btn-export:active { transform: translateY(0); }
.btn-export:disabled { opacity: 0.6; cursor: wait; }

/* ====== Tab Bar ====== */
.result-panel { display: none; }
.result-panel.visible { display: block; }
.tab-bar {
  display: flex; flex-wrap: wrap; gap: 3px;
  padding: 10px;
  background: linear-gradient(180deg, var(--paper-dark), var(--paper));
  border-radius: var(--radius-md);
  border: 1px solid var(--border-ink);
  margin-bottom: 20px;
}
.tab-btn {
  padding: 10px 20px; border: none;
  background: transparent;
  color: var(--ink-gray);
  font-family: var(--font-title); font-size: 0.95rem;
  cursor: pointer; border-radius: var(--radius-sm);
  transition: var(--transition); letter-spacing: 2px;
  white-space: nowrap;
}
.tab-btn:hover { background: rgba(184,148,46,0.1); color: var(--ink-black); }
.tab-btn.active {
  background: var(--ink-black);
  color: var(--gold-light);
  box-shadow: 0 1px 4px var(--shadow);
}
.tab-content { display: none; }
.tab-content.active { display: block; }

/* ====== Result Content ====== */
.paipan-table {
  width: 100%; border-collapse: collapse; margin: 16px 0;
  background: rgba(250,247,239,0.85);
}
.paipan-table th, .paipan-table td {
  padding: 12px 10px; text-align: center;
  border: 1px solid var(--border-ink); font-size: 0.92rem;
}
.paipan-table tr:nth-child(even) td { background: rgba(245,239,224,0.5); }
.paipan-table th {
  background: var(--ink-black); color: var(--gold-light);
  font-weight: normal; letter-spacing: 2px;
  font-family: var(--font-title);
}
.paipan-table .pillar-name {
  font-size: 1.15rem; letter-spacing: 3px; color: var(--cinnabar);
  font-family: var(--font-title);
}
.wuxing-tag {
  display: inline-block; padding: 2px 10px; border-radius: 10px;
  font-size: 0.78rem; letter-spacing: 1px;
}
.wuxing-wood { background: #5b8c5a; color: #fff; }
.wuxing-fire { background: #d94a4a; color: #fff; }
.wuxing-earth { background: #c9a84c; color: #fff; }
.wuxing-metal { background: #9b9b9b; color: #fff; }
.wuxing-water { background: #4a90d9; color: #fff; }

.score-bar {
  display: flex; align-items: center; gap: 14px; margin: 8px 0;
}
.score-bar .bar-label { min-width: 65px; font-size: 0.85rem; color: var(--ink-gray); }
.score-bar .bar-track {
  flex: 1; height: 22px; background: var(--paper-dark);
  border-radius: 11px; overflow: hidden; border: 1px solid var(--border-ink);
}
.bar-fill-high { background: linear-gradient(90deg, var(--cinnabar), var(--cinnabar-light)); }
.bar-fill-mid { background: linear-gradient(90deg, var(--gold), var(--gold-light)); }
.bar-fill-low { background: linear-gradient(90deg, var(--azure), #5a8ab6); }

.analysis-block {
  margin: 20px 0; padding: 18px 20px;
  background: var(--paper-light);
  border-left: 3px solid var(--gold);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  box-shadow: 0 1px 4px var(--shadow);
}
.analysis-block.warning { border-left-color: var(--cinnabar); }
.analysis-block h4 {
  font-family: var(--font-title); font-size: 1.05rem;
  color: var(--ink-black); margin-bottom: 10px; letter-spacing: 2px;
}
.analysis-block p { font-size: 0.92rem; color: var(--ink-gray); line-height: 2; }

.highlight-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px; margin: 16px 0;
}
.highlight-item {
  padding: 16px 12px; background: var(--paper-light);
  border-radius: var(--radius-sm); text-align: center;
  border: 1px solid var(--border-ink);
}
.highlight-item .hi-label { font-size: 0.82rem; color: var(--ink-light); letter-spacing: 1px; }
.highlight-item .hi-value {
  font-size: 1.4rem; color: var(--ink-black);
  font-family: var(--font-title); margin-top: 6px;
}

/* ====== Comparison Grid ====== */
.compare-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }
@media (max-width: 700px) { .compare-grid { grid-template-columns: 1fr; } }
.compare-panel {
  background: var(--paper-light); border: 1px solid var(--border-ink);
  border-radius: var(--radius-md); padding: 20px;
}
.compare-panel h4 {
  text-align: center; font-family: var(--font-title);
  letter-spacing: 3px; color: var(--ink-black);
  margin-bottom: 14px; padding-bottom: 10px;
  border-bottom: 1px solid var(--border-ink);
}

.chart-container { width: 100%; max-width: 280px; margin: 0 auto; }
.chart-container svg { width: 100%; height: auto; }

.compat-score-ring { text-align: center; margin: 20px 0; }
.compat-score-ring .ring-value {
  font-size: 3.2rem; font-family: var(--font-title); color: var(--cinnabar);
}
.compat-score-ring .ring-label { font-size: 0.95rem; color: var(--ink-light); letter-spacing: 2px; }

/* ====== Person Cards ====== */
.person-list { display: flex; flex-direction: column; gap: 14px; margin-bottom: 18px; }
.person-card {
  background: var(--paper-light); border: 1px solid var(--border-ink);
  border-radius: var(--radius-md); padding: 18px 22px;
}
.person-card-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;
}
.person-card-header .person-index {
  font-family: var(--font-title); font-size: 1rem;
  color: var(--ink-black); letter-spacing: 2px;
}
.relationship-select {
  margin: 18px 0; display: flex; align-items: center; gap: 14px;
}
.relationship-select label {
  font-size: 0.9rem; color: var(--ink-gray); letter-spacing: 2px; white-space: nowrap;
}
.relationship-select select {
  padding: 11px 15px; border: 1px solid var(--border-ink);
  border-radius: var(--radius-sm); background: var(--paper-light);
  color: var(--ink-black); font-family: var(--font-body); font-size: 0.95rem;
}

/* ====== Responsive ====== */
@media (max-width: 768px) {
  .app-title { font-size: 2.2rem; letter-spacing: 6px; }
  .form-grid { grid-template-columns: 1fr 1fr; }
  .card { padding: 20px; }
  .tab-btn { padding: 7px 12px; font-size: 0.78rem; }
}
@media (max-width: 480px) {
  .form-grid { grid-template-columns: 1fr; }
  .tab-bar { flex-direction: column; }
}

/* ====== Print ====== */
@media print {
  body { background: #fff; }
  .mode-toggle, .tab-bar, .btn-primary, .btn-secondary, .btn-danger, .btn-export { display: none !important; }
  .card { box-shadow: none; border: 1px solid #ccc; break-inside: avoid; }
  .tab-content { display: block !important; margin-bottom: 20px; }
  .result-panel { display: block !important; }
}"""

with open(r"F:\FTP\操作问题汇总\神算子\shensuanzi.html", "r", encoding="utf-8") as f:
    html = f.read()

# Replace everything between <style> and </style>
old_style = re.search(r'<style>.*?</style>', html, re.DOTALL).group()
new_style = '<style>\n' + NEW_CSS.strip() + '\n</style>'
html = html.replace(old_style, new_style)

with open(r"F:\FTP\操作问题汇总\神算子\shensuanzi.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"CSS updated. New CSS size: {len(NEW_CSS)} bytes, ~{NEW_CSS.count(chr(10))} lines")
print(f"Total HTML size: {len(html)} bytes")
