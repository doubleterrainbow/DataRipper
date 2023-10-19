class RandomDrop:
    def __init__(
        self,
        item_name="",
        min_amount=0,
        max_amount=0,
        drop_weight=0,
        percent_chance=0.0,
    ):
        self.item_name = item_name
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.drop_weight = drop_weight
        self.percent_chance = percent_chance
