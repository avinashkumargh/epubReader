from flask import Flask, render_template, request, url_for, redirect
from epub_parser import Book
from bs4 import BeautifulSoup as bs
import os

app = Flask(__name__)

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
            print(i.attrs, "Found img. just a notification that htmlConverter is working for images")

        #changing css from source to static
        for i in chapter.find_all("link"):
            if i.attrs["rel"] == "stylesheet":    
                i.attrs["href"] = i.attrs["href"].replace("../", "").replace("./", "")
                if i.attrs["href"].startswith("/"):
                    i.attrs["href"] = i.attrs["href"][1:]
                i.attrs["href"] = "{{ url_for('static', filename='images/"+ i.attrs["href"] +"') }}"
                print(i.attrs, "Found link stylesheet. just a notification that htmlConverter is working for css")
            
        head = ""
        body = ""
        #getting head and Body of the html files without the <HEAD> and <BODY> tags
        for i in chapter.findAll("head"):
            for j in i.findChildren():
                head = head+str(j)+"\n"
        for i in chapter.findAll("body"):
            for j in i.findChildren():
                body = body+str(j)+"\n"
        return [head, body]

def xmlConverter(bookObj, spineItem, extension):
    pass

def xhtmlConverter(bookObj, spineItem, extension):
    """
    for reading the files of the spineItem of xHTML
    """
    with open(bookObj.tempAddress+ spineItem.href, "r", encoding="utf8") as chapter:
        chapter = bs(chapter.read(), extension)
        for i in chapter.find_all("image"):
            i.attrs["xlink:href"] = "{{ url_for('static', filename='images/"+ i.attrs["xlink:href"] +"') }}"
            #print(i.attrs)

        #changing css from source to static
        for i in chapter.find_all("link"):
            if i.attrs["rel"] == "stylesheet":    
                i.attrs["href"] = i.attrs["href"].replace("../", "").replace("./", "")
                if i.attrs["href"].startswith("/"):
                    i.attrs["href"] = i.attrs["href"][1:]
                i.attrs["href"] = "{{ url_for('static', filename='images/"+ i.attrs["href"] +"') }}"
                print(i.attrs, "Found link stylesheet. just a notification that xhtmlConverter is working for css")

        head = ""
        body = ""
        #getting head and Body of the html files without the <HEAD> and <BODY> tags
        for i in chapter.findAll("head"):
            for j in i.findChildren():
                head = head+str(j)+"\n"
        for i in chapter.findAll("body"):
            for j in i.findChildren():
                body = body+str(j)+"\n"
        return [head, body]


def moveBooksfromExtractedtoApplicaion(file):
    '''
    This is where we'll convert the relative path to static
    '''

def renderSpine(bookObj):
    '''
    Extracting Spine data and sorting the files into the project
    '''
    for spineItem in bookObj.spine:
        extension = spineItem.href.split(".")[-1]
        print(spineItem.href, "this is spine href")
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
    return currPage # should be a tab forward
    return "loading Book "+ file.filename + "\n".join(str(v.order) for v in bookObj.spine)

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
        openBook(file.filename)
        if newBook.checkEpub():
            newBook.getContainerXml()
            newBook.constructSpine()
            newBook.getToc()
            #newBook.deleteTempFolder()
            #rint(newBook.name, "this is book name")
            try:
                os.mkdir("templates/"+newBook.name)
            except:
                pass
            #done till here
            currPage = ""
            for spineItem in newBook.spine:
                extension = spineItem.href.split(".")[-1]
                print(spineItem.href, "this is spine href")
                currPage = newBook.name+"/"+spineItem.href.split("/")[-1]
                if extension == "xhtml":
                    extension = "html"
                #print(newBook.tempAddress+ spineItem.href)
                with open(newBook.tempAddress+ spineItem.href, "r", encoding="utf8") as chapter:
                    chapter = bs(chapter.read(), extension)
                    for i in chapter.find_all("image"):
                        i.attrs["xlink:href"] = "{{ url_for('static', filename='images/"+ i.attrs["xlink:href"] +"') }}"
                        #print(i.attrs)
                    head = ""
                    body = ""

                    for i in chapter.findAll("head"):
                        for j in i.findChildren():
                            head = head+str(j)+"\n"
                    for i in chapter.findAll("body"):
                        for j in i.findChildren():
                            body = body+str(j)+"\n"
                    #print(head, "\n\n\n\n\n\n\n\n", body)
                print(currPage, "this is the new folder to save templetes")
                with open("templates/"+currPage, "w", encoding="utf8") as book:
                    book.write("{% extends 'base.html' %}\n\n"+ "{% block head %}\n"+head+"{% endblock %}\n" +"{% block body %}\n"+ body +"{% endblock %}")
            return render_template(currPage) # should be a tab forward
            return "loading Book "+ file.filename + "\n".join(str(v.order) for v in newBook.spine)
        else:
            return "There was an error while parsing the book"
    else:
        return redirect(url_for('index'))


app.run(debug= True)