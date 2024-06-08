import datetime

from strings import DatetimeEndings


def get_ending(time_measure: int, time_measure_key: str):
    endings = {"week": DatetimeEndings.week, "day": DatetimeEndings.days, "hour": DatetimeEndings.hours}
    source = endings.get(time_measure_key)
    if source is None:
        raise TypeError()
    if time_measure % 10 == 1:
        ending = source[0]
    elif 2 <= time_measure % 10 <= 4:
        ending = source[1]
    else:
        ending = source[2]
    return ending


def get_timedelta(date: datetime.datetime):
    timedelta = date - datetime.datetime.now()
    seconds = timedelta.total_seconds()
    weeks = int(seconds // 604800)
    seconds -= weeks*604800
    days = int(seconds // 86400)
    seconds -= days*86400
    hours = int(seconds // 3600)
    week_ending = get_ending(weeks, "week")
    day_ending = get_ending(days, "day")
    hour_ending = get_ending(hours, "hour")
    template = f"{weeks} {week_ending} {days} {day_ending} и {hours} {hour_ending}"
    if not weeks:
        template = f"{days} {day_ending} и {hours} {hour_ending}"
        if not days:
            template = f"{hours} {hour_ending}"
        return template
    elif not days:
        template = f"{hours} {hour_ending}"
    return template