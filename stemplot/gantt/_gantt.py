from dataclasses import dataclass
from datetime import date, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

@dataclass
class Task:
    """Represents a task with attributes for Gantt chart plotting."""
    title: str                # Title of the task
    start: date               # Start date of the task
    end: date                 # End date of the task
    group: str = ""           # Group or category to which the task belongs
    resource: str = ""        # Resource or owner of the task
    progress: float = 0.0     # Progress of the task (0.0 to 1.0)
    color: str = ""           # Color code or name for plotting


def plot_gantt(tasks, ax=None):
    """Plots a Gantt chart for a list of Task objects using barh.
    If ax is None, a new figure and axes are created."""
    # Prepare figure and axes
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 6))
    else:
        fig = ax.figure

    # Convert dates to matplotlib format
    start_nums = [mdates.date2num(task.start) for task in tasks]
    end_nums = [mdates.date2num(task.end) for task in tasks]
    durations = [end - start for start, end in zip(start_nums, end_nums)]
    y_positions = list(range(len(tasks)))

    # Plot horizontal bars
    bar_height = 0.8
    ax.barh(y_positions, durations, left=start_nums,
            height=bar_height,
            color=[task.color or 'grey' for task in tasks],
            align='center')

    # Set axis limits
    ax.set_xlim(min(start_nums) - 1, max(end_nums) + 1)
    ax.set_ylim(-0.5, len(tasks) - 0.5)

    # Labeling
    ax.set_yticks(y_positions)
    ax.set_yticklabels([task.title for task in tasks])
    ax.invert_yaxis()

    # Format dates on x-axis
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()

    ax.set_xlabel('Date')
    ax.set_title('Gantt Chart (12 Tasks)')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    return fig, ax