#!/usr/bin/env python3
"""
Digital Clock with Traditional Watch Controls
Uses Textual-EnGlyph for display and traditional digital watch button interface
"""

from datetime import datetime, timedelta
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, Container
from textual.widgets import Button, Static, Label
from textual.timer import Timer
from textual_englyph import EnGlyphText
from enum import Enum


class ClockMode(Enum):
    TIME = "TIME"
    SET_HOUR = "SET HOUR"
    SET_MINUTE = "SET MINUTE"
    SET_SECOND = "SET SECOND"
    ALARM = "ALARM"
    SET_ALARM_HOUR = "SET ALARM HOUR"
    SET_ALARM_MINUTE = "SET ALARM MINUTE"
    STOPWATCH = "STOPWATCH"
    TIMER = "TIMER"


class DigitalClock(App):
    """A digital clock app with traditional watch controls"""
    
    CSS = """
    Screen {
        layout: vertical;
        align: center middle;
        padding: 2;
    }
    
    #clock-display {
        height: 12;
        border: solid $primary;
        margin: 1 2;
        padding: 1;
    }
    
    #status-bar {
        height: 3;
        border: solid $secondary;
        margin: 0 2;
        padding: 0 1;
    }
    
    #controls {
        height: 8;
        margin: 1 2;
    }
    
    .button-row {
        height: 3;
        margin: 0 0 1 0;
    }
    
    Button {
        margin: 0 1;
        min-width: 8;
    }
    
    .mode-button {
        background: $primary;
        color: $text;
    }
    
    .action-button {
        background: $secondary;
        color: $text;
    }
    
    .blink {
        background: $warning;
    }
    """
    
    def __init__(self):
        super().__init__()
        self.current_time = datetime.now()
        self.display_time = self.current_time
        self.alarm_time = datetime.now().replace(hour=7, minute=0, second=0, microsecond=0)
        self.alarm_enabled = False
        self.mode = ClockMode.TIME
        self.stopwatch_start = None
        self.stopwatch_elapsed = timedelta()
        self.stopwatch_running = False
        self.timer_duration = timedelta(minutes=5)
        self.timer_start = None
        self.timer_running = False
        self.blink_state = True
        self.setting_blink = False
        
    def compose(self) -> ComposeResult:
        with Container(id="clock-display"):
            yield EnGlyphText("", id="time-display", text_size="xx-large")
            yield Static("", id="date-display")
            
        with Container(id="status-bar"):
            yield Static("", id="mode-display")
            yield Static("", id="status-info")
            
        with Vertical(id="controls"):
            with Horizontal(classes="button-row"):
                yield Button("MODE", id="mode-btn", classes="mode-button")
                yield Button("LIGHT", id="light-btn", classes="action-button")
                yield Button("SET", id="set-btn", classes="action-button")
                
            with Horizontal(classes="button-row"):
                yield Button("◀", id="prev-btn", classes="action-button")
                yield Button("START/STOP", id="start-stop-btn", classes="action-button")
                yield Button("▶", id="next-btn", classes="action-button")
                
    def on_mount(self) -> None:
        """Initialize timers and display"""
        self.timer = self.set_interval(1/10, self.update_time)  # 100ms updates for smooth blinking
        self.update_display()
        
    def update_time(self) -> None:
        """Update the current time and handle various timers"""
        if self.mode == ClockMode.TIME:
            self.current_time = datetime.now()
            self.display_time = self.current_time
            
        # Handle stopwatch
        if self.stopwatch_running and self.stopwatch_start:
            self.stopwatch_elapsed = datetime.now() - self.stopwatch_start
            
        # Handle countdown timer
        if self.timer_running and self.timer_start:
            elapsed = datetime.now() - self.timer_start
            remaining = self.timer_duration - elapsed
            if remaining.total_seconds() <= 0:
                self.timer_running = False
                # Timer finished - could add beep/alert here
                
        # Handle blinking for setting mode
        if self.mode in [ClockMode.SET_HOUR, ClockMode.SET_MINUTE, ClockMode.SET_SECOND,
                        ClockMode.SET_ALARM_HOUR, ClockMode.SET_ALARM_MINUTE]:
            self.blink_state = not self.blink_state
            
        self.update_display()
        
    def update_display(self) -> None:
        """Update all display elements"""
        time_display = self.query_one("#time-display", EnGlyphText)
        date_display = self.query_one("#date-display", Static)
        mode_display = self.query_one("#mode-display", Static)
        status_info = self.query_one("#status-info", Static)
        
        # Format time based on current mode
        if self.mode == ClockMode.STOPWATCH:
            total_seconds = int(self.stopwatch_elapsed.total_seconds())
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            hundredths = int((self.stopwatch_elapsed.microseconds / 10000))
            time_str = f"{minutes:02d}:{seconds:02d}.{hundredths:02d}"
            
        elif self.mode == ClockMode.TIMER:
            if self.timer_running and self.timer_start:
                elapsed = datetime.now() - self.timer_start
                remaining = self.timer_duration - elapsed
                if remaining.total_seconds() > 0:
                    total_seconds = int(remaining.total_seconds())
                    minutes = total_seconds // 60
                    seconds = total_seconds % 60
                    time_str = f"{minutes:02d}:{seconds:02d}"
                else:
                    time_str = "00:00"
            else:
                total_seconds = int(self.timer_duration.total_seconds())
                minutes = total_seconds // 60
                seconds = total_seconds % 60
                time_str = f"{minutes:02d}:{seconds:02d}"
                
        elif self.mode in [ClockMode.ALARM, ClockMode.SET_ALARM_HOUR, ClockMode.SET_ALARM_MINUTE]:
            # Show alarm time
            display_time = self.alarm_time
            hour_str = f"{display_time.hour:02d}"
            minute_str = f"{display_time.minute:02d}"
            
            # Handle blinking during setting
            if self.mode == ClockMode.SET_ALARM_HOUR and not self.blink_state:
                hour_str = "  "
            elif self.mode == ClockMode.SET_ALARM_MINUTE and not self.blink_state:
                minute_str = "  "
                
            time_str = f"{hour_str}:{minute_str}"
            
        else:
            # Regular time display
            display_time = self.display_time
            hour_str = f"{display_time.hour:02d}"
            minute_str = f"{display_time.minute:02d}"
            second_str = f"{display_time.second:02d}"
            
            # Handle blinking during setting
            if self.mode == ClockMode.SET_HOUR and not self.blink_state:
                hour_str = "  "
            elif self.mode == ClockMode.SET_MINUTE and not self.blink_state:
                minute_str = "  "
            elif self.mode == ClockMode.SET_SECOND and not self.blink_state:
                second_str = "  "
                
            time_str = f"{hour_str}:{minute_str}:{second_str}"
            
        time_display.update(time_str)
        
        # Update date
        if self.mode not in [ClockMode.STOPWATCH, ClockMode.TIMER]:
            date_str = self.current_time.strftime("%A, %B %d, %Y")
            date_display.update(date_str)
        else:
            date_display.update("")
            
        # Update mode display
        mode_display.update(f"Mode: {self.mode.value}")
        
        # Update status info
        status_parts = []
        if self.alarm_enabled:
            status_parts.append("ALM")
        if self.stopwatch_running:
            status_parts.append("SW")
        if self.timer_running:
            status_parts.append("TMR")
            
        status_info.update(" | ".join(status_parts))
        
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id
        
        if button_id == "mode-btn":
            self.cycle_mode()
        elif button_id == "set-btn":
            self.handle_set()
        elif button_id == "prev-btn":
            self.handle_prev()
        elif button_id == "next-btn":
            self.handle_next()
        elif button_id == "start-stop-btn":
            self.handle_start_stop()
        elif button_id == "light-btn":
            self.handle_light()
            
    def cycle_mode(self) -> None:
        """Cycle through different clock modes"""
        modes = [ClockMode.TIME, ClockMode.ALARM, ClockMode.STOPWATCH, ClockMode.TIMER]
        try:
            current_index = modes.index(self.mode)
            self.mode = modes[(current_index + 1) % len(modes)]
        except ValueError:
            self.mode = ClockMode.TIME
            
    def handle_set(self) -> None:
        """Enter setting mode or confirm setting"""
        if self.mode == ClockMode.TIME:
            self.mode = ClockMode.SET_HOUR
            self.display_time = self.current_time
        elif self.mode == ClockMode.SET_HOUR:
            self.mode = ClockMode.SET_MINUTE
        elif self.mode == ClockMode.SET_MINUTE:
            self.mode = ClockMode.SET_SECOND
        elif self.mode == ClockMode.SET_SECOND:
            # Apply the set time
            self.current_time = self.display_time
            self.mode = ClockMode.TIME
        elif self.mode == ClockMode.ALARM:
            self.mode = ClockMode.SET_ALARM_HOUR
        elif self.mode == ClockMode.SET_ALARM_HOUR:
            self.mode = ClockMode.SET_ALARM_MINUTE
        elif self.mode == ClockMode.SET_ALARM_MINUTE:
            self.alarm_enabled = True
            self.mode = ClockMode.ALARM
            
    def handle_prev(self) -> None:
        """Decrease current setting value"""
        if self.mode == ClockMode.SET_HOUR:
            self.display_time = self.display_time.replace(
                hour=(self.display_time.hour - 1) % 24
            )
        elif self.mode == ClockMode.SET_MINUTE:
            self.display_time = self.display_time.replace(
                minute=(self.display_time.minute - 1) % 60
            )
        elif self.mode == ClockMode.SET_SECOND:
            self.display_time = self.display_time.replace(
                second=(self.display_time.second - 1) % 60
            )
        elif self.mode == ClockMode.SET_ALARM_HOUR:
            self.alarm_time = self.alarm_time.replace(
                hour=(self.alarm_time.hour - 1) % 24
            )
        elif self.mode == ClockMode.SET_ALARM_MINUTE:
            self.alarm_time = self.alarm_time.replace(
                minute=(self.alarm_time.minute - 1) % 60
            )
        elif self.mode == ClockMode.TIMER:
            # Decrease timer by 1 minute
            current_minutes = int(self.timer_duration.total_seconds() // 60)
            new_minutes = max(1, current_minutes - 1)
            self.timer_duration = timedelta(minutes=new_minutes)
            
    def handle_next(self) -> None:
        """Increase current setting value"""
        if self.mode == ClockMode.SET_HOUR:
            self.display_time = self.display_time.replace(
                hour=(self.display_time.hour + 1) % 24
            )
        elif self.mode == ClockMode.SET_MINUTE:
            self.display_time = self.display_time.replace(
                minute=(self.display_time.minute + 1) % 60
            )
        elif self.mode == ClockMode.SET_SECOND:
            self.display_time = self.display_time.replace(
                second=(self.display_time.second + 1) % 60
            )
        elif self.mode == ClockMode.SET_ALARM_HOUR:
            self.alarm_time = self.alarm_time.replace(
                hour=(self.alarm_time.hour + 1) % 24
            )
        elif self.mode == ClockMode.SET_ALARM_MINUTE:
            self.alarm_time = self.alarm_time.replace(
                minute=(self.alarm_time.minute + 1) % 60
            )
        elif self.mode == ClockMode.TIMER:
            # Increase timer by 1 minute
            current_minutes = int(self.timer_duration.total_seconds() // 60)
            new_minutes = min(99, current_minutes + 1)
            self.timer_duration = timedelta(minutes=new_minutes)
            
    def handle_start_stop(self) -> None:
        """Handle start/stop for stopwatch and timer"""
        if self.mode == ClockMode.STOPWATCH:
            if self.stopwatch_running:
                self.stopwatch_running = False
            else:
                if self.stopwatch_start is None:
                    self.stopwatch_start = datetime.now()
                    self.stopwatch_elapsed = timedelta()
                else:
                    # Resume - adjust start time
                    self.stopwatch_start = datetime.now() - self.stopwatch_elapsed
                self.stopwatch_running = True
                
        elif self.mode == ClockMode.TIMER:
            if self.timer_running:
                self.timer_running = False
            else:
                self.timer_start = datetime.now()
                self.timer_running = True
                
        elif self.mode == ClockMode.ALARM:
            self.alarm_enabled = not self.alarm_enabled
            
    def handle_light(self) -> None:
        """Toggle light/reset functions"""
        if self.mode == ClockMode.STOPWATCH and not self.stopwatch_running:
            # Reset stopwatch
            self.stopwatch_start = None
            self.stopwatch_elapsed = timedelta()
        elif self.mode == ClockMode.TIMER and not self.timer_running:
            # Reset timer to default
            self.timer_duration = timedelta(minutes=5)

def dw_main():
    app = DigitalClock()
    app.run()

if __name__ == "__main__":
    dw_main()
