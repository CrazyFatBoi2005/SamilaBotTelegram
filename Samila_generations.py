# Библиотека Samila для генерации картинок (сторонний API)
import matplotlib.pyplot as plt
from samila import GenerativeImage
import random
import time
from samila import Projection

# Возможные цвета
colors = ['yellow', 'purple', 'blue', 'red']
# цвет фона
# upd. картинки получаются лучше на черном фоне, поэтому принято решение оставить только его
backs = ['black']
# Проекции картинки - ращнообразие форм генерации
projs = [Projection.POLAR,
         Projection.AITOFF,
         Projection.HAMMER,
         Projection.MOLLWEIDE,
         Projection.LAMBERT]

# открываем файл, в котором записано абсолютное колличество сохраненных генераций
with open('count_pictures.txt', mode='r') as f:
    count = int(f.readlines(1)[0])

# мой chat_id
admin = '394323698'


# проекции
def return_proj(base):
    base = projs
    result = []
    for i in range(0, len(base), 2):
        if i != len(base) - 1:
            result.append([base[i].name, base[i + 1].name])
        else:
            result.append([base[i].name])
    return result


# Генерация картинок Samila
def generate(color, proj, n):
    # обновляем наш абсолютный счетчик
    global count
    for i in range(n):
        count += 1
        with open('count_pictures.txt', mode='w') as f:
            f.write(str(count))

        # выбор фона наугад
        back = random.choice(backs)
        # пкласс проекции по ее имени
        proj_r = None
        for p in projs:
            if proj == p.name:
                proj_r = p
        #  будущее расположение и название файла с картинкой
        file = f'pics/{color}_{back}_{count}.png'
        # генерация
        g = GenerativeImage()
        g.generate()
        g.plot(color=color, bgcolor=back, projection=proj_r)
        # семечко
        seed = g.seed
        # сохраняем
        g.save_image(file)
        # возвращаем расположение файла и семечко
        return file, seed
