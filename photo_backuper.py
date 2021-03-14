import requests
from tqdm import tqdm
from colorama import Fore
import json


class Backup:
    def __init__(self, vk_id, ya_token, directory_name):
        self.vk_id = vk_id
        self.ya_token = ya_token
        self.directory_name = directory_name

    @staticmethod
    def get_photo_data(offset=0, count=50):
        with open('token.txt', encoding='utf-8') as f:
            vk_token = f.read().strip()

            response = requests.get('https://api.vk.com/method/photos.getAll',
                                    params={'owner_id': vktoya.vk_id,
                                            'access_token': vk_token,
                                            'offset': offset,
                                            'count': count,
                                            'photo_sizes': 1,
                                            'extended': 1,
                                            'v': '5.130'
                                            })

        return response.json()['response']

    @staticmethod
    def get_photo():
        photo = vktoya.get_photo_data()
        count_photo = vktoya.get_photo_data()['count']
        offset = 0
        count = 50
        photo_dict = {}
        photo_json = []

        print('Получение списка фото...')

        while offset <= count_photo:
            if offset != 0:
                photo = vktoya.get_photo_data(offset=offset, count=count)

            for i in photo['items']:
                link = i['sizes'][-1]['url']
                p_size = i['sizes'][-1]['type']
                photo_name_0 = str(i['likes']['count']) + '.jpg'
                photo_name_1 = str(i['likes']['count']) + '_' + str(i['date']) + '.jpg'
                if photo_name_0 in photo_dict.keys():
                    photo_dict[photo_name_1] = link
                    photo_json.append({'file_name': photo_name_1, 'size': p_size})
                else:
                    photo_dict[photo_name_0] = link
                    photo_json.append({'file_name': photo_name_0, 'size': p_size})

            offset += count

        with open('photos.json', 'w', encoding='utf-8') as f:
            json.dump(photo_json, f)

        print('Получено', Fore.LIGHTBLUE_EX + str(len(photo_dict)), 'фото\n' +
              Fore.LIGHTWHITE_EX + '=======================================\n')

        return photo_dict

    @staticmethod
    def create_directory(d_name=None):
        if d_name is None:
            d_name = vktoya.directory_name
            if d_name == '':
                d_name = 'Backup from vk.com'

        directory_list = []

        requests.put('https://cloud-api.yandex.net/v1/disk/resources',
                     params={'path': d_name},
                     headers={'Authorization': vktoya.ya_token}
                     )

        directory = requests.get('https://cloud-api.yandex.net/v1/disk/resources',
                                 params={'path': '/'},
                                 headers={'Authorization': vktoya.ya_token})

        for dd in directory.json()['_embedded']['items']:
            directory_list.append([dd['created'], dd['path']])

        path = max(directory_list)

        print(Fore.LIGHTWHITE_EX + '\n=======================================\nДиректория',
              Fore.LIGHTBLUE_EX + path[1],
              Fore.LIGHTWHITE_EX + 'успешно создана')

        return path

    @staticmethod
    def upload_photo(photos=None, ya_dir=None):
        if ya_dir is None:
            ya_dir = vktoya.create_directory()
        if photos is None:
            photos = vktoya.get_photo()

        for i in tqdm(photos.items(), desc='Загрузка фото на Я.Диск', ncols=100,
                      bar_format="%s{l_bar}%s{bar}%s{r_bar}" %
                                 (Fore.LIGHTBLUE_EX, Fore.LIGHTWHITE_EX, Fore.LIGHTBLUE_EX)):
            link = i[1]
            photo_name = i[0]

            post = requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload',
                                 params={'path': ya_dir[1] + '/' + photo_name,
                                         'url': link},
                                 headers={'Authorization': vktoya.ya_token}
                                 )

            if post.status_code != 202:
                print('\nОшибка загрузки, код ответа сервера:',
                      Fore.LIGHTRED_EX + post.status_code)
                quit()

        print('\nВсе файлы успешно загружены в директорию:',
              Fore.LIGHTBLUE_EX + ya_dir[1])

        return tqdm


if __name__ == '__main__':
    vktoya = Backup(input('Введите id пользователя VK: '), input('Введите YA token: '),
                    input('Введите имя новой директории: '))
    vktoya.upload_photo()
