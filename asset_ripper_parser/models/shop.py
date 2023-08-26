"""All classes related to places where stuff can be bought in game."""
from asset_ripper_parser.models.item import Item


class SoldItem(Item):
    """An item that is sold by a merchant."""

    def __init__(self, name: str):
        super().__init__(name)
        self.price = 0
        self.price_type = "Coins"
        self.quantity = None  # None if unlimited, else amount
        self.limited = False
        self.restock_days = 1
        self.stock_chance = 1

    def __str__(self):
        quantity = f"x{self.quantity} " if self.limited else ""
        stocked = (
            f"stocked every {self.restock_days} days " if self.restock_days > 1 else ""
        )
        chance = f" for {self.stock_chance} chance" if self.stock_chance > 1 else ""
        return f"{quantity}{self.name} sells for {self.price} {self.price_type} {stocked}{chance}"


class RandomSelection:
    """Items that are randomly selected to be in stock."""

    def __init__(self):
        self.selection_name = ""
        self.amount_selected = 1
        self.items = []

    def __str__(self) -> str:
        name = "of:" if self.selection_name is None else self.selection_name
        result = [f"x{self.amount_selected} {name}"]
        result += ["\t- " + str(item) for item in self.items]

        return "\n".join(result)


class Shop:
    """Represents someone who sells items in game."""

    def __init__(self):
        self.shop_name = ""
        self.seller_name = ""
        self.always_stocked_items = []
        self.random_selections = []

    def __str__(self) -> str:
        name = self.seller_name
        if self.shop_name is not None:
            name = f"{self.shop_name} ({self.seller_name})"

        if not self.seller_name:
            name = name.replace("()", "")

        result = [name]
        result += ["\t- " + str(item) for item in self.always_stocked_items]
        result += [str(x) for x in self.random_selections]

        return "\n".join(result)

    def combine_colored_items(self):
        filtered_items = []

        # pylint: disable=line-too-long
        for item in self.always_stocked_items:
            # check item is not already added, and verify that the price is the same.
            if not [
                x
                for x in filtered_items
                if x.name == item.name and x.price == item.price
            ]:
                filtered_items.append(item)

        self.always_stocked_items = filtered_items

        for selection in self.random_selections:
            filtered_selections = []
            for item in selection.items:
                # check item is not already added, and verify that the price is the same.
                if not [
                    x
                    for x in filtered_selections
                    if x.name == item.name and x.price == item.price
                ]:
                    filtered_selections.append(item)
            selection.items = filtered_selections

    def to_wiki_tags(self) -> str:
        """Returns a {{Shop}} template that can be used on merchant pages.

        Returns:
            str: resulting populated template tags.
        """
        name = self.seller_name
        if self.shop_name is not None:
            name = f"{self.shop_name} ({self.seller_name})"

        if not self.seller_name:
            name = name.replace("()", "")

        result = [name]

        if self.random_selections and [
            x for x in self.random_selections if x.amount_selected > 0
        ]:
            result.append("Randomly Sells:")
            selection_text = []
            for selection in self.random_selections:
                if (
                    selection.selection_name is not None
                    and selection.amount_selected > 0
                ):
                    selection_text.append(
                        f"\t{selection.amount_selected} {selection.selection_name}"
                    )
                elif selection.amount_selected > 0:
                    item_names = [x.name for x in selection.items]
                    selection_text.append(
                        f"\t{selection.amount_selected}: {','.join(item_names)}"
                    )

            result.append("\n".join(selection_text))

        result.append("\n{{Shop/header}}")

        for item in self.always_stocked_items:
            image_name = ""
            if item.variant is not None:
                image_name = f"|img={item.name}_{item.variant.lower()}_0"

            result.append(
                "{{Shop|"
                + f"{item.name}|{item.price}|{item.price_type}{image_name}"
                + "}}"
            )

        total_random_items = sum(x.amount_selected for x in self.random_selections)
        for selection in self.random_selections:
            if selection.amount_selected > 0:
                for item in selection.items:
                    existing_entry = [x for x in result if item.name in x]
                    note = ""
                    if existing_entry and item.variant is not None:
                        note = f"|note={item.variant} priced differently."
                    elif total_random_items < len(self.always_stocked_items):
                        note = "|note=Randomly available."

                    image_name = ""
                    if item.variant is not None:
                        image_name = f"|img={item.name}_{item.variant.lower()}_0"
                    result.append(
                        "{{Shop|"
                        + f"{item.name}|{item.price}|{item.price_type}{note}{image_name}"
                        + "}}"
                    )

        result.append("{{Shop/footer}}")

        return "\n".join(result)
