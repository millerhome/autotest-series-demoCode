from dataclasses import dataclass


@dataclass
class Policy:
    no: str
    age: int
    days: int = 1

    def is_senior(self) -> bool:
        return self.age >= 65


p = Policy("TP001", 65, days=5)
print(p)
print(p.is_senior(), p == Policy("TP001", 65, 5))
