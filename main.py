import requests
import json
import time
from progress.bar import IncrementalBar
from my_vk_token import MY_VK_TOKEN
from my_token_yandex_disk import MY_TOKEN_YANDEX_DISK
HTTP_STATUS_GET = 200
HTTP_STATUS_CREATE = 201
HTTP_STATUS_UPLOAD = 202
COUNT_NEED_PHOTOS_BIG_SIZE = 5

class UserVk():

    def __init__(self, access_token):
        self.token = access_token
        self.params = {'access_token': self.token,'v': '5.131'}

    def get_photo(self, id_vk):
        URL = 'https://api.vk.com/method/photos.getAll'
        params = {
            'owner_id': id_vk,
            'access_token': self.token,
            'extended': '1',
            'offset': '0',
            'count': '100',
            'photo_sizes': '1',
            'v': '5.131'
        }
        res = requests.get(URL, params=params)
        if res.status_code == HTTP_STATUS_GET: # Everything is great
            data = json.loads(res.text)
            return data
        else: 
            return res.status_code

    
    def parsed_photo(self, json_photo):
        data_foto = json_photo['response']['items']

        # size of photo VK API ('type')
        list_app_vk_size_photos = ['w', 'z', 'y', 'r', 'q', 'p', 'o', 'x', 'm', 's']

        # Empty dict for every 'type'
        dict_foto = {}
        for size in list_app_vk_size_photos:
            dict_foto[size] = []

        # Empty dict for name_file ( key - 'url' , value - name_file )
        name_file = {}

        for element in data_foto:
            sizes_foto = element['sizes']
            for every_foto in sizes_foto:
                dict_foto[every_foto['type']].append(every_foto['url'])
                name_file[every_foto['url']] = 'likes'+str(element['likes']['count'])+'_'+str(element['date'])

        # list_finish_photos - file big size needed us
        list_finish_photos = []
        flag_enough = False
        for sizes_foto in list_app_vk_size_photos:
            if not flag_enough:
                count_list_finish = len(list_finish_photos)
                if count_list_finish < COUNT_NEED_PHOTOS_BIG_SIZE:
                    list_photos = dict_foto[sizes_foto]
                    if len(list_photos) >= COUNT_NEED_PHOTOS_BIG_SIZE:
                        for element in range(0, COUNT_NEED_PHOTOS_BIG_SIZE):
                            list_finish_photos.append(list_photos[element])
                        flag_enough = True
                    else:
                        add_foto = COUNT_NEED_PHOTOS_BIG_SIZE - count_list_finish
                        for element in range(0, add_foto):
                                list_finish_photos.append(list_photos[element])
 
        parsed_photo = {}
        for url_file in list_finish_photos:
            parsed_photo[url_file] = name_file[url_file]
        return parsed_photo


class UserYandex():

    def __init__(self, token):
        self.token = token

    def create_folder(self, path):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = {'Content-Type': 'application/json' , 'Accept': 'application/json','Authorization': f'OAuth {self.token}'}
        response = requests.put(f'{url}?path={path}',headers=headers)
        if response.status_code == HTTP_STATUS_CREATE:
                    print("Папка",path,"успешно создана на Яндекс-Диск ")

    def upload_file(self, parsed_photo, name_folder):
        url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = {'Content-Type': 'application/json' , 'Accept': 'application/json','Authorization': f'OAuth {self.token}'}
        bar = IncrementalBar('Загрузка файлов...', max = len(parsed_photo))
        file_status_upload = {}
        for file_upload in parsed_photo:
            bar.next()
            time.sleep(1)
            path = f'/{name_folder}/{parsed_photo[file_upload]}'
            params = {'path': path ,'url': file_upload}
            response = requests.post(f'{url}', params=params, headers=headers )
            file_status_upload[parsed_photo[file_upload]] = response.status_code
        bar.finish()
        print()
        for element in file_status_upload:
            if file_status_upload[element] == HTTP_STATUS_UPLOAD:
                print("Файл", element, "успешно загружен в папку ", name_folder, "на Яндекс-Диск ")
            else:
                print("Проблемка.Файл", element, " не загружен в папку ", name_folder, "на Яндекс-Диск ")
            

def main():
    id_vk = input("Введите id пользователя VK: ")
    user_vk = UserVk(MY_VK_TOKEN)
    name_directory = input("Введите название папки: ")
    json_photo = user_vk.get_photo(id_vk)
    if str(type(json_photo)) == "<class 'dict'>": # Everything is great
        parsed_photo = user_vk.parsed_photo(json_photo)
        user_yandex = UserYandex(MY_TOKEN_YANDEX_DISK)
        user_yandex.create_folder(name_directory) 
        user_yandex.upload_file(parsed_photo, name_directory)
    else:
        print("Приносим свои извинения .Файлы не загружены в папку . Возможные причины:  некорретный токен,ошибки сервера,проблемы с сетью ... Ну или сегодня просто не Ваш день. Выпейте скорее горячий кофе с ванильной булочкой и завтра все будет ОК.", name_folder, "на Яндекс-Диск")



if __name__ == '__main__':
    main()


