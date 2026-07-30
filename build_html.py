"""
将calendar_data.js中的数据和额外JS算法组装到index.html中。
保留HTML骨架中SECTION 1的核心常量，从SECTION 2标记处注入日历数据+算法。
"""
import re

# Read the calendar data
with open(r"F:\FTP\操作问题汇总\神算子\calendar_data.js", "r", encoding="utf-8") as f:
    cal_data = f.read()

# Read the HTML skeleton (only HTML+CSS matters, JS is fully replaced)
with open(r"F:\FTP\操作问题汇总\神算子\index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Split at <script> and </script> — replace everything between with complete JS
parts_before = html.split('<script>')
pre_script = parts_before[0] + '<script>\n'
parts_after = html.split('</script>')
post_body = '\n</script>' + parts_after[-1]  # last </script> closes, then rest of HTML

# ============================================================
# ALGORITHM & UI JAVASCRIPT CODE
# ============================================================

algo_js = r"""
// ============================================================
//  SECTION 1: CORE CONSTANTS & LOOKUP TABLES
// ============================================================

// 60甲子
const GZ = ["甲子","乙丑","丙寅","丁卯","戊辰","己巳","庚午","辛未","壬申","癸酉","甲戌","乙亥","丙子","丁丑","戊寅","己卯","庚辰","辛巳","壬午","癸未","甲申","乙酉","丙戌","丁亥","戊子","己丑","庚寅","辛卯","壬辰","癸巳","甲午","乙未","丙申","丁酉","戊戌","己亥","庚子","辛丑","壬寅","癸卯","甲辰","乙巳","丙午","丁未","戊申","己酉","庚戌","辛亥","壬子","癸丑","甲寅","乙卯","丙辰","丁巳","戊午","己未","庚申","辛酉","壬戌","癸亥"];
const TG = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"];
const DZ = ["子","丑","寅","卯","辰","巳","午","未","申","酉","戌","亥"];

// 五行映射 (array indexed by stem/branch position)
const WX_TG = ["木","木","火","火","土","土","金","金","水","水"];
const WX_DZ = ["水","土","木","木","土","火","火","土","金","金","土","水"];
function wxOf(s) { return WX_TG[TG.indexOf(s)] || WX_DZ[DZ.indexOf(s)] || s; }
function wxIdx(wx) { return ["木","火","土","金","水"].indexOf(wx); }

// 阴阳 (1=阳 0=阴)
const YY_TG = [1,0,1,0,1,0,1,0,1,0];
const YY_DZ = [1,0,1,0,1,0,1,0,1,0,1,0];
function yyOf(s) { const ti = TG.indexOf(s); return ti >= 0 ? YY_TG[ti] : YY_DZ[DZ.indexOf(s)]; }

// 生肖
const ZODIAC = ["鼠","牛","虎","兔","龙","蛇","马","羊","猴","鸡","狗","猪"];

// 时辰
const SHICHEN_NAMES = ["子时","丑时","寅时","卯时","辰时","巳时","午时","未时","申时","酉时","戌时","亥时"];
const SHICHEN_RANGES = ["23-01","01-03","03-05","05-07","07-09","09-11","11-13","13-15","15-17","17-19","19-21","21-23"];

// 纳音 (from calendar_data.js below, but we need it early for paipan)
// Note: NAYIN is declared in calendar data below

// 地支藏干
const DZ_CG = { "子":["癸"], "丑":["己","癸","辛"], "寅":["甲","丙","戊"], "卯":["乙"], "辰":["戊","乙","癸"], "巳":["丙","戊","庚"], "午":["丁","己"], "未":["己","丁","乙"], "申":["庚","壬","戊"], "酉":["辛"], "戌":["戊","辛","丁"], "亥":["壬","甲"] };

// 年上起月表 [年干组][月支索引] -> 月干支索引
const Y2M_STEM = [
  [2,3,4,5,6,7,8,9,10,11,0,1],
  [14,15,16,17,18,19,20,21,22,23,12,13],
  [26,27,28,29,30,31,32,33,34,35,24,25],
  [38,39,40,41,42,43,44,45,46,47,36,37],
  [50,51,52,53,54,55,56,57,58,59,48,49],
];

// 日上起时表 [日干组][时支索引] -> 时干支索引
const D2H_STEM = [
  [0,1,2,3,4,5,6,7,8,9,10,11],
  [12,13,14,15,16,17,18,19,20,21,22,23],
  [24,25,26,27,28,29,30,31,32,33,34,35],
  [36,37,38,39,40,41,42,43,44,45,46,47],
  [48,49,50,51,52,53,54,55,56,57,58,59],
];

// 天干五合
const TG_HE = { "甲":"己","己":"甲","乙":"庚","庚":"乙","丙":"辛","辛":"丙","丁":"壬","壬":"丁","戊":"癸","癸":"戊" };
const TG_HE_HUA = { "甲":"土","己":"土","乙":"金","庚":"金","丙":"水","辛":"水","丁":"木","壬":"木","戊":"火","癸":"火" };

// 地支六冲
const DZ_CHONG = { "子":"午","午":"子","丑":"未","未":"丑","寅":"申","申":"寅","卯":"酉","酉":"卯","辰":"戌","戌":"辰","巳":"亥","亥":"巳" };

// 地支六合
const DZ_HE = { "子":"丑","丑":"子","寅":"亥","亥":"寅","卯":"戌","戌":"卯","辰":"酉","酉":"辰","巳":"申","申":"巳","午":"未","未":"午" };

// 地支三合局
const DZ_SANHE = [ {zhi:["申","子","辰"],hua:"水"},{zhi:["亥","卯","未"],hua:"木"},{zhi:["寅","午","戌"],hua:"火"},{zhi:["巳","酉","丑"],hua:"金"} ];

// 地支相刑
const DZ_XING = { "子":["卯"],"卯":["子"],"寅":["巳","申"],"巳":["寅","申"],"申":["寅","巳"],"丑":["戌","未"],"戌":["丑","未"],"未":["丑","戌"] };

// 节令名称
const JIELING_NAMES = ["立春","惊蛰","清明","立夏","芒种","小暑","立秋","白露","寒露","立冬","大雪","小寒"];
const JIELING_NOMINAL = [[1,5],[2,4],[3,6],[4,5],[5,6],[6,6],[7,7],[8,7],[9,8],[10,8],[11,7],[12,7]];
const MONTH_JIELING = ["立春(寅月)","惊蛰(卯月)","清明(辰月)","立夏(巳月)","芒种(午月)","小暑(未月)","立秋(申月)","白露(酉月)","寒露(戌月)","立冬(亥月)","大雪(子月)","小寒(丑月)"];

// 十神名称 (华山简称)
const SHISHEN_FULL = ["比肩","劫财","食神","伤官","偏财","正财","正官","七杀","正印","偏印"];
const SHISHEN_SHORT = ["比","劫","食","伤","才","财","官","杀","印","枭"];

// 格局模板
const PATTERN_TEMPLATES = [
  {name:"官印相生", cond:"正官+正印", desc:"适合公职、管理、稳定发展。为人正直，重视名誉地位，得贵人扶持。", careers:"公务员、教育、行政管理、国企"},
  {name:"食神生财", cond:"食神+正财", desc:"技术型人才，善用才华创造财富。创意丰富，实操能力强。", careers:"技术研发、经商、设计师、工程师"},
  {name:"杀印相生", cond:"七杀+正印", desc:"在高压环境中成长，越挫越强。专业技术精深，权威性高。", careers:"军警、法律、医疗、高管"},
  {name:"伤官配印", cond:"伤官+正印", desc:"才华横溢，学术研究能力强。思维敏捷，表达力好。", careers:"学者、研究员、作家、媒体"},
  {name:"财官双美", cond:"正财+正官", desc:"事业有成、名利双收。财运稳定，社会地位较高。", careers:"企业高管、金融、房地产、经商"},
  {name:"比劫夺财", cond:"比肩/劫财+正财", desc:"竞争意识强，但需防小人劫财。合作中注意分利。", careers:"销售、竞技、创业、团队管理"},
  {name:"食伤泄秀", cond:"食神/伤官多", desc:"聪明灵秀，但易好高骛远。需脚踏实地发挥才华。", careers:"艺术、设计、媒体、策划"},
  {name:"财多身弱", cond:"财星多+身弱", desc:"机遇多但难以把握，需借助他人之力。注意理财。", careers:"财务、投资顾问、银行、保险"},
];

// ============================================================
//  SECTION 2: CALENDAR DATA (embedded)
// ============================================================

// 每年1月1日干支索引
""" + cal_data + r"""

// ============================================================
//  SECTION 3: DATE/TIME UTILITIES
// ============================================================

function daysInMonth(y, m) { return new Date(y, m, 0).getDate(); }

function daysBetween(y1, m1, d1, y2, m2, d2) {
  return Math.floor((new Date(y2, m2-1, d2) - new Date(y1, m1-1, d1)) / 86400000);
}

function getDayGZIndex(year, month, day) {
  // Calculate ganzhi index for any date based on 1900-01-01 = index 10
  const days = daysBetween(1900, 1, 1, year, month, day);
  return ((10 + days) % 60 + 60) % 60;
}

function getYearGZ(year) {
  // Year pillar based on 立春 check
  // For dates before 立春, use previous year
  const baseYear = year - 4;
  const stemIdx = ((baseYear % 10) + 10) % 10;
  const branchIdx = ((baseYear % 12) + 12) % 12;
  return { stem: TG[stemIdx], branch: DZ[branchIdx], stemIdx, branchIdx, gzIdx: stemBranchToGZ(stemIdx, branchIdx) };
}

function stemBranchToGZ(si, bi) {
  for (let i = 0; i < 60; i++) {
    if (i % 10 === si && i % 12 === bi) return i;
  }
  return 0;
}

// ============================================================
//  SECTION 4: PAIPAN ENGINE
// ============================================================

function paipan(name, gender, year, month, day, shichenIdx, longitude) {
  const isMale = gender === 'male';
  const warnings = [];

  // ---- True Solar Time Correction ----
  const timezoneMeridian = 120; // Beijing time zone center
  const lonOffset = (longitude - timezoneMeridian) * 4; // minutes
  // Check DST (1986-1991)
  let dstAdjust = 0;
  if (year >= 1986 && year <= 1991) {
    const dstStart = {1986:[4,13],1987:[4,12],1988:[4,10],1989:[4,16],1990:[4,15],1991:[4,14]};
    const dstEnd = {1986:[9,14],1987:[9,13],1988:[9,11],1989:[9,17],1990:[9,16],1991:[9,15]};
    const [sm, sd] = dstStart[year];
    const [em, ed] = dstEnd[year];
    const birthDate = new Date(year, month-1, day);
    const dstStartDate = new Date(year, sm-1, sd);
    const dstEndDate = new Date(year, em-1, ed);
    if (birthDate >= dstStartDate && birthDate <= dstEndDate) dstAdjust = -60;
    if (dstAdjust) warnings.push("出生日期在夏时制期间(1986-1991)，已自动扣除1小时");
  }

  // Calculate true solar shichen
  // shichenIdx selected by user is based on Beijing time
  // Adjust by longitude offset and DST
  const beijingHour = [23,1,3,5,7,9,11,13,15,17,19,21][shichenIdx];
  let trueHour = beijingHour + lonOffset / 60 + dstAdjust / 60;
  // Re-determine shichen from true hour
  let finalShichen = shichenIdx;
  const hourCheck = ((trueHour % 24) + 24) % 24;
  if (hourCheck >= 23 || hourCheck < 1) finalShichen = 0;
  else if (hourCheck >= 1 && hourCheck < 3) finalShichen = 1;
  else if (hourCheck >= 3 && hourCheck < 5) finalShichen = 2;
  else if (hourCheck >= 5 && hourCheck < 7) finalShichen = 3;
  else if (hourCheck >= 7 && hourCheck < 9) finalShichen = 4;
  else if (hourCheck >= 9 && hourCheck < 11) finalShichen = 5;
  else if (hourCheck >= 11 && hourCheck < 13) finalShichen = 6;
  else if (hourCheck >= 13 && hourCheck < 15) finalShichen = 7;
  else if (hourCheck >= 15 && hourCheck < 17) finalShichen = 8;
  else if (hourCheck >= 17 && hourCheck < 19) finalShichen = 9;
  else if (hourCheck >= 19 && hourCheck < 21) finalShichen = 10;
  else if (hourCheck >= 21 && hourCheck < 23) finalShichen = 11;

  if (finalShichen !== shichenIdx) {
    warnings.push(`真太阳时校正：选择${SHICHEN_NAMES[shichenIdx]}→实际${SHICHEN_NAMES[finalShichen]}`);
  }

  // ---- Day Pillar (with 23:00 boundary) ----
  let dayGZIdx;
  // If shichen is 子时 (0) and hour likely >= 23, use next day
  // For simplicity, use the selected shichen - if 子时 selected, day may be next day
  dayGZIdx = getDayGZIndex(year, month, day);

  // ---- Year Pillar ----
  // Check if before 立春
  let solarYear = year;
  const lichunDOY = SOLAR_TERMS[year] ? SOLAR_TERMS[year][0] : 34; // 立春 offset
  const birthDOY = daysBetween(year, 1, 1, year, month, day);
  if (birthDOY < lichunDOY) {
    solarYear = year - 1;
  }

  const yearGZ = getYearGZ(solarYear);

  // ---- Month Pillar ----
  // Determine which solar term interval the birth date falls in
  // SOLAR_TERMS order: [立春,惊蛰,清明,立夏,芒种,小暑,立秋,白露,寒露,立冬,大雪,小寒]
  // 小寒(index 11) is Jan ~5 — it's the LAST month of the previous year's cycle
  // Must check 立春 first, then only iterate terms 0-10 (not 小寒 at index 11)
  const terms = SOLAR_TERMS[year] || [];
  let monthBranchIdx = -1;

  if (birthDOY < lichunDOY) {
    // Born between Jan 1 and 立春 → 丑月 (previous year's last month)
    monthBranchIdx = 11;
  } else {
    // Born after 立春: check terms 0 through 10 (立春 through 大雪)
    for (let i = 0; i < 11; i++) {
      const termDOY = terms[i] || (JIELING_NOMINAL[i][0] - 1) * 30 + JIELING_NOMINAL[i][1];
      if (birthDOY >= termDOY) {
        monthBranchIdx = i;
      }
    }
  }
  // Fallback (shouldn't happen for valid dates)
  if (monthBranchIdx === -1) {
    monthBranchIdx = 11;
  }

  const yearStemGroup = yearGZ.stemIdx % 5; // 甲己=0,乙庚=1,...
  const monthGZIdx = Y2M_STEM[yearStemGroup][monthBranchIdx];
  const monthStemIdx = monthGZIdx % 10;
  const monthBranchIdx2 = monthGZIdx % 12;

  // Boundary warning
  const nominalDOY = (JIELING_NOMINAL[monthBranchIdx][0] - 1) * 30 + JIELING_NOMINAL[monthBranchIdx][1];
  const actualDOY = terms[monthBranchIdx] || nominalDOY;
  if (Math.abs(birthDOY - actualDOY) <= 1) {
    warnings.push(`出生日期临近${JIELING_NAMES[monthBranchIdx]}（月柱分界），请确认月柱是否正确`);
  }
  if (Math.abs(birthDOY - lichunDOY) <= 1) {
    warnings.push("出生日期临近立春（年柱分界），请确认年柱是否正确");
  }

  // ---- Hour Pillar ----
  const dayStemGroup = (dayGZIdx % 10) % 5;
  const hourGZIdx = D2H_STEM[dayStemGroup][finalShichen];
  const hourStemIdx = hourGZIdx % 10;
  const hourBranchIdx = hourGZIdx % 12;

  // ---- Build Result ----
  const dayStemIdx = dayGZIdx % 10;
  const dayBranchIdx = dayGZIdx % 12;

  const pillars = [
    { name:"年柱", gz: GZ[yearGZ.gzIdx], stem:TG[yearGZ.stemIdx], branch:DZ[yearGZ.branchIdx], stemIdx:yearGZ.stemIdx, branchIdx:yearGZ.branchIdx, gzIdx:yearGZ.gzIdx, nayin:NAYIN[yearGZ.gzIdx] },
    { name:"月柱", gz: GZ[monthGZIdx], stem:TG[monthStemIdx], branch:DZ[monthBranchIdx2], stemIdx:monthStemIdx, branchIdx:monthBranchIdx2, gzIdx:monthGZIdx, nayin:NAYIN[monthGZIdx] },
    { name:"日柱", gz: GZ[dayGZIdx], stem:TG[dayStemIdx], branch:DZ[dayBranchIdx], stemIdx:dayStemIdx, branchIdx:dayBranchIdx, gzIdx:dayGZIdx, nayin:NAYIN[dayGZIdx] },
    { name:"时柱", gz: GZ[hourGZIdx], stem:TG[hourStemIdx], branch:DZ[hourBranchIdx], stemIdx:hourStemIdx, branchIdx:hourBranchIdx, gzIdx:hourGZIdx, nayin:NAYIN[hourGZIdx] },
  ];

  const dayMaster = pillars[2];
  const ganZao = isMale ? "乾造" : "坤造";
  const paipanStr = `${ganZao} ${pillars[0].gz} ${pillars[1].gz} ${pillars[2].gz} ${pillars[3].gz}`;

  return {
    name, gender, isMale, year, month, day, shichenIdx: finalShichen,
    longitude, ganZao, paipanStr, warnings,
    pillars, dayMaster,
    dayStemIdx, dayBranchIdx
  };
}

// ============================================================
//  SECTION 5: TEN GODS CALCULATION
// ============================================================

function calcTenGods(dayStemIdx, pillars) {
  const dayWx = WX_TG[dayStemIdx];
  const dayYy = YY_TG[dayStemIdx];
  const result = [];

  for (const p of pillars) {
    const otherWx = WX_TG[p.stemIdx];
    const otherYy = YY_TG[p.stemIdx];
    if (p.name === "日柱") {
      result.push({ name: "日主", short: "日", type: "self", pillar: p.name, stem: p.stem });
      continue;
    }
    const wxDiff = (wxIdx(otherWx) - wxIdx(dayWx) + 5) % 5;
    const sameYY = dayYy === otherYy; // 同性=偏
    let shenIdx;
    if (wxDiff === 0) shenIdx = sameYY ? 0 : 1;  // 比肩/劫财
    else if (wxDiff === 1) shenIdx = sameYY ? 2 : 3;  // 食神/伤官
    else if (wxDiff === 2) shenIdx = sameYY ? 4 : 5;  // 偏财/正财
    else if (wxDiff === 3) shenIdx = sameYY ? 7 : 6;  // 七杀/正官
    else shenIdx = sameYY ? 9 : 8;  // 偏印/正印

    result.push({
      name: SHISHEN_FULL[shenIdx],
      short: SHISHEN_SHORT[shenIdx],
      type: sameYY ? "偏" : "正",
      shenIdx,
      pillar: p.name,
      stem: p.stem
    });
  }
  return result;
}

// ============================================================
//  SECTION 6: STRENGTH ANALYSIS
// ============================================================

function calcStrength(pillars, dayStemIdx) {
  const dayWx = WX_TG[dayStemIdx];
  let score = 0;
  const details = [];

  // 1. Month pillar influence
  const monthPillar = pillars[1];
  const monthWx = WX_DZ[monthPillar.branchIdx];
  const dayWxIdx = wxIdx(dayWx);
  const monthWxIdx = wxIdx(monthWx);

  if ((monthWxIdx + 1) % 5 === dayWxIdx) {
    score += 2;
    details.push(`月令${monthPillar.branch}(${monthWx})生扶日主 +2`);
  } else if (monthWxIdx === dayWxIdx) {
    score += 2;
    details.push(`月令${monthPillar.branch}(${monthWx})与日主同五行 +2`);
  } else if ((monthWxIdx + 2) % 5 === dayWxIdx) {
    // 五行相克: (克者+2)%5 === 被克者 (木0克土2,火1克金3,土2克水4,金3克木0,水4克火1)
    score -= 2;
    details.push(`月令${monthPillar.branch}(${monthWx})克制日主 -2`);
  } else {
    details.push(`月令${monthPillar.branch}(${monthWx})对日主无直接影响 0`);
  }

  // 2. Tong gen (roots in branches)
  let tongGenCount = 0;
  for (const p of pillars) {
    const cg = DZ_CG[p.branch] || [];
    for (const hidden of cg) {
      if (WX_TG[TG.indexOf(hidden)] === dayWx) {
        tongGenCount++;
        break; // count once per pillar
      }
    }
  }
  score += tongGenCount;
  if (tongGenCount > 0) details.push(`地支通根 (同五行藏干) +${tongGenCount}`);

  // 3. Heavenly stem support from other pillars
  let stemSupport = 0;
  const supportingPillars = [];
  for (const p of pillars) {
    if (p.stemIdx === dayStemIdx) continue; // skip day master itself
    const pWx = WX_TG[p.stemIdx];
    const pWxIdx = wxIdx(pWx);
    if (pWxIdx === dayWxIdx || (pWxIdx + 1) % 5 === dayWxIdx) {
      stemSupport++;
      supportingPillars.push(p.stem);
    }
  }
  score += stemSupport;
  if (stemSupport > 0) details.push(`天干生扶(${supportingPillars.join("、")}) +${stemSupport}`);

  let level;
  if (score >= 3) level = "身强";
  else if (score <= 0) level = "身弱";
  else level = "中和";

  return { score, level, details };
}

// ============================================================
//  SECTION 7: FIVE ELEMENTS ANALYSIS
// ============================================================

function calcWuxing(pillars) {
  // Count stems and branches only (integers, total=8)
  const counts = { "木":0, "火":0, "土":0, "金":0, "水":0 };
  for (const p of pillars) {
    counts[WX_TG[p.stemIdx]]++;
    counts[WX_DZ[p.branchIdx]]++;
  }

  // Analyze
  const overWang = [];
  const missing = [];
  const balanced = [];
  for (const [wx, cnt] of Object.entries(counts)) {
    if (cnt >= 4) overWang.push({ wx, cnt });
    else if (cnt === 0) missing.push({ wx, cnt: 0 });
    else balanced.push({ wx, cnt });
  }

  return { counts, overWang, missing, balanced };
}

// ============================================================
//  SECTION 8: CHONG HE ANALYSIS
// ============================================================

function calcChongHe(pillars) {
  const heList = [];
  const chongList = [];
  const xingList = [];
  const sanHeList = [];

  // Heavenly stem combinations among pillars
  const stems = pillars.map((p,i) => ({stem:p.stem, pillar:p.name, idx:i}));
  for (let i = 0; i < stems.length; i++) {
    for (let j = i + 1; j < stems.length; j++) {
      const heTarget = TG_HE[stems[i].stem];
      if (heTarget === stems[j].stem) {
        heList.push({
          type: "天干五合",
          a: stems[i].pillar, b: stems[j].pillar,
          ganA: stems[i].stem, ganB: stems[j].stem,
          hua: TG_HE_HUA[stems[i].stem],
          meaning: `${stems[i].pillar}与${stems[j].pillar}天干相合，化${TG_HE_HUA[stems[i].stem]}。人际关系密切，但亦有牵绊。`
        });
      }
    }
  }

  // Earthly branch clashes
  for (let i = 0; i < pillars.length; i++) {
    for (let j = i + 1; j < pillars.length; j++) {
      if (DZ_CHONG[pillars[i].branch] === pillars[j].branch) {
        chongList.push({
          type: "地支六冲",
          a: pillars[i].name, b: pillars[j].name,
          zhiA: pillars[i].branch, zhiB: pillars[j].branch,
          meaning: `${pillars[i].name}(${pillars[i].branch})与${pillars[j].name}(${pillars[j].branch})相冲。变动、冲突、不稳定因素。`
        });
      }
    }
  }

  // Earthly branch 6-combinations
  for (let i = 0; i < pillars.length; i++) {
    for (let j = i + 1; j < pillars.length; j++) {
      if (DZ_HE[pillars[i].branch] === pillars[j].branch) {
        heList.push({
          type: "地支六合",
          a: pillars[i].name, b: pillars[j].name,
          zhiA: pillars[i].branch, zhiB: pillars[j].branch,
          meaning: `${pillars[i].name}与${pillars[j].name}地支相合。和谐共处，相互吸引。`
        });
      }
    }
  }

  // Three combinations
  for (const sh of DZ_SANHE) {
    const found = [];
    for (const p of pillars) {
      if (sh.zhi.includes(p.branch)) found.push(p.name);
    }
    if (found.length >= 2) {
      sanHeList.push({
        zhi: sh.zhi.join(""),
        hua: sh.hua,
        found,
        meaning: `地支${found.join("、")}形成${sh.hua}局之力。力量集中于${sh.hua}方向。`
      });
    }
  }

  // Xing (punishment)
  for (let i = 0; i < pillars.length; i++) {
    const xingTargets = DZ_XING[pillars[i].branch] || [];
    for (let j = i + 1; j < pillars.length; j++) {
      if (xingTargets.includes(pillars[j].branch)) {
        xingList.push({
          a: pillars[i].name, b: pillars[j].name,
          zhiA: pillars[i].branch, zhiB: pillars[j].branch,
          meaning: `${pillars[i].name}(${pillars[i].branch})与${pillars[j].name}(${pillars[j].branch})相刑。暗中不利，需防范小人或健康问题。`
        });
      }
    }
  }

  return { heList, chongList, xingList, sanHeList };
}

// ============================================================
//  SECTION 9: DAYUN (LUCK PILLARS) CALCULATION
// ============================================================

function calcDayun(gender, year, month, day, yearStemIdx, monthGZIdx) {
  const isMale = gender === 'male';
  const isYangYear = YY_TG[yearStemIdx] === 1;
  const forward = (isMale && isYangYear) || (!isMale && !isYangYear);

  // Calculate starting age
  const terms = SOLAR_TERMS[year] || [];
  const birthDOY = daysBetween(year, 1, 1, year, month, day);

  // Find previous and next jie
  let nextJieDOY = 999, prevJieDOY = -1;
  for (const tDOY of terms) {
    if (tDOY > birthDOY && tDOY < nextJieDOY) nextJieDOY = tDOY;
    if (tDOY <= birthDOY && tDOY > prevJieDOY) prevJieDOY = tDOY;
  }
  if (nextJieDOY === 999) nextJieDOY = birthDOY + 15;
  if (prevJieDOY === -1) prevJieDOY = birthDOY - 15;

  const daysToJie = forward ? (nextJieDOY - birthDOY) : (birthDOY - prevJieDOY);
  const startAge = Math.max(1, Math.round(daysToJie / 3));

  // Generate 8 luck pillars
  const luckPillars = [];
  for (let i = 0; i < 8; i++) {
    const offset = forward ? (i + 1) : -(i + 1);
    const luckGZIdx = ((monthGZIdx + offset) % 60 + 60) % 60;
    const ageStart = startAge + i * 10;
    luckPillars.push({
      gz: GZ[luckGZIdx],
      stem: TG[luckGZIdx % 10],
      branch: DZ[luckGZIdx % 12],
      stemIdx: luckGZIdx % 10,
      branchIdx: luckGZIdx % 12,
      startAge: ageStart,
      endAge: ageStart + 9,
      range: `${ageStart}-${ageStart + 9}岁`
    });
  }

  // Current year luck pillar
  const currentYear = new Date().getFullYear();
  const age = currentYear - year;
  let currentDayun = luckPillars[0];
  for (const lp of luckPillars) {
    if (age >= lp.startAge && age <= lp.endAge) currentDayun = lp;
  }

  // Current liunian (annual pillar)
  const liunianGZ = getYearGZ(currentYear);
  const liunianIdx = liunianGZ.gzIdx;

  // Future 5 years
  const futureYears = [];
  for (let i = 1; i <= 5; i++) {
    const fy = currentYear + i;
    const fygz = getYearGZ(fy);
    futureYears.push({ year: fy, gz: GZ[fygz.gzIdx], stem: fygz.stem, branch: fygz.branch });
  }

  return { forward, startAge, luckPillars, currentDayun, currentYear, liunianGZ, currentLiunian: GZ[liunianIdx], futureYears };
}

// ============================================================
//  SECTION 9b: LUCK PILLAR IMPACT ANALYSIS
// ============================================================

function analyzeLuckPillar(result, luckGZ, label) {
  const dayStemIdx = result.dayStemIdx;
  const dayWx = WX_TG[dayStemIdx];
  const spouseBranch = result.pillars[2].branch;
  const luckWx = WX_TG[luckGZ.stemIdx];
  const wxDiff = (wxIdx(luckWx) - wxIdx(dayWx) + 5) % 5;
  const sameYY = YY_TG[dayStemIdx] === YY_TG[luckGZ.stemIdx];
  let tgIdx;
  if (wxDiff === 0) tgIdx = sameYY ? 0 : 1;
  else if (wxDiff === 1) tgIdx = sameYY ? 2 : 3;
  else if (wxDiff === 2) tgIdx = sameYY ? 4 : 5;
  else if (wxDiff === 3) tgIdx = sameYY ? 7 : 6;
  else tgIdx = sameYY ? 9 : 8;
  const tgName = SHISHEN_FULL[tgIdx];
  const overWang = result.wuxing.overWang.map(o => o.wx);
  const missing = result.wuxing.missing.map(m => m.wx);
  const wxDir = { '木':'东方','火':'南方','土':'中部/本地','金':'西方','水':'北方' };
  const wxColor = { '木':'绿色/青色','火':'红色/紫色','土':'黄色/棕色','金':'白色/金色','水':'黑色/蓝色' };

  // Career
  let career = { level:'平', text:'' };
  const cGood = ['正官','正印','正财','食神'], cBad = ['七杀','偏印','伤官','劫财'];
  if (cGood.includes(tgName)) { career.level='吉'; career.text=`${tgName}运，${tgName==='正官'?'职权提升、管理有序':tgName==='正印'?'贵人扶持、学识资历见长':tgName==='正财'?'稳定发展、正途收益可观':'技艺精进、创意发挥得宜'}`; }
  else if (cBad.includes(tgName)) { career.level='凶'; career.text=`${tgName}运，${tgName==='七杀'?'高压竞争、宜守不宜攻':tgName==='偏印'?'多学少成、避免徒劳奔波':tgName==='伤官'?'锋芒毕露、注意人际关系':'竞争激烈、防小人夺利'}`; }
  else { career.text=`${tgName}运，事业平稳发展，需主动进取`; }
  if (DZ_CHONG[luckGZ.branch] === result.pillars[2].branch) { career.level = career.level==='吉'?'平':'凶'; career.text += '；日柱逢冲，事业变动较大'; }

  // Marriage
  let marriage = { level:'平', text:'' };
  if (DZ_CHONG[luckGZ.branch] === spouseBranch) { marriage.level='凶'; marriage.text=`大运冲夫妻宫(${spouseBranch})，感情波动，注意沟通包容`; }
  else if (DZ_HE[luckGZ.branch] === spouseBranch) { marriage.level='吉'; marriage.text=`大运合夫妻宫(${spouseBranch})，感情和谐，缘分加深`; }
  else if (luckGZ.branch === spouseBranch) { marriage.level='吉'; marriage.text='大运临夫妻宫，婚姻受关注，适合作出婚育决策'; }
  else if (TG_HE[luckGZ.stem] === result.dayMaster.stem) { marriage.level='吉'; marriage.text=`大运天干合日主，人缘佳，感情机遇增多`; }
  else { marriage.text='大运对婚姻宫无直接冲合，感情生活较平稳'; }

  // Wealth
  let wealth = { level:'平', text:'' };
  if (tgName === '正财') { wealth.level='吉'; wealth.text='正财运旺，稳定收入增长，适合储蓄和长期投资'; }
  else if (tgName === '偏财') { wealth.level='吉'; wealth.text='偏财运旺，投资获利机会多，但需控制风险，见好就收'; }
  else if (tgName === '食神') { wealth.level='吉'; wealth.text='食神生财，技术/创意带来财富，生意平顺'; }
  else if (tgName === '劫财') { wealth.level='凶'; wealth.text='劫财运，花销增大，需防破财、借贷担保风险'; }
  else if (tgName === '七杀') { wealth.level='凶'; wealth.text='七杀运，因压力/竞争导致财务波动，谨慎投资'; }
  else if (tgName === '偏印') { wealth.level='凶'; wealth.text='偏印运，徒劳奔波，财运不济，宜守不宜攻'; }
  else if (tgName === '比肩') { wealth.text='比肩运，合作分利，财富缓慢积累'; }
  else if (tgName === '正官') { wealth.text='正官运，财运依附事业，稳健发展为主'; }
  else if (tgName === '正印') { wealth.text='正印运，贵人带来机会，重名望轻利益'; }
  else { wealth.text='伤官运，才华变现但波动大，见好就收'; }

  // Health
  let health = { level:'平', text:'' };
  if (overWang.includes(luckWx)) {
    health.level='凶';
    health.text=`加重命局过旺的${luckWx}，注意${luckWx==='木'?'肝胆/情绪':luckWx==='火'?'心血管/炎症':luckWx==='土'?'脾胃/消化':luckWx==='金'?'肺/呼吸道':'肾/泌尿'}系统`;
  } else if (missing.includes(luckWx)) {
    health.level='吉'; health.text=`补足命局缺失的${luckWx}，身体状况改善`;
  } else if (DZ_CHONG[luckGZ.branch] === result.pillars[2].branch) {
    health.level='凶'; health.text='大运与日柱相冲，身体易有波动，注意劳逸结合';
  } else { health.text='无直接冲击，健康状况较稳定'; }

  // Benefactor
  const benefactor = {
    direction: wxDir[luckWx] || '中部',
    color: wxColor[luckWx] || '黄色',
    text: `五行属${luckWx}，贵人宜向${wxDir[luckWx]||'中部'}发展，宜着${wxColor[luckWx]||'黄色'}衣物`
  };

  return { label, tgName, career, marriage, wealth, health, benefactor };
}

function analyzeLiunian(result, yearGZ) {
  const dayStemIdx = result.dayStemIdx;
  const dayWx = WX_TG[dayStemIdx];
  const yrWx = WX_TG[yearGZ.stemIdx];
  const wxDiff = (wxIdx(yrWx) - wxIdx(dayWx) + 5) % 5;
  const sameYY = YY_TG[dayStemIdx] === YY_TG[yearGZ.stemIdx];
  let tgIdx;
  if (wxDiff === 0) tgIdx = sameYY ? 0 : 1;
  else if (wxDiff === 1) tgIdx = sameYY ? 2 : 3;
  else if (wxDiff === 2) tgIdx = sameYY ? 4 : 5;
  else if (wxDiff === 3) tgIdx = sameYY ? 7 : 6;
  else tgIdx = sameYY ? 9 : 8;

  let overall = '平';
  if ([5,8,2,6].includes(tgIdx)) overall = '吉'; // 正财,正印,食神,正官
  if ([7,9,1,3].includes(tgIdx)) overall = '凶'; // 七杀,偏印,劫财,伤官
  if (DZ_CHONG[yearGZ.branch] === result.pillars[2].branch) overall = overall==='吉'?'平':'凶';
  if (TG_HE[yearGZ.stem] === result.dayMaster.stem) overall = overall==='凶'?'平':'吉';

  const wxDir = { '木':'东方','火':'南方','土':'中部/本地','金':'西方','水':'北方' };
  const wxColor = { '木':'绿色/青色','火':'红色/紫色','土':'黄色/棕色','金':'白色/金色','水':'黑色/蓝色' };
  const yrBranchWx = WX_DZ[yearGZ.branchIdx];
  const overWang = result.wuxing.overWang.map(o => o.wx);
  const missing = result.wuxing.missing.map(m => m.wx);

  // 宜 (favorable actions)
  let yi = [], ji = [];
  if (tgIdx === 5) { yi.push('投资理财','求职加薪','签署合同','置产置业'); ji.push('投机赌博','冲动消费'); }
  else if (tgIdx === 4) { yi.push('短期投资','副业创收','商业谈判'); ji.push('大额投资','长期借贷'); }
  else if (tgIdx === 6) { yi.push('求职晋升','项目启动','婚恋嫁娶','社交拓展'); ji.push('顶撞权威','违规操作'); }
  else if (tgIdx === 8) { yi.push('学习进修','考试考证','拜访长辈','寻求建议'); ji.push('独断专行','拒绝帮助'); }
  else if (tgIdx === 2) { yi.push('创意工作','技能提升','休闲旅游','聚会交友'); ji.push('过度劳累','冒险行为'); }
  else if (tgIdx === 0) { yi.push('合作合伙','团队项目','结交朋友'); ji.push('单打独斗','重大决策'); }
  else if (tgIdx === 7) { yi.push('低调行事','巩固防守','健康检查'); ji.push('扩张冒进','冲突对抗','重大投资'); }
  else if (tgIdx === 9) { yi.push('钻研技术','考证进修'); ji.push('创业开店','大举投资','跳槽换岗'); }
  else if (tgIdx === 1) { yi.push('维护人脉','控制开支'); ji.push('借贷担保','大额消费','合伙投资'); }
  else if (tgIdx === 3) { yi.push('展示才华','艺术创作','学习新知'); ji.push('直言顶撞','离职跳槽','法律纠纷'); }

  // 五行方位宜忌
  let yiDir = [], jiDir = [];
  for (const [wx, dir] of Object.entries(wxDir)) {
    if (missing.includes(wx)) { yiDir.push(`${dir}(${wx})`); }
    if (overWang.includes(wx)) { jiDir.push(`${dir}(${wx})`); }
  }
  if (yiDir.length === 0) yiDir.push(`${wxDir[yrWx]}(${yrWx})`);
  if (jiDir.length === 0) jiDir.push(`${wxDir[WX_DZ[DZ.indexOf(DZ_CHONG[yearGZ.branch]||'子')]]}`);

  // 改运建议
  let gaiyun = [];
  if (missing.length > 0) gaiyun.push(`多接触${missing[0]}能量：${wxColor[missing[0]]}衣物、${wxDir[missing[0]]}方位活动`);
  if (overWang.length > 0) gaiyun.push(`避免${overWang[0]}过旺：减少${wxColor[overWang[0]]}、远离${wxDir[overWang[0]]}`);
  if (overall === '凶') gaiyun.push('佩戴与日主五行相生的饰品，多亲近印星所代表的长辈贵人');
  if (overall === '吉') gaiyun.push('把握时机积极进取，但保持谦虚谨慎，居安思危');
  if (gaiyun.length === 0) gaiyun.push('保持现状稳步前行，多做善事积累福报');

  return {
    tenGod: SHISHEN_FULL[tgIdx],
    overall,
    yi: yi.length > 0 ? yi : ['按部就班','保持现状'],
    ji: ji.length > 0 ? ji : ['重大决策','冒险行为'],
    yiDir: yiDir.join('、'),
    jiDir: jiDir.join('、'),
    gaiyun: gaiyun.join('；'),
    benefactorDir: wxDir[yrBranchWx] || '中部',
    benefactorColor: wxColor[yrBranchWx] || '黄色'
  };
}

// ============================================================
//  SECTION 10: SHENSHA (STAR SPIRITS)
// ============================================================

function calcShensha(pillars, dayStemIdx) {
  const result = [];
  const yearBranch = pillars[0].branchIdx;
  const monthBranch = pillars[1].branchIdx;
  const dayBranch = pillars[2].branchIdx;
  const dayStem = dayStemIdx;

  // Helper: 三合局分组 0=申子辰 1=巳酉丑 2=寅午戌 3=亥卯未
  function group(bi) {
    if (bi === 8 || bi === 0 || bi === 4) return 0;
    if (bi === 5 || bi === 9 || bi === 1) return 1;
    if (bi === 2 || bi === 6 || bi === 10) return 2;
    return 3;
  }
  // 三合局对应的: [桃花, 驿马, 华盖, 劫煞, 灾煞, 将星]
  const SH_TABLE = [
    [9, 2, 4, 5, 6, 0],  // 申子辰 → 酉寅辰巳午子
    [6, 11, 1, 2, 3, 9], // 巳酉丑 → 午亥丑寅卯酉
    [3, 8, 10, 11, 0, 6], // 寅午戌 → 卯申戌亥子午
    [0, 5, 7, 8, 9, 3],  // 亥卯未 → 子巳未申酉卯
  ];

  // 1. 桃花 — 年支/日支 (PDF: 感情/名望/声誉/知名度)
  const thDay = SH_TABLE[group(dayBranch)][0], thYear = SH_TABLE[group(yearBranch)][0];
  for (const p of pillars) {
    if (p.branchIdx === thDay) result.push({ name:"桃花", pillar:p.name, meaning:"人缘好，异性缘佳，有知名度" + (p.name==="日柱"?"（日柱桃花：自身魅力强）":"") });
    else if (p.branchIdx === thYear && thYear !== thDay) result.push({ name:"桃花", pillar:p.name, meaning:"(年支桃花) 童年/远方有知名度" });
  }

  // 2. 驿马 — 年支/日支 (PDF: 奔波远行多动)
  const ymDay = SH_TABLE[group(dayBranch)][1], ymYear = SH_TABLE[group(yearBranch)][1];
  for (const p of pillars) {
    if (p.branchIdx === ymDay) result.push({ name:"驿马", pillar:p.name, meaning:"奔波远行，好动不喜静" + (p.name==="月柱"?"（月柱驿马：一生奔波）":"") });
    else if (p.branchIdx === ymYear && ymYear !== ymDay) result.push({ name:"驿马", pillar:p.name, meaning:"(年支驿马) 远行发展" });
  }

  // 3. 华盖 — 日支 (PDF: 日支/月支才算真正命带华盖)
  const hgDay = SH_TABLE[group(dayBranch)][2];
  for (const p of pillars) {
    if (p.branchIdx === hgDay) {
      const isCore = (p.name === "日柱" || p.name === "月柱");
      result.push({ name:"华盖", pillar:p.name, meaning: isCore ? "真正命带华盖：聪慧孤高，喜神秘文化，研究深入" : "华盖（非定性）：" + p.name + "领域较曲折" });
    }
  }

  // 4. 劫煞 — 年支/日支 (PDF: 阻滞/障碍/小人)
  const jsDay = SH_TABLE[group(dayBranch)][3], jsYear = SH_TABLE[group(yearBranch)][3];
  for (const p of pillars) {
    if (p.branchIdx === jsDay) result.push({ name:"劫煞", pillar:p.name, meaning:"日支劫煞：自身/婚姻家庭方面的障碍与小人" });
    else if (p.branchIdx === jsYear && jsYear !== jsDay) result.push({ name:"劫煞", pillar:p.name, meaning:"年支劫煞：对外关系/人脉中的障碍" });
  }

  // 5. 灾煞 — 年支/日支 (PDF: 短期突发变故)
  const zsDay = SH_TABLE[group(dayBranch)][4], zsYear = SH_TABLE[group(yearBranch)][4];
  for (const p of pillars) {
    if (p.branchIdx === zsDay) result.push({ name:"灾煞", pillar:p.name, meaning:"日支灾煞：自身/家庭的短期突发障碍" });
    else if (p.branchIdx === zsYear && zsYear !== zsDay) result.push({ name:"灾煞", pillar:p.name, meaning:"年支灾煞：对外关系的短期突发变故" });
  }

  // 6. 将星 — 日支 (PDF: 统领/主导/权威)
  const jxDay = SH_TABLE[group(dayBranch)][5];
  for (const p of pillars) {
    if (p.branchIdx === jxDay) result.push({ name:"将星", pillar:p.name, meaning: p.name==="日柱" ? "领导才能，独当一面" : p.name + "有统领/主导特征" });
  }

  // 7. 天乙贵人 — 日干
  const tygrMap = {0:[1,7], 1:[0,8], 2:[11,9], 3:[10,6], 4:[1,7], 5:[0,8], 6:[1,7], 7:[10,6], 8:[3,5], 9:[3,5]};
  for (const p of pillars) {
    if ((tygrMap[dayStem]||[]).includes(p.branchIdx)) result.push({ name:"天乙贵人", pillar:p.name, meaning:"最大吉神，逢凶化吉，得贵人相助" });
  }

  // 8. 文昌 — 日干 (PDF: 技能/技术/实操能力)
  const wcMap = {0:5, 1:6, 2:8, 3:9, 4:8, 5:9, 6:11, 7:0, 8:2, 9:2};
  for (const p of pillars) {
    if (p.branchIdx === wcMap[dayStem]) result.push({ name:"文昌星", pillar:p.name, meaning:"心灵手巧，技能突出，善于总结与出谋划策" });
  }

  // 9. 羊刃 — 日干帝旺位 (PDF: 刚强/冲动)
  const yrMap = {0:3, 1:2, 2:6, 3:5, 4:6, 5:5, 6:9, 7:8, 8:0, 9:11};
  for (const p of pillars) {
    if (p.branchIdx === yrMap[dayStem]) result.push({ name:"羊刃", pillar:p.name, meaning:"性格刚强，行动力强，但易冲动" + (p.name==="日柱"?"（日柱羊刃：配偶性格刚烈或自身易受伤）":"") });
  }

  // 10. 学堂 — 日干长生位 (PDF: 学习/求知)
  const xtMap = {0:11, 1:6, 2:2, 3:9, 4:2, 5:9, 6:5, 7:0, 8:8, 9:3}; // 甲亥乙午丙寅丁酉戊寅己酉庚巳辛子壬申癸卯
  for (const p of pillars) {
    if (p.branchIdx === xtMap[dayStem]) result.push({ name:"学堂", pillar:p.name, meaning: (p.name==="月柱"||p.name==="日柱") ? "一生好学，视学习为乐趣" : p.name + "有求知学习缘分" });
  }

  // 11. 禄神 — 日干临官位 (PDF: 食禄/福气/稳定收入)
  const lsMap = {0:2, 1:3, 2:5, 3:6, 4:5, 5:6, 6:8, 7:9, 8:11, 9:0}; // 甲寅乙卯丙巳丁午戊巳己午庚申辛酉壬亥癸子
  for (const p of pillars) {
    if (p.branchIdx === lsMap[dayStem]) result.push({ name:"禄神", pillar:p.name, meaning:"食禄之福，一生衣食无忧，经济基础稳固" });
  }

  // 12. 天喜 — 月支 (PDF: 喜庆/欢愉/娱乐)
  // 寅卯辰→戌(10), 巳午未→丑(1), 申酉戌→辰(4), 亥子丑→未(7)
  const txMap = {2:10, 3:10, 4:10, 5:1, 6:1, 7:1, 8:4, 9:4, 10:4, 11:7, 0:7, 1:7};
  for (const p of pillars) {
    if (p.branchIdx === txMap[monthBranch]) result.push({ name:"天喜", pillar:p.name, meaning:"多逢喜事（婚育升迁开张），与娱乐喜庆有缘" + (p.name==="日柱"?"（日柱天喜：喜事最直接）":"") });
  }

  // 13. 天医 — 月支推上一位 (PDF: 医学缘分/健康)
  const tyBranch = (monthBranch + 11) % 12; // 月令推上一位
  for (const p of pillars) {
    if (p.branchIdx === tyBranch) result.push({ name:"天医", pillar:p.name, meaning:"与医学有缘，或需注意身体健康" + (p.name==="日柱"?"（日柱天医：医药缘分直接）":"") });
  }

  return result;
}

// ============================================================
//  SECTION 11: PATTERN DETERMINATION
// ============================================================

function calcPattern(tenGods, strength) {
  const shenSet = new Set(tenGods.map(t => t.name));
  const shenCount = {};
  tenGods.forEach(t => { shenCount[t.name] = (shenCount[t.name] || 0) + 1; });

  const matches = [];

  for (const pt of PATTERN_TEMPLATES) {
    let match = false;
    const cond = pt.cond;
    if (cond.includes("+")) {
      const parts = cond.split("+").map(s => s.trim());
      match = parts.every(p => shenSet.has(p) || (p.includes("/") && p.split("/").some(x => shenSet.has(x.trim()))));
    } else if (cond.includes("/")) {
      match = cond.split("/").some(x => shenSet.has(x.trim()));
    }
    if (match) matches.push(pt);
  }

  // If no classic pattern, describe based on most frequent ten god
  if (matches.length === 0) {
    const sorted = Object.entries(shenCount).sort((a,b) => b[1]-a[1]);
    const dominant = sorted[0] ? sorted[0][0] : "日主";
    matches.push({
      name: `${dominant}格`,
      cond: `${dominant}主导`,
      desc: `命局以${dominant}为主导，${dominant === "正官" ? "事业心强、重视规则" : dominant === "七杀" ? "权威果断、竞争意识强" : dominant === "正财" ? "务实重利、稳定进取" : dominant === "偏财" ? "灵活善变、投资意识强" : dominant === "正印" ? "仁慈善良、学识渊博" : dominant === "偏印" ? "思维独特、技艺精湛" : dominant === "食神" ? "温厚善良、享受生活" : dominant === "伤官" ? "才华横溢、不拘一格" : dominant === "比肩" ? "独立自强、重友情" : "竞争进取、善交际"}。`,
      careers: "根据主导十神选择适合的行业方向"
    });
  }

  return { matches, shenCount };
}

// ============================================================
//  SECTION 12: COMPATIBILITY ENGINE
// ============================================================

function calcCompatibility(resultA, resultB, relType) {
  const scores = {};
  const highlights = [];
  const details = [];

  // 1. Wuxing complementarity (30%)
  const wxA = resultA.wuxing.counts;
  const wxB = resultB.wuxing.counts;
  let wxScore = 50;
  const wxOrder = ["木","火","土","金","水"];
  // Check if missing elements in A are supplemented by B
  for (const wx of wxOrder) {
    if (wxA[wx] <= 0.5 && wxB[wx] >= 2) { wxScore += 12; highlights.push(`${resultA.name}缺${wx}，${resultB.name}${wx}旺，五行互补好`); }
    if (wxB[wx] <= 0.5 && wxA[wx] >= 2) { wxScore += 12; highlights.push(`${resultB.name}缺${wx}，${resultA.name}${wx}旺，五行互补好`); }
  }
  // Deduct if same over-strong element
  for (const wx of wxOrder) {
    if (wxA[wx] >= 4 && wxB[wx] >= 4) { wxScore -= 10; highlights.push(`双方${wx}皆过旺，同气相争，需调和`); }
  }
  scores.wuxing = Math.min(100, Math.max(0, wxScore));

  // 2. Chong-he harmony (30%)
  let chScore = 50;
  // Check day pillar interaction
  const dayA = resultA.pillars[2], dayB = resultB.pillars[2];
  if (TG_HE[dayA.stem] === dayB.stem) {
    chScore += 20;
    highlights.push(`日干${dayA.stem}与${dayB.stem}天干五合，缘分深厚`);
    details.push(`日干相合化${TG_HE_HUA[dayA.stem]}，两人心意相通，相互吸引`);
  }
  if (DZ_CHONG[dayA.branch] === dayB.branch) {
    chScore -= 20;
    highlights.push(`日支${dayA.branch}与${dayB.branch}相冲，夫妻宫/自我宫受冲`);
    details.push("日支相冲，代表核心自我冲突，需更多磨合包容");
  }
  if (DZ_HE[dayA.branch] === dayB.branch) {
    chScore += 15;
    highlights.push(`日支${dayA.branch}与${dayB.branch}地支六合，和谐共处`);
    details.push("日支六合，两人本质相吸，相处融洽");
  }

  // Check year pillar (ancestry)
  const yearA = resultA.pillars[0], yearB = resultB.pillars[0];
  if (DZ_CHONG[yearA.branch] === yearB.branch) {
    chScore -= 8;
    highlights.push("年柱地支相冲，家族背景差异大");
  }

  scores.chongHe = Math.min(100, Math.max(0, chScore));

  // 3. Ten God mutual influence (25%)
  let tgScore = 50;
  // Check if A's ten gods are beneficial to B
  const tgA = resultA.tenGods, tgB = resultB.tenGods;

  // RelType specific checks
  if (relType === "夫妻") {
    // Check spouse palace stability
    const spousePalaceA = resultA.pillars[2].branch; // 日支 = 夫妻宫
    const spousePalaceB = resultB.pillars[2].branch;
    // Check for peach blossom in spouse palace
    const chongA = resultA.chongHe.chongList.filter(c => c.a==="日柱" || c.b==="日柱");
    const chongB = resultB.chongHe.chongList.filter(c => c.a==="日柱" || c.b==="日柱");
    if (chongA.length > 0) { tgScore -= 10; highlights.push(`${resultA.name}日柱逢冲，婚姻宫不稳`); }
    if (chongB.length > 0) { tgScore -= 10; highlights.push(`${resultB.name}日柱逢冲，婚姻宫不稳`); }
    details.push("夫妻关系重点看日柱互动、配偶宫稳定性和五行互补");
  } else if (relType === "朋友") {
    // Check 比肩/劫财 mutual
    const hasBijieA = tgA.some(t => t.name === "比肩" || t.name === "劫财");
    const hasBijieB = tgB.some(t => t.name === "比肩" || t.name === "劫财");
    if (hasBijieA && hasBijieB) { tgScore += 10; details.push("双方比劫呼应，朋友间相互扶持"); }
  } else if (relType === "同事") {
    // Check career-related gods
    const hasCareerA = tgA.some(t => t.name === "正官" || t.name === "正财" || t.name === "食神");
    const hasCareerB = tgB.some(t => t.name === "正官" || t.name === "正财" || t.name === "食神");
    if (hasCareerA && hasCareerB) { tgScore += 10; details.push("双方事业心相近，合作共赢"); }
  } else if (relType === "领导") {
    // Check authority dynamic
    const hasGuanA = tgA.some(t => t.name === "正官" || t.name === "七杀");
    const hasYinB = tgB.some(t => t.name === "正印" || t.name === "偏印");
    if (hasGuanA && hasYinB) { tgScore += 10; details.push("一方官杀威严+另一方印星包容，领导关系协调"); }
  }

  scores.tenGod = Math.min(100, Math.max(0, tgScore));

  // 4. Shensha match (15%)
  let ssScore = 50;
  const shenshaA = new Set(resultA.shensha.map(s => s.name));
  const shenshaB = new Set(resultB.shensha.map(s => s.name));
  const commonSS = [...shenshaA].filter(s => shenshaB.has(s));
  if (commonSS.length > 0) {
    ssScore += commonSS.length * 5;
    highlights.push(`双方共有的神煞：${commonSS.join("、")}`);
  }
  scores.shensha = Math.min(100, Math.max(0, ssScore));

  // Weighted total
  const overall = Math.round(
    scores.wuxing * 0.30 +
    scores.chongHe * 0.30 +
    scores.tenGod * 0.25 +
    scores.shensha * 0.15
  );

  let level;
  if (overall >= 80) level = "极佳配合";
  else if (overall >= 70) level = "良好配合";
  else if (overall >= 60) level = "一般配合";
  else if (overall >= 50) level = "需磨合";
  else level = "挑战较大";

  return { overall, level, scores, highlights, details };
}

// ============================================================
//  SECTION 13: INTERPRETATION GENERATION
// ============================================================

function generateInterpretation(result) {
  const interp = {};

  // Strength interpretation
  const s = result.strength;
  if (s.level === "身强") {
    interp.strength = `日主${s.level}（得分${s.score}），命主精力充沛、行动力强。喜克、泄、耗来平衡，宜主动开拓事业，但需注意不过度自信导致刚愎自用。`;
  } else if (s.level === "身弱") {
    interp.strength = `日主${s.level}（得分${s.score}），命主思虑周全、处事谨慎。喜生扶、比助来增强，宜借助贵人、学识之力，合作共赢。`;
  } else {
    interp.strength = `日主${s.level}（得分${s.score}），命局平衡，适应力强。可根据大运流年的变化灵活调整策略。`;
  }

  // Wuxing interpretation — 东方代码启示录"少利多弊"原则
  const wx = result.wuxing;
  const wxDetails = [];
  // 过旺 → 劣势/需防范
  const wxOverInfo = {
    "木": "固执，创意不足，肝胆需注意", "火": "暴躁，不善发扬宣传，心血管需注意",
    "土": "不善转型，缺乏规矩意识，脾胃需注意", "金": "犹豫欠果断，执行能力不强，肺/大肠需注意",
    "水": "创意能力不足，不善忍耐，肾/膀胱需注意"
  };
  for (const ow of wx.overWang) {
    wxDetails.push(ow.wx + '过旺（' + ow.cnt + '个）→不利：' + (wxOverInfo[ow.wx]||ow.wx+'过旺') + '。应防范过多' + ow.wx + '带来的弊端。');
  }
  // 缺失 → 优势/禀赋（少利多弊原则）
  const wxMissInfo = {
    "木": "仁厚理性，擅长细节管理；大局观强；偏财型性格",
    "火": "善于沟通，擅长人际社交；人脉协调能力强；七杀型性格",
    "土": "善于转型，擅长订立规矩；诚信意识强；枭神型性格",
    "金": "为人爽朗，大局观较强；果断敢为；劫财型性格",
    "水": "性格善忍耐；有收藏眼光；创意丰富；伤官型性格"
  };
  const wxDirAdvice = {"木":"东方/绿色/植物/教育","火":"南方/红色/阳光/传媒","土":"中部/黄色/陶瓷/地产","金":"西方/白色/金属/金融","水":"北方/黑色/水流/贸易"};
  for (const ms of wx.missing) {
    var dir = wxDirAdvice[ms.wx] || ms.wx;
    wxDetails.push(ms.wx + '缺失（0个）→优势：' + (wxMissInfo[ms.wx]||ms.wx+'缺失为利好') + '。' + ms.wx + '方向为天赋所在，可主动向' + dir + '领域发展。');
  }
  // 平衡的五行
  for (const bl of wx.balanced) {
    wxDetails.push(bl.wx + '平衡（' + bl.cnt + '个），禀赋适中，可根据大运流年调整倾向。');
  }
  interp.wuxing = wxDetails.join("<br>");

  // Pattern interpretation
  const pt = result.pattern;
  if (pt.matches.length > 0) {
    interp.pattern = `格局定性：${pt.matches[0].name}。${pt.matches[0].desc} 适合方向：${pt.matches[0].careers || "综合发展"}。`;
  }

  // Chong-he interpretation
  const ch = result.chongHe;
  if (ch.chongList.length > 0) {
    interp.chongHeWarn = ch.chongList.map(c => c.meaning).join(" ");
  }

  // Dayun interpretation
  const dy = result.dayun;
  interp.dayun = `当前正行${dy.currentDayun.gz}大运（${dy.currentDayun.range}），大运天干${dy.currentDayun.stem}、地支${dy.currentDayun.branch}。`;
  interp.liunian = `流年${dy.currentLiunian}（${dy.currentYear}年），流年天干${TG[dy.liunianGZ.stemIdx]}、地支${DZ[dy.liunianGZ.branchIdx]}。流年对命局的冲合生克，决定了当年吉凶事件的方向。`;

  // Health
  const dayWx = wxOf(result.dayMaster.stem);
  interp.health = `日主五行属${dayWx}，${dayWx === "木" ? "肝胆为薄弱环节，注意情绪调节、规律作息" : dayWx === "火" ? "心血管为薄弱环节，注意情绪激动、夏季防暑" : dayWx === "土" ? "脾胃为薄弱环节，注意饮食规律、避免暴饮暴食" : dayWx === "金" ? "肺和大肠为薄弱环节，注意呼吸道、戒烟限酒" : "肾和膀胱为薄弱环节，注意腰部保养、避免过劳"}。`;

  // Career
  const dayShen = result.tenGods.find(t => t.pillar === "日柱");
  interp.career = `事业方面，${result.strength.level === "身强" ? "适合开拓性、竞争性强的工作，可独立创业或担任领导者角色" : "适合团队合作、需要专业知识积累的工作，在稳定环境中逐步发展"}。${result.pattern.matches.length > 0 ? result.pattern.matches[0].desc : ""}`;

  // Marriage
  const spousePalace = result.pillars[2].branch;
  const spouseChong = result.chongHe.chongList.filter(c => c.a === "日柱" || c.b === "日柱");
  if (spouseChong.length > 0) {
    interp.marriage = `婚姻宫（日支${spousePalace}）逢冲，感情生活波动较多。建议晚婚、选择异地伴侣，或在婚姻中保持适度独立空间。`;
  } else {
    interp.marriage = `婚姻宫（日支${spousePalace}）较稳定。选择与自己五行互补、日干相合的伴侣更有利于婚姻和谐。`;
  }

  // Wealth
  const hasZhengCai = result.tenGods.some(t => t.name === "正财");
  const hasPianCai = result.tenGods.some(t => t.name === "偏财");
  if (hasZhengCai && hasPianCai) {
    interp.wealth = "正偏财皆备，既适合稳健的正途收入，也具备投资获利的潜质。但需注意投资风险控制。";
  } else if (hasZhengCai) {
    interp.wealth = "正财为用，适合稳定职业收入、长期积累。不宜投机冒险。";
  } else if (hasPianCai) {
    interp.wealth = "偏财为用，适合经商、投资、副业创收。注意控制风险，见好就收。";
  } else {
    interp.wealth = "财星不显，财富需通过专业技能和长期积累获得。大运流年逢财运时把握机会。";
  }

  return interp;
}

// ============================================================
//  SECTION 14: COMPREHENSIVE ANALYSIS PIPELINE
// ============================================================

function fullAnalysis(name, gender, year, month, day, shichenIdx, longitude) {
  const result = paipan(name, gender, year, month, day, shichenIdx, longitude);
  result.tenGods = calcTenGods(result.dayStemIdx, result.pillars);
  result.strength = calcStrength(result.pillars, result.dayStemIdx);
  result.wuxing = calcWuxing(result.pillars);
  result.chongHe = calcChongHe(result.pillars);
  result.dayun = calcDayun(gender, year, month, day, result.pillars[0].stemIdx, result.pillars[1].gzIdx);
  result.shensha = calcShensha(result.pillars, result.dayStemIdx);
  result.pattern = calcPattern(result.tenGods, result.strength.level);
  result.interpretation = generateInterpretation(result);
  return result;
}

// ============================================================
//  SECTION 15: UI RENDERING
// ============================================================

function renderSingleResult(result) {
  const panel = document.getElementById('result-panel');
  const tabBar = document.getElementById('tab-bar');
  const tabContents = document.getElementById('tab-contents');

  const tabs = [
    { id:'tab-paipan', label:'📜 八字排盘', content: renderPaipan(result) },
    { id:'tab-qiangruo', label:'⚖️ 日主强弱', content: renderStrength(result) },
    { id:'tab-shishen', label:'🔟 十神格局', content: renderShishen(result) },
    { id:'tab-chonghe', label:'⚡ 冲合关系', content: renderChongHe(result) },
    { id:'tab-dayun', label:'🕐 大运流年', content: renderDayun(result) },
    { id:'tab-shensha', label:'⭐ 神煞星煞', content: renderShensha(result) },
    { id:'tab-zonghe', label:'💡 综合建议', content: renderZonghe(result) },
  ];

  tabBar.innerHTML = tabs.map((t,i) =>
    `<button class="tab-btn${i===0?' active':''}" onclick="switchTab('${t.id}', this)">${t.label}</button>`
  ).join('');


  tabContents.innerHTML = tabs.map((t,i) =>
    `<div class="tab-content${i===0?' active':''}" id="${t.id}">${t.content}</div>`
  ).join('');

  panel.classList.add('visible');
  panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function switchTab(tabId, btn) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
  document.getElementById(tabId).classList.add('active');
  if (btn) btn.classList.add('active');
}

function renderPaipan(result) {
  const p = result.pillars;
  const wx = result.wuxing.counts;
  const wxOrder = ["木","火","土","金","水"];
  const wxColors = {"木":"#5b8c5a","火":"#d94a4a","土":"#c9a84c","金":"#9b9b9b","水":"#4a90d9"};
  const wxNames = {"木":"木","火":"火","土":"土","金":"金","水":"水"};

  // Lunar birthday with Chinese formatting
  const lunar = gregToLunar ? gregToLunar(result.year, result.month, result.day) : null;
  const LUNAR_MONTHS = ['正','二','三','四','五','六','七','八','九','十','冬','腊'];
  const LUNAR_MONTHS_NUM = ['一','二','三','四','五','六','七','八','九','十','十一','十二'];
  const LUNAR_DAYS = ['','初一','初二','初三','初四','初五','初六','初七','初八','初九','初十','十一','十二','十三','十四','十五','十六','十七','十八','十九','二十','廿一','廿二','廿三','廿四','廿五','廿六','廿七','廿八','廿九','三十'];
  let lunarStr = '';
  if (lunar) {
    const lmName = LUNAR_MONTHS[lunar.lmonth - 1] || lunar.lmonth;
    const lmNum = LUNAR_MONTHS_NUM[lunar.lmonth - 1] || lunar.lmonth;
    const ldName = LUNAR_DAYS[lunar.lday] || lunar.lday;
    // Year to Chinese numerals
    const CN_NUM = ['零','一','二','三','四','五','六','七','八','九'];
    let yearCN = '';
    const yStr = String(lunar.lyear);
    for (let ci = 0; ci < yStr.length; ci++) {
      yearCN += CN_NUM[parseInt(yStr[ci])];
    }
    lunarStr = '农历 ' + yearCN + '年 ' + lmName + '月（' + lmNum + '月）' + ldName;
  }
  const yearAnimal = ZODIAC[p[0].branchIdx];
  const yearNayin = p[0].nayin;

  let html = `<div style="text-align:center;margin:20px 0">
    <div style="font-family:var(--font-heading);font-size:1.4rem;letter-spacing:4px;color:var(--cinnabar)">${result.ganZao} ${p[0].gz} ${p[1].gz} ${p[2].gz} ${p[3].gz}</div>
    <div style="margin-top:8px;font-size:0.9rem;color:var(--text-secondary)">
      ${lunarStr ? `<span style="margin-right:12px">${lunarStr}</span>` : ''}
      <span style="margin-right:12px">🐲 属${yearAnimal}</span>
      <span style="margin-right:12px">📅 ${p[0].gz}年</span>
      <span>🔮 ${yearNayin}命</span>
    </div>`;

  if (result.warnings.length > 0) {
    html += `<div style="margin-top:12px">`;
    result.warnings.forEach(w => {
      html += `<span style="display:inline-block;background:#fff3cd;color:#856404;padding:4px 12px;border-radius:12px;font-size:0.8rem;margin:2px">⚠ ${w}</span> `;
    });
    html += `</div>`;
  }
  html += `</div>`;

  // === Four Pillar Table ===
  html += `<table class="paipan-table">
    <tr><th></th>${p.map(pp => `<th>${pp.name}</th>`).join('')}</tr>
    <tr><td>天干</td>${p.map(pp => `<td><span class="pillar-name">${pp.stem}</span></td>`).join('')}</tr>
    <tr><td>地支</td>${p.map(pp => `<td><span class="pillar-name">${pp.branch}</span></td>`).join('')}</tr>
    <tr><td>纳音</td>${p.map(pp => `<td style="color:var(--text-secondary)">${pp.nayin}</td>`).join('')}</tr>
    <tr><td>十神</td>${result.tenGods.map(t => `<td><span style="font-weight:bold;color:${t.type==='self'?'var(--cinnabar)':t.type==='正'?'var(--jade)':'var(--gold)'}">${t.short}</span></td>`).join('')}</tr>
    <tr><td>正/偏</td>${result.tenGods.map(t => `<td style="font-size:0.8rem;color:var(--text-muted)">${t.type==='self'?'日主':t.type}</td>`).join('')}</tr>
    <tr><td>藏干</td>${p.map(pp => `<td style="font-size:0.8rem;color:var(--text-muted)">${(DZ_CG[pp.branch]||[]).join(' ')}</td>`).join('')}</tr>
    <tr><td>属相</td>${p.map(pp => `<td style="color:var(--text-secondary)">${ZODIAC[pp.branchIdx]}</td>`).join('')}</tr>
    <tr><td>五行</td>${p.map(pp => {
      const stemWx = WX_TG[pp.stemIdx], branchWx = WX_DZ[pp.branchIdx];
      const wc = {"木":"wuxing-wood","火":"wuxing-fire","土":"wuxing-earth","金":"wuxing-metal","水":"wuxing-water"};
      return `<td><span class="wuxing-tag ${wc[stemWx]}">${stemWx}</span> <span class="wuxing-tag ${wc[branchWx]}" style="margin-left:2px">${branchWx}</span></td>`;
    }).join('')}</tr>
  </table>`;

  // === 五行水平彩色条 ===
  html += `<div style="margin:20px 0;padding:16px;background:#fdfaf3;border-radius:8px;border:1px solid var(--border-ink)"><h4 style="text-align:center;letter-spacing:3px;margin-bottom:12px">🌿 五行分布</h4>`;
  const maxWx = Math.max(...wxOrder.map(k => wx[k]), 1);
  const wxIcons = {"木":"🌳","火":"🔥","土":"⛰️","金":"⚜️","水":"💧"};
  const wxLabels = {"木":"木·肝胆","火":"火·心小肠","土":"土·脾胃","金":"金·肺大肠","水":"水·肾膀胱"};
  wxOrder.forEach(k => {
    const cnt = wx[k];
    const pct = Math.round(cnt / 8 * 100);
    let status = '', statColor = '';
    if (cnt >= 4) { status = '过旺'; statColor = 'var(--cinnabar)'; }
    else if (cnt === 0) { status = '缺失'; statColor = 'var(--water-blue)'; }
    else { status = '平衡'; statColor = 'var(--jade)'; }
    html += '<div style="display:flex;align-items:center;gap:10px;padding:5px 10px;margin:4px 0;background:rgba(255,255,255,0.6);border-radius:6px">';
    html += '<span style="font-size:1.1rem;width:28px;text-align:center">' + (wxIcons[k]||'◆') + '</span>';
    html += '<span style="width:90px;font-weight:bold;font-size:0.85rem;color:' + wxColors[k] + '">' + (wxLabels[k]||k) + '</span>';
    html += '<span style="width:22px;text-align:center;font-family:var(--font-title);font-size:1rem;color:' + wxColors[k] + '">' + cnt + '</span>';
    html += '<div style="flex:1;height:14px;background:#ebe2cf;border-radius:7px;overflow:hidden"><div style="width:' + pct + '%;height:100%;background:' + wxColors[k] + ';border-radius:7px;transition:width 0.6s ease"></div></div>';
    html += '<span style="font-size:0.75rem;color:var(--ink-light);min-width:32px">' + pct + '%</span>';
    html += '<span style="font-size:0.7rem;color:' + statColor + ';min-width:28px;text-align:center">' + status + '</span>';
    html += '</div>';
  });
  html += '</div>';

  // === 五行雷达图 ===
  html += renderWuxingChart(wx);

  // === 五行解读 (合并入排盘) ===
  html += `<div class="analysis-block" style="margin-top:20px"><h4>五行解读</h4><p>${result.interpretation.wuxing}</p></div>`;

  return html;
}

function renderWuxingChart(wx) {
  const order = ["木","火","土","金","水"];
  const colors = {"木":"#5b8c5a","火":"#d94a4a","土":"#c9a84c","金":"#9b9b9b","水":"#4a90d9"};
  let svg = '<div class=\"chart-container\" style=\"max-width:280px;margin:0 auto\"><svg viewBox=\"0 0 260 260\" style=\"width:100%;height:auto\">';
  for (let level = 1; level <= 4; level++) {
    const pts = order.map((k, i) => {
      const angle = Math.PI * 2 * i / 5 - Math.PI / 2;
      const r = level * 22;
      return (130 + r * Math.cos(angle)).toFixed(1) + ',' + (130 + r * Math.sin(angle)).toFixed(1);
    });
    svg += '<polygon points=\"' + pts.join(' ') + '\" fill=\"none\" stroke=\"#d4cbb8\" stroke-width=\"0.5\"/>';
  }
  order.forEach((k, i) => {
    const angle = Math.PI * 2 * i / 5 - Math.PI / 2;
    svg += '<line x1=\"130\" y1=\"130\" x2=\"' + (130 + 95 * Math.cos(angle)).toFixed(1) + '\" y2=\"' + (130 + 95 * Math.sin(angle)).toFixed(1) + '\" stroke=\"#d4cbb8\" stroke-width=\"0.8\"/>';
  });
  const dataPts = order.map((k, i) => {
    const angle = Math.PI * 2 * i / 5 - Math.PI / 2;
    const r = (Math.max(wx[k]||0, 0) / 8) * 88;
    return (130 + r * Math.cos(angle)).toFixed(1) + ',' + (130 + r * Math.sin(angle)).toFixed(1);
  });
  svg += '<polygon points=\"' + dataPts.join(' ') + '\" fill=\"rgba(201,169,110,0.2)\" stroke=\"#c9a96e\" stroke-width=\"2\"/>';
  order.forEach((k, i) => {
    const angle = Math.PI * 2 * i / 5 - Math.PI / 2;
    const r = ((wx[k]||0) / 8) * 88;
    svg += '<circle cx=\"' + (130 + r * Math.cos(angle)).toFixed(1) + '\" cy=\"' + (130 + r * Math.sin(angle)).toFixed(1) + '\" r=\"3\" fill=\"' + colors[k] + '\"/>';
  });
  order.forEach((k, i) => {
    const angle = Math.PI * 2 * i / 5 - Math.PI / 2;
    const r = 115;
    svg += '<text x=\"' + (130 + r * Math.cos(angle)).toFixed(1) + '\" y=\"' + (130 + r * Math.sin(angle)).toFixed(1) + '\" text-anchor=\"middle\" dominant-baseline=\"middle\" fill=\"' + colors[k] + '\" font-size=\"13\" font-weight=\"bold\" font-family=\"SimSun,serif\">' + k + '</text>';
    svg += '<text x=\"' + (130 + r * Math.cos(angle)).toFixed(1) + '\" y=\"' + (130 + r * Math.sin(angle) + 16).toFixed(1) + '\" text-anchor=\"middle\" fill=\"' + colors[k] + '\" font-size=\"12\" font-family=\"SimSun,serif\">' + (wx[k]||0) + '</text>';
  });
  svg += '</svg></div>';
  return svg;
}

function renderStrength(result) {
  const s = result.strength;
  const dayWx = wxOf(result.dayMaster.stem);
  const wxDir = {'木':'东方','火':'南方','土':'中部/本地','金':'西方','水':'北方'};
  const wxColor = {'木':'绿色/青色','火':'红色/紫色','土':'黄色/棕色','金':'白色/金色','水':'黑色/蓝色'};

  let html = `<div class="analysis-block"><h4>⚖️ 判定结果：${s.level}</h4>
    <p>综合得分：<strong>${s.score}分</strong>（≥3为身强，≤0为身弱，1-2为中和）</p>
    <p style="font-size:0.85rem;color:var(--text-muted)">日主<strong>${result.dayMaster.stem}</strong>属<strong>${dayWx}</strong>，坐${result.dayMaster.branch}。</p></div>`;

  // Scoring breakdown
  html += `<div class="analysis-block"><h4>📊 得分明细</h4><div style="font-size:0.9rem">`;
  s.details.forEach(d => { html += `<p>• ${d}</p>`; });
  html += `</div></div>`;

  // Detailed analysis based on strength level
  html += `<div class="analysis-block"><h4>🔍 强弱深度解读</h4>`;
  if (s.level === '身强') {
    html += `<p><strong>日主${result.dayMaster.stem}(${dayWx})身强</strong>，精力充沛，行动力足，抗压能力强。如同大树根深叶茂，能承受较大的人生起伏。</p>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:10px 0">
      <div style="padding:10px;background:#e8f5e9;border-radius:6px"><strong style="color:#2e7d32">✅ 优势</strong><ul style="margin:4px 0 0 16px;font-size:0.85rem"><li>自主性强，适合独立创业</li><li>执行力高，说干就干</li><li>抗压能力好，能担重任</li><li>领导力突出，能率众成事</li></ul></div>
      <div style="padding:10px;background:#fff3e0;border-radius:6px"><strong style="color:#e65100">⚠ 注意</strong><ul style="margin:4px 0 0 16px;font-size:0.85rem"><li>易刚愎自用，需学会倾听</li><li>过于自信可能忽视细节</li><li>宜适当放权，不必事事亲为</li><li>注意身体健康，勿过度透支</li></ul></div>
    </div>
    <p><strong>喜忌：</strong>喜<strong>克、泄、耗</strong>（官杀、食伤、财星）。${result.wuxing.overWang.length > 0 ? `命局<strong>${result.wuxing.overWang.map(o=>o.wx).join('、')}</strong>过旺，宜用<strong>${result.wuxing.missing.map(m=>m.wx).join('、') || '其他五行'}</strong>来平衡。` : ''}</p>
    <p><strong>发展建议：</strong>适合开拓性、竞争性强的工作；可独立创业或担任领导角色；在压力中反而能激发潜能；${result.wuxing.missing.length > 0 ? `多接触<strong>${result.wuxing.missing.map(m=>m.wx).join('、')}</strong>能量（${result.wuxing.missing.map(m=>wxDir[m]||m.wx).join('、')}方位，${result.wuxing.missing.map(m=>wxColor[m]||m.wx).join('、')}颜色）来平衡命局。` : '保持现有节奏即可。'}</p>`;
  } else if (s.level === '身弱') {
    html += `<p><strong>日主${result.dayMaster.stem}(${dayWx})身弱</strong>，思虑周全，处事谨慎，善于借助外力。如同藤蔓倚树而生，需要支撑方能茁壮。</p>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:10px 0">
      <div style="padding:10px;background:#e8f5e9;border-radius:6px"><strong style="color:#2e7d32">✅ 优势</strong><ul style="margin:4px 0 0 16px;font-size:0.85rem"><li>善于合作，团队协作能力强</li><li>谦虚谨慎，不轻易犯错</li><li>善用资源，借力打力</li><li>感知敏锐，人情练达</li></ul></div>
      <div style="padding:10px;background:#fff3e0;border-radius:6px"><strong style="color:#e65100">⚠ 注意</strong><ul style="margin:4px 0 0 16px;font-size:0.85rem"><li>易缺乏主见，需增强自信</li><li>依赖性强，需培养独立性</li><li>精力有限，不宜过度操劳</li><li>决策时容易犹豫不决</li></ul></div>
    </div>
    <p><strong>喜忌：</strong>喜<strong>生扶、比助</strong>（印星、比劫）。宜借助贵人、学识、团队之力来增强自身。${result.wuxing.missing.length > 0 ? `命局缺<strong>${result.wuxing.missing.map(m=>m.wx).join('、')}</strong>，需后天补足。` : ''}</p>
    <p><strong>发展建议：</strong>适合在稳定环境中逐步发展；寻找好的平台和团队比单打独斗更重要；注重学习积累，以专业能力弥补先天不足；${result.wuxing.missing.length > 0 ? `主动接触<strong>${result.wuxing.missing.map(m=>m.wx).join('、')}</strong>能量（${result.wuxing.missing.map(m=>wxDir[m]||m.wx).join('、')}方位，${result.wuxing.missing.map(m=>wxColor[m]||m.wx).join('、')}颜色）。` : '多亲近印星所代表的长辈、贵人和知识。'}</p>`;
  } else {
    html += `<p><strong>日主${result.dayMaster.stem}(${dayWx})中和</strong>，命局平衡，适应力强，能屈能伸。</p>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:10px 0">
      <div style="padding:10px;background:#e8f5e9;border-radius:6px"><strong style="color:#2e7d32">✅ 优势</strong><ul style="margin:4px 0 0 16px;font-size:0.85rem"><li>适应力强，各种环境都能生存</li><li>心态平和，不偏激不固执</li><li>进退有度，知所取舍</li><li>可塑性高，发展空间大</li></ul></div>
      <div style="padding:10px;background:#e3f2fd;border-radius:6px"><strong style="color:#1565c0">💡 特点</strong><ul style="margin:4px 0 0 16px;font-size:0.85rem"><li>无特别突出的优势方向</li><li>需依靠大运流年来定向</li><li>适合多元化发展</li><li>变化中寻找最适合自己的路</li></ul></div>
    </div>
    <p><strong>发展建议：</strong>命局中和意味着灵活性高，可根据大运流年的变化调整策略；不执着于单一方向，多元尝试找到最适合自己的领域。</p>`;
  }
  html += `</div>`;

  return html;
}

function renderWuxing(result) {
  const wxData = result.wuxing;
  let html = `<div class="analysis-block"><h4>五行分布解读</h4><p>${result.interpretation.wuxing}</p></div>`;

  html += `<div class="highlight-grid">`;
  const wxAdvice = {
    "木": { color:"绿色", dir:"东方", act:"种植植物、晨练、接近自然", food:"绿色蔬菜" },
    "火": { color:"红色", dir:"南方", act:"多晒太阳、运动、社交", food:"红色食物" },
    "土": { color:"黄色", dir:"中部", act:"园艺、陶艺、稳定环境", food:"黄色蔬果" },
    "金": { color:"白色", dir:"西方", act:"金属饰品、金融活动、秩序管理", food:"白色食物" },
    "水": { color:"黑色", dir:"北方", act:"游泳、静坐、阅读、旅行", food:"黑色食物" },
  };

  for (const [elName, adv] of Object.entries(wxAdvice)) {
    const cnt = wxData.counts[elName];
    const status = cnt >= 4 ? "过旺" : cnt === 0 ? "缺失" : "平衡";
    html += `<div class="highlight-item">
      <div class="hi-label">${elName} (${cnt})</div>
      <div style="font-size:0.8rem;color:var(--text-secondary);margin-top:4px">${status}</div>
      <div style="font-size:0.7rem;color:var(--text-muted);margin-top:2px">补:${adv.color}/${adv.dir}</div>
    </div>`;
  }
  html += `</div>`;

  return html;
}

function renderShishen(result) {
  let html = `<table class="paipan-table">
    <tr><th>柱位</th><th>天干</th><th>十神</th><th>正/偏</th><th>简称</th></tr>`;
  result.tenGods.forEach(t => {
    html += `<tr>
      <td>${t.pillar}</td><td>${t.stem||''}</td>
      <td>${t.name}</td><td>${t.type==='self'?'—':t.type}</td><td>${t.short}</td>
    </tr>`;
  });
  html += `</table>`;

  // === 格局定性 ===
  if (result.pattern.matches.length > 0) {
    html += `<div class="analysis-block"><h4>🔍 格局定性</h4>`;
    result.pattern.matches.forEach(m => {
      html += `<p><strong>${m.name}</strong>（${m.cond}）: ${m.desc}</p>`;
      if (m.careers) html += `<p style="font-size:0.85rem;color:var(--text-muted)">适合方向：${m.careers}</p>`;
    });
    html += `</div>`;
  }

  // === 十神分布 ===
  html += '<div class="analysis-block"><h4>📊 十神分布</h4>';
  const shenSorted = Object.entries(result.pattern.shenCount).sort((a,b) => b[1]-a[1]);
  const maxShenCnt = Math.max(...Object.values(result.pattern.shenCount), 1);
  const shenColors = {
    "比肩":"#5b8c5a","劫财":"#3a6186","食神":"#c9a84c","伤官":"#d94a4a","偏财":"#8b6914",
    "正财":"#b8942e","正官":"#4a7c59","七杀":"#c43a31","正印":"#6b9a78","偏印":"#9b6b9b","日主":"#1a1410"
  };
  const shenIcons = {
    "比肩":"🤝","劫财":"⚔️","食神":"🍃","伤官":"💎","偏财":"🎲",
    "正财":"💰","正官":"🎖️","七杀":"⚡","正印":"📚","偏印":"🔮","日主":"☯️"
  };
  html += '<div style="display:flex;flex-direction:column;gap:8px">';
  shenSorted.forEach(function(_ref) {
    var name = _ref[0], cnt = _ref[1];
    var pct = Math.round(cnt / maxShenCnt * 100);
    var color = shenColors[name] || '#8b8170';
    var icon = shenIcons[name] || '◆';
    html += '<div style="display:flex;align-items:center;gap:10px;padding:6px 10px;background:rgba(255,255,255,0.7);border-radius:6px;border:1px solid #e8e0d0">';
    html += '<span style="font-size:1.2rem;width:28px;text-align:center">' + icon + '</span>';
    html += '<span style="width:50px;font-weight:bold;font-size:0.9rem;color:' + color + '">' + name + '</span>';
    html += '<span style="width:24px;text-align:center;font-family:var(--font-title);font-size:1.1rem;color:' + color + '">' + cnt + '</span>';
    html += '<div style="flex:1;height:16px;background:#ebe2cf;border-radius:8px;overflow:hidden"><div style="width:' + pct + '%;height:100%;background:' + color + ';border-radius:8px;transition:width 0.6s ease"></div></div>';
    html += '<span style="font-size:0.75rem;color:var(--ink-light);min-width:32px">' + pct + '%</span>';
    html += '</div>';
  });
  html += '</div></div>';

  // === 每个十神的单独解析 ===
  html += `<div class="analysis-block"><h4>📖 十神逐一详解</h4>`;
  const seenShens = new Set(result.tenGods.filter(t => t.type !== 'self').map(t => t.name));
  const SHISHEN_DICT = {
    "正官": { nature:"正类·克我", traits:"正直负责、遵纪守法、重视名誉、追求稳定", career:"公职、管理、行政、法律、教育", wealth:"正途收入、稳定增长、不喜投机", relation:"对配偶忠诚、责任感强、重视家庭", advice:"宜在规范环境中发展，适合体制内或大型企业；注意不过度保守，适度冒险有助于突破" },
    "七杀": { nature:"偏类·克我", traits:"权威果断、竞争意识强、敢作敢为、压力下成长", career:"军警、法律、医疗、高管、竞技、创业", wealth:"波动较大、高风险高回报、需谨慎控制", relation:"感情中控制欲较强，需注意给对方空间", advice:"压力是成长的催化剂，但需注意身心健康；在竞争环境中能脱颖而出，宜设定清晰边界" },
    "正财": { nature:"正类·我克", traits:"务实稳重、勤俭节约、重视物质基础、可信赖", career:"金融、财务、商贸、实业、稳定行业", wealth:"正途财运佳、适合储蓄和长期投资", relation:"对伴侣大方但注重实际，婚姻物质基础好", advice:"守财能力强，适合稳健理财；注意不过于看重物质而忽略精神生活；宜在熟悉的领域深耕" },
    "偏财": { nature:"偏类·我克", traits:"灵活善变、商业嗅觉敏锐、慷慨大方、不拘小节", career:"投资、贸易、销售、创业、自由职业", wealth:"横财运佳、投资获利能力强、但波动大", relation:"对异性大方，人缘好但需注意感情专一", advice:"天生的投资者，但需控制风险；慷慨的性格带来人脉，也带来不必要的开销；宜设定财务底线" },
    "正印": { nature:"正类·生我", traits:"仁慈善良、学识渊博、重视精神追求、有慈悲心", career:"教育、研究、文化、医疗、公益、咨询", wealth:"财运依附名誉地位，重名轻利", relation:"温柔体贴、包容心强、是理想的伴侣", advice:"学识是你的最大财富，持续学习能带来好运；贵人运强，遇到困难主动寻求帮助；注意不过于理想化" },
    "偏印": { nature:"偏类·生我", traits:"思维独特、技艺精湛、善于钻研、偏科天才", career:"技术研发、学术研究、艺术创作、咨询", wealth:"多学少成、财运不济时需耐心等待时机", relation:"情感表达含蓄，需要时间建立信任", advice:"天赋异禀但容易半途而废，选定一个方向深耕；适合技术型或专业型工作；避免同时追求太多目标" },
    "食神": { nature:"正类·我生", traits:"温厚善良、乐观豁达、享受生活、有创造力", career:"技术、设计、美食、娱乐、教育、艺术", wealth:"技术生财、稳定增长、知足常乐", relation:"温柔体贴、善解人意、是理想的生活伴侣", advice:"乐观的性格是你的最大优势，也是潜力所在；适合将爱好转化为事业；注意不过于安于现状，适度进取" },
    "伤官": { nature:"偏类·我生", traits:"才华横溢、聪明机智、不拘一格、表达力强", career:"艺术、设计、媒体、写作、演艺、策划", wealth:"才华变现能力强、但波动大、需管理预期", relation:"感情丰富但情绪化，需找包容性强的伴侣", advice:"才华是你的核心竞争力，但需学会收敛锋芒；适合自由职业或创意行业；注意人际关系，避免因直言得罪人" },
    "比肩": { nature:"正类·同我", traits:"独立自强、自尊心强、重视友情、脚踏实地", career:"自主创业、团队管理、竞技、销售", wealth:"合作分利、财富缓慢积累、不宜单打独斗", relation:"重视平等关系、不宜找过于强势的伴侣", advice:"独立性强但不宜孤军奋战；合适的合作伙伴能事半功倍；注意兄弟姐妹/朋友关系中的利益分配" },
    "劫财": { nature:"偏类·同我", traits:"竞争进取、善于交际、行动力强、不甘人后", career:"销售、市场、竞技、公关、创业", wealth:"来快去快、需防小人劫财、不宜担保借贷", relation:"占有欲较强、需学会信任伴侣", advice:"行动力是你的优势，但需控制冲动消费；适合需要社交能力的职业；注意选择可靠的合作伙伴，避免利益纠纷" },
  };

  seenShens.forEach(name => {
    const info = SHISHEN_DICT[name];
    if (info) {
      const count = result.pattern.shenCount[name] || 1;
      html += `<div style="margin:12px 0;padding:12px;background:var(--paper-cream);border-radius:8px;border-left:3px solid ${info.nature.includes('正类')?'var(--jade)':'var(--gold)'}">
        <h5 style="margin:0 0 6px 0;color:var(--ink-black)">${name}（${info.nature}）— 出现${count}次</h5>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:0.85rem">
          <div><strong>性格：</strong>${info.traits}</div>
          <div><strong>事业：</strong>${info.career}</div>
          <div><strong>财富：</strong>${info.wealth}</div>
          <div><strong>感情：</strong>${info.relation}</div>
        </div>
        <p style="margin:6px 0 0 0;font-size:0.82rem;color:var(--text-muted)"><strong>💡 建议：</strong>${info.advice}</p>
      </div>`;
    }
  });
  html += `</div>`;

  // === 综合说明 ===
  html += `<div class="analysis-block"><h4>📝 十神格局综合说明</h4>`;
  const dominant = shenSorted[0] ? shenSorted[0][0] : '日主';
  const dominantInfo = SHISHEN_DICT[dominant];
  let summary = `<p>命局以<strong>${dominant}</strong>为主导`;
  if (shenSorted.length > 1) summary += `，辅以<strong>${shenSorted[1][0]}</strong>`;
  summary += `。日主<strong>${result.strength.level}</strong>（得分${result.strength.score}）。</p>`;

  if (dominantInfo) {
    summary += `<p>${dominantInfo.traits}。${dominantInfo.advice}</p>`;
  }

  // 根据日主强弱给出综合判断
  if (result.strength.level === '身强') {
    summary += `<p>日主身强，喜克、泄、耗。${result.wuxing.overWang.length > 0 ? `命局${result.wuxing.overWang.map(o=>o.wx).join('、')}过旺，宜用${result.wuxing.missing.map(m=>m.wx).join('、') || '其他五行'}来平衡。` : '命局五行较为均衡。'}</p>`;
  } else if (result.strength.level === '身弱') {
    summary += `<p>日主身弱，喜生扶、比助。宜借助印星（学习、贵人）和比劫（合作、团队）来增强自身能量。</p>`;
  } else {
    summary += `<p>日主中和，命局平衡，适应力强。可根据大运流年的变化灵活调整策略。</p>`;
  }

  // 格局总结
  if (result.pattern.matches.length > 0) {
    summary += `<p><strong>格局：</strong>${result.pattern.matches[0].name}。${result.pattern.matches[0].desc}</p>`;
  }

  summary += `<p style="font-size:0.85rem;color:var(--text-muted)">⚠ 十神分析反映的是先天禀赋倾向，后天的努力、选择和环境同样重要。了解十神格局是为了发挥优势、弥补不足，而非给自己设限。</p>`;
  html += summary;
  html += `</div>`;

  return html;
}

function renderChongHe(result) {
  const ch = result.chongHe;
  let html = '';

  // === Summary ===
  const totalRelations = ch.heList.length + ch.chongList.length + ch.xingList.length + ch.sanHeList.length;
  html += `<div class="analysis-block"><h4>📊 冲合总览</h4>
    <p>命局共发现 <strong>${totalRelations}</strong> 组冲合刑害关系：
    ${ch.heList.length > 0 ? `<span style="color:var(--jade)">🟢 ${ch.heList.length}组相合</span> ` : ''}
    ${ch.chongList.length > 0 ? `<span style="color:var(--cinnabar)">🔴 ${ch.chongList.length}组相冲</span> ` : ''}
    ${ch.xingList.length > 0 ? `<span style="color:#e65100">🟠 ${ch.xingList.length}组相刑</span> ` : ''}
    ${ch.sanHeList.length > 0 ? `<span style="color:var(--water-blue)">🔵 ${ch.sanHeList.length}组三合</span> ` : ''}
    </p></div>`;

  // === Detailed: 相合 ===
  if (ch.heList.length > 0) {
    html += `<div class="analysis-block"><h4>🟢 相合关系 — 和谐与羁绊</h4>`;
    ch.heList.forEach((h, i) => {
      html += `<div style="margin:10px 0;padding:12px;background:var(--paper-cream);border-radius:8px;border-left:3px solid var(--jade)">
        <p><strong>${h.type}</strong>：${h.a}与${h.b}相合</p>
        <p style="font-size:0.85rem;color:var(--text-secondary)">${h.meaning}</p>`;
      if (h.type === '天干五合') {
        html += `<div style="margin-top:6px;font-size:0.82rem;color:var(--text-muted)">
          <p><strong>影响分析：</strong>天干五合主外在的人际互动。化${h.hua}，代表此关系在${h.hua === '土' ? '稳定/信任' : h.hua === '金' ? '规则/义气' : h.hua === '水' ? '智慧/沟通' : h.hua === '木' ? '成长/仁爱' : '热情/礼仪'}层面产生联结。</p>
          <p>• 正面：人际关系密切，合作顺利，相互理解</p>
          <p>• 负面：可能因合而受牵绊，难以独立决策</p>
          <p>• 体现领域：${h.a.includes('年') ? '家族/长辈' : h.a.includes('月') ? '父母/事业' : h.a.includes('日') ? '自身/婚姻' : '子女/下属'}关系</p>
        </div>`;
      } else if (h.type === '地支六合') {
        html += `<div style="margin-top:6px;font-size:0.82rem;color:var(--text-muted)">
          <p><strong>影响分析：</strong>地支六合主内在的本质吸引。${h.zhiA}与${h.zhiB}相合，代表两个地支所在柱位的领域产生深度联结。</p>
          <p>• 年日/月时相合 → 家庭与自我或事业与子女的和谐</p>
          <p>• 合得好 → 相关领域顺遂、得心应手</p>
          <p>• 合得过度 → 贪合忘冲，可能失去进取心</p>
        </div>`;
      }
      html += `</div>`;
    });
    html += `</div>`;
  }

  // === Detailed: 相冲 ===
  if (ch.chongList.length > 0) {
    html += `<div class="analysis-block warning"><h4>🔴 相冲关系 — 变动与冲突</h4>`;
    ch.chongList.forEach((c, i) => {
      html += `<div style="margin:10px 0;padding:12px;background:#fef5f5;border-radius:8px;border-left:3px solid var(--cinnabar)">
        <p><strong>${c.type}</strong>：${c.a}与${c.b}相冲（${c.zhiA}冲${c.zhiB}）</p>
        <p style="font-size:0.85rem;color:var(--text-secondary)">${c.meaning}</p>
        <div style="margin-top:6px;font-size:0.82rem;color:var(--text-muted)">
          <p><strong>冲的寓意：</strong></p>
          <p>• <strong>变动：</strong>相关领域（${c.a}和${c.b}代表的时空）容易出现变动、不稳定</p>
          <p>• <strong>冲突：</strong>${c.a === '年柱' && c.b === '日柱' ? '祖业/长辈与自身发展方向有冲突，适合离家发展' : c.a === '月柱' && c.b === '时柱' ? '事业与子女/下属有矛盾，需调整管理方式' : '两个领域之间存在张力'}</p>
          <p>• <strong>破解：</strong>冲不代表一定凶，适当变动反而能激发活力。${c.a.includes('日') || c.b.includes('日') ? '日柱逢冲，建议晚婚、异地发展或保持适度空间。' : '通过主动求变（出差、搬家、换岗）来化解冲力。'}</p>
          <p>• <strong>缘分：</strong>相冲的领域缘分较浅，不必强求，顺其自然反而更好</p>
        </div>
      </div>`;
    });
    html += `</div>`;
  }

  // === Detailed: 相刑 ===
  if (ch.xingList.length > 0) {
    html += `<div class="analysis-block warning"><h4>🟠 相刑关系 — 暗中不利</h4>`;
    ch.xingList.forEach((x, i) => {
      html += `<div style="margin:10px 0;padding:12px;background:#fff8f0;border-radius:8px;border-left:3px solid #e65100">
        <p><strong>相刑</strong>：${x.a}(${x.zhiA})与${x.b}(${x.zhiB})</p>
        <p style="font-size:0.85rem;color:var(--text-secondary)">${x.meaning}</p>
        <div style="margin-top:6px;font-size:0.82rem;color:var(--text-muted)">
          <p><strong>刑的类型：</strong>${(x.zhiA === '子' && x.zhiB === '卯') || (x.zhiA === '卯' && x.zhiB === '子') ? '无礼之刑 — 因礼数不周或沟通不当引发矛盾' : (['寅','巳','申'].includes(x.zhiA) && ['寅','巳','申'].includes(x.zhiB)) ? '无恩之刑 — 因恩将仇报或忘恩负义引发纠纷' : '恃势之刑 — 因仗势欺人或恃才傲物引发冲突'}</p>
          <p>• <strong>应对：</strong>提高自身修养，注意言行举止；凡事多沟通，避免误会积累</p>
          <p>• <strong>化解：</strong>主动示弱、以柔克刚是化解相刑的最佳方式</p>
        </div>
      </div>`;
    });
    html += `</div>`;
  }

  // === Detailed: 三合 ===
  if (ch.sanHeList.length > 0) {
    html += `<div class="analysis-block"><h4>🔵 三合局 — 力量的汇聚</h4>`;
    ch.sanHeList.forEach((s, i) => {
      html += `<div style="margin:10px 0;padding:12px;background:var(--paper-cream);border-radius:8px;border-left:3px solid var(--water-blue)">
        <p><strong>三合${s.hua}局</strong>：${s.found.join('、')}形成${s.hua}的力量</p>
        <p style="font-size:0.85rem;color:var(--text-secondary)">${s.meaning}</p>
        <div style="margin-top:6px;font-size:0.82rem;color:var(--text-muted)">
          <p>• <strong>${s.hua}的性质：</strong>${s.hua === '水' ? '智慧、流动、沟通、适应力强' : s.hua === '木' ? '成长、仁爱、创造力、生命力' : s.hua === '火' ? '热情、行动、知名度、爆发力' : '规则、义气、决断力、执行力'}</p>
          <p>• <strong>应用：</strong>在${s.hua}相关的领域（${s.hua === '水' ? '交通/传媒/贸易' : s.hua === '木' ? '教育/医疗/环保' : s.hua === '火' ? '演艺/餐饮/能源' : '金融/法律/制造'}）更容易成功</p>
          ${s.found.length === 3 ? '<p>• 三支俱全，力量完整，是强势的利好信号</p>' : '<p>• 尚缺一支，大运流年补齐时可激发完整力量</p>'}
        </div>
      </div>`;
    });
    html += `</div>`;
  }

  // === 无冲合 ===
  if (totalRelations === 0) {
    html += `<div class="analysis-block"><h4>📊 冲合总览</h4><p>命局中无明显冲合刑害关系，四柱相对独立平衡。这不代表不好——独立的格局意味着人生更为自主，较少受到外界牵制。</p>
    <div style="margin-top:6px;font-size:0.85rem;color:var(--text-muted)">
      <p>• 无冲 → 人生波折较少，稳定性高</p>
      <p>• 无合 → 独立性较强，不受过多羁绊</p>
      <p>• 无刑 → 人际关系较为顺畅</p>
      <p>• 大运流年带来的冲合将成为人生的主要变数</p>
    </div></div>`;
  }

  // === Summary advice ===
  html += `<div class="analysis-block"><h4>💡 冲合化解总纲</h4>
    <p style="font-size:0.9rem">冲合是八字中最直接的人际关系和人生变动信号。基本原则：</p>
    <p>• <strong>合宜顺：</strong>相合代表缘分，顺势而为，不强行割裂</p>
    <p>• <strong>冲宜缓：</strong>相冲代表变动，主动求变（出差/搬家/换岗）反而能化解不利</p>
    <p>• <strong>刑宜修：</strong>相刑是自身修养的提醒，修身养性是最好的化解</p>
    <p>• <strong>冲合并存：</strong>有冲有合乃人生常态，关键在于顺势而为、趋吉避凶</p>
  </div>`;

  return html;
}

function renderDayun(result) {
  const dy = result.dayun;
  let html = `<div class="analysis-block"><h4>大运排法</h4>
    <p>${dy.forward ? "顺排" : "逆排"}，起运岁数：<strong>${dy.startAge}岁</strong></p></div>`;

  // Main luck pillar table with吉凶 analysis
  html += `<div class="analysis-block"><h4>📊 八步大运 — 各维度吉凶总览</h4>`;
  html += `<div style="overflow-x:auto"><table class="paipan-table" style="font-size:0.82rem">
    <tr><th>#</th><th>大运</th><th>干支</th><th>十神</th><th>年龄段</th><th>事业</th><th>婚姻</th><th>财富</th><th>健康</th></tr>`;

  dy.luckPillars.forEach((lp, i) => {
    const isCurrent = lp === dy.currentDayun;
    const a = analyzeLuckPillar(result, lp, `大运${i+1}`);
    const jxBadge = (lvl) => lvl === '吉' ? '<span style="color:#5b8c5a">●吉</span>' : lvl === '凶' ? '<span style="color:#c41e3a">●凶</span>' : '<span style="color:#c9a96e">●平</span>';
    html += `<tr style="${isCurrent ? 'background:rgba(201,169,110,0.18);font-weight:bold' : ''}">
      <td>${i+1}${isCurrent?' ←':''}</td>
      <td>${lp.gz}</td><td>${lp.stem}+${lp.branch}</td>
      <td style="font-size:0.78rem">${a.tgName}</td><td>${lp.range}</td>
      <td>${jxBadge(a.career.level)}</td><td>${jxBadge(a.marriage.level)}</td>
      <td>${jxBadge(a.wealth.level)}</td><td>${jxBadge(a.health.level)}</td>
    </tr>`;
  });
  html += `</table></div></div>`;

  // Current luck pillar detail
  const currAnalysis = analyzeLuckPillar(result, dy.currentDayun, '当前大运');
  html += `<div class="analysis-block"><h4>🔍 当前大运详解 — ${dy.currentDayun.gz} (${dy.currentDayun.range})</h4>`;
  html += renderLuckDetail(currAnalysis);
  html += `</div>`;

  // Current liunian
  const liunianGZ = { stem: TG[dy.liunianGZ.stemIdx], branch: DZ[dy.liunianGZ.branchIdx], stemIdx: dy.liunianGZ.stemIdx, branchIdx: dy.liunianGZ.branchIdx };
  const lnAnalysis = analyzeLiunian(result, liunianGZ);
  html += `<div class="analysis-block"><h4>📅 当前流年 — ${dy.currentYear}年(${dy.currentLiunian})</h4>`;
  html += renderLiunianDetail(lnAnalysis, dy.currentLiunian, dy.currentYear);
  html += `</div>`;

  // Future years
  html += `<div class="analysis-block"><h4>🔮 未来五年流年速览</h4>`;
  html += `<div style="overflow-x:auto"><table class="paipan-table" style="font-size:0.82rem">
    <tr><th>年份</th><th>干支</th><th>十神</th><th>吉凶</th><th>宜</th><th>忌</th><th>贵人方位</th></tr>`;
  dy.futureYears.forEach(fy => {
    const fyGZ = { stem: fy.stem, branch: fy.branch, stemIdx: TG.indexOf(fy.stem), branchIdx: DZ.indexOf(fy.branch) };
    const fya = analyzeLiunian(result, fyGZ);
    const badge = fya.overall === '吉' ? '🟢 吉' : fya.overall === '凶' ? '🔴 凶' : '🟡 平';
    html += `<tr>
      <td><strong>${fy.year}</strong></td><td>${fy.gz}</td><td>${fya.tenGod}</td>
      <td>${badge}</td>
      <td style="font-size:0.75rem">${fya.yi.slice(0,2).join('、')}</td>
      <td style="font-size:0.75rem">${fya.ji.slice(0,2).join('、')}</td>
      <td style="font-size:0.75rem">${fya.benefactorDir}</td>
    </tr>`;
  });
  html += `</table></div></div>`;

  return html;
}

function renderLuckDetail(a) {
  const jxTag = (lvl, txt) => {
    const clr = lvl === '吉' ? 'var(--jade)' : lvl === '凶' ? 'var(--cinnabar)' : 'var(--gold)';
    return `<span style="color:${clr};font-weight:bold">[${lvl}]</span> ${txt}`;
  };
  return `<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
    <div style="padding:10px;background:var(--paper-cream);border-radius:6px"><strong>💼 事业</strong><br>${jxTag(a.career.level, a.career.text)}</div>
    <div style="padding:10px;background:var(--paper-cream);border-radius:6px"><strong>💕 婚姻</strong><br>${jxTag(a.marriage.level, a.marriage.text)}</div>
    <div style="padding:10px;background:var(--paper-cream);border-radius:6px"><strong>💰 财富</strong><br>${jxTag(a.wealth.level, a.wealth.text)}</div>
    <div style="padding:10px;background:var(--paper-cream);border-radius:6px"><strong>🏥 健康</strong><br>${jxTag(a.health.level, a.health.text)}</div>
    <div style="padding:10px;background:var(--paper-cream);border-radius:6px;grid-column:1/-1"><strong>🙏 贵人方位</strong><br>${a.benefactor.text}</div>
  </div>`;
}

function renderLiunianDetail(a, gzName, year) {
  const badge = a.overall === '吉' ? '🟢 大吉' : a.overall === '凶' ? '🔴 多舛' : '🟡 平稳';
  return `<div style="margin-bottom:12px">
    <p><strong>流年十神：</strong>${a.tenGod} | <strong>总体吉凶：</strong>${badge}</p>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
    <div style="padding:10px;background:#e8f5e9;border-radius:6px">
      <strong style="color:#2e7d32">✅ 宜做</strong>
      <ul style="margin:4px 0 0 16px;font-size:0.85rem">${a.yi.map(y=>`<li>${y}</li>`).join('')}</ul>
    </div>
    <div style="padding:10px;background:#fce4ec;border-radius:6px">
      <strong style="color:#c62828">❌ 忌做</strong>
      <ul style="margin:4px 0 0 16px;font-size:0.85rem">${a.ji.map(j=>`<li>${j}</li>`).join('')}</ul>
    </div>
    <div style="padding:10px;background:#e3f2fd;border-radius:6px">
      <strong style="color:#1565c0">🧭 五行方位</strong>
      <p style="font-size:0.85rem;margin:4px 0">宜向：${a.yiDir}</p>
      <p style="font-size:0.85rem;margin:0">忌向：${a.jiDir}</p>
    </div>
    <div style="padding:10px;background:#fff3e0;border-radius:6px">
      <strong style="color:#e65100">✨ 贵人/改运</strong>
      <p style="font-size:0.85rem;margin:4px 0">贵人方位：${a.benefactorDir}（${a.benefactorColor}）</p>
      <p style="font-size:0.85rem;margin:0">${a.gaiyun}</p>
    </div>
  </div>`;
}

function renderShensha(result) {
  let html = '';
  const ss = result.shensha;

  // Enhanced shensha dictionary
  const SS_INFO = {
    "天乙贵人": { type:"吉", detail:"最大的吉神，逢凶化吉，遇难成祥。所在之柱代表该领域有贵人相助。出现在年柱→祖上有德；月柱→父母/师长提携；日柱→配偶为贵人或自身有贵人运；时柱→子女/下属为贵人。", advice:"主动结交年长者、上位者；遇到困难时不要硬撑，贵人就在身边。", color:"var(--jade)" },
    "文昌星": { type:"吉", detail:"主学业、文采、技术、考试。文昌入命者聪明好学，擅长文字和技术工作。所在柱位代表该阶段学业运最强。", advice:"适合学术研究、技术研发、写作等脑力工作；考试前宜拜文昌、用功读书。", color:"var(--jade)" },
    "桃花": { type:"双刃", detail:"主人缘、魅力、知名度、感情机遇。桃花入命者异性缘佳，社交能力强。但桃花也是一把双刃剑：未婚者桃花运旺利于婚恋；已婚者桃花需防外遇，应将桃花能量转化为知名度和人脉。", advice:"未婚者把握感情机遇；已婚者将桃花转化为社交/事业资源。日柱桃花代表配偶相貌出众或自身有魅力。", color:"var(--gold)" },
    "华盖": { type:"双刃", detail:"主聪明、孤僻、对神秘文化的兴趣。华盖入命者天生聪慧，喜欢钻研，对玄学/哲学/宗教有天赋。但华盖也代表孤芳自赏、不合群的倾向。", advice:"适合研究型工作；培养社交能力以平衡孤僻倾向；可将玄学/哲学发展为副业。", color:"var(--gold)" },
    "驿马": { type:"中性", detail:"主奔波、远行、变动、流动性。驿马入命者一生多动，不适合长期待在一个地方。所在柱位代表该阶段奔波最频繁。", advice:"适合需要出差/外勤/交通/物流的工作；不宜长期宅家，主动出行可化解驿马的负面影响；马车星逢冲→走得远；逢合→走不远。", color:"var(--water-blue)" },
    "羊刃": { type:"凶", detail:"主刚强、冲动、竞争、意外伤害。羊刃入命者性格刚烈，行动力极强，但容易冲动惹事。羊刃在日柱尤需注意，代表自身或配偶性格刚烈。", advice:"控制情绪是核心课题；适合军警/体育/竞技等需要刚性的行业；大运流年逢羊刃需特别注意安全和健康。", color:"var(--cinnabar)" },
    "将星": { type:"吉", detail:"主领导才能、统率力、独当一面的能力。将星入命者天生具备领导气质，能率众成事。", advice:"适合管理岗位或自主创业；培养团队领导力；大运流年临将星是招人/招生/立项目的好时机。", color:"var(--jade)" },
    "禄神": { type:"吉", detail:"主食禄、福气、稳定收入。禄神入命者一生衣食无忧，经济基础稳固。所在柱位代表该阶段的物质生活最充裕。", advice:"珍惜已有的物质基础；不宜过度冒险投资；禄神逢冲则收入不稳，需提前储备。", color:"var(--jade)" },
    "灾煞": { type:"凶", detail:"主突发的短期障碍、变故。灾煞所在柱位代表该领域的突发风险较高。", advice:"灾煞不代表注定有灾，而是提醒在该领域多加小心；购买保险、定期体检、避免高风险活动可有效化解。", color:"var(--cinnabar)" },
    "天喜": { type:"吉", detail:"主喜庆之事：结婚、生育、升迁、开业。天喜入命者一生多逢喜事，尤其在所在柱位代表的阶段。以月支为标尺，寅卯辰→戌、巳午未→丑、申酉戌→辰、亥子丑→未。", advice:"适合在喜庆行业（婚庆/庆典/娱乐）发展；大运流年逢天喜是办喜事的好时机。", color:"var(--jade)" },
    "劫煞": { type:"凶", detail:"主阻滞、障碍、难关或小人。以年支/日支为标尺，申子辰→巳、巳酉丑→寅、寅午戌→亥、亥卯未→申。日支劫煞代表自身及婚姻家庭方面的障碍；年支劫煞代表对外关系中的小人。", advice:"在所涉领域多加防范；做事留有余地；大运流年逢劫煞宜守不宜攻。", color:"var(--cinnabar)" },
    "学堂": { type:"吉", detail:"主学习际遇、知识领悟能力、求知欲望。以日干长生位为标尺（甲亥乙午丙寅丁酉戊寅己酉庚巳辛子壬申癸卯）。月支/日支带学堂者一生好学。", advice:"持续学习是你的最大优势；适合教育/研究/技术类工作；活到老学到老。", color:"var(--jade)" },
    "天医": { type:"中性", detail:"主与医学的缘分。以月支为标尺，月令推上一位即是天医星。带天医者或对医学有兴趣、或从事医疗工作、或身体需注意保养。", advice:"适合医学/保健/养生类工作；注意定期体检；可学习基本医学常识以自利利他。", color:"var(--water-blue)" },
  };

  if (ss.length === 0) {
    html = `<div class="analysis-block"><p>命局中未发现明显神煞配置。这不代表不好——神煞只是辅助参考，命局的十神格局和五行平衡更为重要。</p></div>`;
  } else {
    // Summary table (deduplicate by name, merge pillar locations)
    html += `<div class="analysis-block"><h4>⭐ 神煞总览</h4>`;
    html += `<div style="overflow-x:auto"><table class="paipan-table"><tr><th>神煞</th><th>所在柱位</th><th>吉凶</th><th>简要含义</th></tr>`;
    // Group by name
    const grouped = {};
    ss.forEach(s => {
      if (!grouped[s.name]) grouped[s.name] = { pillars: [], meaning: s.meaning };
      grouped[s.name].pillars.push(s.pillar);
    });
    for (const [name, g] of Object.entries(grouped)) {
      const info = SS_INFO[name] || { type:"中性", color:"var(--text-muted)" };
      const typeBadge = info.type === '吉' ? '🟢吉' : info.type === '凶' ? '🔴凶' : info.type === '双刃' ? '🟡双刃' : '🔵中';
      html += `<tr><td><strong>${name}</strong></td><td>${g.pillars.join('、')}</td><td>${typeBadge}</td><td style="font-size:0.82rem">${g.meaning}</td></tr>`;
    }
    html += `</table></div></div>`;

    // Individual detailed analysis
    html += `<div class="analysis-block"><h4>📖 神煞逐一详解</h4>`;
    const seenSS = new Set(ss.map(s => s.name));
    seenSS.forEach(name => {
      const info = SS_INFO[name];
      if (info) {
        const occurrences = ss.filter(s => s.name === name);
        html += `<div style="margin:12px 0;padding:14px;background:var(--paper-cream);border-radius:8px;border-left:3px solid ${info.color}">
          <h5 style="margin:0 0 6px 0;color:var(--ink-black)">${name} <span style="font-size:0.8rem;color:${info.color}">[${info.type}]</span></h5>
          <p style="font-size:0.88rem">${info.detail}</p>
          <p style="font-size:0.85rem"><strong>出现位置：</strong>${occurrences.map(o=>o.pillar).join('、')}</p>
          <p style="font-size:0.85rem;color:var(--text-muted)"><strong>💡 建议：</strong>${info.advice}</p>
        </div>`;
      }
    });
    html += `</div>`;

    // Statistics (by unique shensha names)
    const uniqueSS = Object.keys(grouped);
    const jiCount = uniqueSS.filter(n => (SS_INFO[n]||{}).type === '吉').length;
    const xiongCount = uniqueSS.filter(n => (SS_INFO[n]||{}).type === '凶').length;
    html += '<div class="analysis-block"><h4>📊 神煞统计</h4>';
    const ssTotal = uniqueSS.length;
    const ssNeutral = ssTotal - jiCount - xiongCount;
    const ssStats = [
      { label:'吉神', icon:'🟢', cnt:jiCount, color:'var(--jade)' },
      { label:'凶煞', icon:'🔴', cnt:xiongCount, color:'var(--cinnabar)' },
      { label:'双刃/中性', icon:'🟡', cnt:ssNeutral, color:'var(--gold)' },
      { label:'总计', icon:'⭐', cnt:ssTotal, color:'var(--ink-black)' }
    ];
    ssStats.forEach(function(s) {
      const pct2 = ssTotal > 0 ? Math.round(s.cnt / ssTotal * 100) : 0;
      html += '<div style=\"display:flex;align-items:center;gap:10px;padding:5px 10px;margin:4px 0;background:var(--paper-light);border-radius:6px\">';
      html += '<span style=\"font-size:1.1rem;width:26px;text-align:center\">' + s.icon + '</span>';
      html += '<span style=\"width:75px;font-weight:bold;font-size:0.85rem;color:' + s.color + '\">' + s.label + '</span>';
      html += '<span style=\"width:24px;text-align:center;font-family:var(--font-title);font-size:1rem;color:' + s.color + '\">' + s.cnt + '</span>';
      html += '<div style=\"flex:1;height:14px;background:#ebe2cf;border-radius:7px;overflow:hidden\"><div style=\"width:' + pct2 + '%;height:100%;background:' + s.color + ';border-radius:7px;transition:width 0.6s ease\"></div></div>';
      html += '<span style=\"font-size:0.75rem;color:var(--ink-light);min-width:30px\">' + pct2 + '%</span>';
      html += '</div>';
    });
    html += '</div>';
  }

  html += `<div class="analysis-block"><h4>⚠ 神煞使用须知</h4>
    <p style="font-size:0.9rem">神煞是八字分析中的辅助参考指标，<strong>不单独决定吉凶</strong>。使用原则：</p>
    <p>• <strong>吉神需运助：</strong>吉神需要大运流年的配合才能发挥最大作用，如天乙贵人逢印运则贵人力更强</p>
    <p>• <strong>凶煞可制化：</strong>凶煞可以被克制或化解，如羊刃逢七杀则化为权威，桃花逢冲则减少困扰</p>
    <p>• <strong>重柱位轻数量：</strong>神煞所在的柱位（年/月/日/时）比数量更重要，日柱神煞影响最直接</p>
    <p>• <strong>结合十神看：</strong>同是桃花，在正官之柱和在伤官之柱的含义截然不同</p>
  </div>`;

  return html;
}

function renderZonghe(result) {
  const interp = result.interpretation;

  // === 今日运势详细分析 ===
  const today = new Date();
  const todayGzIdx = getDayGZIndex(today.getFullYear(), today.getMonth()+1, today.getDate());
  const todayGz = GZ[todayGzIdx];
  const todayGZObj = { stem: TG[todayGzIdx%10], branch: DZ[todayGzIdx%12], stemIdx: todayGzIdx%10, branchIdx: todayGzIdx%12 };
  const todayAnalysis = analyzeLiunian(result, todayGZObj);

  let html = `<div class="analysis-block"><h4>📋 今日运势 — ${today.getFullYear()}年${today.getMonth()+1}月${today.getDate()}日 (${todayGz})</h4>`;

  // Overall badge
  const badge = todayAnalysis.overall === '吉' ? '🟢 吉日' : todayAnalysis.overall === '凶' ? '🔴 凶日' : '🟡 平日';
  html += `<p style="font-size:1.1rem;margin:8px 0">今日十神：<strong>${todayAnalysis.tenGod}</strong> | 总体：<strong>${badge}</strong></p>`;

  // 宜忌
  html += `<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:10px 0">
    <div style="padding:10px;background:#e8f5e9;border-radius:6px">
      <strong style="color:#2e7d32">✅ 今日宜</strong>
      <ul style="margin:4px 0 0 16px;font-size:0.85rem">${todayAnalysis.yi.map(y=>`<li>${y}</li>`).join('')}</ul>
    </div>
    <div style="padding:10px;background:#fce4ec;border-radius:6px">
      <strong style="color:#c62828">❌ 今日忌</strong>
      <ul style="margin:4px 0 0 16px;font-size:0.85rem">${todayAnalysis.ji.map(j=>`<li>${j}</li>`).join('')}</ul>
    </div>
  </div>`;

  // 方位 + 改运
  html += `<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:10px 0">
    <div style="padding:10px;background:#e3f2fd;border-radius:6px">
      <strong style="color:#1565c0">🧭 五行方位宜忌</strong>
      <p style="font-size:0.85rem;margin:4px 0"><span style="color:#2e7d32">宜向：</span>${todayAnalysis.yiDir}</p>
      <p style="font-size:0.85rem;margin:0"><span style="color:#c62828">忌向：</span>${todayAnalysis.jiDir}</p>
    </div>
    <div style="padding:10px;background:#fff3e0;border-radius:6px">
      <strong style="color:#e65100">✨ 改运建议</strong>
      <p style="font-size:0.85rem;margin:4px 0">贵人方：${todayAnalysis.benefactorDir}（${todayAnalysis.benefactorColor}）</p>
      <p style="font-size:0.85rem;margin:0">${todayAnalysis.gaiyun}</p>
    </div>
  </div>`;

  // 日主与今日干支关系
  const tgRelIdx = calcTenGodRelation(result.dayStemIdx, todayGzIdx%10);
  const dayStem = result.dayMaster.stem;
  const todayStem = TG[todayGzIdx%10];
  html += `<p style="font-size:0.85rem;color:var(--text-secondary)">
    日主<strong>${dayStem}</strong>遇今日<strong>${todayStem}</strong>（${SHISHEN_FULL[tgRelIdx]}），
    ${yyOf(todayStem)===1?'阳':'阴'}性日。
    ${DZ_CHONG[result.pillars[2].branch] === DZ[todayGzIdx%12] ? '⚠ 今日地支与日柱相冲，诸事谨慎。' : ''}
    ${TG_HE[dayStem] === todayStem ? '💕 今日天干与日主相合，人际和谐。' : ''}
  </p></div>`;

  // === 事业详细分析 ===
  const dayWx = wxOf(result.dayMaster.stem);
  const lifeWxDir = { '木':'东方','火':'南方','土':'中部/本地','金':'西方','水':'北方' };
  const lifeWxColor = { '木':'绿色/青色','火':'红色/紫色','土':'黄色/棕色','金':'白色/金色','水':'黑色/蓝色' };
  const dominantShen = Object.entries(result.pattern.shenCount).sort((a,b)=>b[1]-a[1])[0];
  const dominantName = dominantShen ? dominantShen[0] : '日主';

  // Career matching based on dominant ten god
  const CAREER_MAP = {
    "正官": { fields:["公务员","行政管理","教育","法律","国企","大型企业中层"], traits:"重视规则、责任心强、适合体制内或规范化组织", advice:"宜在规章制度完善的环境中发展，稳步晋升；注意培养灵活性，避免过于刻板" },
    "七杀": { fields:["军警","律师","医生","企业高管","创业者","竞技体育"], traits:"敢闯敢拼、抗压能力强、适合竞争激烈的领域", advice:"压力是你成长的燃料，但需设定边界；创业或担任一把手能发挥最大潜力" },
    "正财": { fields:["金融","会计","财务","商贸","实业","不动产"], traits:"踏实稳重、善于理财、适合稳定的商业运营", advice:"深耕一个领域，长期积累；正途收入为主，不宜投机；适合做长期投资的复利增长" },
    "偏财": { fields:["投资","贸易","销售","自由职业","跨境电商","娱乐业"], traits:"商业嗅觉敏锐、灵活应变、适合市场化的行业", advice:"天生的商人，但需设定风险底线；多元化收入来源，不要把鸡蛋放一个篮子" },
    "正印": { fields:["教育","研究","文化","医疗","公益","出版","心理咨询"], traits:"学识丰富、有慈悲心、适合知识密集型行业", advice:"持续学习是你的核心优势；教是最好的学，适合知识传播类工作；贵人运强，多拓展人脉" },
    "偏印": { fields:["技术研发","数据分析","编程","工程设计","实验室研究"], traits:"思维独特、专注力强、适合需要深度钻研的技术岗位", advice:"选一个方向做到极致，成为不可替代的专家；避免频繁切换赛道；技术+专利是你的护城河" },
    "食神": { fields:["餐饮","设计","艺术","手工艺","培训","健康管理"], traits:"创造力丰富、服务意识强、适合与人打交道的行业", advice:"把爱好变成事业；适合小而美的商业模式；注意保持进取心，避免安于现状" },
    "伤官": { fields:["艺术创作","广告策划","媒体","演艺","写作","互联网产品"], traits:"才华突出、表达力强、适合创意和内容行业", advice:"才华是你的核心竞争力，但需学会团队协作；自由职业或创意工作室是不错的选择；注意管理好自己的情绪" },
    "比肩": { fields:["自主创业","团队管理","销售","竞技","培训"], traits:"独立性强、重视公平、适合需要个人担当的工作", advice:"找到志同道合的合作伙伴事半功倍；适合扁平化管理的团队；注意分享利益以维持合作" },
    "劫财": { fields:["市场营销","公关","商务拓展","直播","社群运营"], traits:"社交能力强、行动力突出、适合与人打交道的前线岗位", advice:"人脉就是财富，但需筛选可靠伙伴；控制冲动消费和投资；适合以社交为核心的工作" },
  };

  const careerInfo = CAREER_MAP[dominantName] || { fields:["综合发展"], traits:"适应力强", advice:"根据大运流年调整职业方向" };
  html += `<div class="analysis-block"><h4>💼 事业 — 详细分析</h4>
    <p>${interp.career}</p>
    <div style="margin:10px 0;padding:12px;background:var(--paper-cream);border-radius:8px">
      <p><strong>主导十神：</strong>${dominantName} — ${careerInfo.traits}</p>
      <p><strong>适合职业：</strong></p>
      <p style="font-size:0.9rem;margin:4px 0">${careerInfo.fields.map(f=>`<span style="display:inline-block;background:var(--paper-dark);padding:2px 10px;border-radius:10px;margin:2px;font-size:0.82rem">${f}</span>`).join(' ')}</p>
      <p style="margin-top:8px;font-size:0.88rem;color:var(--text-muted)"><strong>💡 发展建议：</strong>${careerInfo.advice}</p>
    </div>
    <p style="font-size:0.85rem;color:var(--text-muted)">以上职业建议基于十神格局，实际选择还需结合个人兴趣、学历背景和大运流年的具体走势。</p>
  </div>`;

  // === 婚姻详细分析 ===
  const spousePalace = result.pillars[2].branch;
  const spouseWx = WX_DZ[result.dayBranchIdx];
  const dayWxMissing = result.wuxing.missing.map(m => m.wx);
  const dayWxOver = result.wuxing.overWang.map(o => o.wx);

  // Ideal partner wuxing
  let idealWx = [];
  if (dayWxMissing.length > 0) idealWx = dayWxMissing; // Missing elements → supplement
  else {
    // Generate (生) or same as day master
    const wxOrder = ["木","火","土","金","水"];
    const dayWxIdx = wxIdx(dayWx);
    idealWx.push(wxOrder[(dayWxIdx + 1) % 5]); // 我生的 (食伤)
    idealWx.push(wxOrder[(dayWxIdx + 4) % 5]); // 生我的 (印)
  }

  // Avoid partner wuxing
  let avoidWx = [];
  if (dayWxOver.length > 0) avoidWx = dayWxOver;
  else {
    const wxOrder = ["木","火","土","金","水"];
    const dayWxIdx = wxIdx(dayWx);
    avoidWx.push(wxOrder[(dayWxIdx + 2) % 5]); // 我克的 (财)
  }

  html += `<div class="analysis-block"><h4>💕 婚姻 — 详细分析</h4>
    <p>${interp.marriage}</p>
    <div style="margin:10px 0;padding:12px;background:var(--paper-cream);border-radius:8px">
      <p><strong>配偶宫：</strong>日支${spousePalace}（五行属${spouseWx}）</p>
      <p><strong>理想伴侣属性：</strong></p>
      <p style="font-size:0.9rem">✅ 五行宜<strong>${idealWx.join('、')}</strong>（${idealWx.map(w=>lifeWxDir[w]+'方位/'+lifeWxColor[w]).join('，')}），可互补命局不足，相互成就。</p>
      <p style="font-size:0.9rem">❌ 避免五行<strong>${avoidWx.join('、')}</strong>过旺的伴侣，易加剧命局失衡。</p>
      <p style="margin-top:8px;font-size:0.88rem"><strong>日干相合：</strong>与<strong>${TG_HE[result.dayMaster.stem]}</strong>日主之人缘分最深（天干五合），其次为同${dayWx}五行之人。</p>
      <p style="font-size:0.88rem"><strong>日支宜忌：</strong>${DZ_HE[spousePalace] ? `与<strong>${DZ_HE[spousePalace]}</strong>支之人六合，和谐稳定` : ''}${DZ_CHONG[spousePalace] ? `与<strong>${DZ_CHONG[spousePalace]}</strong>支之人六冲，需更多磨合（但不代表不能在一起，只是需要更多包容）` : ''}</p>
      <p style="font-size:0.88rem"><strong>🐲 对方适合属相：</strong></p>`;

  // Compute compatible and incompatible zodiac
  const myBranch = result.pillars[2].branch; // 日支
  const myBranchIdx = result.dayBranchIdx;
  const heZhi = DZ_HE[myBranch]; // 六合地支
  const chongZhi = DZ_CHONG[myBranch]; // 六冲地支
  const heZodiac = heZhi ? ZODIAC[DZ.indexOf(heZhi)] : '';
  const chongZodiac = chongZhi ? ZODIAC[DZ.indexOf(chongZhi)] : '';

  // Find 三合
  let sanHeZodiacs = [];
  for (const sh of DZ_SANHE) {
    if (sh.zhi.includes(myBranch)) {
      sanHeZodiacs = sh.zhi.filter(z => z !== myBranch).map(z => ZODIAC[DZ.indexOf(z)]);
      break;
    }
  }

  // Compute 相害 (mutual harm) - 子未害, 丑午害, 寅巳害, 卯辰害, 申亥害, 酉戌害
  const HAI_MAP = { "子":"未","未":"子","丑":"午","午":"丑","寅":"巳","巳":"寅","卯":"辰","辰":"卯","申":"亥","亥":"申","酉":"戌","戌":"酉" };
  const haiZhi = HAI_MAP[myBranch];
  const haiZodiac = haiZhi ? ZODIAC[DZ.indexOf(haiZhi)] : '';

  // Compute 相刑
  const xingTargets = DZ_XING[myBranch] || [];
  const xingZodiacs = xingTargets.map(z => ZODIAC[DZ.indexOf(z)]).filter(z => z && z !== chongZodiac && z !== haiZodiac);

  html += `<div style="margin:8px 0;padding:10px;background:var(--paper-cream);border-radius:6px">`;
  html += `<p style="font-size:0.85rem;margin:4px 0">
    ✅ <strong style="color:var(--jade)">配偶六合属相：</strong>属<strong>${heZodiac}</strong> — 地支六合，天作之合，缘分深厚，相处最和谐</p>`;
  if (sanHeZodiacs.length > 0) {
    html += `<p style="font-size:0.85rem;margin:4px 0">
    ✅ <strong style="color:var(--jade)">配偶三合属相：</strong>属<strong>${sanHeZodiacs.join('、')}</strong> — 三合为局，志趣相投，相互扶持</p>`;
  }

  html += `<p style="font-size:0.85rem;margin:4px 0">
    🔴 <strong style="color:var(--cinnabar)">配偶相冲属相：</strong>属<strong>${chongZodiac}</strong>（六冲）— 性格对立，易有冲突，需更多包容磨合。不代表不能在一起，许多冲中带合的夫妻反而感情更深</p>`;

  if (haiZodiac) {
    html += `<p style="font-size:0.85rem;margin:4px 0">
    🟠 <strong style="color:#e65100">配偶相害属相：</strong>属<strong>${haiZodiac}</strong>（相害）— 暗中不利，易因小事积累矛盾，需加强沟通</p>`;
  }

  if (xingZodiacs.length > 0) {
    html += `<p style="font-size:0.85rem;margin:4px 0">
    🟡 <strong style="color:var(--gold)">配偶相刑属相：</strong>属<strong>${xingZodiacs.join('、')}</strong>（相刑）— 相处需注意方式方法，避免因性格差异产生摩擦</p>`;
  }
  html += `</div>`;

  // Year branch based compatibility
  const yearBranch = result.pillars[0].branch;
  const yearHeZhi = DZ_HE[yearBranch];
  if (yearHeZhi && yearHeZhi !== heZhi) {
    html += `<p style="font-size:0.85rem;margin:4px 0">💡 年柱${yearBranch}六合属<strong>${ZODIAC[DZ.indexOf(yearHeZhi)]}</strong>，也可作为重要参考（祖辈/家庭层面的契合度）。</p>`;
  }

  html += `<p style="margin-top:8px;font-size:0.85rem;color:var(--text-muted)"><strong>💡 建议：</strong>选择五行互补、日干相合的伴侣，婚姻更为和谐。属相配对是重要参考，但感情是两个人的经营，命理只是辅助。</p>
    </div>
  </div>`;

  // === 财富详细分析 + 财运年份表 ===
  html += `<div class="analysis-block"><h4>💰 财富 — 详细分析</h4>
    <p>${interp.wealth}</p>
    <div style="margin:10px 0;padding:12px;background:var(--paper-cream);border-radius:8px">`;

  // Build wealth timeline from luck pillars
  html += `<p><strong>📅 财运走势表</strong></p>
    <div style="overflow-x:auto"><table class="paipan-table" style="font-size:0.82rem">
    <tr><th>年龄段</th><th>大运</th><th>十神</th><th>财运评级</th><th>说明</th></tr>`;

  result.dayun.luckPillars.forEach(lp => {
    const a = analyzeLuckPillar(result, lp, '');
    const wxIcon = { '吉':'🟢','平':'🟡','凶':'🔴' };
    html += `<tr>
      <td>${lp.range}</td><td>${lp.gz}</td><td>${a.tgName}</td>
      <td>${wxIcon[a.wealth.level]||'🟡'} ${a.wealth.level}</td>
      <td style="font-size:0.78rem">${a.wealth.text}</td>
    </tr>`;
  });
  html += `</table></div>`;

  // Wealth tips
  html += `<p style="margin-top:10px;font-size:0.88rem"><strong>💡 理财建议：</strong></p>`;
  const hasZhengCai = result.tenGods.some(t => t.name === '正财');
  const hasPianCai = result.tenGods.some(t => t.name === '偏财');
  const hasShiShen = result.tenGods.some(t => t.name === '食神');
  if (hasZhengCai || hasPianCai) {
    html += `<p style="font-size:0.85rem">• 命带财星，先天财运有基础。${hasZhengCai ? '以正途收入为主，适合长期积累。' : ''}${hasPianCai ? '投资运不错，但需控制风险。' : ''}</p>`;
  } else {
    html += `<p style="font-size:0.85rem">• 财星不显，财富需通过专业技能和长期积累获得。大运流年逢财运时把握机会。</p>`;
  }
  if (hasShiShen) html += `<p style="font-size:0.85rem">• 食神生财，技术/创意是主要收入来源，将爱好变现是最佳路径。</p>`;
  html += `<p style="font-size:0.85rem">• 在财运评级为<strong style="color:var(--jade)">吉</strong>的大运中积极进取；评级为<strong style="color:var(--cinnabar)">凶</strong>时以守为主，减少投资。</p>`;
  html += `<p style="font-size:0.85rem">• 财富的本质是价值的交换——提升自身价值才是最好的财运。</p>`;
  html += `</div></div>`;

  // === 健康详细分析 ===
  const wxColors2 = {"木":"#5b8c5a","火":"#d94a4a","土":"#c9a84c","金":"#9b9b9b","水":"#4a90d9"};
  const wxHealth = {
    "木": { organ:"肝胆", symptom:"头痛、眼睛干涩、情绪抑郁、筋骨酸痛", advice:"保持情绪舒畅，避免长期压抑；多做伸展运动（瑜伽、太极）；23:00前入睡以养肝血；多吃绿色蔬菜、枸杞、菊花茶", season:"春季", time:"23:00-03:00" },
    "火": { organ:"心脏/小肠", symptom:"心悸、失眠、口腔溃疡、血压波动", advice:"保持心态平和，避免情绪大起大落；适当出汗（运动）；午间小憩养心；多吃红色食物、苦味食物", season:"夏季", time:"11:00-15:00" },
    "土": { organ:"脾胃", symptom:"消化不良、胃胀、食欲不振、四肢乏力", advice:"饮食规律，少食多餐；避免生冷油腻；饭后散步助消化；多吃黄色食物（小米、南瓜、山药）", season:"长夏", time:"07:00-11:00" },
    "金": { organ:"肺/大肠", symptom:"咳嗽、气喘、皮肤干燥、便秘", advice:"深呼吸练习（腹式呼吸）；避免吸烟和空气污染；多喝水润肺；多吃白色食物（梨、百合、银耳）", season:"秋季", time:"03:00-07:00" },
    "水": { organ:"肾/膀胱", symptom:"腰膝酸软、耳鸣、畏寒、泌尿问题", advice:"注意腰部保暖；避免过度劳累和熬夜；节制房事以养肾精；多吃黑色食物（黑豆、黑芝麻、海带）", season:"冬季", time:"17:00-19:00" },
  };

  html += `<div class="analysis-block"><h4>🏥 健康 — 详细分析</h4>
    <p>${interp.health}</p>

    <div style="margin:12px 0;padding:12px;background:var(--paper-cream);border-radius:8px">
    <p><strong>🔬 五行—脏腑对应分析</strong></p>
    <div style="overflow-x:auto"><table class="paipan-table" style="font-size:0.82rem">
    <tr><th>五行</th><th>数量</th><th>状态</th><th>对应脏腑</th><th>易出现症状</th><th>养生要点</th></tr>`;

  const wxOrder2 = ["木","火","土","金","水"];
  wxOrder2.forEach(wx => {
    const cnt = result.wuxing.counts[wx];
    let status = cnt >= 4 ? '🔴 过旺' : cnt === 0 ? '⚠ 缺失' : '🟢 平衡';
    const info = wxHealth[wx];
    html += `<tr>
      <td><strong style="color:${wxColors2[wx]}">${wx}</strong></td>
      <td>${cnt}</td><td>${status}</td>
      <td>${info.organ}</td>
      <td style="font-size:0.75rem">${info.symptom}</td>
      <td style="font-size:0.75rem">${info.advice.substring(0,40)}…</td>
    </tr>`;
  });
  html += `</table></div></div>`;

  // Key concerns
  html += `<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:10px 0">`;
  if (result.wuxing.overWang.length > 0) {
    html += `<div style="padding:10px;background:#fce4ec;border-radius:6px">
      <strong style="color:#c62828">🔴 重点关注的脏腑</strong>
      <ul style="margin:4px 0 0 16px;font-size:0.85rem">`;
    result.wuxing.overWang.forEach(o => {
      const info = wxHealth[o.wx];
      html += `<li><strong>${o.wx}(${o.cnt})过旺→${info.organ}</strong>：${info.symptom}</li>`;
    });
    html += `</ul></div>`;
  }
  if (result.wuxing.missing.length > 0) {
    html += `<div style="padding:10px;background:#e3f2fd;border-radius:6px">
      <strong style="color:#1565c0">⚠ 需后天补足的脏腑</strong>
      <ul style="margin:4px 0 0 16px;font-size:0.85rem">`;
    result.wuxing.missing.forEach(m => {
      const info = wxHealth[m.wx];
      html += `<li><strong>${m.wx}(缺失)→${info.organ}</strong>：${info.advice}</li>`;
    });
    html += `</ul></div>`;
  }
  html += `</div>`;

  // Health timeline from luck pillars
  html += `<div style="margin:12px 0"><p><strong>📅 健康走势表</strong></p>
    <div style="overflow-x:auto"><table class="paipan-table" style="font-size:0.82rem">
    <tr><th>年龄段</th><th>大运</th><th>五行</th><th>健康评级</th><th>说明</th></tr>`;
  result.dayun.luckPillars.forEach(lp => {
    const a = analyzeLuckPillar(result, lp, '');
    const wxIcon = { '吉':'🟢','平':'🟡','凶':'🔴' };
    html += `<tr>
      <td>${lp.range}</td><td>${lp.gz}</td><td>${WX_TG[lp.stemIdx]}+${WX_DZ[lp.branchIdx]}</td>
      <td>${wxIcon[a.health.level]||'🟡'} ${a.health.level}</td>
      <td style="font-size:0.78rem">${a.health.text}</td>
    </tr>`;
  });
  html += `</table></div></div>`;

  // 养生建议
  html += `<div style="margin:10px 0;padding:12px;background:var(--paper-cream);border-radius:8px">
    <p><strong>💡 综合养生建议</strong></p>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:0.85rem">`;
  wxOrder2.forEach(wx => {
    const cnt = result.wuxing.counts[wx];
    const info = wxHealth[wx];
    if (cnt >= 4 || cnt === 0) {
      html += `<div style="padding:8px;background:var(--paper-light);border-radius:4px">
        <strong style="color:${wxColors2[wx]}">${wx}·${info.organ}：</strong>
        ${cnt >= 4 ? `过旺，注意${info.season}${info.time}时段的保养` : `缺失，宜${info.season}重点调养`}
        <br><span style="font-size:0.8rem;color:var(--text-muted)">${info.advice}</span>
      </div>`;
    }
  });
  html += `</div>
    <p style="margin-top:8px;font-size:0.85rem;color:var(--text-muted)">
    养生核心原则：<strong>过则泄之，虚则补之</strong>。${result.strength.level === '身强' ? '身强者宜多运动、多出汗、保持新陈代谢旺盛。' : '身弱者宜静养、不妄作劳、注重睡眠质量。'}建议定期体检，保持规律作息，心态平和是最好的养生。
    </p>
  </div></div>`;

  // 贵人方位（终身）
  html += `<div class="analysis-block"><h4>🙏 终身贵人方位</h4>
    <p>日主五行属<strong>${dayWx}</strong>，贵人方位在<strong>${lifeWxDir[dayWx]}</strong>，
    宜着<strong>${lifeWxColor[dayWx]}</strong>衣物，多关注该方位的人脉和机会。
    ${result.wuxing.missing.length > 0 ? `命局缺<strong>${result.wuxing.missing.map(m=>m.wx).join('、')}</strong>，可通过对应方位/颜色/行为补足。` : ''}
    ${result.wuxing.overWang.length > 0 ? `命局<strong>${result.wuxing.overWang.map(o=>o.wx).join('、')}</strong>过旺，避免过度强化该五行。` : ''}
  </p></div>`;

  html += `<div class="analysis-block"><h4>⚠ 注意事项</h4>
    <p>• 以上分析基于出生时间的惯性特征，反映的是概率趋势，并非绝对。</p>
    <p>• 后天努力和选择同样重要，了解命理是为了顺应时运、补足缺陷。</p>
    <p>• 重要决策请结合实际情况综合判断，命理仅供辅助参考。</p></div>`;

  // Export button at bottom-right
  html += `<div style="text-align:right;margin-top:16px">
    <button class="btn-export" onclick="exportToPDF()" style="padding:10px 24px;font-size:0.9rem">📄 导出PDF报告</button>
  </div>`;

  return html;
}

function calcTenGodRelation(dayStemIdx, otherStemIdx) {
  if (dayStemIdx === otherStemIdx) return 0; // 比肩
  const dayWx = WX_TG[dayStemIdx], otherWx = WX_TG[otherStemIdx];
  const dayYy = YY_TG[dayStemIdx], otherYy = YY_TG[otherStemIdx];
  const wxDiff = (wxIdx(otherWx) - wxIdx(dayWx) + 5) % 5;
  const sameYY = dayYy === otherYy;
  if (wxDiff === 0) return sameYY ? 0 : 1;
  if (wxDiff === 1) return sameYY ? 2 : 3;
  if (wxDiff === 2) return sameYY ? 4 : 5;
  if (wxDiff === 3) return sameYY ? 7 : 6;
  return sameYY ? 9 : 8;
}

// ============================================================
//  SECTION 16: MULTI-PLAYER COMPARISON RENDERING
// ============================================================

function renderMultiResults(results, relType) {
  const panel = document.getElementById('result-panel');
  const tabBar = document.getElementById('tab-bar');
  const tabContents = document.getElementById('tab-contents');
  const compat = calcCompatibility(results[0], results[1], relType);

  const tabs = [
    { id:'tab-m-paipan', label:'📜 八字合盘', content: renderMultiPaipan(results, compat, relType) },
    { id:'tab-m-shishen', label:'🔟 十神合盘', content: renderMultiShishen(results) },
    { id:'tab-m-chonghe', label:'⚡ 冲合合盘', content: renderMultiChongHe(results, compat) },
    { id:'tab-m-dayun', label:'🕐 大运合盘', content: renderMultiDayun(results) },
    { id:'tab-m-shensha', label:'⭐ 神煞合盘', content: renderMultiShensha(results) },
    { id:'tab-m-zonghe', label:'💡 综合建议', content: renderMultiZonghe(results, compat, relType) },
  ];

  tabBar.innerHTML = tabs.map((t,i) =>
    `<button class="tab-btn${i===0?' active':''}" onclick="switchTab('${t.id}', this)">${t.label}</button>`
  ).join('');

  tabContents.innerHTML = tabs.map((t,i) =>
    `<div class="tab-content${i===0?' active':''}" id="${t.id}">${t.content}</div>`
  ).join('');

  panel.classList.add('visible');
  panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ====== Multi-mode combined renderers ======

function renderMultiPaipan(results, compat, relType) {
  let html = '';
  // Compatibility score header
  html += '<div class="compat-score-ring"><div class="ring-label">' + relType + ' — 综合兼容度</div>';
  html += '<div class="ring-value">' + compat.overall + '<span style="font-size:1.2rem">/100</span></div>';
  html += '<div style="font-size:1.2rem;color:var(--gold);letter-spacing:3px">' + compat.level + '</div></div>';

  // Score bars with icon design
  html += '<div style="margin:16px 0">';
  var barConfig = [
    { key:'wuxing', label:'五行互补', icon:'🌿', color:'#5b8c5a' },
    { key:'chongHe', label:'冲合和谐', icon:'⚡', color:'#c9a84c' },
    { key:'tenGod', label:'十神互涉', icon:'🔗', color:'#3a6186' },
    { key:'shensha', label:'神煞匹配', icon:'⭐', color:'#8b6914' }
  ];
  barConfig.forEach(function(cfg) {
    var val = compat.scores[cfg.key] || 50;
    var barColor = val >= 70 ? 'var(--jade)' : val >= 50 ? 'var(--gold)' : 'var(--cinnabar)';
    html += '<div style="display:flex;align-items:center;gap:10px;padding:4px 10px;margin:4px 0;background:var(--paper-light);border-radius:6px">';
    html += '<span style="font-size:1.1rem;width:26px;text-align:center">' + cfg.icon + '</span>';
    html += '<span style="width:75px;font-weight:bold;font-size:0.85rem;color:' + cfg.color + '">' + cfg.label + '</span>';
    html += '<span style="width:28px;text-align:center;font-family:var(--font-title);font-size:1rem;color:' + cfg.color + '">' + val + '</span>';
    html += '<div style="flex:1;height:14px;background:#ebe2cf;border-radius:7px;overflow:hidden"><div style="width:' + val + '%;height:100%;background:' + barColor + ';border-radius:7px;transition:width 0.6s ease"></div></div>';
    html += '<span style="font-size:0.75rem;color:var(--ink-light);min-width:30px">' + val + '/100</span>';
    html += '</div>';
  });
  html += '</div>';

  // Side-by-side paipan
  html += '<div class="compare-grid">';
  results.forEach(function(r) {
    html += '<div class="compare-panel"><h4>' + r.name + ' — ' + r.ganZao + '</h4>';
    html += '<div style="text-align:center;font-family:var(--font-heading);letter-spacing:2px;margin:8px 0;font-size:0.95rem">' + r.paipanStr + '</div>';
    // Mini four-pillar table
    html += '<table class="paipan-table" style="font-size:0.78rem"><tr><th></th>';
    r.pillars.forEach(function(p) { html += '<th>' + p.name + '</th>'; });
    html += '</tr><tr><td>天干</td>';
    r.pillars.forEach(function(p) { html += '<td>' + p.stem + '</td>'; });
    html += '</tr><tr><td>地支</td>';
    r.pillars.forEach(function(p) { html += '<td>' + p.branch + '</td>'; });
    html += '</tr><tr><td>十神</td>';
    r.tenGods.forEach(function(t) { html += '<td style="font-size:0.75rem">' + t.short + '</td>'; });
    html += '</tr><tr><td>纳音</td>';
    r.pillars.forEach(function(p) { html += '<td style="font-size:0.7rem;color:var(--text-muted)">' + p.nayin + '</td>'; });
    html += '</tr></table>';
    // Wuxing bars
    html += '<div style="margin:8px 0">';
    var wxColors2 = {"木":"#5b8c5a","火":"#d94a4a","土":"#c9a84c","金":"#9b9b9b","水":"#4a90d9"};
    ["木","火","土","金","水"].forEach(function(k) {
      var cnt = r.wuxing.counts[k];
      html += '<div style="display:flex;align-items:center;gap:6px;margin:2px 0;font-size:0.75rem"><span style="width:16px;color:' + wxColors2[k] + '">' + k + '</span><span style="width:14px">' + cnt + '</span><div style="flex:1;height:10px;background:var(--paper-dark);border-radius:5px"><div style="width:' + Math.round(cnt/8*100) + '%;height:100%;background:' + wxColors2[k] + ';border-radius:5px"></div></div></div>';
    });
    html += renderWuxingChart(r.wuxing.counts);
    html += '</div></div>';
  });
  html += '</div>';

  // === 详细合盘分析 ===
  html += '<div class="analysis-block"><h4>🔍 合盘详细解读</h4>';

  // Analyze each highlight with good/bad/impact
  compat.highlights.forEach(function(h) {
    var level = 'info', icon = '💡', impact = '';
    if (h.includes('互补')) { level = 'good'; icon = '✅'; impact = '五行互补是最理想的配合模式，双方缺失的元素互相补足，命局趋于平衡，各方面运势都会提升。'; }
    else if (h.includes('相冲')) { level = 'bad'; icon = '⚠️'; impact = '相冲代表对立和冲突，在相处中容易产生摩擦。影响的领域取决于相冲的柱位——日柱相冲影响感情核心，月柱相冲影响事业和家庭观念，年柱相冲影响家族和长远规划。但冲不代表不能在一起，主动求变、保持适度距离反而能化解冲力。'; }
    else if (h.includes('相合') || h.includes('五合') || h.includes('六合')) { level = 'good'; icon = '✅'; impact = '相合代表和谐与吸引力，缘分深厚。合得好的双方沟通顺畅、配合默契。但需注意：合过度也可能导致互相牵绊、失去独立性。'; }
    else if (h.includes('逢冲') || h.includes('不稳')) { level = 'bad'; icon = '⚠️'; impact = '婚姻宫/自我宫逢冲，代表核心关系容易波动。建议晚婚、保持适度个人空间，或在变动中寻求平衡（如异地发展、经常出差等）。'; }
    else if (h.includes('过旺') || h.includes('同气相争')) { level = 'bad'; icon = '⚠️'; impact = '双方同一五行过旺，同气相争，容易在相关领域产生竞争而非合作。需要有意识地在角色分工上做出区隔。'; }
    else { impact = '此项发现值得关注，具体影响需结合双方大运流年的具体走势来判断。'; }
    var badge = level === 'good' ? '<span style=\"color:var(--jade)\">【有利】</span>' : level === 'bad' ? '<span style=\"color:var(--cinnabar)\">【需注意】</span>' : '<span style=\"color:var(--gold)\">【参考】</span>';
    html += '<div style=\"margin:10px 0;padding:12px;background:' + (level === 'good' ? '#e8f5e9' : level === 'bad' ? '#fef5f5' : '#faf7f0') + ';border-radius:8px;border-left:3px solid ' + (level === 'good' ? 'var(--jade)' : level === 'bad' ? 'var(--cinnabar)' : 'var(--gold)') + '\">';
    html += '<p><strong>' + icon + ' ' + badge + ' ' + h + '</strong></p>';
    html += '<p style=\"font-size:0.85rem;color:var(--text-secondary);margin-top:4px\">' + impact + '</p>';
    html += '</div>';
  });

  // Score interpretation
  html += '<div style=\"margin-top:12px;padding:12px;background:var(--paper-cream);border-radius:8px\">';
  html += '<p><strong>📊 综合评分解读：</strong></p>';
  if (compat.overall >= 80) html += '<p style=\"font-size:0.88rem\">综合评分<strong style=\"color:var(--jade)\">' + compat.overall + '分</strong>，属于<strong>极佳配合</strong>。两人在五行、冲合、十神、神煞四个维度上都较为匹配，是天作之合的组合。适合长期合作或婚姻关系。</p>';
  else if (compat.overall >= 70) html += '<p style=\"font-size:0.88rem\">综合评分<strong style=\"color:var(--jade)\">' + compat.overall + '分</strong>，属于<strong>良好配合</strong>。大部分维度匹配较好，只需在个别方面稍加注意和调整。适合深入发展关系。</p>';
  else if (compat.overall >= 60) html += '<p style=\"font-size:0.88rem\">综合评分<strong style=\"color:var(--gold)\">' + compat.overall + '分</strong>，属于<strong>一般配合</strong>。有一些有利的匹配点，也有一些需要磨合的地方。关系需要双方共同努力经营，求同存异。</p>';
  else if (compat.overall >= 50) html += '<p style=\"font-size:0.88rem\">综合评分<strong style=\"color:var(--cinnabar)\">' + compat.overall + '分</strong>，属于<strong>需磨合</strong>。存在较多不匹配的维度，需要更多的包容和理解。建议先以朋友或合作伙伴的方式相处，给彼此足够的时间磨合。</p>';
  else html += '<p style=\"font-size:0.88rem\">综合评分<strong style=\"color:var(--cinnabar)\">' + compat.overall + '分</strong>，属于<strong>挑战较大</strong>。关键维度上存在较多冲突。如果已经在一起，建议各自保持独立性，避免过度捆绑。如果还在考虑阶段，建议三思而后行。</p>';
  html += '</div>';
  html += '</div>';

  return html;
}

function renderMultiShishen(results) {
  let html = '';
  var a = results[0], b = results[1];
  var relIdx = calcTenGodRelation(a.dayStemIdx, b.dayStemIdx);
  var relIdx2 = calcTenGodRelation(b.dayStemIdx, a.dayStemIdx);

  // === Header ===
  html += '<div class="analysis-block"><h4>🔗 十神互涉核心</h4>';
  html += '<p>' + a.name + '日主<strong>' + a.dayMaster.stem + '(' + wxOf(a.dayMaster.stem) + ')</strong> ← → ' + b.name + '日主<strong>' + b.dayMaster.stem + '(' + wxOf(b.dayMaster.stem) + ')</strong></p>';
  html += '</div>';

  // === 1. 双向匹配分析 ===
  html += '<div class="analysis-block"><h4>📊 双向匹配分析</h4>';

  // A→B
  var infoA = getTenGodRelInfo(relIdx, a.name, b.name);
  var levelA = infoA.level;
  html += '<div style="margin:10px 0;padding:14px;background:' + (levelA==='good'?'#e8f5e9':levelA==='bad'?'#fef5f5':'#faf7f0') + ';border-radius:8px;border-left:4px solid ' + (levelA==='good'?'var(--jade)':levelA==='bad'?'var(--cinnabar)':'var(--gold)') + '">';
  html += '<h5 style="margin:0 0 6px 0">' + a.name + ' → ' + b.name + '：' + SHISHEN_FULL[relIdx] + '关系 ' + (levelA==='good'?'✅ 匹配':levelA==='bad'?'⚠️ 互斥':'🟡 中性') + '</h5>';
  html += '<p style="font-size:0.85rem">' + infoA.desc + '</p>';
  html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px">';
  html += '<div style="font-size:0.82rem"><strong style="color:var(--jade)">✅ 优点：</strong>' + getAdvantage(relIdx, a.name, b.name) + '</div>';
  html += '<div style="font-size:0.82rem"><strong style="color:var(--cinnabar)">⚠️ 需注意：</strong>' + getRisk(relIdx, a.name, b.name) + '</div>';
  html += '</div></div>';

  // B→A
  var infoB = getTenGodRelInfo(relIdx2, b.name, a.name);
  var levelB = infoB.level;
  html += '<div style="margin:10px 0;padding:14px;background:' + (levelB==='good'?'#e8f5e9':levelB==='bad'?'#fef5f5':'#faf7f0') + ';border-radius:8px;border-left:4px solid ' + (levelB==='good'?'var(--jade)':levelB==='bad'?'var(--cinnabar)':'var(--gold)') + '">';
  html += '<h5 style="margin:0 0 6px 0">' + b.name + ' → ' + a.name + '：' + SHISHEN_FULL[relIdx2] + '关系 ' + (levelB==='good'?'✅ 匹配':levelB==='bad'?'⚠️ 互斥':'🟡 中性') + '</h5>';
  html += '<p style="font-size:0.85rem">' + infoB.desc + '</p>';
  html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px">';
  html += '<div style="font-size:0.82rem"><strong style="color:var(--jade)">✅ 优点：</strong>' + getAdvantage(relIdx2, b.name, a.name) + '</div>';
  html += '<div style="font-size:0.82rem"><strong style="color:var(--cinnabar)">⚠️ 需注意：</strong>' + getRisk(relIdx2, b.name, a.name) + '</div>';
  html += '</div></div>';
  html += '</div>';

  // === 2. 匹配度总评 ===
  html += '<div class="analysis-block"><h4>📈 匹配度总评</h4>';
  var bothGood = (levelA==='good'||levelA==='neutral') && (levelB==='good'||levelB==='neutral');
  var bothBad = levelA==='bad' && levelB==='bad';
  var mixed = !bothGood && !bothBad;

  if (bothGood) {
    html += '<div style="padding:12px;background:#e8f5e9;border-radius:8px">';
    html += '<p><strong style="color:var(--jade)">🟢 双向利好</strong> — 双方互为吉神，十神层面匹配度很高。</p>';
    html += '<ul style="font-size:0.85rem;margin:6px 0 0 16px"><li>互相是对方的贵人或福星，天然有互助倾向</li><li>关系稳定，适合长期发展</li><li>在各自擅长的领域能给对方带来实质帮助</li></ul></div>';
  } else if (bothBad) {
    html += '<div style="padding:12px;background:#fef5f5;border-radius:8px">';
    html += '<p><strong style="color:var(--cinnabar)">🔴 双向挑战</strong> — 双方互为忌神，十神层面存在较大张力。</p>';
    html += '<ul style="font-size:0.85rem;margin:6px 0 0 16px"><li>双方都可能感受到来自对方的压力</li><li>需要更多的时间和空间来磨合</li><li>建议通过共同的第三方（事业、家庭、兴趣）来缓冲</li></ul></div>';
  } else {
    html += '<div style="padding:12px;background:#faf7f0;border-radius:8px">';
    html += '<p><strong style="color:var(--gold)">🟡 混合态势</strong> — 一方有利一方中性或不利，十神关系存在不对等。</p>';
    html += '<ul style="font-size:0.85rem;margin:6px 0 0 16px"><li>有利方宜多包容和付出，不利方宜多感恩和调整</li><li>如果双方都愿意为关系努力，可以达到动态平衡</li><li>十神层面只是参考，大运流年可以改善互涉关系</li></ul></div>';
  }
  html += '</div>';

  // === 3. 改善建议 ===
  html += '<div class="analysis-block"><h4>💡 十神互涉改善建议</h4>';
  html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">';

  // Matching actions
  html += '<div style="padding:10px;background:#e8f5e9;border-radius:6px">';
  html += '<strong style="color:var(--jade)">✅ 发挥匹配优势</strong>';
  html += '<ul style="margin:4px 0 0 16px;font-size:0.82rem">';
  if (relIdx === 5 || relIdx === 6 || relIdx === 8 || relIdx === 2) {
    html += '<li>' + a.name + '对' + b.name + '有天然的好感/照顾倾向，可主动多承担</li>';
  }
  if (relIdx2 === 5 || relIdx2 === 6 || relIdx2 === 8 || relIdx2 === 2) {
    html += '<li>' + b.name + '对' + a.name + '有天然的好感/照顾倾向，可主动多承担</li>';
  }
  if (relIdx === 0 || relIdx2 === 0) html += '<li>比肩关系适合平等协作，如朋友般的相处模式最自然</li>';
  html += '<li>利用各自的十神优势分工——印旺者多谋划、食伤旺者多创意、官杀旺者多执行</li>';
  html += '</ul></div>';

  // Conflict resolution
  html += '<div style="padding:10px;background:#fef5f5;border-radius:6px">';
  html += '<strong style="color:var(--cinnabar)">⚠️ 缓解互斥张力</strong>';
  html += '<ul style="margin:4px 0 0 16px;font-size:0.82rem">';
  if (relIdx === 1 || relIdx === 7) {
    html += '<li>' + a.name + '感受到压力时，' + b.name + '宜给予更多空间和理解</li>';
  }
  if (relIdx2 === 1 || relIdx2 === 7) {
    html += '<li>' + b.name + '感受到压力时，' + a.name + '宜给予更多空间和理解</li>';
  }
  html += '<li>建立清晰的边界——财务、时间、个人空间各自独立</li>';
  html += '<li>定期坦诚沟通，避免小问题积累成大矛盾</li>';
  html += '<li>大运流年带来的十神变化会动态改变互涉关系，耐心等待有利时机</li>';
  html += '</ul></div>';
  html += '</div></div>';

  // === 4. 十神互涉总结 ===
  html += '<div class="analysis-block"><h4>📝 互涉总结</h4>';
  html += '<p style="font-size:0.9rem">' + getMutualSummary(relIdx, relIdx2) + '</p>';
  html += '<p style="font-size:0.82rem;color:var(--text-muted);margin-top:6px">十神互涉是合盘分析中最核心的维度——它揭示了两人在对方命局中的角色定位：是贵人还是压力、是福星还是竞争者。理解这层关系，就能更好地调整相处模式，扬长避短。</p>';
  html += '</div>';
  return html;
}

function getAdvantage(idx, viewer, target) {
  var adv = {
    0: '平等相待，互相尊重，如兄弟/姐妹般自然。适合做朋友或合作伙伴',
    1: '清楚彼此的底线，反而能在规则明确的前提下高效合作',
    2: viewer + '对' + target + '有天然的好感和照顾意愿，付出时感到快乐',
    3: viewer + '欣赏' + target + '的才华，可以激发' + target + '的创造力和表现力',
    4: viewer + '会被' + target + '吸引，有较强的动力去经营这段关系',
    5: viewer + '珍惜和重视' + target + '，愿意长期投入。关系稳定持久',
    6: target + '能引导和规范' + viewer + '，帮助' + viewer + '成长和进步',
    7: target + '的严格要求能激发' + viewer + '的潜力，在压力下快速成长',
    8: target + '是' + viewer + '的贵人和庇护者，给予无私的帮助和支持',
    9: target + '能给' + viewer + '带来独特的视角和思维方式',
  };
  return adv[idx] || '关系复杂，需具体分析';
}

function getRisk(idx, viewer, target) {
  var risk = {
    0: '双方都好强时容易互不相让，需避免硬碰硬。利益分配需明确',
    1: viewer + '需注意财务边界，避免因金钱产生矛盾。可能有第三方介入风险',
    2: viewer + '可能过度付出导致自身压力。' + target + '需懂得感恩和回报',
    3: viewer + '可能对' + target + '要求过高、挑剔过多，需学会包容和欣赏',
    4: viewer + '需注意不过度控制' + target + '，给对方足够的自由空间',
    5: viewer + '需注意不拘泥于物质层面，也要关注精神层面的交流',
    6: '约束不能变成压制——' + target + '需注意方式方法，' + viewer + '需保持自主性',
    7: viewer + '在' + target + '面前易感到压力，需足够的心理承受力。' + target + '宜适当放权',
    8: viewer + '可能过度依赖' + target + '，需培养独立性。' + target + '不宜包办代替',
    9: viewer + '可能不太感激' + target + '的付出。帮助的方式需调整，多沟通',
  };
  return risk[idx] || '需具体分析双方的互动模式';
}

function getTenGodRelInfo(idx, viewer, target) {
  var info = {
    0: { level:'neutral', desc: target + '的日干与' + viewer + '相同五行且同阴阳，为<strong>比肩</strong>关系。两人性格相似，如兄弟/姐妹般平等相待。', impact:'适合做朋友或合作伙伴。但如果双方都太好强，容易互不相让。在婚姻中，比肩关系意味着势均力敌的平等关系。' },
    1: { level:'bad', desc: target + '的日干与' + viewer + '相同五行但异阴阳，为<strong>劫财</strong>关系。劫财代表竞争、争夺，' + viewer + '可能感受到来自' + target + '的竞争压力。', impact:'在财务上需要特别注意界限分明；在感情中可能有第三方介入的风险；合作时容易因利益分配产生矛盾。需要明确的规则和边界。' },
    2: { level:'good', desc: target + '的日干是' + viewer + '日干所生（同阴阳），为<strong>食神</strong>关系。' + viewer + '对' + target + '有天然的照顾和付出的意愿。', impact:'食神是福星，' + target + '能给' + viewer + '带来舒适和快乐的感觉。在婚姻中是很好的组合，一方愿意付出，一方懂得享受和回报。适合师生、师徒、服务与被服务的关系。' },
    3: { level:'neutral', desc: target + '的日干是' + viewer + '日干所生（异阴阳），为<strong>伤官</strong>关系。' + viewer + '对' + target + '既有欣赏也有挑剔。', impact:'伤官代表才华也代表挑剔。' + viewer + '可能会对' + target + '要求较高，容易产生批评和不满。但如果能转化为建设性的意见，反而能促进彼此成长。需要' + viewer + '学会包容，' + target + '学会接受反馈。' },
    4: { level:'good', desc: target + '的日干被' + viewer + '日干所克（同阴阳），为<strong>偏财</strong>关系。' + viewer + '对' + target + '有掌控力和吸引力。', impact:'偏财代表意外的收获和吸引力。在感情中，' + viewer + '会被' + target + '吸引，有较强的占有欲。在合作中，' + viewer + '适合主导商业运作。需要注意不过度控制对方。' },
    5: { level:'good', desc: target + '的日干被' + viewer + '日干所克（异阴阳），为<strong>正财</strong>关系。' + viewer + '视' + target + '为值得珍惜的财富。', impact:'正财是最理想的夫妻十神关系之一。' + viewer + '会珍惜和重视' + target + '，愿意为对方提供物质和情感上的支持。关系稳定持久，适合长期婚姻和商业合作。' },
    6: { level:'good', desc: target + '的日干克制' + viewer + '日干（异阴阳），为<strong>正官</strong>关系。' + target + '对' + viewer + '有约束和引导的作用。', impact:'正官代表规则、责任和权威。在婚姻中这是传统\"夫官\"关系的体现，一方愿意被另一方约束和引导。在职场中是很好的上下级关系。需要注意约束不能变成压制。' },
    7: { level:'bad', desc: target + '的日干克制' + viewer + '日干（同阴阳），为<strong>七杀</strong>关系。' + target + '给' + viewer + '带来压力和挑战。', impact:'七杀代表压力、竞争和疾病。' + viewer + '在' + target + '面前可能感到紧张和压力。但如果' + viewer + '身强，七杀反而能激发斗志和成长。在婚姻中，七杀关系需要' + viewer + '有足够的承受力，否则容易产生压抑感。' },
    8: { level:'good', desc: target + '的日干生扶' + viewer + '日干（异阴阳），为<strong>正印</strong>关系。' + target + '是' + viewer + '的贵人和庇护者。', impact:'正印代表贵人、学识和庇护。' + target + '会自然地关照和帮助' + viewer + '。这是最理想的支持关系——在婚姻中是很好的\"相敬如宾\"模式，在职场中是导师和学生的关系。需要注意不过度依赖。' },
    9: { level:'neutral', desc: target + '的日干生扶' + viewer + '日干（同阴阳），为<strong>偏印</strong>关系。' + target + '给' + viewer + '的帮助有时不被认可。', impact:'偏印的帮助带有一定的疏离感和不确定性。' + viewer + '可能不太感激' + target + '的付出，或者帮助的方式不太对路。需要双方更多沟通和理解，明确表达各自的需求。' },
  };
  return info[idx] || { level:'neutral', desc:'关系较为复杂', impact:'建议结合具体命局深入分析' };
}

function getMutualSummary(idx1, idx2) {
  var bothGood = (idx1 === 5 || idx1 === 6 || idx1 === 8 || idx1 === 2 || idx1 === 4) && (idx2 === 5 || idx2 === 6 || idx2 === 8 || idx2 === 2 || idx2 === 4);
  var bothBad = (idx1 === 1 || idx1 === 7 || idx1 === 9) && (idx2 === 1 || idx2 === 7 || idx2 === 9);
  var oneGoodOneBad = (idx1 === 5 || idx1 === 6 || idx1 === 8) && (idx2 === 1 || idx2 === 7) || (idx2 === 5 || idx2 === 6 || idx2 === 8) && (idx1 === 1 || idx1 === 7);

  if (bothGood) return '双方互为吉神，是难得的好组合。互相滋养、互相成就，关系稳定且能长期发展。';
  if (bothBad) return '双方互为忌神，关系挑战较大。建议保持适度距离，或通过共同的第三方（朋友/家人/事业纽带）来缓冲直接冲突。明确各自的边界和期望非常重要。';
  if (oneGoodOneBad) return '一方有利一方不利，关系中存在不对等。有利方需要更多包容和付出，不利方需要更多感恩和调整。如果双方都愿意为关系努力，可以达到动态平衡。';
  return '双方关系较为复杂，既有利好也有挑战。关键是找到彼此都能接受的相处模式。';
}

function renderMultiChongHe(results, compat) {
  let html = '';
  var a = results[0], b = results[1];

  // Summary table
  html += '<div class="analysis-block"><h4>📊 四柱冲合总览</h4>';
  html += '<div style="overflow-x:auto"><table class="paipan-table" style="font-size:0.82rem"><tr><th>柱位</th><th>' + a.name + '</th><th>' + b.name + '</th><th>关系</th><th>评级</th></tr>';
  var heCount = 0, chongCount = 0;
  for (var i = 0; i < 4; i++) {
    var pA = a.pillars[i], pB = b.pillars[i];
    var rel = '—', rating = '平', rColor = 'var(--text-muted)';
    if (TG_HE[pA.stem] === pB.stem) { rel = '天干五合→化' + TG_HE_HUA[pA.stem]; rating = '🟢合'; rColor = 'var(--jade)'; heCount++; }
    else if (DZ_HE[pA.branch] === pB.branch) { rel = '地支六合'; rating = '🟢合'; rColor = 'var(--jade)'; heCount++; }
    else if (DZ_CHONG[pA.branch] === pB.branch) { rel = '地支六冲'; rating = '🔴冲'; rColor = 'var(--cinnabar)'; chongCount++; }
    else if (WX_TG[pA.stemIdx] === WX_TG[pB.stemIdx]) { rel = '五行相同'; rating = '🟡同'; rColor = 'var(--gold)'; }
    html += '<tr><td>' + pA.name + '</td><td>' + pA.gz + '</td><td>' + pB.gz + '</td><td style="color:' + rColor + '">' + rel + '</td><td>' + rating + '</td></tr>';
  }
  html += '</table></div>';
  html += '<p style="font-size:0.85rem;margin-top:8px">冲合统计：🟢相合 <strong>' + heCount + '</strong>组 | 🔴相冲 <strong>' + chongCount + '</strong>组 | 🟡其他 <strong>' + (4-heCount-chongCount) + '</strong>组</p>';
  html += '</div>';

  // === 相合关系 — 和谐与羁绊 ===
  html += '<div class="analysis-block"><h4>🟢 相合关系 — 和谐与羁绊</h4>';
  var hasHe = false;
  for (var i = 0; i < 4; i++) {
    var pA = a.pillars[i], pB = b.pillars[i];
    if (TG_HE[pA.stem] === pB.stem) {
      hasHe = true;
      html += '<div style="margin:10px 0;padding:14px;background:#e8f5e9;border-radius:8px;border-left:3px solid var(--jade)">';
      html += '<p><strong>✅ ' + pA.name + '天干五合：' + pA.stem + '合' + pB.stem + '→化' + TG_HE_HUA[pA.stem] + '</strong></p>';
      html += '<p style="font-size:0.85rem;color:var(--text-secondary)">天干五合是外在的人际吸引与互动。' + pA.stem + '与' + pB.stem + '相合化' + TG_HE_HUA[pA.stem] + '，代表两人在' + pA.name + '层面有天然的默契与吸引力。</p>';
      html += '<p style="font-size:0.82rem;color:var(--text-muted)"><strong>影响：</strong>';
      if (pA.name === '日柱') html += '日柱天干相合是感情最深厚的信号，两人心意相通，相处融洽。正面是缘分深、难分离；负面是可能因合而受牵绊，缺乏独立性。';
      else if (pA.name === '年柱') html += '年柱相合代表家族背景契合，长辈支持度高，长远目标一致。';
      else if (pA.name === '月柱') html += '月柱相合代表事业方向和价值观匹配，适合共同创业或合作。';
      else html += '时柱相合代表对未来规划、子女教育理念一致。';
      html += '</p><p style="font-size:0.8rem;color:var(--jade);margin-top:4px"><strong>✅ 好：</strong>缘分深厚、沟通顺畅、相互理解 | <strong style="color:var(--gold)">羁绊：</strong>合过强可能互相牵制，需保持适当独立空间</p>';
      html += '</div>';
    }
    if (DZ_HE[pA.branch] === pB.branch) {
      hasHe = true;
      html += '<div style="margin:10px 0;padding:14px;background:#e8f5e9;border-radius:8px;border-left:3px solid var(--jade)">';
      html += '<p><strong>✅ ' + pA.name + '地支六合：' + pA.branch + '合' + pB.branch + '</strong></p>';
      html += '<p style="font-size:0.85rem;color:var(--text-secondary)">地支六合是内在的本质吸引，比天干五合更深层。' + pA.branch + '与' + pB.branch + '六合，代表两人本质上的和谐共处。</p>';
      html += '<p style="font-size:0.82rem;color:var(--text-muted)"><strong>影响：</strong>';
      if (pA.name === '日柱') html += '日柱地支六合是婚姻最吉利的信号之一，夫妻宫相合，感情生活和谐美满。';
      else if (pA.name === '年柱') html += '年柱六合代表家族关系融洽，门当户对。';
      else html += pA.name + '层面和谐共处，有助于形成合力。';
      html += '</p></div>';
    }
  }
  if (!hasHe) {
    html += '<p style="font-size:0.9rem;color:var(--text-muted)">两人四柱未见明显的相合关系。这不代表不好——缺少相合意味着关系更独立自主，不受过多牵绊。大运流年带来的相合将成为关系的重要变数。</p>';
  }
  html += '</div>';

  // === 相冲关系 — 变动与冲突 ===
  html += '<div class="analysis-block warning"><h4>🔴 相冲关系 — 变动与冲突</h4>';
  var hasChong = false;
  for (var i = 0; i < 4; i++) {
    var pA = a.pillars[i], pB = b.pillars[i];
    if (DZ_CHONG[pA.branch] === pB.branch) {
      hasChong = true;
      html += '<div style="margin:10px 0;padding:14px;background:#fef5f5;border-radius:8px;border-left:3px solid var(--cinnabar)">';
      html += '<p><strong>⚠️ ' + pA.name + '地支六冲：' + pA.branch + '冲' + pB.branch + '</strong></p>';
      html += '<p style="font-size:0.85rem;color:var(--text-secondary)">' + pA.branch + '与' + pB.branch + '六冲，代表两人在' + pA.name + '层面存在对立和张力。冲不是绝对的坏——冲也代表变动与活力。</p>';
      html += '<p style="font-size:0.82rem;color:var(--text-muted)"><strong>影响：</strong>';
      if (pA.name === '日柱') html += '日柱相冲是关系中最需注意的信号。核心自我冲突，感情易波动，双方性格、习惯差异大。';
      else if (pA.name === '年柱') html += '年柱相冲代表家庭背景差异大，长辈关系需谨慎处理。';
      else if (pA.name === '月柱') html += '月柱相冲代表事业观、生活方式有较大差异。';
      else html += '时柱相冲代表对未来的规划、子女教育理念不同。';
      html += '</p><p style="font-size:0.8rem;color:var(--cinnabar);margin-top:4px"><strong>🔴 冲突：</strong>意见不合、步调不一的根源 | <strong style="color:var(--gold)">变动：</strong>适当的冲突也能激发活力，避免一成不变</p>';
      html += '</div>';
    }
  }
  if (!hasChong) {
    html += '<p style="font-size:0.9rem;color:var(--text-muted)">两人四柱未见相冲关系，这是非常有利的信号——核心层面没有根本性的冲突和对立，关系稳定和谐。但过度的平静也可能缺乏激情和变化，需主动创造新鲜感。</p>';
  }
  html += '</div>';

  // === 冲合化解 ===
  html += '<div class="analysis-block"><h4>💡 冲合化解指南</h4>';
  html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px">';

  html += '<div style="padding:12px;background:#e8f5e9;border-radius:6px">';
  html += '<strong style="color:var(--jade)">🟢 合的养护</strong>';
  html += '<ul style="margin:6px 0 0 16px;font-size:0.82rem">';
  html += '<li>珍惜相合的缘分，但不依赖——保持各自的独立性</li>';
  html += '<li>利用合的和谐期共同发展事业或家庭</li>';
  html += '<li>合过强时主动制造小别（出差/旅行），避免合久生厌</li>';
  html += '</ul></div>';

  html += '<div style="padding:12px;background:#fef5f5;border-radius:6px">';
  html += '<strong style="color:var(--cinnabar)">🔴 冲的化解</strong>';
  html += '<ul style="margin:6px 0 0 16px;font-size:0.82rem">';
  html += '<li>主动求变——出差、搬家、换岗可将冲力导向外部</li>';
  html += '<li>日柱相冲→建议晚婚、异地发展、保持适度空间</li>';
  html += '<li>年柱相冲→独立生活，减少双方家庭直接介入</li>';
  html += '<li>月柱相冲→事业各自发展，生活中求同存异</li>';
  html += '<li>时柱相冲→给彼此充分的决策自主权</li>';
  html += '</ul></div>';
  html += '</div>';

  html += '<p style="font-size:0.85rem;color:var(--text-muted);margin-top:10px">冲合是人际关系的自然体现。最好的关系不是无冲无合，而是在冲合中找到动态平衡——有合时懂珍惜，有冲时懂化解。</p>';
  html += '</div>';

  return html;
}

function renderMultiDayun(results) {
  let html = '<div class="compare-grid">';
  results.forEach(function(r) {
    html += '<div class="compare-panel"><h4>' + r.name + '</h4>';
    html += '<p style="font-size:0.85rem">当前大运：<strong>' + r.dayun.currentDayun.gz + '</strong> (' + r.dayun.currentDayun.range + ')</p>';
    html += '<p style="font-size:0.85rem">流年：<strong>' + r.dayun.currentLiunian + '</strong> (' + r.dayun.currentYear + '年)</p>';
    // Mini luck table
    html += '<table class="paipan-table" style="font-size:0.75rem"><tr><th>#</th><th>大运</th><th>十神</th><th>年龄</th></tr>';
    r.dayun.luckPillars.forEach(function(lp, i) {
      var isCur = lp === r.dayun.currentDayun;
      var a = analyzeLuckPillar(r, lp, '');
      html += '<tr style="' + (isCur ? 'background:rgba(201,169,110,0.15)' : '') + '"><td>' + (i+1) + (isCur?'←':'') + '</td><td>' + lp.gz + '</td><td style="font-size:0.7rem">' + a.tgName + '</td><td>' + lp.range + '</td></tr>';
    });
    html += '</table></div>';
  });
  html += '</div>';
  // Sync analysis with relationship status table
  html += '<div class="analysis-block"><h4>📅 大运同步关系状况表</h4>';
  html += '<p style="font-size:0.85rem;margin-bottom:8px">同一年龄段两人的大运十神交互，决定该阶段的共同运势基调。</p>';

  // Build a unified timeline from youngest start to oldest end
  var a = results[0], b = results[1];
  var allPeriods = [];
  // Combine both people's luck pillars into age-based periods
  a.dayun.luckPillars.forEach(function(lp) {
    allPeriods.push({ startAge: lp.startAge, endAge: lp.endAge, person: 'A', lp: lp });
  });
  b.dayun.luckPillars.forEach(function(lp) {
    allPeriods.push({ startAge: lp.startAge, endAge: lp.endAge, person: 'B', lp: lp });
  });
  allPeriods.sort(function(x, y) { return x.startAge - y.startAge; });

  // Find overlapping periods and analyze
  var timeline = [];
  var curAge = Math.min(a.dayun.luckPillars[0].startAge, b.dayun.luckPillars[0].startAge);
  var maxAge = Math.max(a.dayun.luckPillars[7].endAge, b.dayun.luckPillars[7].endAge);

  // Find which luck pillar each person is in at a given age
  function findLP(person, age) {
    for (var i = 0; i < person.dayun.luckPillars.length; i++) {
      if (age >= person.dayun.luckPillars[i].startAge && age <= person.dayun.luckPillars[i].endAge) {
        return person.dayun.luckPillars[i];
      }
    }
    return null;
  }

  // Generate timeline at key ages (start of each luck period)
  var keyAges = [];
  a.dayun.luckPillars.forEach(function(lp) { keyAges.push(lp.startAge); });
  b.dayun.luckPillars.forEach(function(lp) { keyAges.push(lp.startAge); });
  keyAges = keyAges.filter(function(v, i, arr) { return arr.indexOf(v) === i; }).sort(function(x, y) { return x - y; });

  html += '<div style="overflow-x:auto"><table class="paipan-table" style="font-size:0.78rem"><tr><th>年龄段</th><th>' + a.name + '大运</th><th>' + a.name + '十神</th><th>' + b.name + '大运</th><th>' + b.name + '十神</th><th>关系状况</th></tr>';

  for (var i = 0; i < keyAges.length; i++) {
    var ageStart = keyAges[i];
    var ageEnd = (i + 1 < keyAges.length) ? keyAges[i+1] - 1 : 77;
    var lpA = findLP(a, ageStart);
    var lpB = findLP(b, ageStart);
    if (!lpA || !lpB) continue;

    var aAnalysis = analyzeLuckPillar(a, lpA, '');
    var bAnalysis = analyzeLuckPillar(b, lpB, '');

    // Determine relationship status
    var relStatus = '';
    var relColor = '';
    var aGood = aAnalysis.career.level === '吉' || aAnalysis.wealth.level === '吉';
    var bGood = bAnalysis.career.level === '吉' || bAnalysis.wealth.level === '吉';
    var aBad = aAnalysis.career.level === '凶' || aAnalysis.wealth.level === '凶';
    var bBad = bAnalysis.career.level === '凶' || bAnalysis.wealth.level === '凶';

    // Check if luck pillars interact
    var lpInteraction = '';
    if (TG_HE[lpA.stem] === lpB.stem) { lpInteraction = '天干五合，配合默契'; }
    else if (DZ_CHONG[lpA.branch] === lpB.branch) { lpInteraction = '地支六冲，步调不一'; }
    else if (DZ_HE[lpA.branch] === lpB.branch) { lpInteraction = '地支六合，和谐共进'; }
    else if (WX_TG[lpA.stemIdx] === WX_TG[lpB.stemIdx]) { lpInteraction = '五行相同，有共同方向'; }

    if (aGood && bGood) {
      relStatus = '🟢 双方利好'; relColor = 'var(--jade)';
    } else if (aBad && bBad) {
      relStatus = '🔴 双方挑战'; relColor = 'var(--cinnabar)';
    } else if (aBad && bGood) {
      relStatus = '🟡 ' + b.name + '带动' + a.name; relColor = 'var(--gold)';
    } else if (aGood && bBad) {
      relStatus = '🟡 ' + a.name + '带动' + b.name; relColor = 'var(--gold)';
    } else {
      relStatus = '🟡 平稳发展'; relColor = 'var(--gold)';
    }

    if (lpInteraction) relStatus += '（' + lpInteraction + '）';

    html += '<tr><td>' + ageStart + '-' + ageEnd + '岁</td>';
    html += '<td>' + lpA.gz + '</td><td style="font-size:0.7rem">' + aAnalysis.tgName + '</td>';
    html += '<td>' + lpB.gz + '</td><td style="font-size:0.7rem">' + bAnalysis.tgName + '</td>';
    html += '<td style="color:' + relColor + ';font-weight:bold">' + relStatus + '</td></tr>';
  }
  html += '</table></div>';

  // Summary
  html += '<div style="margin-top:12px;padding:10px;background:var(--paper-cream);border-radius:6px">';
  html += '<p style="font-size:0.85rem"><strong>💡 解读：</strong></p>';
  html += '<p style="font-size:0.82rem">🟢 <strong style="color:var(--jade)">双方利好</strong>：两人同时处于好运期，共同发展事半功倍，适合做出重大共同决策（结婚、创业、投资）。</p>';
  html += '<p style="font-size:0.82rem">🟡 <strong style="color:var(--gold)">一方带动</strong>：运势好的一方可以带动弱势方，适合分工合作——强势方主外开拓，弱势方主内稳固。</p>';
  html += '<p style="font-size:0.82rem">🔴 <strong style="color:var(--cinnabar)">双方挑战</strong>：两人同时处于低谷期，需互相扶持共渡难关。不建议在此期间做重大共同决策，以守为主。</p>';
  html += '</div>';
  html += '</div>';
  return html;
}

function renderMultiShensha(results) {
  let html = '';
  var a = results[0], b = results[1];

  // Collect all shensha by name with pillar info
  var shenshaA = {}, shenshaB = {};
  a.shensha.forEach(function(s) { if (!shenshaA[s.name]) shenshaA[s.name] = []; shenshaA[s.name].push(s.pillar); });
  b.shensha.forEach(function(s) { if (!shenshaB[s.name]) shenshaB[s.name] = []; shenshaB[s.name].push(s.pillar); });

  var allNames = new Set([...Object.keys(shenshaA), ...Object.keys(shenshaB)]);
  var commonSS = [];
  var uniqueA = [];
  var uniqueB = [];
  allNames.forEach(function(name) {
    if (shenshaA[name] && shenshaB[name]) commonSS.push(name);
    else if (shenshaA[name]) uniqueA.push(name);
    else uniqueB.push(name);
  });

  // === Similarity Score ===
  var totalTypes = allNames.size;
  var similarity = totalTypes > 0 ? Math.round(commonSS.length / totalTypes * 100) : 0;
  var simLevel = similarity >= 60 ? '高' : similarity >= 30 ? '中' : '低';

  html += '<div class="analysis-block"><h4>📊 神煞匹配度分析</h4>';
  html += '<div class="compat-score-ring">';
  html += '<div class="ring-label">神煞相似度</div>';
  html += '<div class="ring-value">' + similarity + '<span style="font-size:1.2rem">%</span></div>';
  html += '<div style="font-size:1.1rem;color:var(--gold);letter-spacing:2px">匹配等级：' + simLevel + '</div>';
  html += '</div>';

  // Similarity interpretation
  html += '<div style="padding:10px;background:var(--paper-cream);border-radius:6px;margin-top:8px">';
  if (similarity >= 60) {
    html += '<p><strong style="color:var(--jade)">高相似度</strong>：两人神煞重叠度高，性格/兴趣/命运轨迹相似。相处起来默契自然，容易理解对方。但需注意：过于相似也可能导致缺乏新鲜感和互补性。</p>';
  } else if (similarity >= 30) {
    html += '<p><strong style="color:var(--gold)">中等相似度</strong>：两人既有共同点也有差异，可以在相似的基础上互相补充。这是较为理想的状态——有共同话题也有新鲜视角。</p>';
  } else {
    html += '<p><strong style="color:var(--water-blue)">低相似度</strong>：两人神煞差异较大，性格/兴趣/命运轨迹各不相同。这既是挑战也是机遇——差异带来新鲜感和互补性，但需要更多理解和包容。</p>';
  }
  html += '</div>';
  html += '</div>';

  // === Detailed match table ===
  html += '<div class="analysis-block"><h4>🔍 神煞逐一匹配</h4>';
  html += '<div style="overflow-x:auto"><table class="paipan-table" style="font-size:0.82rem"><tr><th>神煞</th><th>' + a.name + '</th><th>' + b.name + '</th><th>匹配状态</th><th>影响</th></tr>';

  // 吉神匹配规则
  var JI_MATCH = {
    "天乙贵人": { both:"贵人运双倍叠加，遇到困难时贵人更多，是极好的组合", aOnly:a.name+"贵人运更强，可带动"+b.name, bOnly:b.name+"贵人运更强，可带动"+a.name, neither:"两人都需主动拓展人脉" },
    "文昌星": { both:"都重视学习和技能，适合一起学习进修", aOnly:a.name+"在技术/学习方面更有优势", bOnly:b.name+"在技术/学习方面更有优势", neither:"需互相督促学习进步" },
    "将星": { both:"两人都有领导才能，需明确分工避免权力冲突", aOnly:a.name+"主导性更强，适合担任决策角色", bOnly:b.name+"主导性更强，适合担任决策角色", neither:"适合平等协商的相处模式" },
    "禄神": { both:"双方物质基础稳固，适合共同理财置业", aOnly:a.name+"经济基础更好，宜多承担家庭开支", bOnly:b.name+"经济基础更好，宜多承担家庭开支", neither:"需共同努力积累财富" },
    "学堂": { both:"两人都热爱学习，可一起进修或培养共同爱好", aOnly:a.name+"学习能力更强，可帮助"+b.name+"成长", bOnly:b.name+"学习能力更强，可帮助"+a.name+"成长", neither:"需互相激励学习进步" },
    "天喜": { both:"双方都多喜庆事，共同生活充满欢乐", aOnly:a.name+"喜庆运更强，能带动关系中的欢乐氛围", bOnly:b.name+"喜庆运更强，能带动关系中的欢乐氛围", neither:"可主动创造共同的活动和仪式感" },
  };

  var PIAN_MATCH = {
    "桃花": { both:"两人都有桃花人缘，感情丰富但也需防范外遇。将桃花能量转化为社交资源是明智之选", aOnly:a.name+"人缘/知名度更高，需注意"+b.name+"的感受", bOnly:b.name+"人缘/知名度更高，需注意"+a.name+"的感受", neither:"感情关系较为纯粹，不易受外界干扰——这反而是好事" },
    "华盖": { both:"两人都对神秘文化有兴趣，可以一起探索哲学/玄学。但都偏孤僻，需注意社交", aOnly:a.name+"更倾向独立思考和研究", bOnly:b.name+"更倾向独立思考和研究", neither:"两人都非孤僻型，社交生活丰富" },
    "驿马": { both:"两人都喜欢奔波变动，适合一起旅行或异地发展", aOnly:a.name+"更需要外出奔波，"+b.name+"宜给予支持", bOnly:b.name+"更需要外出奔波，"+a.name+"宜给予支持", neither:"适合稳定的生活模式" },
  };

  var XIONG_MATCH = {
    "羊刃": { both:"两人性格都较刚烈，容易硬碰硬。需学会示弱和妥协", aOnly:a.name+"性格更刚强，需注意控制情绪", bOnly:b.name+"性格更刚强，需注意控制情绪", neither:"双方性格都较温和，冲突较少" },
    "劫煞": { both:"双方都可能遭遇障碍，需共同面对外部挑战", aOnly:a.name+"需注意自身/家庭方面的障碍", bOnly:b.name+"需注意自身/家庭方面的障碍", neither:"关系受外部障碍影响较小" },
    "灾煞": { both:"双方都需注意突发变故，建议共同做好预防措施", aOnly:a.name+"需更注意突发状况", bOnly:b.name+"需更注意突发状况", neither:"突发风险较低" },
  };

  allNames.forEach(function(name) {
    var inA = shenshaA[name] ? shenshaA[name].join('、') : '—';
    var inB = shenshaB[name] ? shenshaB[name].join('、') : '—';
    var both = shenshaA[name] && shenshaB[name];
    var aOnly = shenshaA[name] && !shenshaB[name];
    var bOnly = !shenshaA[name] && shenshaB[name];
    var neither = !shenshaA[name] && !shenshaB[name];

    var status = '', statColor = '', impact = '';
    if (both) { status = '🟢 共有'; statColor = 'var(--jade)'; }
    else if (aOnly) { status = '🟡 ' + a.name + '独有'; statColor = 'var(--gold)'; }
    else if (bOnly) { status = '🟡 ' + b.name + '独有'; statColor = 'var(--gold)'; }

    // Find matching rule
    var rule = JI_MATCH[name] || PIAN_MATCH[name] || XIONG_MATCH[name];
    if (rule) {
      if (both) impact = rule.both;
      else if (aOnly) impact = rule.aOnly;
      else if (bOnly) impact = rule.bOnly;
      else impact = rule.neither;
    } else {
      impact = both ? '共同特质，加深默契' : '差异带来互补';
    }

    html += '<tr><td><strong>' + name + '</strong></td><td>' + inA + '</td><td>' + inB + '</td><td style="color:' + statColor + '">' + status + '</td><td style="font-size:0.78rem">' + (impact || '—') + '</td></tr>';
  });

  if (allNames.size === 0) {
    html += '<tr><td colspan="5" style="color:var(--text-muted)">两人命局均无明显神煞，命运轨迹各有特色</td></tr>';
  }
  html += '</table></div></div>';

  // === Improvement suggestions ===
  html += '<div class="analysis-block"><h4>💡 神煞匹配改善建议</h4>';

  // Analyze gaps
  var suggestions = [];
  if (similarity < 40) {
    suggestions.push('<strong>尊重差异：</strong>神煞差异大代表两人的天赋和际遇方向不同。不要试图改变对方成为自己的样子，而是利用差异实现互补。');
  }
  if (commonSS.length === 0) {
    suggestions.push('<strong>创造共同点：</strong>虽然没有共同神煞，但可以通过共同的兴趣爱好、生活方式来建立新的连接点。');
  }
  if (commonSS.length >= 2) {
    suggestions.push('<strong>强化共同优势：</strong>在共同神煞领域深入合作，发挥1+1>2的协同效应。');
  }
  if (uniqueA.length > uniqueB.length + 1) {
    suggestions.push('<strong>' + a.name + '宜多引导：</strong>' + a.name + '神煞较丰富，可在自己擅长的领域多引导' + b.name + '。');
  }
  if (uniqueB.length > uniqueA.length + 1) {
    suggestions.push('<strong>' + b.name + '宜多引导：</strong>' + b.name + '神煞较丰富，可在自己擅长的领域多引导' + a.name + '。');
  }
  // General advice
  suggestions.push('<strong>大运流年补足：</strong>即使本命神煞不匹配，大运流年带来的神煞也能临时改善匹配度。关注双方同步遇到吉神的大运。</p>');
  suggestions.push('<strong>神煞为辅：</strong>神煞只是辅助参考指标，关系的核心在于十神互涉和五行互补。不要过分纠结于神煞的匹配度。</p>');

  suggestions.forEach(function(s) {
    html += '<p style="font-size:0.85rem;margin:6px 0">• ' + s + '</p>';
  });
  html += '</div>';

  return html;
}

function renderMultiZonghe(results, compat, relType) {
  let html = '';
  var a = results[0], b = results[1];
  var wxDir = {"木":"东方","火":"南方","土":"中部","金":"西方","水":"北方"};

  // === Header ===
  html += '<div class="analysis-block"><h4>📋 ' + relType + '合盘 — 综合建议</h4>';
  html += '<p>综合兼容度：<strong style="color:var(--cinnabar);font-size:1.2rem">' + compat.overall + '/100</strong> — ' + compat.level + '</p>';
  html += '<p style="font-size:0.85rem;color:var(--text-muted)">' + a.name + '：' + a.ganZao + ' ' + a.paipanStr + ' | ' + b.name + '：' + b.ganZao + ' ' + b.paipanStr + '</p>';
  html += '</div>';

  // === 1. 相处模式 ===
  html += '<div class="analysis-block"><h4>💑 相处模式</h4>';
  var relIdx = calcTenGodRelation(a.dayStemIdx, b.dayStemIdx);
  var relIdx2 = calcTenGodRelation(b.dayStemIdx, a.dayStemIdx);
  var info = getTenGodRelInfo(relIdx, a.name, b.name);
  var info2 = getTenGodRelInfo(relIdx2, b.name, a.name);

  html += '<p><strong>' + a.name + '→' + b.name + '：</strong>' + b.name + '是' + a.name + '的<strong>' + SHISHEN_FULL[relIdx] + '</strong>。' + info.desc.replace(/<[^>]+>/g,'') + '</p>';
  html += '<p style="font-size:0.85rem;color:var(--text-muted)">表现：' + info.impact + '</p>';
  html += '<p><strong>' + b.name + '→' + a.name + '：</strong>' + a.name + '是' + b.name + '的<strong>' + SHISHEN_FULL[relIdx2] + '</strong>。' + info2.desc.replace(/<[^>]+>/g,'') + '</p>';
  html += '<p style="font-size:0.85rem;color:var(--text-muted)">表现：' + info2.impact + '</p>';

  // Key findings with good/bad
  html += '<div style="margin-top:10px"><strong>关键发现：</strong></div>';
  compat.highlights.forEach(function(h) {
    var icon = h.includes('互补')||h.includes('相合')||h.includes('五合')||h.includes('六合') ? '✅' : h.includes('冲')||h.includes('不稳') ? '⚠️' : '💡';
    html += '<p style="font-size:0.85rem;margin:4px 0">' + icon + ' ' + h + '</p>';
  });
  html += '</div>';

  // === 2. 事业发展 ===
  html += '<div class="analysis-block"><h4>💼 共同事业分析</h4>';
  var aDOM = a.tenGods.filter(function(t){return t.name!=='日主'}).map(function(t){return t.name});
  var bDOM = b.tenGods.filter(function(t){return t.name!=='日主'}).map(function(t){return t.name});
  var hasCGa = aDOM.includes('正官')||aDOM.includes('七杀');
  var hasCGb = bDOM.includes('正官')||bDOM.includes('七杀');
  var hasCWa = aDOM.includes('正财')||aDOM.includes('偏财');
  var hasCWb = bDOM.includes('正财')||bDOM.includes('偏财');

  html += '<div style="padding:10px;background:var(--paper-cream);border-radius:8px;margin:8px 0">';
  if (hasCGa && hasCWb) {
    html += '<p><strong>最佳事业组合：</strong>' + a.name + '的官杀配合' + b.name + '的财星，形成"官护财、财生官"的良性循环。适合共同经营事业，' + a.name + '主外拓展、' + b.name + '主内运营。</p>';
  } else if (hasCGb && hasCWa) {
    html += '<p><strong>最佳事业组合：</strong>' + b.name + '的官杀配合' + a.name + '的财星，形成互补。' + b.name + '主外拓展、' + a.name + '主内运营。</p>';
  } else if (a.strength.level === '身强' && b.strength.level === '身弱') {
    html += '<p><strong>事业互补：</strong>' + a.name + '身强行动力足，适合开拓；' + b.name + '身弱善谋划，适合策略。分工明确可事半功倍。</p>';
  } else if (b.strength.level === '身强' && a.strength.level === '身弱') {
    html += '<p><strong>事业互补：</strong>' + b.name + '身强行动力足，适合开拓；' + a.name + '身弱善谋划，适合策略。分工明确可事半功倍。</p>';
  } else {
    html += '<p><strong>事业合作建议：</strong>两人都' + a.strength.level + '，适合平等协作。根据各自十神优势分工——官杀旺者主外、财星旺者主内、食伤旺者主创意。</p>';
  }
  html += '<p style="font-size:0.85rem"><strong>适合共同从事的领域：</strong>结合双方五行和十神，宜向' + (a.wuxing.missing.length>0 ? wxDir[a.wuxing.missing[0].wx] : wxDir[wxOf(a.dayMaster.stem)]) + '和' + (b.wuxing.missing.length>0 ? wxDir[b.wuxing.missing[0].wx] : wxDir[wxOf(b.dayMaster.stem)]) + '方向发展。</p>';
  html += '</div></div>';

  // === 3. 感情/关系分析 ===
  html += '<div class="analysis-block"><h4>💕 ' + (relType==='夫妻'?'婚姻感情':'关系分析') + '</h4>';
  html += '<div style="padding:10px;background:var(--paper-cream);border-radius:8px;margin:8px 0">';

  // Check spouse palace interaction
  var dayA = a.pillars[2], dayB = b.pillars[2];
  if (TG_HE[dayA.stem] === dayB.stem) {
    html += '<p><strong style="color:var(--jade)">✅ 日干相合：</strong>两人日干' + dayA.stem + '与' + dayB.stem + '天干五合化' + TG_HE_HUA[dayA.stem] + '，缘分极深，心意相通。这是最高级别的吸引力。</p>';
  }
  if (DZ_HE[dayA.branch] === dayB.branch) {
    html += '<p><strong style="color:var(--jade)">✅ 日支六合：</strong>夫妻宫' + dayA.branch + '与' + dayB.branch + '六合，感情和谐，性生活协调。</p>';
  }
  if (DZ_CHONG[dayA.branch] === dayB.branch) {
    html += '<p><strong style="color:var(--cinnabar)">⚠️ 日支六冲：</strong>夫妻宫' + dayA.branch + '冲' + dayB.branch + '，是关系中的核心挑战。建议晚婚、保持适度空间、不互相过度依赖。许多冲中带合的夫妻反而感情更深。</p>';
  }
  if (!TG_HE[dayA.stem] === dayB.stem && !DZ_HE[dayA.branch] === dayB.branch && !DZ_CHONG[dayA.branch] === dayB.branch) {
    html += '<p>两人日柱无直接冲合，感情发展较为自然，受外界因素影响较大。需要双方主动经营维护。</p>';
  }

  // 五行互补
  var aMissing = a.wuxing.missing.map(function(m){return m.wx});
  var bOver = b.wuxing.overWang.map(function(o){return o.wx});
  var complement = aMissing.filter(function(wx){return bOver.includes(wx)});
  if (complement.length > 0) {
    html += '<p><strong style="color:var(--jade)">✅ 五行互补：</strong>' + a.name + '缺' + complement.join('、') + '，' + b.name + '旺' + complement.join('、') + '——完美互补，相互成就。</p>';
  }

  html += '<p style="font-size:0.85rem;margin-top:6px"><strong>' + relType + '相处要点：</strong></p>';
  if (relType === '夫妻') {
    html += '<p style="font-size:0.82rem">• 尊重彼此的独立性，给对方适当的空间<br>• 五行互补的方面可深度合作，共同发展<br>• 大运流年同步遇吉时，适合做重大共同决策<br>• 记住：感情是两个人的经营，命理只是趋势参考</p>';
  } else if (relType === '朋友') {
    html += '<p style="font-size:0.82rem">• 利用五行互补，在各自擅长的领域互相帮助<br>• 日干相合者缘分最深，珍惜这份难得的友谊<br>• 保持适当距离，不过度介入对方生活</p>';
  } else if (relType === '同事') {
    html += '<p style="font-size:0.82rem">• 明确分工，各司其职，发挥各自的十神优势<br>• 官星旺者负责统筹管理，财星旺者负责运营执行<br>• 注意竞争关系中的公平性，避免利益冲突</p>';
  } else if (relType === '领导') {
    html += '<p style="font-size:0.82rem">• 官杀为用者适合担任决策角色，印星为用者适合辅助支持<br>• 五行相生的上下级关系最为顺畅<br>• 保持尊重和沟通，避免权力压制</p>';
  } else {
    html += '<p style="font-size:0.82rem">• 珍惜血缘关系中的天然纽带<br>• 年柱相合则家族和睦，月柱相合则家庭和谐<br>• 适当的距离感有助于维持良好的亲属关系</p>';
  }
  html += '</div></div>';

  // === 4. 财富合作 ===
  html += '<div class="analysis-block"><h4>💰 财富合作分析</h4>';
  html += '<div style="padding:10px;background:var(--paper-cream);border-radius:8px;margin:8px 0">';
  var aWealthGood = a.dayun.luckPillars.filter(function(lp) { var al = analyzeLuckPillar(a, lp, ''); return al.wealth.level === '吉'; });
  var bWealthGood = b.dayun.luckPillars.filter(function(lp) { var al = analyzeLuckPillar(b, lp, ''); return al.wealth.level === '吉'; });
  html += '<p><strong>财运同步：</strong>' + a.name + '有<strong>' + aWealthGood.length + '</strong>步财运吉运，' + b.name + '有<strong>' + bWealthGood.length + '</strong>步。</p>';

  // Find overlapping wealth-good periods
  var bothWealthGood = 0;
  a.dayun.luckPillars.forEach(function(lpA) {
    b.dayun.luckPillars.forEach(function(lpB) {
      if (lpA.startAge <= lpB.endAge && lpA.endAge >= lpB.startAge) {
        var alA = analyzeLuckPillar(a, lpA, ''), alB = analyzeLuckPillar(b, lpB, '');
        if (alA.wealth.level === '吉' && alB.wealth.level === '吉') bothWealthGood++;
      }
    });
  });

  if (bothWealthGood > 0) {
    html += '<p><strong style="color:var(--jade)">✅ 有' + bothWealthGood + '个时期双方财运同步利好</strong>，适合共同投资置业。</p>';
  } else {
    html += '<p>双方财运高峰不同步，建议各自管理财务，共同支出部分需提前规划。</p>';
  }
  html += '<p style="font-size:0.85rem"><strong>合作建议：</strong>' + (compat.scores.wuxing >= 60 ? '五行互补度高，适合共同投资理财。' : '建议保持财务相对独立，共同支出部分明确约定。') + '</p>';
  html += '</div></div>';

  // === 5. 健康与注意事项 ===
  html += '<div class="analysis-block"><h4>🏥 健康互相关注</h4>';
  html += '<div style="padding:10px;background:var(--paper-cream);border-radius:8px;margin:8px 0">';
  html += '<p><strong>' + a.name + '需关注：</strong>' + a.interpretation.health + '</p>';
  html += '<p><strong>' + b.name + '需关注：</strong>' + b.interpretation.health + '</p>';
  if (a.wuxing.overWang.length > 0 || b.wuxing.overWang.length > 0) {
    html += '<p style="font-size:0.85rem;color:var(--text-muted)">双方过旺的五行可能在饮食偏好、作息习惯上产生冲突，需互相理解和包容。</p>';
  }
  html += '</div></div>';

  // === 6. 合盘总结 ===
  html += '<div class="analysis-block"><h4>📝 合盘总结</h4>';
  html += '<p>' + a.name + '（' + a.paipanStr + '）与' + b.name + '（' + b.paipanStr + '）的合盘分析：</p>';
  html += '<p style="margin:8px 0">综合评分<strong>' + compat.overall + '/100</strong>（' + compat.level + '），五行互补' + compat.scores.wuxing + '分，冲合和谐' + compat.scores.chongHe + '分，十神互涉' + compat.scores.tenGod + '分，神煞匹配' + compat.scores.shensha + '分。</p>';
  html += '<p style="font-size:0.88rem">' + getMutualSummary(relIdx, relIdx2) + '</p>';
  html += '<p style="font-size:0.85rem;color:var(--text-muted);margin-top:8px">命理合盘反映的是先天趋势和概率，是两人关系的客观参考。但人与人之间真正的相处，靠的是理解、包容和共同经营。命理只是工具，爱与智慧才是关键。</p>';
  html += '</div>';

  // Export button at bottom-right
  html += '<div style="text-align:right;margin-top:16px"><button class="btn-export" onclick="exportToPDF()" style="padding:10px 24px;font-size:0.9rem">📄 导出合盘PDF</button></div>';

  return html;
}

function renderCompareView(results, compat, relType) {
  let html = `<div class="compat-score-ring">
    <div class="ring-label">${relType} — 综合兼容度</div>
    <div class="ring-value">${compat.overall}<span style="font-size:1.2rem">/100</span></div>
    <div style="font-size:1.2rem;color:var(--gold);letter-spacing:3px">${compat.level}</div>
  </div>`;

  // Score bars with icons
  html += `<div style="margin:16px 0">`;
  var barCfg2 = [
    { key:'wuxing', label:'五行互补', icon:'🌿', color:'#5b8c5a' },
    { key:'chongHe', label:'冲合和谐', icon:'⚡', color:'#c9a84c' },
    { key:'tenGod', label:'十神互涉', icon:'🔗', color:'#3a6186' },
    { key:'shensha', label:'神煞匹配', icon:'⭐', color:'#8b6914' }
  ];
  barCfg2.forEach(function(cfg) {
    var val = compat.scores[cfg.key] || 50;
    var barColor = val >= 70 ? 'var(--jade)' : val >= 50 ? 'var(--gold)' : 'var(--cinnabar)';
    html += '<div style=\"display:flex;align-items:center;gap:10px;padding:4px 10px;margin:4px 0;background:var(--paper-light);border-radius:6px\">';
    html += '<span style=\"font-size:1.1rem;width:26px;text-align:center\">' + cfg.icon + '</span>';
    html += '<span style=\"width:75px;font-weight:bold;font-size:0.85rem;color:' + cfg.color + '\">' + cfg.label + '</span>';
    html += '<span style=\"width:28px;text-align:center;font-family:var(--font-title);font-size:1rem;color:' + cfg.color + '\">' + val + '</span>';
    html += '<div style=\"flex:1;height:14px;background:#ebe2cf;border-radius:7px;overflow:hidden\"><div style=\"width:' + val + '%;height:100%;background:' + barColor + ';border-radius:7px;transition:width 0.6s ease\"></div></div>';
    html += '<span style=\"font-size:0.75rem;color:var(--ink-light);min-width:30px\">' + val + '/100</span>';
    html += '</div>';
  });
  html += `</div>`;

  // Side by side wuxing comparison
  html += `<div class="compare-grid">`;
  results.forEach(r => {
    html += `<div class="compare-panel"><h4>${r.name} — ${r.ganZao}</h4>`;
    html += `<div style="text-align:center;font-family:var(--font-heading);letter-spacing:2px;margin:8px 0">${r.paipanStr}</div>`;
    html += renderWuxingChart(r.wuxing.counts);
    html += `<div class="highlight-grid" style="grid-template-columns:1fr 1fr 1fr 1fr 1fr">`;
    for (const [k,v] of Object.entries(r.wuxing.counts)) {
      html += `<div class="highlight-item"><div class="hi-label">${k}</div><div class="hi-value" style="font-size:0.9rem">${v}</div></div>`;
    }
    html += `</div></div>`;
  });
  html += `</div>`;

  // Highlights
  if (compat.highlights.length > 0) {
    html += `<div class="analysis-block"><h4>关键发现</h4>`;
    compat.highlights.forEach(h => { html += `<p>• ${h}</p>`; });
    html += `</div>`;
  }

  return html;
}

function renderCompatDetail(results, compat, relType) {
  let html = `<div class="analysis-block"><h4>合盘分析 — ${relType}</h4>
    <p>关系类型判定基于双方命盘的交叉比对，分析维度因关系类型而异。</p></div>`;

  // Face-to-face four pillar comparison
  html += `<table class="paipan-table">
    <tr><th>柱位</th><th>${results[0].name}</th><th>${results[1].name}</th><th>关系</th></tr>`;
  for (let i = 0; i < 4; i++) {
    const pA = results[0].pillars[i], pB = results[1].pillars[i];
    let rel = "—";
    if (TG_HE[pA.stem] === pB.stem) rel = `天干五合(化${TG_HE_HUA[pA.stem]})`;
    else if (DZ_CHONG[pA.branch] === pB.branch) rel = "地支相冲";
    else if (DZ_HE[pA.branch] === pB.branch) rel = "地支六合";
    else if (wxOf(pA.stem) === wxOf(pB.stem)) rel = "五行相同";
    html += `<tr>
      <td>${pA.name}</td>
      <td>${pA.gz} (${pA.nayin})</td>
      <td>${pB.gz} (${pB.nayin})</td>
      <td style="color:${rel.includes('冲')?'var(--cinnabar)':'var(--jade)'}">${rel}</td>
    </tr>`;
  }
  html += `</table>`;

  // Analysis details
  html += `<div class="analysis-block"><h4>维度分析</h4>`;
  compat.details.forEach(d => { html += `<p>• ${d}</p>`; });
  html += `</div>`;

  // Suggestions by relationship type
  html += `<div class="analysis-block"><h4>综合建议</h4>`;
  const suggestions = {
    "夫妻": [
      "注意日柱互动的冲合关系，冲则需磨合，合则和谐但需防过度依赖",
      "五行互补度高的伴侣更能长久，互补缺失元素可相互成就",
      "大运流年同步性高的时期，重大决策（婚育置业）更顺利"
    ],
    "亲戚": [
      "年柱纳音相生为佳，代表家族根基相融",
      "月柱五行相生则家庭氛围和谐",
      "适当的距离感有助于维持良好的亲属关系"
    ],
    "朋友": [
      "比劫旺者宜与食伤旺者交友，可激发创造力",
      "五行互补的朋友能带来新的视角和资源",
      "日干相合的朋友缘分最深"
    ],
    "同事": [
      "官星互补的同事关系，工作协作效率高",
      "财星相生的合作伙伴，利于项目收益",
      "注意七杀过旺者之间的竞争张力"
    ],
    "领导": [
      "官杀为用的下属与印星为用的领导配合最佳",
      "五行相生（向上相生）的上下级关系最为顺畅",
      "注意地支相冲的领导-下属组合，易产生价值观冲突"
    ],
  };
  (suggestions[relType] || suggestions["朋友"]).forEach(s => {
    html += `<p>• ${s}</p>`;
  });
  html += `</div>`;

  return html;
}

// ============================================================
//  SECTION 17: EVENT HANDLERS
// ============================================================

let currentMode = 'single';
let multiPersonCount = 0;
let multiPersons = [];

function switchMode(mode) {
  currentMode = mode;
  document.getElementById('btn-single').classList.toggle('active', mode === 'single');
  document.getElementById('btn-multi').classList.toggle('active', mode === 'multi');
  document.getElementById('panel-single').style.display = mode === 'single' ? '' : 'none';
  document.getElementById('panel-multi').style.display = mode === 'multi' ? '' : 'none';
  document.getElementById('result-panel').classList.remove('visible');
}

// ============================================================
//  SECTION 17b: EXPORT TO IMAGE
// ============================================================

function exportToPDF() {
  const panel = document.getElementById('result-panel');
  if (!panel || !panel.classList.contains('visible')) { alert('请先生成分析结果'); return; }

  // Show all tabs
  const tabContents = document.querySelectorAll('.tab-content');
  const activeTabs = [];
  tabContents.forEach(tc => { if (tc.classList.contains('active')) activeTabs.push(tc.id); tc.style.display = 'block'; });

  // Build export content
  const resultDiv = document.getElementById('tab-contents');
  let bodyHTML = '';
  if (resultDiv) {
    const clone = resultDiv.cloneNode(true);
    clone.querySelectorAll('.tab-content').forEach(c => { c.style.display = 'block'; c.style.marginBottom = '16px'; });
    clone.querySelectorAll('.btn-export').forEach(b => b.remove());
    clone.querySelectorAll('.tab-bar').forEach(b => b.style.display = 'none');
    bodyHTML = clone.innerHTML;
  }

  // Restore tabs
  tabContents.forEach(tc => {
    tc.style.display = activeTabs.includes(tc.id) ? '' : 'none';
  });

  var styles = document.querySelector('style')?.outerHTML || '';
  var html = '<!DOCTYPE html><html><head><meta charset=\"UTF-8\"><title>神算子·八字分析</title>' + styles;
  html += '<style>@media print{body{-webkit-print-color-adjust:exact;print-color-adjust:exact}@page{size:A4;margin:12mm}}body{background:#f5f0e8;padding:20px 30px;font-family:SimSun,STSong,serif;color:#2c2416;max-width:900px;margin:0 auto}</style></head><body>';
  html += '<h1 style=\"text-align:center;letter-spacing:6px;color:#1a1a2e;font-size:1.4rem;margin-bottom:2px\">神算子 · 华山八字</h1>';
  html += '<p style=\"text-align:center;color:#c41e3a;letter-spacing:3px;font-size:0.8rem;margin-top:0\">道，可道</p>';
  html += '<hr style=\"border-color:#c9a96e;margin:10px 0\">';
  html += bodyHTML;
  html += '<hr style=\"border-color:#c9a96e;margin:10px 0\">';
  html += '<p style=\"text-align:center;color:#9b8e7a;font-size:0.7rem\">' + new Date().toLocaleString() + ' | 华山八字命理分析 | 仅供参考</p>';
  html += '</body></html>';

  var w = window.open('', '_blank');
  w.document.write(html);
  w.document.close();
  w.onload = function() { w.print(); };
}

function runSingleMode() {
  const name = document.getElementById('s-name').value || '命主';
  const gender = document.getElementById('s-gender').value;
  const year = parseInt(document.getElementById('s-year').value);
  const month = parseInt(document.getElementById('s-month').value);
  const day = parseInt(document.getElementById('s-day').value);
  const shichenIdx = parseInt(document.getElementById('s-shichen').value);
  const lon = parseFloat(document.getElementById('s-lon').value) || 120;

  // Validation
  if (year < 1900 || year > 2099) { alert("年份需在1900-2099之间"); return; }
  if (month < 1 || month > 12) { alert("月份需在1-12之间"); return; }
  if (day < 1 || day > daysInMonth(year, month)) { alert("日期无效"); return; }

  const result = fullAnalysis(name, gender, year, month, day, shichenIdx, lon);

  // Store for compatibility use
  window._lastSingleResult = result;

  renderSingleResult(result);
}

function addPerson() {
  if (multiPersonCount >= 6) { alert("最多支持6人"); return; }
  multiPersonCount++;
  const idx = multiPersonCount;
  const personList = document.getElementById('person-list');

  const card = document.createElement('div');
  card.className = 'person-card';
  card.id = `person-${idx}`;
  card.innerHTML = `
    <div class="person-card-header">
      <span class="person-index">👤 第${idx}人</span>
      <button class="btn-danger btn-sm" onclick="removePerson(${idx})">移除</button>
    </div>
    <div class="form-grid">
      <div class="form-group"><label>姓名</label><input type="text" id="m-name-${idx}" placeholder="姓名"></div>
      <div class="form-group"><label>性别</label><select id="m-gender-${idx}"><option value="male">男</option><option value="female">女</option></select></div>
      <div class="form-group"><label>出生年份</label><input type="number" id="m-year-${idx}" min="1900" max="2099" value="1990"></div>
      <div class="form-group"><label>月份</label><input type="number" id="m-month-${idx}" min="1" max="12" value="1"></div>
      <div class="form-group"><label>日期</label><input type="number" id="m-day-${idx}" min="1" max="31" value="1"></div>
      <div class="form-group"><label>时辰</label><select id="m-shichen-${idx}">
        ${SHICHEN_NAMES.map((s,i) => `<option value="${i}" ${i===6?'selected':''}>${s} (${SHICHEN_RANGES[i]})</option>`).join('')}
      </select></div>
      <div class="form-group"><label>出生城市</label><input type="text" id="m-city-${idx}" placeholder="如：上海" onchange="autoFillLonM(${idx})" list="city-list"></div>
      <div class="form-group"><label>经度</label><input type="number" id="m-lon-${idx}" step="0.01" min="-180" max="180" value="121.47"></div>
    </div>`;
  personList.appendChild(card);
}

function removePerson(idx) {
  document.getElementById(`person-${idx}`).remove();
  // Renumber remaining
  const cards = document.querySelectorAll('.person-card');
  cards.forEach((card, i) => {
    card.querySelector('.person-index').textContent = `👤 第${i+1}人`;
  });
  multiPersonCount = cards.length;
}

function autoFillLon(prefix) {
  const city = document.getElementById(`${prefix}-city`).value.trim();
  const lon = getCityLon(city);
  if (lon !== null) {
    document.getElementById(`${prefix}-lon`).value = lon;
  }
}

function autoFillLonM(idx) {
  const city = document.getElementById(`m-city-${idx}`).value.trim();
  const lon = getCityLon(city);
  if (lon !== null) {
    document.getElementById(`m-lon-${idx}`).value = lon;
  }
}

function getCityLon(city) {
  // Parse hidden city data
  const dataEl = document.getElementById('hidden-city-data');
  if (!dataEl) return null;
  const pairs = dataEl.textContent.split('|');
  for (const pair of pairs) {
    const [name, lon] = pair.split('=');
    if (name === city) return parseFloat(lon);
  }
  return null;
}

function runMultiMode() {
  const cards = document.querySelectorAll('.person-card');
  if (cards.length < 2) { alert("多人模式至少需要2人"); return; }

  const relType = document.getElementById('rel-type').value;
  const results = [];

  for (let i = 0; i < cards.length; i++) {
    const card = cards[i];
    // Read inputs directly from each card's DOM (robust against ID changes after removals)
    const allInputs = card.querySelectorAll('input, select');
    const getVal = (idPart) => {
      for (const el of allInputs) {
        if (el.id && el.id.indexOf(idPart) >= 0) return el.value;
      }
      return null;
    };

    const name = getVal('name') || ('人员' + (i + 1));
    const gender = getVal('gender') || 'male';
    const year = parseInt(getVal('year')) || 1990;
    const month = parseInt(getVal('month')) || 1;
    const day = parseInt(getVal('day')) || 1;
    const shichenStr = getVal('shichen');
    const shichenIdx = shichenStr !== null ? parseInt(shichenStr) : 6;
    const lon = parseFloat(getVal('lon')) || 121.47;

    if (isNaN(year) || year < 1900 || year > 2099) { alert(name + ': 年份需在1900-2099之间'); return; }
    if (isNaN(month) || month < 1 || month > 12) { alert(name + ': 月份需在1-12之间'); return; }
    if (isNaN(day) || day < 1 || day > daysInMonth(year, month)) { alert(name + ': 日期无效'); return; }

    results.push(fullAnalysis(name, gender, year, month, day, shichenIdx, lon));
  }

  renderMultiResults(results, relType);
}

// ============================================================
//  SECTION 18: INITIALIZATION
// ============================================================

function init() {
  // Inject export button CSS
  const styleEl = document.createElement('style');
  styleEl.textContent = '.btn-export{padding:6px 14px;background:linear-gradient(135deg,var(--gold),#a8893a);color:#fff;border:none;border-radius:var(--radius-sm);font-family:var(--font-cn);font-size:0.82rem;cursor:pointer;letter-spacing:1px;transition:var(--transition);white-space:nowrap;margin-left:8px}.btn-export:hover{background:linear-gradient(135deg,#b8942e,#8a702a);transform:translateY(-1px);box-shadow:0 2px 8px rgba(201,169,110,0.4)}.btn-export:disabled{opacity:0.6;cursor:wait}@media print{.btn-export{display:none}}';
  document.head.appendChild(styleEl);

  // Populate city datalist
  const dataEl = document.getElementById('hidden-city-data');
  const datalist = document.getElementById('city-list');
  if (dataEl && datalist) {
    const pairs = dataEl.textContent.split('|');
    pairs.forEach(pair => {
      const [name] = pair.split('=');
      const opt = document.createElement('option');
      opt.value = name;
      datalist.appendChild(opt);
    });
  }

  // Initialize multi-mode with 2 persons
  addPerson();
  addPerson();
}

// Run on load
window.addEventListener('DOMContentLoaded', init);

// ============================================================
//  END OF SCRIPT
// ============================================================
"""

# Assemble: HTML wrapper + complete JS (constants + data + algorithms + UI)
final_html = pre_script + algo_js.strip() + post_body

# Write final HTML
with open(r"F:\FTP\操作问题汇总\神算子\index.html", "w", encoding="utf-8") as f:
    f.write(final_html)

print(f"Built index.html ({len(final_html)} bytes, ~{final_html.count(chr(10))} lines)")
