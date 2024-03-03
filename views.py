from datetime import datetime
import numpy as np
from django.shortcuts import render, redirect
from app.models import *
import urllib.request
from bs4 import BeautifulSoup
import requests
import time
import re
import nltk
from nltk import pos_tag, word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import app.admin as admin
from django.db.models import Q

nltk.data.path.append("D:\\nltk_data")
stop_words = stopwords.words('english')
pos = ["NN", "NNP", "NNS", "NNPS", "JJ"]
lemmatizer = WordNetLemmatizer()
skillset = ['html', 'css', 'bootstrap', 'javascript',
            'angularjs', 'angular', 'node', 'reactjs',
            'mongodb', 'nodejs', 'db2', 'ibm db2', 'sql',
            'java', 'c', 'cpp', 'oop', 'react', 'maven',
            'aws', 'azure', 'oracle', 'sybase', 'hardware',
            'networking', 'selenium', 'testing', 'unix', 'linux']
myss = list()
video_category = "CoreTech Computer Education"
youtube_url = "https://www.youtube.com/results?search_query="


def home(request):
    if 'uid' in request.session:
        del request.session['uid']
    return render(request, 'app/home.html')


def registration(request):
    if request.method == 'POST':
        try:
            usermodel = UserModel1()
            usermodel.uid = str(request.POST.get('uid')).strip()
            usermodel.uname = request.POST.get('uname')
            usermodel.upassword = str(request.POST.get('upassword')).strip()
            usermodel.uarea = str(request.POST.get('uarea')).strip()
            usermodel.uskills = str(request.POST.get('uskills')).strip()
            usermodel.umobile = str(request.POST.get('umobile')).strip()
            usermodel.save(force_insert=True)
            message = 'User registration done'
        except Exception as ex:
            message = ex
        return render(request, 'app/registration.html', {'message': message})
    else:
        return render(request, 'app/registration.html')


def login(request):
    if request.method == 'POST':
        try:
            urole = str(request.POST.get('urole')).strip()
            uid = str(request.POST.get('uid')).strip()
            upassword = str(request.POST.get('upassword')).strip()
            if urole == 'Admin':
                if uid == admin.uid and upassword == admin.upassword:
                    return redirect(add_uploads)
            else:
                usermodel = UserModel.objects.get(uid=uid)
                if usermodel.upassword == upassword:
                    request.session['uid'] = usermodel.uid
                    request.session['uname'] = usermodel.uname
                    return redirect(assignments)
            message = 'Wrong password'
        except UserModel1.DoesNotExist:
            message = 'Wrong email id'
        except Exception as ex:
            message = ex
        return render(request, 'app/login.html', {'message': message})
    else:
        return render(request, 'app/login.html')


def add_uploads(request):
    if request.method == 'POST':
        try:
            upid = datetime.now().strftime('%d%m%y%I%M%S')
            upsubject = str(request.POST.get('upsubject')).strip()
            uptype = str(request.POST.get('uptype')).strip()
            updata = f'media/{upsubject}/{uptype}/{upid}.pdf'
            with open(updata, 'wb') as fw:
                fw.write(request.FILES['updata'].read())
            upload = UploadModel()
            upload.upid = upid
            upload.update = datetime.now().strftime('%d/%m/%y')
            upload.upsubject = upsubject
            upload.uptype = uptype
            upload.save(force_insert=True)
            message = 'Data uploaded successfully.'
        except Exception as ex:
            message = ex
        return render(request, 'app/add_uploads.html', {'message': message})
    else:
        return render(request, 'app/add_uploads.html')


def add_videos(request):
    if request.method == 'POST':
        try:
            upid = datetime.now().strftime('%d%m%y%I%M%S')
            upsubject = str(request.POST.get('upsubject')).strip()
            upload = UploadModel()
            upload.upid = upid
            upload.update = datetime.now().strftime('%d/%m/%y')
            upload.upsubject = upsubject
            upload.uptype = 'Video'
            upload.upvideolink = str(request.POST.get('upvideolink')).strip()
            upload.save(force_insert=True)
            message = 'Video added successfully.'
        except Exception as ex:
            message = ex
        return render(request, 'app/add_videos.html', {'message': message})
    else:
        return render(request, 'app/add_videos.html')


def view_uploads(request):
    try:
        if request.method == 'POST':
            upid = request.POST.get('upid')
            upload = UploadModel.objects.get(upid=upid)
            upload.delete()
        uploads = UploadModel.objects.filter(~Q(uptype='Video'))
        return render(request, 'app/view_uploads.html', {'uploads': uploads})
    except Exception as ex:
        return render(request, 'app/view_uploads.html', {'message': ex})


