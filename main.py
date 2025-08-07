import customtkinter as ctk
import subprocess
import os
import shutil
from tkinter import messagebox, Toplevel, Label
import winreg

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event):
        x, y = self.widget.winfo_pointerxy()
        self.tooltip_window = Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x + 10}+{y + 10}")
        label = Label(
            self.tooltip_window,
            text=self.text,
            background="#333333",
            foreground="#FFFFFF",
            relief="solid",
            borderwidth=1,
            wraplength=300,
            padx=5,
            pady=5,
            font=("Roboto", 10)
        )
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class ModernMenuUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Solar.Win - Open Source")
        self.geometry("1000x600")
        self.minsize(800, 500)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=180, corner_radius=0, fg_color="#1E1E1E")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(2, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Solar.Win", font=ctk.CTkFont(family="Roboto", size=20, weight="bold"), text_color="#FFFFFF")
        self.logo_label.grid(row=0, column=0, padx=10, pady=(10, 10))

        self.nav_buttons = []
        self.general_button = ctk.CTkButton(
            self.sidebar_frame, text="General", command=self.general_button_event,
            corner_radius=8, height=42, fg_color="#2C2C2C", text_color="#00A3FF",
            hover_color="#3A3A3A", anchor="w", font=ctk.CTkFont(family="Roboto", size=15),
            compound="left", border_width=0, border_spacing=8
        )
        self.general_button.grid(row=1, column=0, padx=(8, 5), pady=1, sticky="ew")
        self.nav_buttons.append(self.general_button)

        self.active_indicator = ctk.CTkFrame(self.sidebar_frame, width=3, height=42, fg_color="#00A3FF")
        self.active_indicator.grid(row=1, column=0, padx=(0, 0), pady=1, sticky="w")

        self.main_frame = ctk.CTkFrame(self, corner_radius=8, fg_color="#252526")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.content_label = ctk.CTkLabel(self.main_frame, text="General - Performance Tweaks", font=ctk.CTkFont(family="Roboto", size=22, weight="bold"), text_color="#FFFFFF")
        self.content_label.grid(row=0, column=0, pady=10, sticky="nw", padx=20)

        self.tweaks_frame = ctk.CTkScrollableFrame(self.main_frame, fg_color="transparent")
        self.tweaks_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.tweaks_frame.grid_columnconfigure(0, weight=1)

        self.tweak_vars = []
        tweaks = [
            {"name": "Disable Visual Effects", "tooltip": "Reduces GPU/CPU load by disabling Windows animations and transparency.", "action": self.disable_visual_effects},
            {"name": "High Performance Power Plan", "tooltip": "Sets power plan to High Performance for better CPU/GPU speed (may increase power usage).", "action": self.set_high_performance},
            {"name": "Disable Windows Search Indexing", "tooltip": "Reduces disk/CPU usage for faster performance (not recommended if you rely on search).", "action": self.disable_search_indexing},
            {"name": "Clear Temporary Files", "tooltip": "Deletes temporary files to free up disk space and improve I/O performance.", "action": self.clear_temp_files},
            {"name": "Enable Game Mode", "tooltip": "Optimizes Windows for gaming by prioritizing game performance.", "action": self.enable_game_mode},
            {"name": "Disable Background Apps", "tooltip": "Stops unnecessary apps from running in the background to free up resources. Manual action: Go to Settings > Apps > Apps & features > Background apps, and turn off unnecessary apps.", "action": None},
            {"name": "Disable Startup Programs", "tooltip": "Prevents non-essential programs from launching at boot to speed up startup. Manual action: Open Task Manager (Ctrl+Shift+Esc) > Startup tab, and disable unnecessary programs.", "action": None},
            {"name": "Disable Telemetry", "tooltip": "Reduces background data collection by disabling telemetry services, improving performance and privacy (reversible via Services settings).", "action": self.disable_telemetry},
            {"name": "Debloat Microsoft Edge", "tooltip": "Disables unnecessary features and telemetry in Microsoft Edge for better performance and privacy (reversible via Edge settings or registry).", "action": self.debloat_edge},
            {"name": "Debloat Google Chrome", "tooltip": "Disables telemetry and unnecessary features in Google Chrome for improved performance and privacy (reversible via Chrome settings).", "action": self.debloat_chrome},
            {"name": "Disable Location Tracking", "tooltip": "Disables Windows location services to improve privacy and reduce resource usage (reversible via Settings or Services).", "action": self.disable_location_tracking},
            {"name": "Disable Explorer Automatic Folder Discovery", "tooltip": "Disables File Explorer’s automatic folder type detection to reduce CPU/disk usage (reversible via registry or Explorer settings).", "action": self.disable_explorer_folder_discovery},
            {"name": "Set Unneeded Services to Manual", "tooltip": "Sets certain non-essential Windows services to Manual startup to save resources.", "action": self.set_unneeded_services_manual}
        ]

        self.tweaks_list = tweaks

        for i, tweak in enumerate(tweaks):
            var = ctk.BooleanVar(value=False)
            self.tweak_vars.append(var)
            checkbox = ctk.CTkCheckBox(self.tweaks_frame, text=tweak["name"], variable=var, font=ctk.CTkFont(family="Roboto", size=14), hover_color="#3A3A3A", checkmark_color="#00A3FF")
            checkbox.grid(row=i, column=0, padx=10, pady=5, sticky="w")
            Tooltip(checkbox, tweak["tooltip"])

        self.apply_button = ctk.CTkButton(self.main_frame, text="Apply Tweaks", command=self.apply_tweaks, corner_radius=8, height=36, fg_color="#00A3FF", hover_color="#007ACC", font=ctk.CTkFont(family="Roboto", size=14))
        self.apply_button.grid(row=2, column=0, pady=10, padx=20, sticky="ew")

        self.status_label = ctk.CTkLabel(self.main_frame, text="", font=ctk.CTkFont(family="Roboto", size=12), text_color="#FFFFFF")
        self.status_label.grid(row=3, column=0, pady=5, padx=20)

        self.theme_switch = ctk.CTkSwitch(
            self.sidebar_frame, text="Dark Mode", command=self.toggle_theme, onvalue="dark", offvalue="light",
            font=ctk.CTkFont(family="Roboto", size=12), width=80, height=24, corner_radius=12,
            fg_color="#3A3A3A", progress_color="#00A3FF", button_color="#FFFFFF",
            button_hover_color="#E0E0E0", switch_width=36, switch_height=18
        )
        self.theme_switch.grid(row=9, column=0, padx=10, pady=(8, 10))
        self.theme_switch.select()

    def toggle_theme(self):
        mode = self.theme_switch.get()
        ctk.set_appearance_mode(mode)
        sidebar_color = "#F0F0F0" if mode == "light" else "#1E1E1E"
        main_color = "#FFFFFF" if mode == "light" else "#252526"
        text_color = "#000000" if mode == "light" else "#FFFFFF"
        self.sidebar_frame.configure(fg_color=sidebar_color)
        self.main_frame.configure(fg_color=main_color)
        self.logo_label.configure(text_color=text_color)
        self.content_label.configure(text_color=text_color)
        self.status_label.configure(text_color=text_color)

    def general_button_event(self):
        self.content_label.configure(text="General - Performance Tweaks")

    def apply_tweaks(self):
        applied = []
        manual = []
        for i, var in enumerate(self.tweak_vars):
            if var.get():
                tweak = self.tweaks_list[i]
                if tweak["action"]:
                    try:
                        tweak["action"]()
                        applied.append(tweak["name"])
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to apply {tweak['name']}: {str(e)}")
                else:
                    manual.append(tweak["tooltip"])

        text = ""
        if applied:
            text += "Applied: " + ", ".join(applied) + "\n"
        if manual:
            text += "Manual actions required:\n" + "\n".join(manual)
        if not text:
            text = "No tweaks selected."
        self.status_label.configure(text=text)

    def disable_visual_effects(self):
        subprocess.run('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f', shell=True)

    def set_high_performance(self):
        subprocess.run('powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c', shell=True)

    def disable_search_indexing(self):
        subprocess.run('sc config WSearch start= disabled', shell=True)
        subprocess.run('net stop WSearch', shell=True)

    def clear_temp_files(self):
        temp_path = os.environ.get("TEMP")
        for item in os.listdir(temp_path):
            item_path = os.path.join(temp_path, item)
            try:
                if os.path.isfile(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path, ignore_errors=True)
            except:
                pass

    def enable_game_mode(self):
        subprocess.run('reg add "HKCU\\Software\\Microsoft\\GameBar" /v AllowAutoGameMode /t REG_DWORD /d 1 /f', shell=True)

    def disable_telemetry(self):
        subprocess.run('sc config DiagTrack start= disabled', shell=True)
        subprocess.run('net stop DiagTrack', shell=True)
        subprocess.run('sc config dmwappushservice start= disabled', shell=True)
        subprocess.run('net stop dmwappushservice', shell=True)
        subprocess.run('reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f', shell=True)

    def debloat_edge(self):
        commands = [
            'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Edge" /v DiagnosticData /t REG_DWORD /d 0 /f',
            'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Edge" /v HideFirstRunExperience /t REG_DWORD /d 1 /f',
            'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Edge" /v HubsSidebarEnabled /t REG_DWORD /d 0 /f',
            'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Edge" /v ShowMicrosoftRewards /t REG_DWORD /d 0 /f',
            'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Edge" /v EdgeShoppingAssistantEnabled /t REG_DWORD /d 0 /f'
        ]
        for cmd in commands:
            subprocess.run(cmd, shell=True)

    def debloat_chrome(self):
        try:
            winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Policies\\Google\\Chrome")
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\\Policies\\Google\\Chrome", 0, winreg.KEY_SET_VALUE) as key:
                winreg.SetValueEx(key, "MetricsReportingEnabled", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "ChromeCleanupEnabled", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "ExtensionInstallBlocklist", 0, winreg.REG_SZ, "*")
                winreg.SetValueEx(key, "PersonalizedSearchSuggestions", 0, winreg.REG_DWORD, 0)
        except Exception as e:
            raise Exception(f"Failed to apply Chrome policies: {str(e)}")

    def disable_location_tracking(self):
        subprocess.run('sc config lfsvc start= disabled', shell=True)
        subprocess.run('net stop lfsvc', shell=True)
        commands = [
            'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\LocationAndSensors" /v DisableLocation /t REG_DWORD /d 1 /f',
            'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\LocationAndSensors" /v DisableSensors /t REG_DWORD /d 1 /f'
        ]
        for cmd in commands:
            subprocess.run(cmd, shell=True)

    def disable_explorer_folder_discovery(self):
        commands = [
            'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v AutoCheckSelect /t REG_DWORD /d 0 /f',
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer" /v NoAutodetectFolderType /t REG_DWORD /d 1 /f'
        ]
        for cmd in commands:
            subprocess.run(cmd, shell=True)

    def set_unneeded_services_manual(self):
        services = [
            "XblGameSave", "XblAuthManager", "XboxNetApiSvc", "WMPNetworkSvc", "DiagTrack",
            "RetailDemo", "WerSvc", "RemoteRegistry", "Fax", "diagnosticshub.standardcollector.service", "PcaSvc"
        ]
        for svc in services:
            subprocess.run(f'sc config "{svc}" start= demand', shell=True)

if __name__ == "__main__":
    app = ModernMenuUI()
    app.mainloop()
