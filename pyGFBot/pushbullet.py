import json
import requests


class PushBullet:
    def __init__(self):
        self.headers = {
            'Access-Token': 'o.D9SRmMJubMSiOWzPr9LZ6qtqnkQkafnu',
            'Conten-Type': 'application/json'
        }

    def push_note(self, title=None, body=None, email=None):
        data = {
            'title': title,
            'body': body,
            'email': email,
            'type': 'note'
        }
        requests.post('https://api.pushbullet.com/v2/pushes', headers=self.headers, data=data)
        print('Bullet Pushed')

    def upload_request(self, file_name, file_type):
        data = {'file_name': file_name, 'file_type': file_type}

        response = requests.post('https://api.pushbullet.com/v2/upload-request', headers=self.headers, data=data)
        parsed = json.loads(response.text)

        return {'file_name': parsed['file_name'],
                'file_type': parsed['file_type'],
                'file_url': parsed['file_url'],
                'upload_url': parsed['upload_url']}

    def push_img(self, image, email=None):
        img = self.upload_request('t.jpeg', 'image/jpeg')
        requests.post(img['upload_url'], files={'file': (image, open(image, 'rb'))})

        data = {
            'email': email,
            'type': 'file',
            'body': None,
            'file_name': img['file_name'],
            'file_type': img['file_type'],
            'file_url': img['file_url']
        }

        requests.post('https://api.pushbullet.com/v2/pushes', headers=self.headers, data=data)