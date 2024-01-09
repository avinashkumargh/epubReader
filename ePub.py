from flask import Flask, render_template, request, url_for, redirect
from epub_parser import Book
from bs4 import BeautifulSoup as bs
import os, glob, shutil

app = Flask(__name__)

def removeParsedFile(loc):
    os.remove(loc)


def htmlConverter(bookObj, spineItem, extension):
    """
    for reading the files of the spineItem of HTML

    Parsing can be better by taking into account the ../ and ./ format
    """
    with open(bookObj.tempAddress+ spineItem.href, "r", encoding="utf8") as chapter:
        chapter = bs(chapter.read(), extension)
        #changing images from source to static
        for i in chapter.find_all("img"):
            i.attrs["src"] = i.attrs["src"].replace("../", "").replace("./", "")
            if i.attrs["src"].startswith("/"):
                i.attrs["src"] = i.attrs["src"][1:]
            i.attrs["src"] = "{{ url_for('static', filename='images/"+ i.attrs["src"] +"') }}"
            #print(i.attrs, "Found img. just a notification that htmlConverter is working for images")

        #changing css from source to static
        for i in chapter.find_all("link"):
            if i.attrs["rel"][0] == "stylesheet":
                i.attrs["href"] = i.attrs["href"].replace("../", "").replace("./", "")
                if i.attrs["href"].startswith("/"):
                    i.attrs["href"] = i.attrs["href"][1:]
                i.attrs["href"] = "{{ url_for('static', filename='css/"+ i.attrs["href"] +"') }}"
                #print(i.attrs, "Found link stylesheet. just a notification that htmlConverter is working for css")

        #getting head and Body of the html files without the <HEAD> and <BODY> tags
        head = ""
        body = ""
        for i in chapter.find("head").findChildren(recursive=False):
            head += str(i)+"\n"
        for i in chapter.find("body").findChildren(recursive=False):
            body += str(i)+"\n"
        
    removeParsedFile(bookObj.tempAddress+ spineItem.href)
    return [head, body]    

def xmlConverter(bookObj, spineItem, extension):
    return ["Head is empty", "Ddint impliment this bitch. I am xmlConverter"]

def xhtmlConverter(bookObj, spineItem, extension):
    """
    for reading the files of the spineItem of xHTML
    """
    with open(bookObj.tempAddress+ spineItem.href, "r", encoding="utf8") as chapter:
        chapter = bs(chapter.read(), "xml")
        print("Start of cover")
        for i in chapter.find_all("image"):
            i.attrs["xlink:href"] = "{{ url_for('static', filename='images/"+ i.attrs["xlink:href"] +"') }}"
            #print(i.attrs)

        for i in chapter.find_all("img"):
            i.attrs["src"] = i.attrs["src"].replace("../", "").replace("./", "")
            if i.attrs["src"].startswith("/"):
                i.attrs["src"] = i.attrs["src"][1:]
            i.attrs["src"] = "{{ url_for('static', filename='images/"+ i.attrs["src"] +"') }}"

        #changing css from source to static
        for i in chapter.find_all("link"):
            if i.attrs["rel"][0] == "stylesheet":    
                i.attrs["href"] = i.attrs["href"].replace("../", "").replace("./", "")
                if i.attrs["href"].startswith("/"):
                    i.attrs["href"] = i.attrs["href"][1:]
                i.attrs["href"] = "{{ url_for('static', filename='images/"+ i.attrs["href"] +"') }}"
                print(i.attrs, "Found link stylesheet. just a notification that xhtmlConverter is working for css")

        head = ""
        body = ""
        #getting head and Body of the html files without the <HEAD> and <BODY> tags
        for i in chapter.find("head").findChildren(recursive=False):
            head += str(i)+"\n"
        for i in chapter.find("body").findChildren(recursive=False):
            body += str(i)+"\n"
    removeParsedFile(bookObj.tempAddress+ spineItem.href)
    return [head, body]


