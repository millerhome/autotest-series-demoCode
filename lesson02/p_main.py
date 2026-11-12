from premium import calc_premium


def main():
    print("成人 5 天：", calc_premium(30, 5))


print("__name__ =", __name__)

if __name__ == "__main__":      # 直接執行這個檔案時才成立
    main()
