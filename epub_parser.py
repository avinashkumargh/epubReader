from zipfile import ZipFile
from bs4 import BeautifulSoup as bs
import shutil

class indexItemData:
    def __init__(self, href, id, mediaType, order =-1, linear = False, name = None):
        self.href = href
        self.id = id
        self.mediaType = mediaType
        self.order = order
        self.linear = linear
        self.name = name
    
    def getItemData(self):
        return [self.href, self.id, self.mediaType, self.order, self.linear, self.name]


class Book:
    def __init__(self, loc, name):
        #see if you want to extract the books when adding them...
        self.address = loc
        self.extractedFolderName = name
        self.name = name.split(".")[0]
        self.tempAddress = "./Extracted/"+self.extractedFolderName+"/"
        self.contentOpf = ""
        self.contentFolder = ""
        self.TOC = []
        self.spine = []
        self.reordered_manifest = {} #key is id(used to merge spine and manifest)
        self.reordered_manifest_byhref = {} # key is address used to make TOC from toc file and merging the data with manifest file
        self.extractEpub()
    
    def extractEpub(self):
        with ZipFile(self.address, "r") as book:
            book.extractall(self.tempAddress)
    
    def checkEpub(self):
        with open(self.tempAddress+"mimetype", "r") as mimetype:
            mimetype = mimetype.read()
        if mimetype == "application/epub+zip":
            print("The ePub is successfully extracted")
            return True
        else:
            print("The imported file is corrupted")
            self.deleteTempFolder()
            return False

    def getContainerXml(self):
        '''
        This is where we get the meta data of where everythung is.
        '''
        with open(self.tempAddress+"META-INF/container.xml", "r") as f:
            container = bs(f.read(), "xml")
        container = container.findAll("rootfile")[0]
        self.contentOpf = container.get("full-path")
        self.contentOpf.replace("\\", "/")  
        if "/" in self.contentOpf:
            self.contentFolder = self.contentOpf.split("/")[0]+"/"
            #print("specific folder available")
        else:
            self.contentFolder = ""
            #print("no specific folder")  
        return True
    

    def constructSpine(self):
        '''
        This is were we get the order of our book from (Spine).
        '''
        with open(self.tempAddress+self.contentOpf, "r") as f:
            data = bs(f.read(), "xml")

        manifest = data.find("manifest")
        for j in manifest.findChildren("item"):
            temp_data = indexItemData(j.attrs['href'], j.attrs['id'], j.attrs['media-type'])#[j.attrs['href'], j.attrs['media-type']]
            self.reordered_manifest[j.attrs['id']] = temp_data
            self.reordered_manifest_byhref[j.attrs['href']] = temp_data

        spine = data.find("spine")
        order=0
        for i in spine.findChildren("itemref"):
            self.spine.append(self.reordered_manifest[i.attrs['idref']])
            self.reordered_manifest[i.attrs['idref']].order = order
            try:
                self.reordered_manifest[i.attrs['idref']].linear = i.attrs['linear']
            except KeyError:
                #print("Key error, rectified")
                self.reordered_manifest[i.attrs['idref']].linear = 'yes'
            except:
                print("Error")

            #print(i.attrs['idref'], i.attrs['linear'], order, self.reordered_manifest[i.attrs['idref']])
            #self.reordered_manifest[i.attrs['idref']].getItemData()  to print the data of indexedItemData
            order+=1

    def getToc(self):
        '''
        This is where well extract the table of content
        '''
        
        with open(self.tempAddress+self.contentFolder+'toc.ncx', "r") as f:
            data = bs(f.read(), "xml")

        navMpa = data.find("navMap")
        
        tocKey = ""
        for i in navMpa.findChildren("navPoint"):
            #print(i.attrs["playOrder"])    index of Table of content
            #print(i.findChildren("content")[0].attrs["src"])     Address of table of content
            #tocKey = ""
            tocKey = i.findChildren("content")[0].attrs["src"]
            '''try:
                tocKey = i.findChildren("content")[0].attrs["src"].split("/")[1]
                print(i.findChildren("content")[0].attrs["src"].split("/")[1], "This is tockey")
            except:
                tocKey = i.findChildren("content")[0].attrs["src"]
                print(i.findChildren("content")[0].attrs["src"], "This is tockey")
            '''
            try:
                self.reordered_manifest_byhref[tocKey].name = i.findChildren("text")[0].get_text()
                #self.reordered_manifest[tocKey].name = i.findChildren("text")[0].get_text()
                self.TOC.append(self.reordered_manifest_byhref[tocKey])
            except:
                pass
            
        #for i in self.reordered_manifest.values():
        for i in self.TOC:
            i.getItemData()
        

    def deleteTempFolder(self):
        shutil.rmtree(self.tempAddress)
'''
if __name__ == "__main__":
    newBook = Book("book.epub")
    if newBook.checkEpub():
        newBook.getContainerXml()
        newBook.constructSpine()
        newBook.getToc()
        newBook.deleteTempFolder()
'''