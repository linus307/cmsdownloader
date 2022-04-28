import json, re, subprocess, os
from bs4 import BeautifulSoup
from pathlib import Path

def cleanName(str):
    return re.sub(r"[\./]", " ", str)

def cleanPath(str):
    return re.sub(r"[/]", " ", str)

def cmsWget(location, link):
    args = ['wget', '--tries=3', '--load-cookies', '/usr/local/bin/cmsCookie.txt', '-O', location, link]
    subprocess.run(args)

def wget(location, link):
    args = ['wget', '--tries=3', '-O', location, link]
    subprocess.run(args)

documents_path = Path.home() + "/Dokumente/Unterlagen/"
books_path = Path.home() + "/Dokumente/Bücher/"


cmsfiles_path = Path.home() + "/.cmsfiles"
cmsfiles = {}

if os.path.exists(cmsfiles_path):
    with open(cmsfiles_path, 'r') as file:
        cmsfiles = json.load(file)

coursesStr = subprocess.run(['wget', '--tries=3', '-O', '-', '-o', '/dev/null', '--load-cookies', '/usr/local/bin/cmsCookie.txt', 'https://cms.sic.saarland/system/courses'],stdout = subprocess.PIPE).stdout.decode("utf-8")

soup = BeautifulSoup(coursesStr, 'html.parser')
coursesSrc = soup.find_all("td", class_="td-name")
courses = [(re.match(r'.+/([^/]*)', course.find('a', href=True)['href']).groups()[0], cleanPath(course.find('a', href=True).text)) for course in coursesSrc if not course.find('span', class_="label label-success") == None]

for course in courses:
    if not course[1] in cmsfiles:
        cmsfiles[course[1]] = {'courseLink' : course[0], 'materials' : {}, 'toDownloade' : True}
    else:
        cmsfiles[course[1]]['courseLink'] = course[0]
    if not cmsfiles[course[1]]['toDownloade']:
        continue
    course_documents_path = documents_path + course[1] + "/"
    course_books_path = books_path + course[1] + "/"
    
    courseStr = subprocess.run(['wget', '--tries=3', '-O', '-', '-o', '/dev/null', '--load-cookies', '/usr/local/bin/cmsCookie.txt', 'https://cms.sic.saarland/' + course[0] + '/materials'],stdout = subprocess.PIPE).stdout.decode("utf-8")
    soup = BeautifulSoup(courseStr, 'html.parser')
    downloadsCategories = soup.find_all("div", class_="accordion-group")

    for downloadsCategory in downloadsCategories:
        title = downloadsCategory.find("div", class_="title")
        categoryTitle = cleanPath(title.text.lstrip().rstrip())
        if not categoryTitle in cmsfiles[course[1]]['materials']:
            cmsfiles[course[1]]['materials'][categoryTitle] = {'files' : {}, 'isExcercise' : True, 'toDownloade' : True}
        if not cmsfiles[course[1]]['materials'][categoryTitle]['toDownloade']:
            continue
        if cmsfiles[course[1]]['materials'][categoryTitle]['isExcercise']:
            categoryPath = course_documents_path + categoryTitle + "/"
        else:
            categoryPath = course_books_path + course[1] + " - " + categoryTitle + "/"
        
        for download in downloadsCategory.find_all("tr"):
            linkAttribute = download.find('a', href=True)
            if linkAttribute != None:
                linkTitle = cleanName(linkAttribute.text)
                link = linkAttribute['href']
                rev = -1
                fileExtension = re.match(r'.+(\.\w*)',link).groups()[0]
                if download.find('a', target=True) != None and fileExtension != ".pdf":
                    continue
                if cmsfiles[course[1]]['materials'][categoryTitle]['isExcercise']:
                    dirpath = categoryPath + linkTitle + "/"
                else:
                    dirpath = categoryPath
                filepath = dirpath + linkTitle + fileExtension
                    
                if not linkTitle in cmsfiles[course[1]]['materials'][categoryTitle]['files']:
                    cmsfiles[course[1]]['materials'][categoryTitle]['files'][linkTitle] = {'rev' : -2, 'link' : link}

                if rev <= cmsfiles[course[1]]['materials'][categoryTitle]['files'][linkTitle]['rev'] and os.path.exists(filepath):
                    continue

                Path(dirpath).mkdir(parents=True, exist_ok=True)
                if download.find('a', target=True) == None:
                    revColumn = download.find("td", class_="rev-column")
                    if revColumn != None:
                        rev = int(revColumn.text.lstrip().rstrip().removeprefix('rev').lstrip())
                    downloadLink = 'https://cms.sic.saarland' + link
                    cmsWget(filepath, downloadLink)
                else:
                    wget(filepath, link)
                
                if rev < 0:
                        rev = -2
                cmsfiles[course[1]]['materials'][categoryTitle]['files'][linkTitle]['rev'] = rev
                cmsfiles[course[1]]['materials'][categoryTitle]['files'][linkTitle]['link'] = link

with open(cmsfiles_path, 'w') as file:
    json.dump(cmsfiles, file, indent=True)
