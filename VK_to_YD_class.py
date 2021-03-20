import requests
import json
import time
from progress.bar import IncrementalBar

class VK_user:
    def __init__(self, vk_token):
        self.vk_token = vk_token

    def get_pics_make_json(self, vk_url = 'https://api.vk.com/method/', user_id=None, version='5.126'):
        self.vk_url = vk_url
        self.user_id = user_id
        self.version = version
        self.params = {
            'access_token': vk_token,
            'v': version
        }
        self.owner_id = requests.get(self.vk_url + 'users.get', self.params).json()['response'][0]['id']

        if self.user_id is None:
            self.user_id = self.owner_id
        self.all_pics = self.vk_url + 'photos.get'
        self.pics_params = {
            'user_id': self.user_id,
            'album_id': 'profile',
            'extended': 1
            }

        self.res_get = requests.get(self.all_pics, params={**self.params, **self.pics_params})
        self.pic_items = self.res_get.json()['response']['items']

        self.album_id = str(self.pic_items[0]['album_id'])
        self.likes_links = {}
        self.sizes_links_json = []

        for pic in self.pic_items:
            height_width = {}
            self.name_and_size = {}
            big_pic = pic['sizes'][-1]['url']
            for i in big_pic:
                like_num = str(pic['likes']['count'])
                like_num_name = like_num + '.jpg'

                if like_num_name in self.likes_links:
                    like_num_name = like_num_name[:-4] + '.1.jpg'

            self.likes_links[like_num_name] = big_pic

            big_pic_height = pic['sizes'][-1]['height']
            big_pic_width = pic['sizes'][-1]['width']

            height_width.update({'height': big_pic_height, 'width': big_pic_width})
            self.name_and_size.update({'file_name': like_num_name, 'size': height_width})
            self.sizes_links_json.append(self.name_and_size)

        with open('vk_class.json', 'w') as f:
            json.dump(self.sizes_links_json, f)


class YD_user:
    def __init__(self, yadisk_token):
        self.yadisk_token = yadisk_token

    def album_to_YD(self, yadisk_url='https://cloud-api.yandex.net/v1/disk/resources/', album_name='Profile pics'):
        self.yadisk_url = yadisk_url
        self.album_name = album_name
        response = requests.put(yadisk_url,
                                params={'path': self.album_name},
                                headers={'Authorization': f'OAuth {self.yadisk_token}'})
        return response


class VK_to_YD(VK_user, YD_user):
    def __init__(self):
        VK_user.__init__(self, vk_token)
        YD_user.__init__(self, yadisk_token)
        self.get_pics_make_json()
        self.album_to_YD()

    def send_pics(self):
        bar = IncrementalBar('Countdown', max=len(self.likes_links))
        for k in self.likes_links:
            response = requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload',
                                     params={'url': self.likes_links[k],
                                             'path': f'{self.album_name}/{k}'},
                                     headers={'Authorization': f'OAuth {self.yadisk_token}'})
            bar.next()
            time.sleep(1)

        bar.finish()
        return response






with open('VK_token.txt') as file_object:
    vk_token = file_object.read().strip()

with open('YaDisk_token.txt') as file_object:
    yadisk_token = file_object.read().strip()


bulgakov = VK_to_YD()
bulgakov.send_pics()

