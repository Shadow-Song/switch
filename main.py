import sys
import json
import subprocess
import sdl2
import sdl2.ext
import sdl2.sdlimage as sdlimage

# 全局设置
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
ICON_SIZE = 128
SPACING = 20

class AppIcon:
    def __init__(self, renderer, name, icon_path, command, x, y):
        self.name = name
        self.command = command
        self.texture = self.load_texture(renderer, icon_path)
        self.x = x
        self.y = y
        self.selected = False

    def load_texture(self, renderer, icon_path):
        image = sdlimage.IMG_Load(icon_path.encode())
        if not image:
            raise ValueError(f"Failed to load image: {icon_path}")
        texture = sdl2.SDL_CreateTextureFromSurface(renderer, image)
        sdl2.SDL_FreeSurface(image)
        return texture

    def draw(self, renderer):
        dst_rect = sdl2.SDL_Rect(self.x, self.y, ICON_SIZE, ICON_SIZE)
        sdl2.SDL_RenderCopy(renderer, self.texture, None, dst_rect)

class Launcher:
    def __init__(self, apps):
        sdl2.ext.init()
        self.window = sdl2.ext.Window("Switch-like Launcher", size=(SCREEN_WIDTH, SCREEN_HEIGHT))
        self.window.show()
        self.renderer = sdl2.SDL_CreateRenderer(self.window.window, -1, 0)

        # 初始化应用图标
        self.apps = []
        for i, app in enumerate(apps):
            x = (i % 3) * (ICON_SIZE + SPACING) + SPACING
            y = (i // 3) * (ICON_SIZE + SPACING) + SPACING
            self.apps.append(AppIcon(self.renderer, app["name"], app["icon"], app["command"], x, y))

        self.selected_index = 0
        self.running = True

    def run(self):
        while self.running:
            self.handle_events()
            self.draw()
            sdl2.SDL_Delay(16)  # 控制帧率，16ms约为60 FPS

        sdl2.ext.quit()

    def handle_events(self):
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                self.running = False
            elif event.type == sdl2.SDL_KEYDOWN:
                if event.key.keysym.sym == sdl2.SDLK_RIGHT:
                    self.selected_index = (self.selected_index + 1) % len(self.apps)
                elif event.key.keysym.sym == sdl2.SDLK_LEFT:
                    self.selected_index = (self.selected_index - 1) % len(self.apps)
                elif event.key.keysym.sym == sdl2.SDLK_RETURN:
                    self.launch_app()

    def draw(self):
        sdl2.SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, 255)
        sdl2.SDL_RenderClear(self.renderer)

        # 绘制应用图标
        for i, app in enumerate(self.apps):
            if i == self.selected_index:
                sdl2.SDL_SetRenderDrawColor(self.renderer, 255, 255, 0, 255)  # 高亮颜色
                border_rect = sdl2.SDL_Rect(app.x - 4, app.y - 4, ICON_SIZE + 8, ICON_SIZE + 8)
                sdl2.SDL_RenderDrawRect(self.renderer, border_rect)
            app.draw(self.renderer)

        sdl2.SDL_RenderPresent(self.renderer)

    def launch_app(self):
        app = self.apps[self.selected_index]
        print(f"Launching {app.name}...")
        subprocess.Popen(app.command.split())  # 启动应用

def load_apps(config_path):
    with open(config_path, "r") as f:
        return json.load(f)

if __name__ == "__main__":
    apps = load_apps("apps.json")
    launcher = Launcher(apps)
    launcher.run()