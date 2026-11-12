"""自動化多久回本？（簡化模型，數字請換成自己團隊的）"""
import math


def break_even_runs(build_hours, manual_hours_per_run, maintain_hours_per_run):
    saved = manual_hours_per_run - maintain_hours_per_run
    if saved <= 0:
        return None            # 每跑一次都在賠，永遠不會回本
    return math.ceil(build_hours / saved)


print("穩定流程：", break_even_runs(16, 0.5, 0.1), "次回本")
print("常改版流程：", break_even_runs(16, 0.5, 0.6))
