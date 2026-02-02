#!/usr/bin/env python3
"""Claude Code 週次バジェット計算スクリプト

Usage:
    python3 budget_calc.py <current_usage> <year> <month> <day> <iso_weekday> <hour> <minute>

Example:
    python3 budget_calc.py 45.0 2026 1 28 3 9 40
"""
import sys
import math
from datetime import datetime, timedelta

# === 引数パース ===
if len(sys.argv) != 8:
    print("Usage: python3 budget_calc.py <usage%> <year> <month> <day> <iso_weekday> <hour> <minute>")
    sys.exit(1)

current_usage = float(sys.argv[1])
year = int(sys.argv[2])
month = int(sys.argv[3])
day = int(sys.argv[4])
iso_weekday = int(sys.argv[5])
current_hour = int(sys.argv[6])
current_minute = int(sys.argv[7])

# === 定数 ===
total_cycle_hours = 168.0
current_time_fraction = current_hour + current_minute / 60.0

# === 経過時間計算（木曜17:00起算） ===
if iso_weekday == 4 and current_time_fraction >= 17:
    elapsed_hours = current_time_fraction - 17
elif iso_weekday == 4 and current_time_fraction < 17:
    elapsed_hours = 7 + 6 * 24 + current_time_fraction
else:
    days_since_friday = (iso_weekday - 5 + 7) % 7
    elapsed_hours = 7 + days_since_friday * 24 + current_time_fraction

remaining_hours = total_cycle_hours - elapsed_hours
remaining_budget = 100.0 - current_usage
hourly_budget = remaining_budget / remaining_hours

# === 今日の残り時間とEOD目標 ===
hours_left_today = 24.0 - current_time_fraction
effective_hours_today = min(hours_left_today, remaining_hours)
today_budget = hourly_budget * effective_hours_today
target_eod = current_usage + today_budget

# === 理想ペース ===
ideal_usage = elapsed_hours / total_cycle_hours * 100
pace_diff = current_usage - ideal_usage
remaining_days_display = remaining_hours / 24.0

# === ペースステータス判定 ===
if pace_diff >= 15:
    icon, status_name = "\U0001f534", "危険"
elif pace_diff >= 5:
    icon, status_name = "\U0001f7e1", "注意"
elif pace_diff >= -5:
    icon, status_name = "\U0001f7e2", "良好"
elif pace_diff >= -15:
    icon, status_name = "\U0001f535", "余裕"
else:
    icon, status_name = "\u26aa", "大幅余裕"

# === サイクル期間計算 ===
today_date = datetime(year, month, day)
if iso_weekday == 4 and current_time_fraction >= 17:
    cycle_start = today_date.replace(hour=17)
elif iso_weekday == 4 and current_time_fraction < 17:
    cycle_start = (today_date - timedelta(days=7)).replace(hour=17)
else:
    days_back = (iso_weekday - 4 + 7) % 7
    cycle_start = (today_date - timedelta(days=days_back)).replace(hour=17)
cycle_end = cycle_start + timedelta(days=7)

# === 出力 ===
weekday_names = ["月", "火", "水", "木", "金", "土", "日"]
today_wday = weekday_names[today_date.weekday()]
pace_sign = "+" if pace_diff >= 0 else ""

# プログレスバー
bar_len = 20
used_chars = round(current_usage / 100 * bar_len)
remain_chars = bar_len - used_chars
bar = "[" + "=" * used_chars + "-" * remain_chars + "]"
ideal_pos = round(ideal_usage / 100 * bar_len) + 1

print(f"""## Claude Code 週次バジェットレポート

### 基本情報
| 項目 | 値 |
|------|-----|
| 実行日 | {year}-{month:02d}-{day:02d}（{today_wday}） |
| サイクル期間 | {cycle_start.month:02d}/{cycle_start.day:02d}（木）17:00 〜 {cycle_end.month:02d}/{cycle_end.day:02d}（木）17:00 |
| 進捗 | {elapsed_hours:.0f}h経過 / 168hサイクル（残り{remaining_hours:.0f}h） |

### 使用量サマリー
| 項目 | 値 |
|------|-----|
| 現在の使用量 | {current_usage:.1f}% |
| 残りバジェット | {remaining_budget:.1f}% |
| 残り時間 | {remaining_hours:.0f}h（{remaining_days_display:.1f}日相当） |
| 今日の目標（EOD） | {target_eod:.1f}% |
| 1時間あたりバジェット | {hourly_budget:.2f}% |

### ペースメーター
{icon} **{status_name}**（理想比 {pace_sign}{pace_diff:.1f}%）

{bar} {current_usage:.1f}% / 100%
{' ' * ideal_pos}↑現在値    ↑理想({ideal_usage:.1f}%)""")

# === アドバイス ===
print("\n### アドバイス")
if pace_diff >= 15:
    print(f"""今週の使用ペースが大幅に速いです。
- 残り{remaining_hours:.0f}時間（{remaining_days_display:.1f}日相当）で{remaining_budget:.1f}%を使う必要があります
- 今日の残り配分: {today_budget:.1f}%
- 重要度の低いタスクは来週に回すことを検討してください
- コンテキストの大きいタスク（コードベース探索等）は控えめに""")
elif pace_diff >= 5:
    print(f"""やや使いすぎのペースです。意識的にセーブしましょう。
- 今日の目標: {target_eod:.1f}%以内
- 1回のセッションを短めに区切ると効果的です
- `/usage` でこまめに確認しましょう""")
elif pace_diff >= -5:
    print(f"""理想的なペースです。このまま継続しましょう。
- 今日の目標: {target_eod:.1f}%以内
- 均等配分で週末まで快適に使えます""")
elif pace_diff >= -15:
    print(f"""余裕があります。積極的に活用できます。
- 今日の残り配分: {today_budget:.1f}%
- コードベース探索や大きなリファクタリングにも対応可能
- 記事の品質チェック（/polish）なども余裕を持って実行できます""")
else:
    print(f"""大幅に余裕があります。週の後半で集中的に活用しましょう。
- 今日の残り配分: {today_budget:.1f}%
- 複数記事の一括チェックや大規模タスクに最適
- 使い切れない場合でも翌週にリセットされるため、積極活用を推奨""")

# === 日別バジェット配分テーブル ===
print(f"""
### 残り日別バジェット配分
| 日付 | 曜日 | 時間 | 割当% | 累計目標% |
|------|------|------|-------|----------|""")

cumulative = 0.0
hrs_left = remaining_hours
day_offset = 0

while hrs_left > 0.01:
    d = today_date + timedelta(days=day_offset)
    d_iso_weekday = d.isoweekday()

    if day_offset == 0:
        day_hours = effective_hours_today
    elif d_iso_weekday == 4:
        day_hours = 17.0
    else:
        day_hours = 24.0

    day_hours = min(day_hours, hrs_left)
    alloc = hourly_budget * day_hours
    cumulative += alloc
    cumul_target = current_usage + cumulative

    date_str = f"{d.month:02d}/{d.day:02d}"
    wday = weekday_names[d.weekday()]

    if day_offset == 0:
        print(f"| **{date_str}** | **{wday}** | **{day_hours:.1f}h** | **{alloc:.1f}%** | **{cumul_target:.1f}%** |")
    else:
        print(f"| {date_str} | {wday} | {day_hours:.1f}h | {alloc:.1f}% | {cumul_target:.1f}% |")

    hrs_left -= day_hours
    day_offset += 1