def moveFilesfromExtractedtoApplicaion(loc):
    '''
    This is where we'll convert the relative path to static
    Moving Css and Images from the source to Static folder
    '''
    for i in os.walk(loc):
        for j in i[2]:
            currentFileLocation = (i[0]+"/"+j).replace("//", "/")
            currentFileStaticLocation = (currentFileLocation).replace(loc, "")
            folderToCreate = currentFileStaticLocation.rsplit("/", 1)
            if j.endswith((".jpg", ".jpeg", ".svg")):
                if len(folderToCreate) > 1: 
                    try:
                        os.mkdir(os.path.join("static/images/"+folderToCreate[0])) 
                    except FileExistsError as e:
                        print(e, " File already exists no issues anyway")
                shutil.move(currentFileLocation, "static/images/"+currentFileStaticLocation)
                #print(currentFileStaticLocation)
                #print("image move from", (currentFileLocation).replace(loc, ""), " to static/images")
            elif j.endswith(".css"):
                if len(folderToCreate) > 1:
                    try:
                        os.mkdir(os.path.join("static/css/"+folderToCreate[0])) 
                    except FileExistsError as e:
                        print(e, " File already exists no issues anyway")
                shutil.move(currentFileLocation, "static/css/"+currentFileStaticLocation)
                #print(currentFileStaticLocation)
                #print("CSS move from", (currentFileLocation).replace(loc, ""), " to static/css")
            else:
                '''
                These files are not necessary as we extracted data from them initially
                '''
                #print(currentFileLocation, "       ", "static/images/"+currentFileStaticLocation)
                #print("No need to create")
                pass

def renderSpine(bookObj):
    '''
    Extracting Spine data and sorting the files into the project
    '''
    modifiedSpineItems = []
    for spineItem in bookObj.spine:
        extension = spineItem.href.split(".")[-1]
        #print(bookObj.tempAddress, "is the temp address ", bookObj.name, " is the ename is the book")
        currPage = bookObj.name+"/"+spineItem.href.split("/")[-1]
        #if extension == "xhtml":
        #    extension = "html"
        #print(bookObj.tempAddress+ spineItem.href)
        #depending on the extension open the book in respective parser and look for images and css files
        #Must change
        extension = extension.lower()
        head = ""
        body = ""
        if extension == "html":
            head, body = htmlConverter(bookObj, spineItem, "html")
        elif extension == "xhtml":
            head, body = xhtmlConverter(bookObj, spineItem, "html")
        elif extension == "xml":
            head, body = xmlConverter(bookObj, spineItem, "xml")
        else:
            print("Different extenion man TF It is ", extension)
        print(currPage, "this is the new folder to save templetes")
        with open("templates/"+currPage, "w", encoding="utf8") as book:
            book.write("{% extends 'base.html' %}\n\n"+ "{% block head %}\n"+head+"\n{% endblock %}\n" +"{% block body %}\n"+ body +"\n{% endblock %}")
        modifiedSpineItems.append(currPage)
        moveFilesfromExtractedtoApplicaion(bookObj.tempAddress)
    return modifiedSpineItems # should be a tab forward
    #return "loading Book "+ file.filename + "\n".join(str(v.order) for v in bookObj.spine)

def openBook(name):
    '''
    Extracting the uploaded book and parsing it.
    '''
    loc = "uploads/"+name
    newBook = Book(loc, name)
    if newBook.checkEpub():
        newBook.getContainerXml()
        newBook.constructSpine()
        newBook.getToc()
        #newBook.deleteTempFolder()
        try:
            os.mkdir("templates/"+newBook.name)
        except:
            #os.mkdir("templates/"+newBook.name+"_1")
            # should make forlders with followup names
            pass
        return newBook
    else:
        return False


def removeCache():
    '''
    removing extra templates, static files
    '''
    '''
    Produces multiple errors 
    look for a workaround to add files manually or 
    see how the error is being created with the \ 
    and / while using blob and os.walk
    '''
    for clean_up in glob.glob('templates/*'):
        clean_up = clean_up.replace("\\", "/")
        if clean_up not in ["templates/base.html", "templates/index.html"]:    
            shutil.rmtree(clean_up)
    print("Templates cleared")

    for basePath, folders, files in os.walk("static/"):
        #print(basePath, folders, files)
        if files != []:
            for file in files:
                filePath = (basePath+"/"+file).replace("\\", "/")
                if filePath not in ["static/css/style.css"]:
                    print(filePath, " original file ", basePath+"/"+file)
                    os.remove(basePath+"/"+file)#os.path.join(basePath,file))
    print("static files cleared")

#removeCache()

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")
    
@app.route('/', methods=["POST"])
@app.route('/index', methods=["POST"])
def upload_file():
    file = request.files.get('file')
    if file.filename.strip() != "":
        file.save("uploads/"+file.filename)
        newBook = Book("uploads/"+file.filename, file.filename)
        bookObj = openBook(file.filename)
        if bookObj == False:
            return "There was an error while parsing the book"
        #currPage = "This has no impact"
        spineItems = renderSpine(bookObj)
        
        return render_template(spineItems[8]) # should be a tab forward
        #return "loading Book "+ file.filename + "\n".join(str(v.order) for v in newBook.spine)
        
    else:
        return redirect(url_for('index'))


app.run(debug= True)