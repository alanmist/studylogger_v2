import datetime as dt

class Session:
    def __init__(self, subject,topic, planned_minutes):
        self.subject  =subject
        self.topic = topic
        self.planned_minutes = int(planned_minutes)
        self.start_time = dt.datetime.now().astimezone()
        self.planned_end = self.start_time + dt.timedelta(minutes=self.planned_minutes)
        self.paused = False
        self.paused_at = None
        self.pause_accum_sec = 0

    def pause(self):
        if self.paused:
            return
        self.paused =True
        self.paused_at = dt.datetime.now().astimezone()

    def resume(self):
        if not self.paused or self.paused_at is None:
            return
        pause_duration = dt.datetime.now().astimezone() - self.paused_at
        self.pause_accum_sec += int(pause_duration.total_seconds())
        self.planned_end += pause_duration
        self.paused = False
        self.paused_at = None

            
    def actual_study_minutes(self):
        now = dt.datetime.now().astimezone()
        total_seconds = (now - self.start_time).total_seconds()
        return int((total_seconds -self.pause_accum_sec)//60)
    
if __name__ == "__main__":
    s = Session("Math", "Quadratic equations", 60)
    print(f"Subject: {s.subject}")
    print(f"Topic: {s.topic}")
    print(f"Planned minutes: {s.planned_minutes}")
    print(f"Start time: {s.start_time}")
    print(f"Planned end: {s.planned_end}")
    print(f"Paused: {s.paused}")
