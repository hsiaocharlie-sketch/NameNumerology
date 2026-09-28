#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
姓名数理姓名学工具（五格剖象法）
数据来源: Unicode Unihan_RadicalStrokeCounts.txt 的 kRSKangXi 字段
        （康熙字典 部首.部外笔画）
部首笔画表: 214 个康熙部首按传统笔画分组（标准固定表）
"""

import sys

UNIHAN_PATH = "/mnt/user-data/outputs/Unihan_RadicalStrokeCounts.txt"

# ---------- 214 个康熙部首 -> 部首本身的笔画数 ----------
# (起始部首号, 结束部首号, 笔画数)  含头含尾
RADICAL_STROKE_RANGES = [
    (1, 6, 1),
    (7, 29, 2),
    (30, 60, 3),
    (61, 94, 4),
    (95, 117, 5),
    (118, 146, 6),
    (147, 166, 7),
    (167, 175, 8),
    (176, 186, 9),
    (187, 194, 10),
    (195, 204, 11),
    (205, 208, 12),
    (209, 210, 13),
    (211, 211, 14),
    (212, 212, 15),
    (213, 213, 16),
    (214, 214, 17),
]

def radical_strokes(radical_no: int) -> int:
    for lo, hi, strokes in RADICAL_STROKE_RANGES:
        if lo <= radical_no <= hi:
            return strokes
    raise ValueError(f"未知部首编号: {radical_no}")

# ---------- 加载 Unihan kRSKangXi 数据 ----------
def load_kangxi_table(path):
    table = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("U+"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) != 3:
                continue
            cp, field, value = parts
            if field != "kRSKangXi":
                continue
            codepoint = int(cp[2:], 16)
            # 值形如 "140.12" 或 "140.12'"（撇号表示异体，先去掉）
            value = value.replace("'", "")
            rad_str, residual_str = value.split(".")
            radical_no = int(rad_str)
            residual = int(residual_str)
            table[codepoint] = (radical_no, residual)
    return table

KANGXI_TABLE = load_kangxi_table(UNIHAN_PATH)

def char_strokes(ch: str):
    """返回 (总笔画, 部首号, 部首笔画, 部外笔画)；查不到时返回 None"""
    cp = ord(ch)
    if cp not in KANGXI_TABLE:
        return None
    radical_no, residual = KANGXI_TABLE[cp]
    rad_strokes = radical_strokes(radical_no)
    total = rad_strokes + residual
    return total, radical_no, rad_strokes, residual

# ---------- 五行（尾数） ----------
WUXING_BY_LAST_DIGIT = {
    1: "木", 2: "木",
    3: "火", 4: "火",
    5: "土", 6: "土",
    7: "金", 8: "金",
    9: "水", 0: "水",
}

def wuxing(n: int) -> str:
    return WUXING_BY_LAST_DIGIT[n % 10]

# ---------- 五格计算 ----------
def analyze_name(surname: str, given: str):
    all_chars = list(surname) + list(given)
    strokes_info = []
    for ch in all_chars:
        info = char_strokes(ch)
        if info is None:
            raise ValueError(f"字 '{ch}' 未在 kRSKangXi 表中找到笔画数据，需要手动核对（如汉典）")
        strokes_info.append((ch, info))

    surname_strokes = [info[0] for _, info in strokes_info[:len(surname)]]
    given_strokes = [info[0] for _, info in strokes_info[len(surname):]]

    tian_ge = sum(surname_strokes) + (1 if len(surname) == 1 else 0)
    di_ge = sum(given_strokes) + (1 if len(given) == 1 else 0)
    ren_ge = surname_strokes[-1] + given_strokes[0]
    zong_ge = sum(surname_strokes) + sum(given_strokes)
    wai_ge = zong_ge - ren_ge + 1

    result = {
        "字笔画": [(ch, info[0]) for ch, info in strokes_info],
        "天格": (tian_ge, wuxing(tian_ge)),
        "人格": (ren_ge, wuxing(ren_ge)),
        "地格": (di_ge, wuxing(di_ge)),
        "外格": (wai_ge, wuxing(wai_ge)),
        "总格": (zong_ge, wuxing(zong_ge)),
    }
    return result

def print_report(surname: str, given: str):
    r = analyze_name(surname, given)
    print(f"姓名: {surname}{given}")
    print("各字笔画（康熙笔画，来自 kRSKangXi）：")
    for ch, s in r["字笔画"]:
        print(f"  {ch}: {s} 画")
    print()
    print("五格与三才五行：")
    for key in ["天格", "人格", "地格", "外格", "总格"]:
        num, wx = r[key]
        print(f"  {key}: {num}  （五行: {wx}）")
    print()
    tian, ren, di = r["天格"][1], r["人格"][1], r["地格"][1]
    print(f"三才配置（天·人·地）: {tian} · {ren} · {di}")

if __name__ == "__main__":
    if len(sys.argv) == 3:
        surname, given = sys.argv[1], sys.argv[2]
    else:
        # 默认演示：萧 茂豐
        surname, given = "萧", "茂豐"
    print_report(surname, given)
