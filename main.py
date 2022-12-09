import PySimpleGUI as sg
from PIL import ImageGrab, ImageTk, Image
import cv2
import numpy as np
import copy
import webbrowser
import json


class Thunter():
    def __init__(self):
        self.tmap_image = cv2.imread('lib/Felucca')
        self.tmap_image2 = cv2.imread('lib/t-map')

        try:
            with open('lib/config.json', 'r') as json_file:
                self.variaveis = json.load(json_file)
        except:
            self.variaveis = [
                        {'window_x': 350, 'window_y': 50, 'keep_top': False}, 
                        {'window_x': 30, 'window_y': 58, 'keep_top': True}, 
                        {'window_x': 400, 'window_y': 50, 'keep_top': True}, 
                        {'window_x': 400, 'window_y': 50, 'keep_top': True}
                        ]

    def make_win1(self):
        layout = [
                [sg.Push(), sg.Text('Localizador de Mapas'), sg.Push()],
                [sg.Push(), sg.Image(filename='', size=(140, 140), key ='image'), sg.Push()],
                [sg.Push(), sg.Text('Coordenadas'), sg.InputText('0', size=(5, 1), key='cord_x'), sg.Text('X'), sg.InputText('0', size=(5, 1), key='cord_y'), sg.Button('Go', size=(5, 1), enable_events=True, key='go_url'), sg.Push()],
                [sg.Push(), sg.Button('Local do Mapa', size=(15, 1), key = 'selecionar'), sg.Button('Resultado', key='result', size=(15, 1)), sg.Push()], 
                [sg.Push(), sg.Button('Sair', size=(15, 1), enable_events=True, key= 'Exit'), sg.Push()],
                [sg.Checkbox('Sempre no Topo', enable_events= True, key='anywhere')]
                ]
                #sg.Button('Recortar', key = 'cut_map', size=(15, 1))
        return sg.Window('T-Hunter Assist', layout, no_titlebar=False, keep_on_top = self.variaveis[0]['keep_top'], grab_anywhere = True, location=(self.variaveis[0]['window_x'], self.variaveis[0]['window_y']), finalize=True)

    def make_win2(self):
        layout = [
                []
                ]
        return sg.Window('Area de corte', layout, transparent_color=None, keep_on_top = self.variaveis[1]['keep_top'], location=(self.variaveis[1]['window_x'], self.variaveis[1]['window_y']), no_titlebar=True, alpha_channel=.5, 
                        grab_anywhere = True, finalize=True, size=(140, 140))

    def make_win3(self):
        layout = [
                [sg.Push(), sg.Image(filename='', key ='image1'), sg.Push()],
                [sg.Button('Esconder/Mostrar', key = 'hide_unhide'),sg.Button('Proximo Resultado', key = 'next_result'), sg.Button('Fechar Resultado', key='close_result')]
            ]
        return sg.Window('T-Hunter Assist',  layout, no_titlebar=True, keep_on_top = self.variaveis[2]['keep_top'], grab_anywhere = True, finalize=True, location=(self.variaveis[2]['window_x'], self.variaveis[2]['window_y']))

    def screenshot(self):
        global img, window2, window1
        window2.refresh()
        lx, ly = self.variaveis[1]['window_x'], self.variaveis[1]['window_y']
        x, y = window2.size
        coord = ((lx, ly,(x+lx), (y+ly)))
        window2.Hide()
        img = ImageGrab.grab(coord, all_screens=True).convert('RGB')
        image = ImageTk.PhotoImage(image=img)
        return img


    def verifica_resultado(self):
        global img
        try:
            source = img
            source2 = np.array(source)
            source2 = source2[:, :, ::-1]
            tmap = copy.copy(self.tmap_image)
            tmap2 = copy.copy(self.tmap_image2)
            img_search = source2
            result = []
            image_output = []
            metod = cv2.TM_CCOEFF_NORMED
            result.append(cv2.matchTemplate(tmap, img_search, method=metod))
            for a in result:
                (*_, maxLoc) = cv2.minMaxLoc(a)
                (startX, startY) = maxLoc
                endX = startX + img_search.shape[1]
                endY = startY + img_search.shape[0]
                window1['cord_x'].update('{0}'.format(int((startX + endX)/2)))
                window1['cord_y'].update('{0}'.format(int((startY + endY)/2)))
                window3.UnHide()
                image = tmap2[startY - 110 :endY + 110, startX - 250 :endX - 50]
                image_output.append(image)
                if len(image) == 0:
                    image_output.append(img_search)
            b,g,r = cv2.split(image_output[0])
            image_output2 = cv2.merge((r,g,b))
            im = Image.fromarray(image_output2)
            image = ImageTk.PhotoImage(image=im)
            window3['image1'].update(data=image)
            window1['image'].update(data=image)
        except:
            sg.PopupError('ERRO 404', 'Mapa não encontrado')

    def open_url(self, cordx, cordy):
        url = 'https://exploreoutlands.com/#pos:{0},{1},12.31'.format(int(cordx), int(cordy))
        webbrowser.open(url, new=2)

    def save_json(self, var_to_save):
        json_to_save = var_to_save
        try:
            with open('lib/config.json', 'w', encoding='utf-8') as json_config:
                json.dump(json_to_save, json_config)
        except:
            sg.PopupError('ERRO', 'Não foi possível salvar o arquivo de configuração')

    def save_window_localition(self):
        self.variaveis[0]['window_x'], self.variaveis[0]['window_y'] = window1.CurrentLocation()
        self.variaveis[1]['window_x'], self.variaveis[1]['window_y'] = window2.CurrentLocation()
        self.variaveis[2]['window_x'], self.variaveis[2]['window_y'] = window3.CurrentLocation()
        return self.variaveis


    def selecionar(self):
        global window2
        if window2._Hidden:
            window2.UnHide()
        elif not window2._Hidden:
            window2.Hide()
    
    def anywhere(self):
        global window1
        if window1.TKroot.wm_attributes("-topmost") == 1:
            window1.TKroot.wm_attributes("-topmost", 0)
            window1.TKroot.overrideredirect(False)
            window1['anywhere'].update(False)
        elif window1.TKroot.wm_attributes("-topmost") == 0:
            window1.TKroot.wm_attributes("-topmost", 1)
            window1.TKroot.overrideredirect(True)
            window1['anywhere'].update(True)

    def hide_unhide(self):
        global window1
        if window1._Hidden:
            window1.UnHide()
        elif not window1._Hidden:
            window1.Hide()
    
    def go_url(self):
        self.open_url(values['cord_x'], values['cord_y'])


    def cut_map(self):
        self.save_json(self.save_window_localition())
        self.screenshot()

    def close_result(self):
        global window1, window3
        window1.UnHide()
        window3.Hide()

    def result(self):
        self.cut_map()
        self.verifica_resultado()

    def next_result(self):
        self.cut_map()
        self.verifica_resultado()


if __name__ == '__main__':
    programa = Thunter()
    window1, window2, window3 = programa.make_win1(), programa.make_win2(), programa.make_win3()
    window1.bind('<Double-Button-1>', 'anywhere')
    window2.Hide()
    window3.Hide()


    while True:
        window, event, values = sg.read_all_windows()
        try:
            funcao = getattr(programa, event)
            funcao()
        except:
            if event == sg.WIN_CLOSED or event == 'Exit':
                programa.save_json(programa.save_window_localition())
                window.close()
                if window == window1:
                    break
                elif window == window2:
                    break
                elif window == window3:
                    break

    window.close()