from __future__ import annotations

import argparse
import time

import numpy as np
import pandas as pd

from src.config import DA_CONFIG
from utils import ConnectMysql


def sample_by_user(percent: int) -> pd.DataFrame:
    """流式扫描 CSV，只保留 user_id 落在抽样桶里的行（这些用户的行全部保留）。"""
    stride = max(1, 100 // percent)
    chunks: list[pd.DataFrame] = []
    scanned = 0
    started = time.time()

    reader = pd.read_csv(DA_CONFIG["data_path"], chunksize=2_000_000)
    for chunk in reader:
        scanned += len(chunk)
        hit = chunk[chunk["user_id"] % stride == 0]
        if not hit.empty:
            chunks.append(hit)
        kept = sum(len(c) for c in chunks)
        print(f"\r  扫描 {scanned:>11,} 行，命中 {kept:>9,} 行", end="", flush=True)

    print(f"\n  扫描完成：{scanned:,} 行，用时 {time.time() - started:.0f}s")
    if not chunks:
        raise RuntimeError(f"没抽到数据，percent={percent} 可能过小")

    data = pd.concat(chunks, ignore_index=True)
    data["user_id"] = data["user_id"].astype(str)
    data["product_id"] = data["product_id"].astype(str)
    data["category_id"] = data["category_id"].astype(str)
    data["datetime"] = pd.to_datetime(data["timestamp"], unit="s")
    data["date"] = data["datetime"].dt.normalize()
    data["month"] = data["datetime"].dt.month
    data["hour"] = data["datetime"].dt.hour

    start, end = DA_CONFIG["date"]["start"], DA_CONFIG["date"]["end"]
    data = data[(data["date"] >= start) & (data["date"] <= end)]
    return data.reset_index(drop=True)


def write_mysql(data: pd.DataFrame) -> None:
    engine = ConnectMysql().get_engine()
    started = time.time()
    data.to_sql(
        DA_CONFIG["table"],
        engine,
        index=False,
        if_exists="replace",
        method="multi",
        chunksize=10_000,
    )
    print(f"  写入 {DA_CONFIG['table']}：{len(data):,} 行，用时 {time.time() - started:.0f}s")


def report(data: pd.DataFrame) -> None:
    """把可以直接写进简历的指标打印出来。"""
    pv_s = set(data.loc[data["behavior"] == "pv", "user_id"])
    fav_s = set(data.loc[data["behavior"] == "fav", "user_id"])
    cart_s = set(data.loc[data["behavior"] == "cart", "user_id"])
    buy_s = set(data.loc[data["behavior"] == "buy", "user_id"])
    intent_s = fav_s | cart_s
    buy_in_intent = buy_s & intent_s
    total_users = int(data["user_id"].nunique())

    print("\n" + "=" * 60)
    print("数据规模")
    print(
        f"  日志 {len(data):,} 条 ｜ 用户 {total_users:,} ｜ "
        f"商品 {data['product_id'].nunique():,} ｜ 类目 {data['category_id'].nunique():,}"
    )
    print(
        f"  时间 {data['datetime'].min():%Y-%m-%d} ~ {data['datetime'].max():%Y-%m-%d}"
        f"（{data['date'].nunique()} 天） ｜ 平均每用户 {len(data) / total_users:.1f} 条行为"
    )

    print("\n行为分布（去重用户 / 行数）")
    for name, users, rows in (
        ("浏览 pv", pv_s, int((data["behavior"] == "pv").sum())),
        ("收藏 fav", fav_s, int((data["behavior"] == "fav").sum())),
        ("加购 cart", cart_s, int((data["behavior"] == "cart").sum())),
        ("购买 buy", buy_s, int((data["behavior"] == "buy").sum())),
    ):
        print(f"  {name:<10}{len(users):>8,} 人 ({len(users) / total_users:6.1%}) ｜ {rows:>10,} 行")

    print("\n转化漏斗（去重用户）")
    print(f"  浏览 {len(pv_s):,} → 意向（收藏或加购）{len(intent_s):,} → 购买 {len(buy_s):,}")
    print(
        f"  浏览→意向 {len(intent_s) / len(pv_s):.2%} ｜ "
        f"浏览→购买 {len(buy_s) / len(pv_s):.2%} ｜ "
        f"意向→购买 {len(buy_in_intent) / len(intent_s):.2%}"
    )

    buyers = (
        data[data["behavior"] == "buy"]
        .groupby("user_id")
        .agg(R=("datetime", "max"), F=("datetime", "size"))
    )
    repeat = int((buyers["F"] >= 2).sum())
    print("\n购买用户")
    print(
        f"  购买用户 {len(buyers):,} ｜ 复购用户 {repeat:,}（{repeat / len(buyers):.1%}）"
        f" ｜ 人均购买 {buyers['F'].mean():.2f} 次 ｜ 最高 {int(buyers['F'].max())} 次"
    )

    desc = buyers["R"].describe()
    r_bin = [desc["min"], desc["50%"], desc["75%"], desc["max"]]
    buyers["R_score"] = pd.cut(buyers["R"], bins=r_bin, labels=[1, 2, 3], include_lowest=True)
    buyers["F_score"] = pd.cut(
        buyers["F"], bins=[0, 1, 3, np.inf], labels=[1, 2, 3], right=True
    )
    buyers["RF"] = buyers["R_score"].astype(str) + buyers["F_score"].astype(str)
    seg = buyers.groupby("RF").size().sort_values(ascending=False)
    print("\nRF 分层（R 越近分越高，F 越买分越高）")
    for code, cnt in seg.items():
        print(f"  RF={code}  {cnt:>8,} 人  {cnt / len(buyers):>6.1%}")
    print("=" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(description="按 user_id 抽样并写入 MySQL")
    parser.add_argument("--percent", type=int, default=2, help="抽样比例，默认 2（约 2 万用户）")
    parser.add_argument("--skip-write", action="store_true", help="只统计，不写库")
    args = parser.parse_args()

    data = sample_by_user(args.percent)
    report(data)
    if not args.skip_write:
        write_mysql(data)


if __name__ == "__main__":
    main()
