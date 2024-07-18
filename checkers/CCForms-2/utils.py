import uuid
import requests
import random
import string
import base64 as b64

def random_string(lmin, lmax, alphabet=None):
    if not alphabet:
        alphabet = string.ascii_letters + string.digits

        if random.randint(0, 100) < 10:
            alphabet += string.punctuation
        if random.randint(0, 100) < 10:
            alphabet += string.whitespace
        if random.randint(0, 100) < 10:
            alphabet = string.printable
        
    return ''.join(random.choices(alphabet, k=random.randint(lmin, lmax)))

def is_uuid(s):
    try:
        uuid.UUID(s)
        return True
    except:
        return False
    
class ClientSession:
    def __init__(self, url, port, credentials=None):
        self.url = url
        self.port = port
        self.user_id = None
        if credentials is not None:
            self.token = credentials['token']
            self.username = credentials['username']
            self.password = credentials['password']
        self.forms = []
    
    def export_credentials(self):
        return {
            'token': self.token,
            'username': self.username,
            'password': self.password
        }
    
    def register(self):
        self.username = random_string(5, 20)
        self.password = random_string(5, 20)

        r = requests.post(f'http://{self.url}:{self.port}/register', json={'username': self.username, 'password': self.password})

        if r.status_code != 200:
            raise Exception(f'Failed to register: {r.text}')
        
        j = r.json()

        if not j.get('token') or not j.get('id'):
            raise Exception(f'Failed to register: {r.text}')

        self.token = j['token']
        self.user_id = j['id']

        return self.user_id
    
    def login(self):
        r = requests.post(f'http://{self.url}:{self.port}/login', json={'username': self.username, 'password': self.password})

        if r.status_code != 200:
            raise Exception(f'Failed to login: {r.text}')
        
        j = r.json()

        if not j.get('token') or not j.get('id'):
            raise Exception(f'Failed to login: {r.text}')

        self.token = j['token']
        self.user_id = j['id']

        return self.user_id

    def new_form(self, note=None):

        questions = []

        for _ in range(random.randint(1, 10)):
            type = random.choice(['text', 'file', 'multiple', 'embedded'])
                
            if type == 'text':
                questions.append({
                    'type': 'text',
                    'question': random_string(5, 20)
                })
            elif type == 'file':
                questions.append({
                    'type': 'file',
                    'question': random_string(5, 20)
                })
            elif type == 'multiple':
                questions.append({
                    'type': 'multiple',
                    'question': random_string(5, 20),
                    'options': [random_string(5, 20) for i in range(random.randint(2, 5))]
                })
            elif type == 'embedded':
                if len(self.forms) != 0:
                    questions.append({
                        'type': 'embedded',
                        'data': {'id': random.choice(self.forms)['id']}
                    })
                else:
                    questions.append({
                        'type': 'text',
                        'question': random_string(5, 20)
                    })
                    
        if note is not None:
            q = random.choice(questions)
            q['note'] = note
        else:
            if random.randint(0, 100) < 80:
                for q in questions:
                    if random.randint(0, 100) < 30:
                        q['note'] = random_string(5, 50)
                    else:
                        q['note'] = ''
                        
        form = {
            'title': random_string(5, 20),
            'questions': questions
        }

        r = requests.post(f'http://{self.url}:{self.port}/new', json=form, headers={'Authorization': 'Bearer: ' + self.token})

        if r.status_code != 200:
            raise Exception(f'Failed to create form: {r.text}')
        
        j = r.json()

        if not j.get('id'):
            raise Exception(f'Failed to create form: {r.text}')
        
        
        form['id'] = j['id']

        self.forms.append(form)

        return form

    def get_form(self, form_id):
        r = requests.get(f'http://{self.url}:{self.port}/form/{form_id}', headers={'Authorization': 'Bearer: ' + self.token})

        if r.status_code != 200:
            raise Exception(f'Failed to get form {form_id} : {r.text}')
        
        j = r.json()

        return j
    
    def get_forms(self):
        r = requests.get(f'http://{self.url}:{self.port}/forms', headers={'Authorization': 'Bearer: ' + self.token})

        if r.status_code != 200:
            raise Exception(f'Failed to get forms: {r.text}')
        
        j = r.json()

        return j
    
    def submit_answer(self, form, flag=None):
        form_id = form['id']

        answers = []

        for question in form['questions']:
            if question['type'] == 'text':
                answers.append(random_string(5, 20))
            elif question['type'] == 'file':
                answers.append({
                    'name': random_string(5, 20, string.ascii_letters + string.digits),
                    'content': b64.b64encode(random_string(5, 50).encode()).decode()
                })
            elif question['type'] == 'multiple':
                answers.append(random.choice(question['options']))
            elif question['type'] == 'embedded':
                answers.append(None)
                
        if flag is not None:
            #print(form)
            q = form['questions'][0]
            if  q['type'] == 'file':
                answers[0]['name'] = flag
            else:
                answers[0] = flag

        r = requests.post(f'http://{self.url}:{self.port}/form/{form_id}/answer', json=answers, headers={'Authorization': 'Bearer: ' + self.token})

        if r.status_code != 200:
            raise Exception(f'Failed to submit form {form_id} : {r.text}')
        
        j = r.json()

        if not j.get('id'):
            raise Exception(f'Failed to submit form {form_id} : {r.text}')
        
        return j['id'], answers
    
    def get_answers(self, form):
        form_id = form['id']

        r = requests.get(f'http://{self.url}:{self.port}/form/{form_id}/answers', headers={'Authorization': 'Bearer: ' + self.token})

        if r.status_code != 200:
            raise Exception(f'Failed to get answers for form {form_id} : {r.text}')
        
        j = r.json()

        return j
    
    def get_file(self, file_id):

        headers = {}

        # files are not protected by token
        if random.randint(0, 100) < 50:
            headers['Authorization'] = 'Bearer: ' + self.token

        r = requests.get(f'http://{self.url}:{self.port}/file/{file_id}', headers=headers)

        if r.status_code != 200:
            raise Exception(f'Failed to get file {file_id} : {r.text}')
        
        return r.content