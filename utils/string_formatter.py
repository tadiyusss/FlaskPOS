from datetime import datetime, timedelta
import random

class Format:
    def __init__(self):
        pass

    def convert_to_readable(self, num):
        if num == None:
            return 0
        if num >= 1_000_000_000:
            return f"{num / 1_000_000_000:.2f}B".rstrip('0').rstrip('.')
        elif num >= 1_000_000:
            return f"{num / 1_000_000:.2f}M".rstrip('0').rstrip('.')
        elif num >= 1_000:
            return f"{num / 1_000:.2f}k".rstrip('0').rstrip('.')
        return str(num)

    def get_current_week_range(self):
        today = datetime.today().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        return start_of_week, end_of_week

    def get_current_month_range(self):
        today = datetime.today().date()
        start_of_month = today.replace(day=1)
        end_of_month = start_of_month + timedelta(days=32)
        return start_of_month, end_of_month
    
    def rgb_generator(self, opacity=1):
        r = lambda: random.randint(0,255)
        return f'rgb({r()},{r()},{r()}, {opacity})'