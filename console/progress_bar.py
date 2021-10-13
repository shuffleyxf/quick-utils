from progressbar import widgets, ProgressBar

base_widgets = [
    ' ', widgets.Bar(),
    widgets.Percentage(),
    ' ', widgets.SimpleProgress(
        format='(%s)' % widgets.SimpleProgress.DEFAULT_FORMAT),
]
IN_VALID = -1


global_bar = None


def init_bar(min_val=0, max_val=100, show_time=False, show_eta=False):
    global global_bar
    t_widgets = base_widgets.copy()
    if show_time:
        t_widgets.extend([' ', widgets.Timer()])
    if show_eta:
        t_widgets.extend([' ', widgets.AdaptiveETA()])
    global_bar = ProgressBar(min_value=min_val, max_value=max_val, widgets=t_widgets)


def iter_bar(iterable):
    if global_bar is None or global_bar.end_time is not None:
        init_bar()
    global_bar.max_value = len(iterable)
    return global_bar(iterable)


def update_bar(val=-1, step=1):
    if global_bar is None:
        init_bar()
        global_bar.start()
    if val != IN_VALID:
        global_bar.update(val)
    else:
        try:
            global_bar.update(global_bar.value + step)
        except ValueError:
            global_bar.finish()
            raise
    if val == global_bar.max_value:
        global_bar.finish()

