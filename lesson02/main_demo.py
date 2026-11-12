from premium import calc_premium, load_rates
import premium as p

print(calc_premium(30, 5))
print(load_rates()["max_age"], p.RATES_FILE.name)
