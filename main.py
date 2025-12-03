from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.graphics import Color, Ellipse, Rectangle, Line
from kivy.clock import Clock
from kivy.properties import BooleanProperty
from kivy.logger import Logger
import os

# --- إعدادات اللغة والنصوص ---
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False
    Logger.warning("LANG: Arabic libraries (arabic_reshaper, python-bidi) not found.")

FONT_NAME = 'Arial'
if os.path.exists('Arial.ttf'):
    LabelBase.register(name=FONT_NAME, fn_regular='Arial.ttf')
else:
    Logger.warning("FONT: Arial.ttf not found. Using default font.")
    FONT_NAME = 'Roboto'

# قاموس الترجمة
TRANSLATIONS = {
    'title': {'en': 'SALEMFLASH', 'ar': 'سالم فلاش'},
    'tap_on': {'en': 'Tap to Turn On', 'ar': 'اضغط للتشغيل'},
    'tap_off': {'en': 'Tap to Turn Off', 'ar': 'اضغط للإيقاف'},
    'screen_on': {'en': 'Screen Light On', 'ar': 'ضوء الشاشة يعمل'},
    'flash_on': {'en': 'Flashlight On', 'ar': 'الفلاش يعمل'},
    'led_mode': {'en': 'LED Flash', 'ar': 'فلاش LED'},
    'screen_mode': {'en': 'White Screen', 'ar': 'شاشة بيضاء'},
    'switch_lang': {'en': 'عربي', 'ar': 'English'},
    'error_perm': {'en': 'Check Camera Permission', 'ar': 'تأكد من صلاحيات الكاميرا'},
    'simulation': {'en': 'Simulation Mode', 'ar': 'وضع المحاكاة'},
    'try_screen': {'en': 'Try White Screen Mode', 'ar': 'جرب وضع الشاشة البيضاء'}
}

def txt(key, lang='en'):
    text = TRANSLATIONS.get(key, {}).get(lang, key)
    if lang == 'ar' and ARABIC_SUPPORT:
        reshaped_text = arabic_reshaper.reshape(text)
        return get_display(reshaped_text)
    return text

# --- التحقق من الأندرويد ---
ANDROID_AVAILABLE = False
try:
    from jnius import autoclass
    ANDROID_AVAILABLE = True
except ImportError:
    ANDROID_AVAILABLE = False

class FlashlightController:
    def __init__(self):
        self.is_on = False
        self.camera_manager = None
        self.camera_id = None
        self.initialized = False
    
    def initialize_camera(self):
        if not ANDROID_AVAILABLE or self.initialized:
            return self.camera_id is not None
        
        try:
            Context = autoclass('android.content.Context')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            CameraCharacteristics = autoclass('android.hardware.camera2.CameraCharacteristics')
            
            self.camera_manager = PythonActivity.mActivity.getSystemService(Context.CAMERA_SERVICE)
            camera_ids = self.camera_manager.getCameraIdList()
            
            for cam_id in camera_ids:
                characteristics = self.camera_manager.getCameraCharacteristics(cam_id)
                has_flash = characteristics.get(CameraCharacteristics.FLASH_INFO_AVAILABLE)
                if has_flash:
                    self.camera_id = cam_id
                    break
            
            if not self.camera_id and camera_ids:
                self.camera_id = camera_ids[0]
            
            self.initialized = True
            return self.camera_id is not None
        except Exception as e:
            Logger.error(f"FLASHLIGHT: Camera init error: {e}")
            return False
    
    def toggle(self):
        if not ANDROID_AVAILABLE:
            return None
        
        if not self.initialized:
            if not self.initialize_camera():
                return None
        
        if self.camera_manager and self.camera_id:
            try:
                self.is_on = not self.is_on
                self.camera_manager.setTorchMode(self.camera_id, self.is_on)
                return self.is_on
            except Exception as e:
                Logger.error(f"FLASHLIGHT: Torch error: {e}")
                self.is_on = False
                return None
        return None
    
    def turn_off(self):
        if not ANDROID_AVAILABLE:
            return
        if self.camera_manager and self.camera_id and self.is_on:
            try:
                self.camera_manager.setTorchMode(self.camera_id, False)
                self.is_on = False
            except Exception:
                pass

