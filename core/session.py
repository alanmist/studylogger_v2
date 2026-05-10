import datetime as dt


class Session:
    def __init__(self, subject, topic, planned_minutes):
        self.subject = subject
        self.topic = topic
        self.planned_minutes = int(planned_minutes)
        self.start_time = dt.datetime.now().astimezone()
        self.planned_end = self.start_time + dt.timedelta(minutes=self.planned_minutes)
        self.paused = False
        self.paused_at = None
        self.pause_accum_sec = 0
        self.remaining_at_pause_min = None

    def pause(self):
        if self.paused:
            return
        self.paused = True
        self.paused_at = dt.datetime.now().astimezone()
        self.remaining_at_pause_min = max(
            0, int((self.planned_end - self.paused_at).total_seconds() // 60)
        )

    def resume(self):
        if not self.paused or self.paused_at is None:
            return
        pause_duration = dt.datetime.now().astimezone() - self.paused_at
        self.pause_accum_sec += int(pause_duration.total_seconds())
        self.planned_end += pause_duration
        self.paused = False
        self.paused_at = None
        self.remaining_at_pause_min = None

    def actual_study_minutes(self):
        now = dt.datetime.now().astimezone()
        total_seconds = (now - self.start_time).total_seconds()
        return int((total_seconds - self.pause_accum_sec) // 60)
