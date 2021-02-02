#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets
import mainwindow  # Это наш конвертированный файл дизайна

import os
from fpdf import FPDF
from PIL import Image
import re
from tqdm import tqdm
import shutil
import piexif


class ExampleApp(QtWidgets.QMainWindow, mainwindow.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.btnBrowse.clicked.connect(self.browse_folder)  # Выполнить функцию browse_folder
                                                            # при нажатии кнопки
    def print(self,message):
        self.plainTextEdit.insertPlainText(message+"\n")

    def browse_folder(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select folder with JPEGs")
        # открыть диалог выбора директории и установить значение переменной
        # равной пути к выбранной директории

        if not directory:  # не продолжать выполнение, если пользователь не выбрал директорию
            self.print('Select directory with JPEGs')

        path = directory
        pdf_filename = 'output.pdf'
        files = [f for f in os.listdir(path) if re.match(r'\S+\.jpg', f, re.IGNORECASE)]

        if len(files)<1:

            error_dialog = QtWidgets.QErrorMessage()
            error_dialog.showMessage('not found *.jpg files')
            self.print('not found *.jpg files')
            #quit('not found *.jpg files')
            return

        self.process(path, 'output_quality70.pdf', jpg_quality=70)
        self.process(path, 'output_quality90.pdf', jpg_quality=90)        
        
    def process(path, pdf_filename, jpg_quality = 90):
        with tqdm(total=10) as outer_pbar:
            outer_pbar.update(1)
            self.print('Creating temporary folders')
            PATH_STAGE1 = os.path.join(path,'_tmp_stage1')
            PATH_STAGE2 = os.path.join(path,'_tmp_stage2')
            PATH_STAGE3 = os.path.join(path,'_tmp_stage3')
            self.makeSubdir(PATH_STAGE1)
            self.makeSubdir(PATH_STAGE2)
            self.makeSubdir(PATH_STAGE3)
            outer_pbar.update(1)
            self.copy2subfolder(path,PATH_STAGE1)
            outer_pbar.update(1)
            self.print('Sharpering')
            self.sharpering(PATH_STAGE1,PATH_STAGE2, jpg_quality)
            outer_pbar.update(1)

            self.print('drop EXIF')
            self.dropEXIF(PATH_STAGE2,PATH_STAGE3)
            outer_pbar.update(1)

            self.print('Making PDF')
            self.makePdf(PATH_STAGE3,pdf_filename)
            outer_pbar.update(1)
            shutil.move(os.path.join(PATH_STAGE3,pdf_filename),os.path.join(path,pdf_filename))
            self.print('Removing temporary files')
            outer_pbar.update(1)
            shutil.rmtree(PATH_STAGE1)
            outer_pbar.update(1)
            shutil.rmtree(PATH_STAGE2)
            outer_pbar.update(1)
            shutil.rmtree(PATH_STAGE3)
            outer_pbar.update(1)
            self.print('PDF is ready')
                

    def makePdf(self,dir,pdfFileName):

        listPages = self.getImagesList(dir)

        cover = Image.open(os.path.join(dir,str(listPages[0])))
        width, height = cover.size

        pdf = FPDF(unit = "pt", format = [width, height])
        #pdf.set_author(u'')
        #pdf.set_title(u'')
        #pdf.set_subject('')

        for page in tqdm(listPages):
            pdf.add_page()
            pdf.image(os.path.join(dir,str(page)), 0, 0)

        pdf.output(os.path.join(dir,pdfFileName), "F")

    def makeSubdir(self,dirpath):
        if os.path.exists(dirpath) and os.path.isdir(dirpath): shutil.rmtree(dirpath)
        os.mkdir(dirpath)

    def copy2subfolder(self,folder,new_folder):
        files = self.getImagesList(folder)
        for f in files:
            shutil.copyfile(os.path.join(folder,f),os.path.join(new_folder,f))

    def sharpering(self,folder,new_folder, jpg_quality=90):
        from PIL import Image
        from PIL import ImageFilter

        files = self.getImagesList(folder)
        for f in files:
            #shutil.copyfile(os.path.join(folder,f),os.path.join(new_folder,f))

            # Open an already existing image
            imageObject = Image.open(os.path.join(folder,f));

            # Apply sharp filter
            sharpened1 = imageObject.filter(ImageFilter.SHARPEN);
            sharpened1.save(os.path.join(new_folder,f),quality = jpg_quality,subsampling=0)

    def dropEXIF(self,folder,new_folder):
        files = self.getImagesList(folder)
        for f in files:
            shutil.copyfile(os.path.join(folder,f),os.path.join(new_folder,f))

        files = self.getImagesList(new_folder)
        for f in tqdm(files, desc='remove EXIF tags'):
            piexif.remove(os.path.join(new_folder,f))

    def getImagesList(self,path):
        # return list with images in folder
        files = [f for f in os.listdir(path) if re.match(r'\S+\.jpg', f, re.IGNORECASE)]
        return files

def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
