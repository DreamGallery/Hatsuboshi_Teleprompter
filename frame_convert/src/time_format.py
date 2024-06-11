def format_time(second: float) -> str:
    H = second // 3600
    M = (second - H * 3600) // 60
    S = second - H * 3600 - M * 60
    format_time = "%d:%02d:%05.2f" % (H, M, S)
    return format_time


def end_time(startTime: float, duration: float) -> str:
    endTime = format_time(startTime + duration)
    return endTime
