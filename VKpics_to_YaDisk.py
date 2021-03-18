import requests
import json
import time
from tqdm import tqdm

with open('VK_token.txt') as file_object:
    vk_token = file_object.read().strip()

with open('YaDisk_token.txt') as file_object:
    yadisk_token = file_object.read().strip()

vk_url = 'https://api.vk.com/method/'
ya_url = 'https://cloud-api.yandex.net/v1/disk/resources/'


def put_pics(v_token, version, ya_token, user_id=None):
    params = {
            'access_token': v_token,
            'v': version
             }
    owner_id = requests.get(vk_url + 'users.get', params).json()['response'][0]['id']

    if user_id is None:
        user_id = owner_id
    all_pics = vk_url + 'photos.get'
    pics_params = {
            'user_id': user_id,
            'album_id': 'profile',
            'extended': 1
        }

    res_get = requests.get(all_pics, params={**params, **pics_params})

    pic_items = res_get.json()['response']['items']
    album_id = str(pic_items[0]['album_id'])

    likes_links = {}
    sizes_links_json = []

    for pic in pic_items:
        height_width = {}
        name_and_size = {}
        big_pic = pic['sizes'][-1]['url']
        like_num = str(pic['likes']['count'])
        like_num_name = like_num + '.jpg'

        if like_num_name in likes_links:
            like_num_name = like_num_name[:-4] + '.1.jpg'

        likes_links[like_num_name] = big_pic

        big_pic_height = pic['sizes'][-1]['height']
        big_pic_width = pic['sizes'][-1]['width']

        height_width.update({'height': big_pic_height, 'width': big_pic_width})
        name_and_size.update({'file_name': like_num_name, 'size': height_width})

        sizes_links_json.append(name_and_size)

    with open('vk_pics.json', 'w') as f:
        json.dump(sizes_links_json, f)

    response = requests.put('https://cloud-api.yandex.net/v1/disk/resources',
                            params={'path': album_id},
                            headers={'Authorization': f'OAuth {ya_token}'})

    for k in likes_links:
        response = requests.post('https://cloud-api.yandex.net/v1/disk/resources/upload',
                                  params={'url': likes_links[k],
                                          'path': f'/{album_id}/{k}'},
                                  headers={'Authorization': f'OAuth {ya_token}'})

    for i in tqdm(likes_links):
        time.sleep(1)

    return response


put_pics(vk_token, '5.126', yadisk_token)
