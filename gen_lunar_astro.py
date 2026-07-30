"""
精确农历计算 — 基于天文算法计算朔日（新月）
使用Jean Meeus天文算法计算太阳和月球位置
"""
import math
from datetime import date, timedelta

# 太阳黄经计算 (简化VSOP87)
def solar_longitude(jd):
    """计算太阳黄经（度数）"""
    T = (jd - 2451545.0) / 36525.0
    L0 = 280.46646 + 36000.76983 * T + 0.0003032 * T * T
    M = 357.52911 + 35999.05029 * T - 0.0001537 * T * T
    C = (1.914602 - 0.004817 * T - 0.000014 * T * T) * math.sin(math.radians(M))
    C += (0.019993 - 0.000101 * T) * math.sin(math.radians(2 * M))
    C += 0.000289 * math.sin(math.radians(3 * M))
    L = L0 + C
    return L % 360

def new_moon_times(year):
    """计算给定年份的所有朔日（新月）时刻，返回(年,月,日)列表"""
    # 1900-01-01 12:00:00 UT 对应的儒略日
    jd0 = 2415020.5
    # 1900-01-01 的近似月龄 (以朔望月为单位)
    # 已知: 1900-01-01 大约在新月后12.4天
    k = int((year - 1900) * 12.3685)

    new_moons = []
    for i in range(k, k + 15):
        # 第k个朔望月的近似儒略日
        T = i / 1236.85
        jd = 2415020.75933 + 29.53058868 * i + 0.0001178 * T * T - 0.000000155 * T * T * T
        jd += 0.00033 * math.sin(math.radians(166.56 + 132.87 * T - 0.009173 * T * T))

        M = 359.2242 + 29.10535608 * i - 0.0000333 * T * T - 0.00000347 * T * T * T
        Mpr = 306.0253 + 385.81691806 * i + 0.0107306 * T * T + 0.00001236 * T * T * T
        F = 21.2964 + 390.67050646 * i - 0.0016528 * T * T - 0.00000239 * T * T * T

        jd += (0.1734 - 0.000393 * T) * math.sin(math.radians(M))
        jd += 0.0021 * math.sin(math.radians(2 * M))
        jd -= 0.4068 * math.sin(math.radians(Mpr))
        jd += 0.0161 * math.sin(math.radians(2 * Mpr))
        jd -= 0.0004 * math.sin(math.radians(3 * Mpr))
        jd += 0.0104 * math.sin(math.radians(2 * F))
        jd -= 0.0051 * math.sin(math.radians(M + Mpr))
        jd -= 0.0074 * math.sin(math.radians(M - Mpr))
        jd += 0.0004 * math.sin(math.radians(2 * F + M))
        jd -= 0.0004 * math.sin(math.radians(2 * F - M))
        jd -= 0.0006 * math.sin(math.radians(2 * F + Mpr))
        jd += 0.0010 * math.sin(math.radians(2 * F - Mpr))
        jd += 0.0005 * math.sin(math.radians(M + 2 * Mpr))

        # 转换为公历日期
        jd_int = int(jd + 0.5)
        z = jd_int
        if z < 2299161:
            a = z
        else:
            alpha = int((z - 1867216.25) / 36524.25)
            a = z + 1 + alpha - int(alpha / 4)
        b = a + 1524
        c = int((b - 122.1) / 365.25)
        d = int(365.25 * c)
        e = int((b - d) / 30.6001)
        day = b - d - int(30.6001 * e)
        month = e - 1 if e < 14 else e - 13
        yr = c - 4716 if month > 2 else c - 4715

        if 1899 <= yr <= 2100:
            new_moons.append((yr, month, day))

    return new_moons

def get_solar_term_jd(year, term_index):
    """计算24节气对应的儒略日 (term_index: 0=春分, 每15度一个)"""
    # Simplified: use the mean tropical year
    # This is approximate - accurate to about 1 day
    pass  # We don't need exact solar terms for the lunar calendar approach below

def generate_lunar_data():
    """生成1900-2099年农历数据"""
    lunar_data = {}

    # 已知的春节日期用于校准 (1900年)
    # 1900年春节 = 1月31日
    # 使用天文算法计算新月，然后确定春节（第二个新月在冬至后的日期）

    for year in range(1900, 2100):
        new_moons = new_moon_times(year)
        # 也获取前一年的最后几个新月
        prev_moons = new_moon_times(year - 1)

        # 合并前后年份的新月
        all_moons = [(y,m,d) for (y,m,d) in prev_moons if y == year or y == year - 1]
        all_moons += [(y,m,d) for (y,m,d) in new_moons if y == year]

        # 去重并排序
        all_moons = sorted(set(all_moons))

        if len(all_moons) < 12:
            continue

        # 取前13个（含可能的闰月）
        moons = all_moons[:14]  # Take up to 14 new moons

        # 计算每月长度（从新月到下一个新月）
        month_lengths = []
        for i in range(len(moons) - 1):
            d1 = date(*moons[i])
            d2 = date(*moons[i+1])
            days = (d2 - d1).days
            month_lengths.append(days)

        # 春节 = 第2个或第3个新月（取决于是否有闰）
        # 简化：春节 = 冬至后第二个新月
        # 实际中，我们取第2或第3个作为春节

        # 简单的启发式：取第2个新月作为春节（大多数年份如此）
        if len(month_lengths) >= 12:
            lny_idx = 1  # 第2个新月 = 春节
            lny_yr, lny_m, lny_d = moons[lny_idx]

            # 取前12个月的长度
            months = month_lengths[lny_idx:lny_idx+12]
            if len(months) >= 12:
                leap = 0  # Simplified

                lunar_data[year] = {
                    "lny": [lny_m, lny_d],
                    "months": months[:12],
                    "leap": leap
                }

    return lunar_data

# Generate and test
if __name__ == "__main__":
    data = generate_lunar_data()

    # Print sample
    for year in [1964, 1991, 2024]:
        if year in data:
            d = data[year]
            print(f"{year}: LNY={d['lny']}, months={d['months'][:3]}..., leap={d['leap']}")

    print(f"Total years: {len(data)}")
