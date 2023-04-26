from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn
from rich.theme import Theme
from rich.console import Console


class ProgressBar(object):
    def __init__(self):
        custom_theme = Theme({"bar.finished": "cyan", "bar.complete": "cyan", "progress.percentage": "yellow"})
        console = Console(theme=custom_theme)
        self.progress = Progress(TextColumn("{task.description}"), BarColumn(), TaskProgressColumn(), console=console)
        self.progress.__enter__()
        self.task = self.progress.add_task("[bold]Fan Speed[/bold]", total=100)

    def __del__(self):
        self.progress.__exit__(None, None, None)

    def display_fan_speed(self, duty_cycle: float):
        self.progress.update(self.task, completed=duty_cycle)
