from flask import Flask, render_template, request, url_for, redirect
from epub_parser import Book
from bs4 import BeautifulSoup as bs
import os

app = Flask(__name__)

def htmlConverter():
    pass

def xmlConverter():
    pass

def xhtmlConverter():
    pass


def moveBooksfromExtractedtoApplicaion(file):
    '''
    This is where we'll convert the relative path to static
    '''

def renderSpine():
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
        if newBook.checkEpub():
            newBook.getContainerXml()
            newBook.constructSpine()
            newBook.getToc()
            #newBook.deleteTempFolder()
            currPage = ""
            print(newBook.name, "this is book name")
            try:
                os.mkdir("templates/"+newBook.name)
            except:
                pass
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