class PowerButton(Widget):
    is_on = BooleanProperty(False)
    
    def __init__(self, callback=None, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.size_hint = (None, None)
        self.size = (200, 200)
        self.bind(pos=self.update_canvas, size=self.update_canvas, is_on=self.update_canvas)
        Clock.schedule_once(self.update_canvas, 0)
    
    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            if self.is_on:
                Color(1, 0.85, 0, 0.3)
                outer_size = 220
                Ellipse(pos=(self.center_x - outer_size/2, self.center_y - outer_size/2), size=(outer_size, outer_size))
                Color(1, 0.85, 0, 1)
            else:
                Color(0.3, 0.3, 0.3, 1)
            Ellipse(pos=(self.center_x - 100, self.center_y - 100), size=(200, 200))
            if self.is_on:
                Color(0.2, 0.2, 0.2, 1)
            else:
                Color(0.5, 0.5, 0.5, 1)
            Ellipse(pos=(self.center_x - 80, self.center_y - 80), size=(160, 160))
            if self.is_on:
                Color(1, 0.9, 0.4, 1)
            else:
                Color(0.6, 0.6, 0.6, 1)
            Line(circle=(self.center_x, self.center_y - 5, 25, 45, 315), width=4)
            Line(points=[self.center_x, self.center_y + 25, self.center_x, self.center_y + 5], width=4)
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            return True
        return super().on_touch_down(touch)
    
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if self.callback:
                self.callback()
            return True
        return super().on_touch_up(touch)

class FlashlightApp(FloatLayout):
    flashlight_on = BooleanProperty(False)
    screen_mode = BooleanProperty(False)
    current_lang = 'en'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.flashlight_controller = FlashlightController()
        self.bind(pos=self.update_background, size=self.update_background)
        Clock.schedule_once(self.update_background, 0)
        
        self.power_button = PowerButton(callback=self.toggle_flashlight)
        self.power_button.pos_hint = {'center_x': 0.5, 'center_y': 0.55}
        self.add_widget(self.power_button)
        
        self.lang_btn = Button(
            text=txt('switch_lang', self.current_lang),
            font_name=FONT_NAME,
            font_size='16sp',
            size_hint=(None, None),
            size=(100, 50),
            pos_hint={'right': 0.95, 'top': 0.95},
            background_color=(0, 0, 0, 0.5)
        )
        self.lang_btn.bind(on_press=self.switch_language)
        self.add_widget(self.lang_btn)

        self.title_label = Label(
            text=txt('title', self.current_lang),
            font_name=FONT_NAME,
            font_size='28sp',
            color=(1, 1, 1, 1),
            pos_hint={'center_x': 0.5, 'top': 0.90},
            size_hint=(None, None),
            size=(300, 50),
            bold=True
        )
        self.add_widget(self.title_label)
        
        self.status_label = Label(
            text=txt('tap_on', self.current_lang),
            font_name=FONT_NAME,
            font_size='22sp',
            color=(0.7, 0.7, 0.7, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.35},
            size_hint=(None, None),
            size=(300, 50)
        )
        self.add_widget(self.status_label)
        
        mode_layout = BoxLayout(
            orientation='horizontal',
            size_hint=(0.9, None),
            height=50,
            pos_hint={'center_x': 0.5, 'center_y': 0.15},
            spacing=20
        )
        
        self.flash_btn = Button(
            text=txt('led_mode', self.current_lang),
            font_name=FONT_NAME,
            font_size='16sp',
            background_color=(0.3, 0.3, 0.3, 1),
            background_normal='',
            color=(1, 1, 1, 1)
        )
        self.flash_btn.bind(on_press=self.set_flash_mode)
        
        self.screen_btn = Button(
            text=txt('screen_mode', self.current_lang),
            font_name=FONT_NAME,
            font_size='16sp',
            background_color=(0.2, 0.2, 0.2, 1),
            background_normal='',
            color=(0.7, 0.7, 0.7, 1)
        )
        self.screen_btn.bind(on_press=self.set_screen_mode)
        
        mode_layout.add_widget(self.flash_btn)
        mode_layout.add_widget(self.screen_btn)
        self.add_widget(mode_layout)

    def switch_language(self, instance):
        self.current_lang = 'ar' if self.current_lang == 'en' else 'en'
        self.update_ui_texts()

    def update_ui_texts(self):
        self.lang_btn.text = txt('switch_lang', self.current_lang)
        self.title_label.text = txt('title', self.current_lang)
        self.flash_btn.text = txt('led_mode', self.current_lang)
        self.screen_btn.text = txt('screen_mode', self.current_lang)
        status_key = 'tap_on'
        if self.flashlight_on:
            if self.screen_mode:
                status_key = 'screen_on'
            elif ANDROID_AVAILABLE:
                status_key = 'flash_on'
            else:
                status_key = 'simulation'
        self.status_label.text = txt(status_key, self.current_lang)

    def update_background(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.flashlight_on and self.screen_mode:
                Color(1, 1, 1, 1)
            else:
                Color(0.2, 0.2, 0.4, 1)
            Rectangle(pos=self.pos, size=self.size)
    
    def toggle_flashlight(self):
        if self.screen_mode:
            self.flashlight_on = not self.flashlight_on
            self.power_button.is_on = self.flashlight_on
            if self.flashlight_on:
                Window.clearcolor = (1, 1, 1, 1)
                self.status_label.text = txt('screen_on', self.current_lang)
                self.status_label.color = (0.2, 0.2, 0.2, 1)
            else:
                Window.clearcolor = (0.2, 0.2, 0.4, 1)
                self.status_label.text = txt('tap_on', self.current_lang)
                self.status_label.color = (0.7, 0.7, 0.7, 1)
        else:
            if ANDROID_AVAILABLE:
                if not self.flashlight_controller.initialized:
                    if not self.flashlight_controller.initialize_camera():
                        self.status_label.text = txt('try_screen', self.current_lang)
                        self.status_label.color = (1, 0.5, 0.5, 1)
                        return
                result = self.flashlight_controller.toggle()
                if result is not None:
                    self.flashlight_on = result
                    self.power_button.is_on = result
                    if result:
                        self.status_label.text = txt('flash_on', self.current_lang)
                        self.status_label.color = (1, 0.85, 0, 1)
                    else:
                        self.status_label.text = txt('tap_on', self.current_lang)
                        self.status_label.color = (0.7, 0.7, 0.7, 1)
                else:
                    self.status_label.text = txt('error_perm', self.current_lang)
                    self.status_label.color = (1, 0.5, 0.5, 1)
            else:
                self.flashlight_on = not self.flashlight_on
                self.power_button.is_on = self.flashlight_on
                if self.flashlight_on:
                    self.status_label.text = txt('simulation', self.current_lang)
                    self.status_label.color = (1, 0.85, 0, 1)
                else:
                    self.status_label.text = txt('tap_on', self.current_lang)
                    self.status_label.color = (0.7, 0.7, 0.7, 1)
        self.update_background()
    
    def set_flash_mode(self, instance):
        if self.flashlight_on:
            self.flashlight_controller.turn_off()
            if self.screen_mode:
                Window.clearcolor = (0.2, 0.2, 0.4, 1)
            self.flashlight_on = False
            self.power_button.is_on = False
            self.status_label.text = txt('tap_on', self.current_lang)
            self.status_label.color = (0.7, 0.7, 0.7, 1)
        self.screen_mode = False
        self.flash_btn.background_color = (0.3, 0.3, 0.3, 1)
        self.flash_btn.color = (1, 1, 1, 1)
        self.screen_btn.background_color = (0.2, 0.2, 0.2, 1)
        self.screen_btn.color = (0.7, 0.7, 0.7, 1)
        Window.clearcolor = (0.2, 0.2, 0.4, 1)
        self.update_background()
    
    def set_screen_mode(self, instance):
        if self.flashlight_on and not self.screen_mode:
            self.flashlight_controller.turn_off()
            self.flashlight_on = False
            self.power_button.is_on = False
        self.screen_mode = True
        self.screen_btn.background_color = (0.3, 0.3, 0.3, 1)
        self.screen_btn.color = (1, 1, 1, 1)
        self.flash_btn.background_color = (0.2, 0.2, 0.2, 1)
        self.flash_btn.color = (0.7, 0.7, 0.7, 1)
        self.status_label.text = txt('tap_on', self.current_lang)
        self.status_label.color = (0.7, 0.7, 0.7, 1)
        self.update_background()

class FlashlightMainApp(App):
    def build(self):
        self.title = 'SALEMFLASH'
        if os.path.exists('flashlight-app-icon-14.jpg'):
            self.icon = 'flashlight-app-icon-14.jpg'
        Window.clearcolor = (0.2, 0.2, 0.4, 1)
        return FlashlightApp()
    
    def on_stop(self):
        if hasattr(self.root, 'flashlight_controller'):
            self.root.flashlight_controller.turn_off()

if __name__ == '__main__':
    FlashlightMainApp().run()
              
