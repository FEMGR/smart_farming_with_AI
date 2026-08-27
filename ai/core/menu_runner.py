# ai/core/menu_runner.py

from dataclasses import dataclass
from typing import Callable, Optional, Sequence


@dataclass
class MenuItem:
    key: str
    label: str
    action: Callable[[bool], None]


class MenuRunner:
    def __init__(
        self,
        title: str,
        items: Sequence[MenuItem],
        prompt_func: Callable[[], Optional[str]],
        pause_func: Callable[[], bool],
        notes: Optional[Sequence[str]] = None,
    ):
        self.title = title
        self.items = {item.key: item for item in items}
        self.prompt_func = prompt_func
        self.pause_func = pause_func
        self.notes = notes or []

    def print_menu(self) -> None:
        print("\n" + "=" * 49)
        print(self.title)
        print("=" * 49)

        for key, item in self.items.items():
            print(f"{key}. {item.label}")

        if self.notes:
            print("")
            for note in self.notes:
                print(f"Note: {note}")

        print("=" * 49)

    def run(self, dry_run: bool = False) -> None:
        while True:
            self.print_menu()
            choice = self.prompt_func()

            if choice is None or choice == "0":
                print("Goodbye.")
                return

            menu_item = self.items.get(choice)

            if not menu_item:
                print("Invalid option.")
                if not self.pause_func():
                    return
                continue

            print(f"\nSelected: {menu_item.label}")
            menu_item.action(dry_run)

            if not self.pause_func():
                return