def viewvideos(request):
    try:
        if request.method == 'POST':
            upid = request.POST.get('upid')
            upload = UploadModel.objects.get(upid=upid)
            upload.delete()
        uploads = UploadModel.objects.filter(uptype='Video')
        return render(request, 'app/viewvideos.html', {'uploads': uploads})
    except Exception as ex:
        return render(request, 'app/viewvideos.html', {'message': ex})


def assignments(request):
    try:
        uploads = UploadModel.objects.filter(uptype='Assignment')
        return render(request, 'app/assignments.html', {'uploads': uploads})
    except Exception as ex:
        return render(request, 'app/assignments.html', {'message': ex})


def papers(request):
    try:
        uploads = UploadModel.objects.filter(uptype='Question Papers')
        return render(request, 'app/papers.html', {'uploads': uploads})
    except Exception as ex:
        return render(request, 'app/papers.html', {'message': ex})


def lecturevideos(request):
    try:
        uploads = UploadModel.objects.filter(uptype='Video')
        return render(request, 'app/lecturevideos.html', {'uploads': uploads})
    except Exception as ex:
        return render(request, 'app/lecturevideos.html', {'message': ex})


def notes(request):
    try:
        uploads = UploadModel.objects.filter(uptype='Notes')
        return render(request, 'app/notes.html', {'uploads': uploads})
    except Exception as ex:
        return render(request, 'app/notes.html', {'message': ex})


def view_videos(request):
    global myss
    try:
        if 'uid' in request.session:
            uid = request.session['uid']
            user = UserModel1.objects.get(uid=uid)
            for skill in str(user.uskills).split():
                if skill.lower() in skillset:
                    myss.append(skill)
            query = (video_category + str(user.uarea) + str(myss)).replace(' ', '+')
            html = urllib.request.urlopen(youtube_url + query)
            video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
            video_ids = unique(video_ids)
            video_data = []
            skills = []
            for video_id in video_ids[:20]:
                url = f"https://www.youtube.com/watch?time_continue=17&v={video_id}"
                video = scrape_info(url)
                if video:
                    video_data.append({'id': video_id, 'title': video['title'], 'description': video['description']})
                time.sleep(2)
            df_train = pd.DataFrame(video_data)
            df_train['title'] = df_train['title'].apply(clean_text)
            df_train['title'] = df_train['title'].apply(remove_stopwords)
            df_train['title'] = df_train['title'].apply(stemmer)

            df_test = pd.DataFrame({'skills': [user.uskills]})
            df_test['skills'] = df_test['skills'].apply(clean_text)
            df_test['skills'] = df_test['skills'].apply(remove_stopwords)
            df_test['skills'] = df_test['skills'].apply(stemmer)

            vectorizer = TfidfVectorizer()
            train_data = vectorizer.fit_transform(df_train['title'])
            true_k = 3
            model = KMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=1)
            labels = model.fit_predict(train_data)

            test_data = vectorizer.transform(df_test['skills'])
            prediction = model.predict(test_data)
            for index, label in enumerate(labels):
                if label == prediction:
                    skills.append({'id': video_data[index]['id'], 'title': video_data[index]['title'],
                                   'description': video_data[index]['description']})

            return render(request, 'app/view_videos.html', {'video_data': skills})
        else:
            return redirect('/')
    except Exception as ex:
        message = ex
    return render(request, 'app/view_videos.html', {'message': message})


def scrape_info(url):
    content = requests.get(url)
    soup = BeautifulSoup(content.text, 'html.parser')
    title = soup.find("meta", {"name": "title"})['content']
    description = soup.find("meta", {"name": "description"})['content']
    return {'title': title, 'description': description}


def unique(video_lds):
    x = np.array(video_lds)
    return np.unique(x)


def clean_text(words):
    words = re.sub("[^a-zA-Z]", " ", words)
    text = words.lower().split()
    return " ".join(text)


def remove_stopwords(text):
    text = word_tokenize(text)
    text = [word.lower() for word in text if word.lower() not in stop_words]
    text = [word for word in text if pos_tag(word.split())[0][1] in pos]
    return " ".join(text)


def stemmer(stem_text):
    stem_text = [lemmatizer.lemmatize(word) for word in stem_text.split()]
    return " ".join(stem_text)
