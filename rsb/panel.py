import pygame as pg
from pygame.locals import *
from rsb.redisutil import RedisUtil
import json

CMD_TIME = 10  # time that CMD's last
LINEAR_CMD_SCALE = 0.05  # amount that successive 
ANGULAR_CMD_SCALE = 3
CORNER_OFFSET = 15  # distance panel sits on screen from the top left corner
BUTTON_CLR = pg.Color("firebrick")
BACKGRND = pg.Color("grey75")
INFO_BG = pg.Color("darkslategray")
BTN_FNC = {
    "turn left": ("rotate", ANGULAR_CMD_SCALE), 
    "turn right": ("rotate", -ANGULAR_CMD_SCALE), 
    "stop": ("stop", 0),
    "forward": ("move", LINEAR_CMD_SCALE),
    "reverse": ("move", -LINEAR_CMD_SCALE)
    }
STOP = json.dumps({"cmd": "stop"})
ACTION = {"cmd": None, "duration": CMD_TIME, "speed": None}

class Panel(object):
    def __init__(self, ns, enable_debug=False):
        self.ru = RedisUtil(ns, keys={"Odom": "string", "Cmd": "list", "Cmd_Feedback": "list"})
        self.odom_info = None
        self.current_cmd = ACTION
        self.turning = False
        self.driving = False
        self.opened = True
        self.panel_rect = Rect(CORNER_OFFSET, CORNER_OFFSET, 200, 500)
        # panel buttons
        self.buttons = []  # TODO fill
        self.buttons.append(Panel_Button("toggle", CORNER_OFFSET, CORNER_OFFSET, 20, 20))
        self.buttons.append(Panel_Button("stop", 102, 352, 25, 25))
        self.buttons.append(Panel_Button("forward", 90, 290, 50, 50))
        self.buttons.append(Panel_Button("reverse", 90, 390, 50, 50))
        self.buttons.append(Panel_Button("turn left", 40, 340, 50, 50))
        self.buttons.append(Panel_Button("turn right", 140, 340, 50, 50))
        if enable_debug:
            self.buttons.append(Panel_Button("debug", 200, CORNER_OFFSET, CORNER_OFFSET, CORNER_OFFSET))  # an extra button that pritns the state of the panel's redisutil
        # delete later
        self.debug_text = "Hello"
        

    def collapse(self):
        self.panel_rect = Rect(CORNER_OFFSET, CORNER_OFFSET, 20, 20)
        self.opened = False

    def expand(self):
        self.panel_rect = Rect(CORNER_OFFSET, CORNER_OFFSET, 200, 500)
        self.opened = True

    def draw(self, surface):
        self.ru.bulk_update()
        if self.opened:
            pg.draw.rect(surface, BACKGRND, self.panel_rect)
            for b in self.buttons:
                pg.draw.rect(surface, BUTTON_CLR, b.rect)
            f = pg.font.SysFont(None, 18)
            text = f.render(self.debug_text, True, pg.Color("black"))
            surface.blit(text, (CORNER_OFFSET + 10, 300))
            
            pg.draw.rect(surface, INFO_BG, Rect(CORNER_OFFSET + 5, 40, 190, 245))  # Odom Panel
            pg.draw.rect(surface, INFO_BG, Rect(CORNER_OFFSET + 5, 445, 190, 65))  # fedback panel
            # TODO: write odom info
            if self.ru.odom:
                y = 45
                for k in ["odom_id", "location", "orientation", "linearvelocity", "angularvelocity"]:
                    text = f.render("{}: {}".format(k, self.ru.odom[k]), True, pg.Color("whitesmoke"))
                    surface.blit(text, (CORNER_OFFSET + 10, y))
                    y += 25
            if self.ru.cmd_feedback:
                info = self.ru.cmd_feedback["code"]
                text = f.render(info, True, pg.Color("whitesmoke"))
                surface.blit(text, (CORNER_OFFSET + 10, 450))
                info = self.ru.cmd_feedback["message"]
                if len(info) > 25:
                    info = info[:25] + "..."
                text = f.render(info, True, pg.Color("whitesmoke"))
                surface.blit(text, (CORNER_OFFSET + 10, 475))

        else:
            pg.draw.rect(surface, BUTTON_CLR, self.buttons[0].rect)
        

    def send_cmd(self, btn_name):
        self.ru.change_key_value("Cmd", STOP)          # first send a stop to interrupt last command
        if btn_name != "middle":
            cmd = {key: ACTION[key] for key in ACTION}      # copy action dict 
            cmd["cmd"] = BTN_FNC[btn_name][0]          # fill in command
            if cmd["cmd"] == self.current_cmd["cmd"]:  # update speed if same movemnet type
                cmd["speed"] = self.current_cmd["speed"] + BTN_FNC[btn_name][1]
            else:                                      # else set speed
                cmd["speed"] = BTN_FNC[btn_name][1]
            try:
                if cmd["speed"] != 0:
                    self.ru.change_key_value("Cmd", json.dumps(cmd))  # send command and update current 
                    self.current_cmd = cmd
                return True
            except:
                return False
        else:
            self.current_cmd = ACTION
        return True

    def handle_click(self):
        for event in pg.event.get():
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                pos = pg.mouse.get_pos()
                for b in self.buttons:
                    if b.is_pushed(*pos):
                        self.debug_text = b.name + " " + str(self.current_cmd["speed"])
                        if b.name in BTN_FNC.keys():
                            self.send_cmd(b.name)
                        elif b.name == "toggle":
                            if self.opened:
                                self.collapse()
                            else:
                                self.expand()
                        elif b.name == "debug":
                            print(self.ru.__dict__)


class Panel_Button(object):
    def __init__(self, name, x, y, w, h):
        self.name = name
        self.rect = Rect(x, y, w, h)

    def is_pushed(self, x, y):
        return self.rect.collidepoint(x, y)

